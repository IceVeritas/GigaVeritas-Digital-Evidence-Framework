#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
GigaVeritas Digital Evidence Framework — Módulo de Trazabilidad Temporal (V2.0.0)
================================================================================

Proyecto       : GigaVeritas-Digital-Evidence-Framework
Organización   : IceVeritas
Autor          : Atanas Atanasov
Módulo         : time_stamp.py
Dependencia    : Biblioteca estándar de Python
Versión        : 2.0.0

Marco metodológico:
    ISO/IEC 27037:2012 — Guidelines for identification, collection,
    acquisition and preservation of digital evidence.

Compatibilidad : Python 3.10+ (biblioteca estándar; Windows / Linux)

Descripción:
    Ejecuta el descubrimiento recursivo de archivos asociados a los registros
    de un expediente local. Calcula huellas SHA-256, registra el tamaño y los
    atributos temporales del sistema de archivos y comprueba posibles cambios
    detectables durante la lectura.

    Incorpora un bloque descriptivo de los archivos descubiertos en una copia
    derivada del documento HTML original y genera un informe JSON independiente
    con los resultados del procesamiento. Registra asimismo la ejecución
    mediante un archivo de log.

Alcance y limitaciones metodológicas:
    Este módulo procesa expedientes locales previamente recopilados. No realiza
    captura ni scraping en vivo. Los timestamps registrados corresponden a
    atributos del sistema de archivos y no acreditan necesariamente el momento
    original de creación o captura del contenido.

    SHA-256 permite identificar y comparar los bytes examinados, pero no
    demuestra por sí solo autenticidad, autoría, procedencia ni integridad
    histórica de los archivos.

    Los archivos originales se leen sin modificaciones deliberadas. Los
    resultados se generan en un directorio de salida independiente.

Documentación:
    docs/TIME_STAMP.md

Nota sobre el marco metodológico:
    La ISO/IEC 27037:2012 se utiliza como referencia metodológica. Su mención
    no implica certificación ni conformidad integral del software con dicha
    norma.

Estado         : [PENDIENTE DE CLASIFICACIÓN]
================================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Catálogo común del proyecto IceVeritas.
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".heic", ".heif", ".gif"}
VIDEO_EXT = {".mp4", ".mkv", ".avi", ".mov"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".odt", ".txt", ".html", ".mht"}
EMAIL_EXT = {".eml", ".msg", ".pst", ".ost", ".mbox"}
ALL_EXTS = IMAGE_EXT | VIDEO_EXT | AUDIO_EXT | DOC_EXT | EMAIL_EXT

RECORD_ID_RE = re.compile(r"\bAUD-A8-REYRAN-\d{4}\b")
ARTICLE_RE = re.compile(
    r"<article\b(?=[^>]*\bclass\s*=\s*(['\"])[^'\"]*\bcard\b[^'\"]*\1)[^>]*>.*?</article\s*>",
    re.IGNORECASE | re.DOTALL,
)
DIV_TAG_RE = re.compile(r"<div\b[^>]*>|</div\s*>", re.IGNORECASE)


def utc_now_stamp() -> str:
    """Identificador de ejecución UTC con microsegundos y sufijo único."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "_" + uuid.uuid4().hex[:8]


def get_file_category(suffix: str) -> str:
    suffix = suffix.lower()
    if suffix in IMAGE_EXT:
        return "IMAGE"
    if suffix in VIDEO_EXT:
        return "VIDEO"
    if suffix in AUDIO_EXT:
        return "AUDIO"
    if suffix in DOC_EXT:
        return "DOCUMENT"
    if suffix in EMAIL_EXT:
        return "EMAIL"
    return "UNKNOWN"


def setup_logger(output_dir: Path, run_stamp: str) -> logging.Logger:
    """Crea un logger aislado para esta ejecución, sin acumular handlers."""
    logger = logging.getLogger(f"IceVeritas.TimeStampSync.{run_stamp}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
    file_handler = logging.FileHandler(
        output_dir / f"time_stamp_sync_{run_stamp}.log", encoding="utf-8"
    )
    stream_handler = logging.StreamHandler()
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def hash_and_stat_file(filepath: Path) -> dict[str, Any]:
    """
    Calcula el hash leyendo un descriptor abierto y obtiene stat del mismo
    descriptor. Registra si el tamaño/mtime cambió durante la lectura.
    """
    try:
        with filepath.open("rb") as stream:
            before = os.fstat(stream.fileno())
            digest = hashlib.sha256()
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
            after = os.fstat(stream.fileno())

        changed_during_read = (
            before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
        )
        return {
            "sha256": digest.hexdigest(),
            "hash_status": "OK",
            "size_bytes": after.st_size,
            "mtime_utc": datetime.fromtimestamp(
                after.st_mtime, timezone.utc
            ).isoformat(timespec="seconds").replace("+00:00", "Z"),
            # ctime tiene significado distinto según el sistema operativo.
            "ctime_utc": datetime.fromtimestamp(
                after.st_ctime, timezone.utc
            ).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "file_changed_during_read": changed_during_read,
        }
    except OSError as exc:
        return {
            "sha256": None,
            "hash_status": "ERROR",
            "hash_error": f"{type(exc).__name__}: {exc}",
            "size_bytes": None,
            "mtime_utc": None,
            "ctime_utc": None,
            "file_changed_during_read": None,
        }


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def remove_previous_artifact_block(card_html: str) -> str:
    """
    Elimina un bloque previo completo contando etiquetas DIV anidadas.
    Evita el fallo de una regex simple ante los DIV interiores del bloque.
    """
    marker = re.search(
        r'<div\b(?=[^>]*\bclass\s*=\s*([\'"])[^\'"]*\bforensic-artifacts-block\b[^\'"]*\1)[^>]*>',
        card_html,
        re.IGNORECASE,
    )
    if not marker:
        return card_html

    depth = 0
    for tag in DIV_TAG_RE.finditer(card_html, marker.start()):
        token = tag.group(0)
        if token[:4].lower() == "<div":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return card_html[:marker.start()] + card_html[tag.end():]
    # Si el bloque está mal formado, no se elimina parcialmente.
    return card_html


def build_artifact_block(artifacts: list[dict[str, Any]]) -> str:
    rows = []
    for artifact in artifacts:
        filename = html.escape(str(artifact["filename"]), quote=True)
        category = html.escape(str(artifact["category"]), quote=True)
        digest = artifact.get("sha256")
        digest_text = html.escape(digest if digest else "NO DISPONIBLE")
        hash_status = html.escape(str(artifact.get("hash_status", "UNKNOWN")))
        mtime = html.escape(str(artifact.get("mtime_utc") or "NO DISPONIBLE"))

        rows.append(
            f"""
            <div class="mb-2 small" style="border-left: 3px solid #6c757d; padding-left: 10px;">
                <strong>{category}:</strong> {filename}<br>
                <span style="font-family: monospace;">SHA-256: {digest_text}</span><br>
                <span>Estado del hash: {hash_status}</span><br>
                <span class="text-muted">FS mtime (UTC): {mtime}</span>
            </div>"""
        )

    return f"""
    <div class="forensic-artifacts-block mt-3 p-3 bg-light border rounded" data-field="forensic-artifacts">
        <h6 class="text-uppercase text-muted mb-2" style="font-size: 0.85rem;">Artefactos descubiertos</h6>
        {''.join(rows)}
        <div class="text-muted mt-2" style="font-size: 0.75rem;">
            <em>Nota metodológica: SHA-256 identifica el contenido binario leído durante esta ejecución.
            Los timestamps son atributos del sistema de archivos; por sí solos no acreditan
            autenticidad, autoría ni momento de captura.</em>
        </div>
    </div>
    """


def extract_record_id(card_html: str, index: int) -> str:
    match = RECORD_ID_RE.search(card_html)
    return match.group(0) if match else f"UNKNOWN_{index}"


def discover_artifacts(
    record_folder: Path,
    input_root: Path,
    logger: logging.Logger,
) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []

    # No se acepta una carpeta de registro que sea enlace o salga de la raíz.
    try:
        if record_folder.is_symlink():
            logger.warning("Carpeta de registro enlazada; omitida: %s", record_folder)
            return artifacts
        resolved_record = record_folder.resolve(strict=True)
        if not is_within(resolved_record, input_root):
            logger.warning("Carpeta fuera de la raíz; omitida: %s", record_folder)
            return artifacts
        if not resolved_record.is_dir():
            return artifacts
    except OSError as exc:
        logger.warning("No se pudo validar carpeta %s: %s", record_folder, exc)
        return artifacts

    try:
        candidates = resolved_record.rglob("*")
        for candidate in candidates:
            try:
                # La comprobación precede a is_file() y resolve().
                if candidate.is_symlink():
                    logger.warning("Enlace simbólico omitido: %s", candidate)
                    continue
                if not candidate.is_file():
                    continue

                resolved = candidate.resolve(strict=True)
                if not is_within(resolved, resolved_record):
                    logger.warning("Ruta fuera de la carpeta del registro: %s", candidate)
                    continue
                if candidate.suffix.lower() not in ALL_EXTS:
                    continue

                file_info = hash_and_stat_file(candidate)
                artifacts.append({
                    "filename": candidate.name,
                    "relative_path": candidate.relative_to(input_root).as_posix(),
                    "category": get_file_category(candidate.suffix),
                    **file_info,
                })
            except (OSError, RuntimeError, ValueError) as exc:
                logger.warning("Archivo omitido durante validación %s: %s", candidate, exc)
    except OSError as exc:
        logger.warning("Error recorriendo %s: %s", resolved_record, exc)

    artifacts.sort(key=lambda item: (item["category"], item["relative_path"]))
    return artifacts


def process_and_fix_forensics(
    root_dir: Path,
    output_dir: Path,
    html_filename: str = "index.html",
) -> tuple[Path, Path]:
    try:
        root_dir = root_dir.resolve(strict=True)
        if not root_dir.is_dir():
            raise NotADirectoryError(f"Directorio de entrada inválido: {root_dir}")

        # Impide rutas absolutas o subrutas en --index.
        if Path(html_filename).name != html_filename or html_filename in {"", ".", ".."}:
            raise ValueError("--index debe ser un nombre de archivo, no una ruta.")

        output_resolved = output_dir.resolve(strict=False)
        if is_within(output_resolved, root_dir):
            raise ValueError(
                "El directorio de salida no puede ser igual ni estar dentro "
                "del directorio de entrada."
            )
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Error crítico en rutas: {exc}") from exc

    run_stamp = utc_now_stamp()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir = output_dir.resolve(strict=True)
    logger = setup_logger(output_dir, run_stamp)

    try:
        html_path = root_dir / html_filename
        if html_path.is_symlink():
            raise ValueError("El HTML de entrada es un enlace simbólico.")
        html_resolved = html_path.resolve(strict=True)
        if not is_within(html_resolved, root_dir) or not html_resolved.is_file():
            raise ValueError("El HTML de entrada no es un archivo regular dentro de la raíz.")

        html_content = html_resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError, RuntimeError, ValueError) as exc:
        logger.exception("No se pudo leer/validar el HTML de entrada: %s", exc)
        raise SystemExit(f"No se pudo procesar el HTML: {exc}") from exc

    articles = list(ARTICLE_RE.finditer(html_content))
    if not articles:
        logger.warning("No se encontraron elementos <article class='card...'> en el HTML.")

    audit_results: list[dict[str, Any]] = []
    replacements: list[tuple[int, int, str]] = []

    logger.info("Inicio de sincronización; raíz de entrada: %s", root_dir)
    logger.info("Registros HTML detectados: %d", len(articles))

    for index, match in enumerate(articles, 1):
        card_html = match.group(0)
        record_id = extract_record_id(card_html, index)

        # Los IDs válidos proceden de una expresión cerrada; UNKNOWN es generado aquí.
        folder_path = root_dir / record_id
        if not folder_path.exists() and record_id.startswith("AUD-A8-REYRAN-"):
            alternative = root_dir / record_id.replace("-", "_")
            if alternative.exists():
                folder_path = alternative

        artifacts = discover_artifacts(folder_path, root_dir, logger) if folder_path.exists() else []
        audit_results.append({
            "record_id": record_id,
            "record_folder": (
                folder_path.relative_to(root_dir).as_posix()
                if is_within(folder_path, root_dir) else None
            ),
            "artifacts_discovered": len(artifacts),
            "artifacts": artifacts,
        })

        cleaned_card = remove_previous_artifact_block(card_html)
        if artifacts:
            block = build_artifact_block(artifacts)
            closing = re.search(r"</article\s*>", cleaned_card, re.IGNORECASE)
            if closing:
                cleaned_card = (
                    cleaned_card[:closing.start()]
                    + block
                    + "\n"
                    + cleaned_card[closing.start():]
                )

        replacements.append((match.start(), match.end(), cleaned_card))
        logger.info("%s | %d artefactos descubiertos", record_id, len(artifacts))

    # Sustituye desde el final para no desplazar los offsets originales.
    updated_html = html_content
    for start, end, replacement in reversed(replacements):
        updated_html = updated_html[:start] + replacement + updated_html[end:]

    html_path_out = output_dir / f"{Path(html_filename).stem}_FIXED.html"
    json_path_out = output_dir / f"time_stamp_sync_{run_stamp}.json"

    try:
        html_path_out.write_text(updated_html, encoding="utf-8")
        with json_path_out.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                {
                    "tool": "IceVeritas time_stamp_sync",
                    "version": "2.0.0",
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "source_html": html_filename,
                    "records_processed": len(audit_results),
                    "records": audit_results,
                },
                stream,
                ensure_ascii=False,
                indent=2,
            )
            stream.write("\n")
    except OSError as exc:
        logger.exception("Error escribiendo resultados derivados: %s", exc)
        raise

    logger.info("HTML derivado generado: %s", html_path_out)
    logger.info("JSON generado: %s", json_path_out)
    logger.info("El directorio fuente no se ha utilizado como destino de escritura.")

    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    return html_path_out, json_path_out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="IceVeritas: sincronizador descriptivo HTML/JSON (sin modificar originales)"
    )
    parser.add_argument(
        "--input", type=Path, required=True,
        help="Directorio raíz del expediente original",
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Directorio independiente para HTML, JSON y log derivados",
    )
    parser.add_argument(
        "--index", default="index.html",
        help="Nombre del HTML original situado directamente en --input",
    )
    args = parser.parse_args()
    process_and_fix_forensics(args.input, args.output, args.index)


if __name__ == "__main__":
    main()
