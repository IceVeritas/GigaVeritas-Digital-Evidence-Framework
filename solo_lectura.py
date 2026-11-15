#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GigaVeritas Digital Evidence Framework — Módulo Solo Lectura (V9.2)
================================================================================

Proyecto       : GigaVeritas-Digital-Evidence-Framework
Organización   : IceVeritas
Autor          : Atanas Atanasov
Módulo         : solo_lectura.py
Dependencia    : forensic_core.py (IceVeritas-Core 2.3.0)
Versión        : V9.2

Marco metodológico:
    ISO/IEC 27037:2012 — Guidelines for identification, collection,
    acquisition and preservation of digital evidence.
Compatibilidad : Python 3.7+ (biblioteca estándar; Windows / Linux)

Descripción:
    Ejecuta el inventario técnico en modo de solo lectura sobre un expediente
    local estructurado mediante un índice HTML y carpetas por identificador.
    Calcula huellas SHA-256 sobre descriptores abiertos, aplica límites de
    seguridad para el recorrido del sistema de archivos, inspecciona metadatos
    internos (PNG, OOXML, EML) y registra la identidad física de la carpeta
    raíz del expediente.

Alcance y limitaciones metodológicas:
    Este programa procesa archivos locales previamente recopilados. No realiza
    captura ni scraping en vivo, ni acredita por sí solo la autoría, autenticidad
    o procedencia original de los archivos. Los timestamps del sistema de
    archivos (mtime/ctime) son atributos locales observados y no constituyen
    un sellado de tiempo confiable.

Nota sobre el marco metodológico:
    La ISO/IEC 27037:2012 se utiliza como referencia metodológica. Su mención
    no implica certificación ni conformidad integral del software con dicha
    norma.

Estado         : [PENDIENTE DE CLASIFICACIÓN]

================================================================================
"""


from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import forensic_core as fc

# ==============================================================================
# CONSTANTES Y METADATOS DEL MÓDULO
# ==============================================================================
PROJECT_NAME = "GigaVeritas-Digital-Evidence-Framework"
BRAND_NAME = "IceVeritas"
AUTHOR_NAME = "Atanas  Atanasov"
PROJECT_PROFILE = "IceDux.art"
PROGRAM_VERSION = "Solo Lectura V9.2"
SCHEMA_VERSION = "iceveritas.solo_lectura.report.v1"

MAX_FILE_SIZE = 50 * 1024 * 1024 * 1024  # Límite por archivo: 50 GiB
MAX_TRAVERSAL_DEPTH = 32                  # Profundidad máxima de subdirectorios


# ==============================================================================
# CONFIGURACIÓN DE REGISTRO (LOGGING) Y VALIDACIONES DE ENTRADA
# ==============================================================================
def setup_logger(output_dir: Path, run_stamp: str) -> logging.Logger:
    """Inicializa un logger aislado por ejecución con salida a archivo y consola."""
    logger = logging.getLogger(f"IceVeritas.ForensicAudit.{run_stamp}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)sZ [%(levelname)s] %(message)s", "%Y-%m-%dT%H:%M:%S")

    fh = logging.FileHandler(output_dir / f"solo_lectura_{run_stamp}.log", encoding="utf-8")
    sh = logging.StreamHandler()
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def _validate_index_name(index_name: str) -> None:
    """Valida estrictamente que --index sea solo un nombre de archivo local sin rutas."""
    if not index_name:
        raise ValueError("El nombre del índice no puede estar vacío.")
    if os.sep in index_name or (os.altsep and os.altsep in index_name):
        raise ValueError(f"El índice no debe contener separadores de ruta ('{os.sep}' o '{os.altsep}').")
    if index_name in {".", ".."}:
        raise ValueError("El índice no puede ser una referencia relativa a directorios.")
    p = Path(index_name)
    if p.is_absolute() or len(p.parts) > 1:
        raise ValueError("El índice debe ser estrictamente un nombre de archivo (sin rutas).")


def _get_root_identity(root: Path) -> dict[str, Any]:
    """Captura identificadores físicos del volumen/sistema de archivos para la raíz."""
    try:
        st = root.stat()
        return {
            "st_dev": st.st_dev,
            "st_ino": getattr(st, "st_ino", None),
            "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
            "ctime_utc": datetime.fromtimestamp(st.st_ctime, timezone.utc).isoformat(),
            "error": None,
        }
    except OSError as exc:
        return {"st_dev": None, "st_ino": None, "mtime_utc": None, "ctime_utc": None, "error": str(exc)}


# ==============================================================================
# EXTRACCIÓN DE IDENTIFICADORES Y METADATOS TÉCNICOS
# ==============================================================================
def _extract_record_ids(html_text: str) -> list[str]:
    """Extrae identificadores únicos de expediente desde bloques <article> del HTML."""
    cards = re.findall(r"<article\b[^>]*>.*?</article\s*>", html_text, flags=re.IGNORECASE | re.DOTALL)
    found: list[str] = []
    seen: set[str] = set()
    id_pattern = re.compile(r"\b([A-Z0-9]+(?:-[A-Z0-9]+)*-\d{4})\b", re.IGNORECASE)
    for card in cards:
        match = id_pattern.search(card)
        if match:
            record_id = match.group(1)
            if record_id not in seen:
                seen.add(record_id)
                found.append(record_id)
    return found


def _metadata_for_file(filepath: Path, extension: str) -> dict[str, Any]:
    """Despacha la inspección estructural de metadatos según la extensión del archivo."""
    metadata: dict[str, Any] = {
        "observed_timestamp": None,
        "source_origin": None,
        "metadata_status": "NOT_ANALYZED",
        "metadata_errors": [],
        "metadata_details": {},
    }

    # 1. Imágenes PNG: validación binaria de firma, chunks (IHDR/IDAT/IEND), CRC32 y tIME/tEXt
    if extension == ".png":
        parsed = fc.inspect_png_binary_chunks(filepath)
        metadata["metadata_details"]["png_validation"] = parsed
        metadata["metadata_errors"].extend(parsed["errors"])
        if parsed["chunk_tIME"]:
            metadata["observed_timestamp"] = parsed["chunk_tIME"]
            metadata["source_origin"] = "PNG_CHUNK_tIME"
            metadata["metadata_status"] = "EXTRACTED" if parsed["structure_status"] == "VALIDATED" else "ERROR"
        elif "Creation Time" in parsed["text_metadata"]:
            metadata["observed_timestamp"] = parsed["text_metadata"]["Creation Time"]
            metadata["source_origin"] = "PNG_tEXt_CreationTime"
            metadata["metadata_status"] = "EXTRACTED" if parsed["structure_status"] == "VALIDATED" else "ERROR"
        else:
            metadata["metadata_status"] = "ERROR" if parsed["structure_status"] == "ERROR" else "NOT_FOUND"
        return metadata

    # 2. Documentos OOXML (.docx, .xlsx): extracción de dcterms:created en docProps/core.xml
    if extension in {".docx", ".xlsx"}:
        parsed = fc.inspect_ooxml(filepath)
        metadata["metadata_details"]["ooxml"] = parsed
        metadata["metadata_status"] = parsed["status"]
        if parsed.get("error"):
            metadata["metadata_errors"].append(parsed["error"])
        if parsed.get("created"):
            metadata["observed_timestamp"] = parsed["created"]
            metadata["source_origin"] = "OOXML_core_xml_dcterms_created"
        return metadata

    # 3. Correos electrónicos (.eml): extracción y normalización UTC de cabecera Date
    if extension == ".eml":
        parsed = fc.inspect_eml(filepath)
        metadata["metadata_details"]["eml"] = parsed
        metadata["metadata_status"] = parsed["status"]
        if parsed.get("error"):
            metadata["metadata_errors"].append(parsed["error"])
        if parsed.get("date_utc"):
            metadata["observed_timestamp"] = parsed["date_utc"]
            metadata["source_origin"] = "EML_HEADER_Date"
        elif parsed.get("date_raw"):
            metadata["observed_timestamp"] = parsed["date_raw"]
            metadata["source_origin"] = "EML_HEADER_Date_RAW"
        return metadata

    return metadata


# ==============================================================================
# FLUJO PRINCIPAL DE AUDITORÍA EN MODO SOLO LECTURA
# ==============================================================================
def run_forensic_audit(root_dir: Path, output_dir: Path, html_filename: str = "index.html") -> Path:
    """Ejecuta el recorrido auditado, cálculo SHA-256 y generación del informe JSON."""
    _validate_index_name(html_filename)

    root = fc.validate_input_root(root_dir)
    output = fc.validate_output_dir(root, output_dir)
    index_path = fc.validate_regular_file(root / html_filename, root)

    output.mkdir(parents=True, exist_ok=True)
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_id = str(uuid.uuid4())
    logger = setup_logger(output, run_stamp)

    initial_root_identity = _get_root_identity(root)
    logger.info(f"Inicio de inventario técnico — {PROJECT_NAME} | {PROGRAM_VERSION}")

    try:
        html_text = index_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        logger.exception("Fallo crítico al leer el índice HTML")
        raise

    record_ids = _extract_record_ids(html_text)

    audit_results: list[dict[str, Any]] = []
    security_stats = {
        "symlinks_detected": 0,
        "reparse_points_detected": 0,
        "depth_limit_exceeded": 0,
        "access_denied": 0,
        "path_outside_root": 0,
        "skipped_files_too_large": 0,
    }
    security_events: list[dict[str, Any]] = []
    skipped_files: list[dict[str, Any]] = []

    for record_id in record_ids:
        candidate_dirs = [root / record_id, root / record_id.replace("-", "_")]
        folder_path = next(
            (c.resolve(strict=True) for c in candidate_dirs if c.exists() and c.is_dir() and fc.is_within(c.resolve(), root)),
            None,
        )

        record: dict[str, Any] = {
            "record_id": record_id,
            "folder_exists": folder_path is not None,
            "evidences": [],
        }

        if folder_path is not None:
            for item in fc.iter_files_audited(folder_path, root, max_depth=MAX_TRAVERSAL_DEPTH):
                # 1. Registro de incidentes y bloqueos de seguridad en el recorrido
                if item["status"] != "OK":
                    rel_path = item["path"].relative_to(root).as_posix() if fc.is_within(item["path"], root) else str(item["path"])
                    event = {
                        "event_type": item["status"],
                        "relative_path": rel_path,
                        "timestamp_utc": fc.utc_now(),
                        "reason": item["error"] or "Política de seguridad",
                        "depth": item["depth"],
                    }
                    security_events.append(event)

                    if item["status"] == "SYMLINK_BLOCKED":
                        security_stats["symlinks_detected"] += 1
                    elif item["status"] == "REPARSE_POINT_BLOCKED":
                        security_stats["reparse_points_detected"] += 1
                    elif item["status"] == "DEPTH_LIMIT_EXCEEDED":
                        security_stats["depth_limit_exceeded"] += 1
                    elif item["status"] == "ACCESS_DENIED":
                        security_stats["access_denied"] += 1
                    elif item["status"] == "PATH_OUTSIDE_ROOT":
                        security_stats["path_outside_root"] += 1
                    continue

                # 2. Filtrado por catálogo de extensiones admitidas en Core
                filepath = item["path"]
                extension = filepath.suffix.lower()
                if extension not in fc.ALL_EXTS:
                    continue

                # 3. Comprobación de tamaño (50 GiB) y hashing SHA-256 sobre descriptor abierto
                hash_info = fc.hash_and_stat_file(filepath, max_size_bytes=MAX_FILE_SIZE)

                if hash_info["hash_status"] == "SKIPPED_FILE_TOO_LARGE":
                    security_stats["skipped_files_too_large"] += 1
                    rel_str = filepath.relative_to(root).as_posix()
                    skipped_files.append({
                        "filename": filepath.name,
                        "relative_path": rel_str,
                        "size_bytes": hash_info["size_bytes"],
                        "reason": "FILE_EXCEEDS_50GIB_LIMIT",
                    })
                    security_events.append({
                        "event_type": "FILE_SIZE_LIMIT_EXCEEDED",
                        "relative_path": rel_str,
                        "timestamp_utc": fc.utc_now(),
                        "reason": f"Tamaño ({hash_info['size_bytes']} bytes) supera 50 GiB.",
                        "depth": item["depth"],
                    })
                    continue

                # 4. Extracción de metadatos internos o respaldo con mtime del sistema de archivos
                metadata = _metadata_for_file(filepath, extension)
                if metadata["observed_timestamp"] is None:
                    metadata["observed_timestamp"] = hash_info.get("mtime_utc")
                    metadata["source_origin"] = "FILESYSTEM_MTIME" if hash_info.get("mtime_utc") else None

                evidence = {
                    "filename": filepath.name,
                    "relative_path": filepath.relative_to(root).as_posix(),
                    "extension": extension,
                    "sha256": hash_info.get("sha256"),
                    "hash_status": hash_info.get("hash_status"),
                    "hash_error": hash_info.get("hash_error"),
                    "observed_timestamp": metadata["observed_timestamp"],
                    "source_origin": metadata["source_origin"],
                    "metadata_status": metadata["metadata_status"],
                    "metadata_errors": metadata["metadata_errors"],
                    "metadata_details": metadata["metadata_details"],
                    "fs_timestamps": {
                        "mtime_utc": hash_info.get("mtime_utc"),
                        "ctime_utc": hash_info.get("ctime_utc"),
                    },
                }
                record["evidences"].append(evidence)
                logger.info(f"Evidencia examinada: {filepath.name} | hash={hash_info.get('hash_status')}")

        audit_results.append(record)

    # Verificación de integridad física de la carpeta raíz antes y después del recorrido
    final_root_identity = _get_root_identity(root)
    identity_discrepancy = initial_root_identity != final_root_identity
    if identity_discrepancy:
        security_events.append({
            "event_type": "ROOT_IDENTITY_CHANGED",
            "relative_path": ".",
            "timestamp_utc": fc.utc_now(),
            "reason": "Discrepancia detectada en atributos físicos de la raíz durante la auditoría.",
            "depth": 0,
        })

    # Serialización del informe JSON (esquema v1 compatible con manifest.py)
    report = {
        "schema": SCHEMA_VERSION,
        "project": PROJECT_NAME,
        "brand": BRAND_NAME,
        "author": AUTHOR_NAME,
        "program_version": PROGRAM_VERSION,
        "core_version": fc.VERSION_CORE,
        "run_id": run_id,
        "run_timestamp_utc": fc.utc_now(),
        "input_directory": str(root),
        "index_filename": html_filename,
        "output_directory": str(output),
        "root_identity": {
            "initial": initial_root_identity,
            "final": final_root_identity,
            "discrepancy_detected": identity_discrepancy,
        },
        "security_stats": security_stats,
        "security_events": security_events,
        "skipped_files": skipped_files,
        "records_found_in_index": len(record_ids),
        "records": audit_results,
        "scope_note": "Extracción técnica objetiva. El límite de tamaño, profundidad y seguridad en recorrido previene disrupción.",
    }

    output_json = output / f"solo_lectura_report_{run_stamp[:15]}_{run_id[:8]}.json"
    with output_json.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

    logger.info("Auditoría finalizada.")
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)
    return output_json


# ==============================================================================
# PUNTO DE ENTRADA CLI
# ==============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} ({BRAND_NAME}) — {PROGRAM_VERSION}"
    )
    parser.add_argument("--input", type=Path, required=True, help="Directorio raíz del expediente")
    parser.add_argument("--output", type=Path, required=True, help="Directorio aislado de salida")
    parser.add_argument("--index", default="index.html", help="Nombre del archivo HTML índice")
    args = parser.parse_args()

    try:
        report_path = run_forensic_audit(args.input, args.output, args.index)
        print(f"[DONE] Informe generado: {report_path}")
        return 0
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())