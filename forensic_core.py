#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
GigaVeritas Digital Evidence Framework — Forensic Core (2.3.0)
================================================================================

Proyecto       : GigaVeritas-Digital-Evidence-Framework
Organización   : IceVeritas
Autor          : Atanas Atanasov
Módulo         : forensic_core.py
Nombre interno : IceVeritas-Core
Versión        : 2.3.0
Dependencia    : Ninguna dependencia externa

Marco metodológico:
    ISO/IEC 27037:2012 — Guidelines for identification, collection,
    acquisition and preservation of digital evidence.

Descripción:
    Núcleo compartido de utilidades técnicas y validaciones del framework
    GigaVeritas. Proporciona funciones comunes para la clasificación de
    archivos, validación de rutas, control de acceso a directorios y
    archivos, recorrido auditado de estructuras documentales y cálculo
    de huellas criptográficas SHA-256.

    Implementa mecanismos de detección y tratamiento de enlaces simbólicos
    y puntos de reanálisis, controles de profundidad de recorrido y
    comprobaciones de identidad y estado de archivos mediante descriptores
    abiertos y os.fstat().

    Incorpora parsers estructurales para la inspección de archivos PNG,
    extracción de propiedades documentales OOXML y lectura de cabeceras
    de fecha de mensajes de correo electrónico EML.

Alcance y limitaciones metodológicas:
    Este módulo proporciona servicios técnicos compartidos para el
    procesamiento post-adquisición de expedientes digitales locales.
    No realiza captura ni adquisición de evidencias desde plataformas
    externas, ni acredita por sí solo autoría, autenticidad o procedencia
    original de los archivos.

    Las huellas SHA-256 permiten comprobar identidad binaria entre los
    contenidos comparados. Los metadatos y atributos temporales obtenidos
    representan información observada, no una certificación independiente
    de su origen o antigüedad.

Nota sobre el marco metodológico:
    La ISO/IEC 27037:2012 se utiliza como referencia metodológica.
    Su mención no implica certificación ni conformidad integral del
    software con dicha norma.

================================================================================
"""

from __future__ import annotations

import email
import hashlib
import os
import re
import stat
import struct
import zlib
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Iterator

VERSION_CORE = "IceVeritas-Core 2.3.0"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".heic", ".heif", ".gif"}
VIDEO_EXT = {".mp4", ".mkv", ".avi", ".mov"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".odt", ".txt", ".html", ".mht"}
EMAIL_EXT = {".eml", ".msg", ".pst", ".ost", ".mbox"}
ALL_EXTS = IMAGE_EXT | VIDEO_EXT | AUDIO_EXT | DOC_EXT | EMAIL_EXT


def get_file_category(suffix: str) -> str:
    """Devuelve una categoría estable a partir de una extensión de archivo."""
    ext = str(suffix or "").lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    if ext in IMAGE_EXT:
        return "IMAGE"
    if ext in VIDEO_EXT:
        return "VIDEO"
    if ext in AUDIO_EXT:
        return "AUDIO"
    if ext in DOC_EXT:
        return "DOCUMENT"
    if ext in EMAIL_EXT:
        return "EMAIL"
    return "UNKNOWN"

RECORD_ID_RE = re.compile(r"\bAUD-A8-REYRAN-\d{4}\b")
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_TEXT_MAX_BYTES = 1_048_576
IO_CHUNK_SIZE = 1024 * 1024


class ForensicPathError(RuntimeError):
    """Ruta no admisible o imposible de verificar."""


# ==========================================
# UTILIDADES Y VALIDACIÓN DE RUTAS
# ==========================================
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

def is_within(child: Path, parent: Path) -> bool:
    try:
        Path(child).relative_to(Path(parent))
        return True
    except ValueError:
        return False

def _is_link_or_reparse(path: Path, st: os.stat_result | None = None) -> bool:
    try:
        if path.is_symlink(): return True
        info = st if st is not None else path.lstat()
        return bool(getattr(info, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)
    except OSError:
        return True

def validate_input_root(path: Path) -> Path:
    p = Path(path).expanduser()
    if _is_link_or_reparse(p): raise ForensicPathError(f"Raíz de entrada es enlace/reparse point: {p}")
    resolved = p.resolve(strict=True)
    if not resolved.is_dir(): raise NotADirectoryError(str(resolved))
    return resolved

def validate_output_dir(input_root: Path, output_dir: Path) -> Path:
    root = Path(input_root).resolve(strict=True)
    out = Path(output_dir).expanduser()
    probe = out
    while not probe.exists() and probe.parent != probe: probe = probe.parent
    if probe.exists() and _is_link_or_reparse(probe):
        raise ForensicPathError(f"La ruta de salida atraviesa un enlace/reparse point: {probe}")
    resolved = out.resolve(strict=False)
    if is_within(resolved, root): raise ForensicPathError("La salida no puede estar dentro de la entrada.")
    return resolved

def _relative_under(path: Path, root: Path) -> Path:
    try: return Path(path).absolute().relative_to(Path(root).resolve(strict=True))
    except ValueError as exc: raise ForensicPathError(f"Ruta fuera de la raíz: {path}") from exc

def validate_directory(path: Path, allowed_root: Path) -> Path:
    root = Path(allowed_root).resolve(strict=True)
    rel = _relative_under(path, root)
    cur = root
    if _is_link_or_reparse(cur): raise ForensicPathError(f"Raíz no admisible: {cur}")
    for part in rel.parts:
        cur = cur / part
        try: st = cur.lstat()
        except OSError as exc: raise ForensicPathError(f"No se puede inspeccionar {cur}: {exc}") from exc
        if _is_link_or_reparse(cur, st): raise ForensicPathError(f"Enlace/reparse point: {cur}")
    resolved = Path(path).resolve(strict=True)
    if not is_within(resolved, root) or not resolved.is_dir(): raise ForensicPathError(f"Directorio no admisible: {path}")
    return resolved

def validate_regular_file(path: Path, allowed_root: Path) -> Path:
    root = Path(allowed_root).resolve(strict=True)
    rel = _relative_under(path, root)
    cur = root
    if _is_link_or_reparse(cur): raise ForensicPathError(f"Raíz no admisible: {cur}")
    for part in rel.parts:
        cur = cur / part
        try: st = cur.lstat()
        except OSError as exc: raise ForensicPathError(f"No se puede inspeccionar {cur}: {exc}") from exc
        if _is_link_or_reparse(cur, st): raise ForensicPathError(f"Enlace/reparse point: {cur}")
    resolved = Path(path).resolve(strict=True)
    if not is_within(resolved, root) or not resolved.is_file(): raise ForensicPathError(f"Archivo no admisible: {path}")
    return resolved

def iter_files_safe(folder: Path, allowed_root: Path) -> Iterator[Path]:
    """Iterador seguro resistente a enlaces simbólicos y Path Traversal."""
    root = Path(allowed_root).resolve(strict=True)
    start = validate_directory(folder, root)
    stack = [start]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    p = Path(entry.path)
                    try:
                        st = entry.stat(follow_symlinks=False)
                        if _is_link_or_reparse(p, st): continue
                        if stat.S_ISDIR(st.st_mode):
                            d = p.resolve(strict=True)
                            if is_within(d, root): stack.append(d)
                        elif stat.S_ISREG(st.st_mode):
                            yield validate_regular_file(p, root)
                    except (OSError, ForensicPathError): continue
        except OSError: continue


def iter_files_audited(
    folder: Path,
    allowed_root: Path,
    max_depth: int = 32,
) -> Iterator[dict[str, Any]]:
    """Recorre un expediente y emite tanto archivos admitidos como incidencias.

    Cada elemento tiene: path, status, error y depth. Los archivos regulares
    admitidos llevan status=OK. Los elementos bloqueados se emiten como eventos
    para que el llamador pueda conservar trazabilidad de los descartes.
    La profundidad de la carpeta inicial es 0.
    """
    if not isinstance(max_depth, int) or isinstance(max_depth, bool) or max_depth < 0:
        raise ValueError("max_depth debe ser un entero mayor o igual que cero")

    root = Path(allowed_root).resolve(strict=True)
    start = validate_directory(folder, root)
    stack: list[tuple[Path, int]] = [(start, 0)]

    while stack:
        current, depth = stack.pop()
        try:
            entries_context = os.scandir(current)
            with entries_context as entries:
                try:
                    for entry in entries:
                        candidate = Path(entry.path)
                        try:
                            st = entry.stat(follow_symlinks=False)
                        except PermissionError as exc:
                            yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth + 1}
                            continue
                        except OSError as exc:
                            yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth + 1}
                            continue

                        attrs = getattr(st, "st_file_attributes", 0)
                        is_reparse = bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT)
                        try:
                            is_symlink = entry.is_symlink()
                        except OSError:
                            is_symlink = False

                        if is_symlink:
                            yield {"path": candidate, "status": "SYMLINK_BLOCKED", "error": "Enlace simbólico bloqueado; no se siguió.", "depth": depth + 1}
                            continue
                        if is_reparse:
                            yield {"path": candidate, "status": "REPARSE_POINT_BLOCKED", "error": "Punto de reanálisis bloqueado; no se siguió.", "depth": depth + 1}
                            continue

                        if stat.S_ISDIR(st.st_mode):
                            child_depth = depth + 1
                            if child_depth > max_depth:
                                yield {"path": candidate, "status": "DEPTH_LIMIT_EXCEEDED", "error": f"Límite de profundidad ({max_depth}) superado.", "depth": child_depth}
                                continue
                            try:
                                resolved_dir = candidate.resolve(strict=True)
                                if not is_within(resolved_dir, root):
                                    yield {"path": candidate, "status": "PATH_OUTSIDE_ROOT", "error": "El directorio resuelve fuera de la raíz autorizada.", "depth": child_depth}
                                    continue
                                # Revalidar cada componente antes de incorporarlo a la pila.
                                safe_dir = validate_directory(candidate, root)
                                stack.append((safe_dir, child_depth))
                            except PermissionError as exc:
                                yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": child_depth}
                            except ForensicPathError as exc:
                                status = "PATH_OUTSIDE_ROOT" if "fuera de la raíz" in str(exc).lower() or "fuera" in str(exc).lower() else "REPARSE_POINT_BLOCKED"
                                yield {"path": candidate, "status": status, "error": str(exc), "depth": child_depth}
                            except OSError as exc:
                                yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": child_depth}
                        elif stat.S_ISREG(st.st_mode):
                            try:
                                safe_file = validate_regular_file(candidate, root)
                                yield {"path": safe_file, "status": "OK", "error": None, "depth": depth + 1}
                            except PermissionError as exc:
                                yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth + 1}
                            except ForensicPathError as exc:
                                status = "PATH_OUTSIDE_ROOT" if "fuera" in str(exc).lower() else "REPARSE_POINT_BLOCKED"
                                yield {"path": candidate, "status": status, "error": str(exc), "depth": depth + 1}
                            except OSError as exc:
                                yield {"path": candidate, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth + 1}
                except PermissionError as exc:
                    yield {"path": current, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth}
        except PermissionError as exc:
            yield {"path": current, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth}
        except OSError as exc:
            yield {"path": current, "status": "ACCESS_DENIED", "error": str(exc), "depth": depth}


# ==========================================
# HASHING ATÓMICO Y ESTADÍSTICAS (OS.FSTAT)
# ==========================================
def hash_and_stat_file(filepath: Path, max_size_bytes: int | None = None) -> dict[str, Any]:
    """Calcula SHA-256 sobre un descriptor abierto y detecta cambios durante la lectura.

    Si se especifica max_size_bytes, el tamaño se comprueba mediante fstat()
    sobre el descriptor abierto antes de leer el contenido.
    """
    try:
        with Path(filepath).open("rb") as stream:
            before = os.fstat(stream.fileno())

            if max_size_bytes is not None:
                if not isinstance(max_size_bytes, int) or isinstance(max_size_bytes, bool) or max_size_bytes < 0:
                    raise ValueError("max_size_bytes debe ser un entero mayor o igual que cero")
                if before.st_size > max_size_bytes:
                    return {
                        "sha256": None,
                        "hash_status": "SKIPPED_FILE_TOO_LARGE",
                        "hash_error": None,
                        "size_bytes": before.st_size,
                        "bytes_read": 0,
                        "mtime_utc": datetime.fromtimestamp(before.st_mtime, timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
                        "ctime_utc": datetime.fromtimestamp(before.st_ctime, timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
                        "file_changed_during_read": False,
                        "st_nlink": getattr(before, "st_nlink", None),
                    }

            digest = hashlib.sha256()
            count = 0
            for block in iter(lambda: stream.read(IO_CHUNK_SIZE), b""):
                digest.update(block)
                count += len(block)
            after = os.fstat(stream.fileno())

        changed = (
            before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or before.st_ctime_ns != after.st_ctime_ns
            or count != after.st_size
            or (max_size_bytes is not None and after.st_size > max_size_bytes)
        )
        return {
            "sha256": digest.hexdigest(),
            "hash_status": "CHANGED_DURING_READ" if changed else "OK",
            "size_bytes": after.st_size,
            "bytes_read": count,
            "mtime_utc": datetime.fromtimestamp(after.st_mtime, timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "ctime_utc": datetime.fromtimestamp(after.st_ctime, timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "file_changed_during_read": changed,
            "st_nlink": getattr(after, "st_nlink", None),
        }
    except OSError as exc:
        return {
            "sha256": None,
            "hash_status": "ERROR",
            "hash_error": str(exc),
            "size_bytes": None,
            "bytes_read": None,
            "file_changed_during_read": None,
        }


# ==========================================
# PARSERS DE METADATOS INTERNOS
# ==========================================
def _read_exact(stream, size: int) -> bytes:
    data = stream.read(size)
    if len(data) != size:
        raise EOFError(f"TRUNCATED_PNG: se esperaban {size} bytes y se recibieron {len(data)}")
    return data

def _read_png_chunk_data_and_crc(stream, chunk_type: bytes, length: int, capture_limit: int = 0) -> tuple[bytes | None, bool]:
    crc = zlib.crc32(chunk_type)
    captured = bytearray() if capture_limit and length <= capture_limit else None
    remaining = length
    while remaining:
        block = _read_exact(stream, min(IO_CHUNK_SIZE, remaining))
        crc = zlib.crc32(block, crc)
        if captured is not None: captured.extend(block)
        remaining -= len(block)
    expected_crc = struct.unpack(">I", _read_exact(stream, 4))[0]
    actual_crc = crc & 0xFFFFFFFF
    return (bytes(captured) if captured is not None else None, expected_crc == actual_crc)

def inspect_png_binary_chunks(png_path: Path) -> dict[str, Any]:
    """Parser estructural completo para PNG recuperado de la versión 9."""
    result: dict[str, Any] = {
        "structure_status": "NOT_ANALYZED",
        "signature_valid": False,
        "chunks_checked": 0,
        "chunk_tIME": None,
        "text_metadata": {},
        "crc_errors": [],
        "errors": [],
        "warnings": [],
    }
    try:
        with png_path.open("rb") as stream:
            if _read_exact(stream, 8) != PNG_SIGNATURE:
                result["errors"].append("INVALID_PNG_SIGNATURE")
                result["structure_status"] = "ERROR"
                return result
            result["signature_valid"] = True

            first_chunk = True
            ihdr_seen = False
            idat_seen = False
            idat_ended = False
            iend_seen = False

            while not iend_seen:
                length = struct.unpack(">I", _read_exact(stream, 4))[0]
                chunk_type = _read_exact(stream, 4)
                
                try: chunk_name = chunk_type.decode("ascii")
                except UnicodeDecodeError: raise ValueError("INVALID_PNG_CHUNK_TYPE: bytes no ASCII")
                
                if not re.fullmatch(r"[A-Za-z]{4}", chunk_name):
                    raise ValueError(f"INVALID_PNG_CHUNK_TYPE: {chunk_type!r}")
                if first_chunk and chunk_name != "IHDR":
                    raise ValueError("INVALID_PNG_ORDER: IHDR no es el primer chunk")
                first_chunk = False

                if chunk_name == "IHDR":
                    if ihdr_seen or result["chunks_checked"] != 0 or length != 13:
                        raise ValueError("INVALID_PNG_IHDR: duplicado, fuera de orden o longitud distinta de 13")
                    ihdr_seen = True
                elif not ihdr_seen:
                    raise ValueError("INVALID_PNG_ORDER: aparece un chunk antes de IHDR")

                if chunk_name == "IDAT":
                    if idat_ended: raise ValueError("INVALID_PNG_ORDER: chunks IDAT no contiguos")
                    idat_seen = True
                elif idat_seen and chunk_name != "IEND":
                    idat_ended = True

                capture_limit = (PNG_TEXT_MAX_BYTES if chunk_name == "tEXt" else 7 if chunk_name == "tIME" else 13 if chunk_name == "IHDR" else 0)
                chunk_data, crc_ok = _read_png_chunk_data_and_crc(stream, chunk_type, length, capture_limit)
                result["chunks_checked"] += 1
                if not crc_ok: result["crc_errors"].append(chunk_name)

                if chunk_name == "IHDR":
                    if chunk_data is None or len(chunk_data) != 13: result["errors"].append("INVALID_PNG_IHDR_DATA")
                    else:
                        width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk_data)
                        valid_depths = {0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8}, 4: {8, 16}, 6: {8, 16}}
                        if width == 0 or height == 0: result["errors"].append("INVALID_PNG_DIMENSIONS")
                        if color_type not in valid_depths or bit_depth not in valid_depths.get(color_type, set()):
                            result["errors"].append("INVALID_PNG_BIT_DEPTH_OR_COLOR_TYPE")
                        if compression != 0 or filtering != 0 or interlace not in {0, 1}:
                            result["errors"].append("INVALID_PNG_IHDR_METHOD")

                if chunk_name == "tIME":
                    if length != 7: result["errors"].append("INVALID_PNG_tIME_LENGTH")
                    elif chunk_data is not None:
                        year, month, day, hour, minute, second = struct.unpack(">HBBBBB", chunk_data)
                        try:
                            timestamp = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
                            result["chunk_tIME"] = timestamp.isoformat()
                        except ValueError: result["errors"].append("INVALID_PNG_tIME_VALUE")

                elif chunk_name == "tEXt":
                    if chunk_data is None: result["warnings"].append("PNG_tEXt_TOO_LARGE_TO_EXTRACT")
                    else:
                        separator = chunk_data.find(b"\x00")
                        if separator <= 0: result["errors"].append("INVALID_PNG_tEXt_FORMAT")
                        else:
                            keyword = chunk_data[:separator].decode("latin-1", errors="replace")
                            text_value = chunk_data[separator + 1:].decode("latin-1", errors="replace")
                            result["text_metadata"][keyword] = text_value

                if chunk_name == "IEND":
                    if length != 0: result["errors"].append("INVALID_PNG_IEND_LENGTH")
                    if not idat_seen: result["errors"].append("PNG_IDAT_NOT_FOUND")
                    iend_seen = True

            if not iend_seen: result["errors"].append("PNG_IEND_NOT_FOUND")
            if stream.read(1): result["errors"].append("PNG_TRAILING_DATA_AFTER_IEND")
        
        if result["crc_errors"]: result["errors"].append("PNG_CRC_MISMATCH")
        result["structure_status"] = "ERROR" if result["errors"] else "VALIDATED"

    except (OSError, EOFError, ValueError, struct.error, zlib.error) as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
        result["structure_status"] = "ERROR"
    return result

def inspect_ooxml(filepath: Path) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(filepath, "r") as archive:
            try: xml_bytes = archive.read("docProps/core.xml")
            except KeyError: return {"status": "NOT_FOUND", "created": None, "error": None}
        root = ET.fromstring(xml_bytes)
        created = None
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "created":
                created = (element.text or "").strip() or None
                break
        return {"status": "EXTRACTED" if created else "NOT_FOUND", "created": created, "error": None}
    except (OSError, zipfile.BadZipFile, ET.ParseError, RuntimeError) as exc:
        return {"status": "ERROR", "created": None, "error": f"{type(exc).__name__}: {exc}"}

def inspect_eml(filepath: Path) -> dict[str, Any]:
    try:
        with filepath.open("rb") as stream: message = email.message_from_binary_file(stream)
        raw_date = message.get("Date")
        if not raw_date: return {"status": "NOT_FOUND", "date_raw": None, "date_utc": None, "error": None}
        try:
            parsed = parsedate_to_datetime(raw_date)
            if parsed is None: raise ValueError("No se pudo interpretar la cabecera Date")
            if parsed.tzinfo is None: return {"status": "EXTRACTED", "date_raw": raw_date, "date_utc": None, "error": "DATE_HEADER_WITHOUT_TIMEZONE"}
            normalized = parsed.astimezone(timezone.utc).isoformat()
            return {"status": "EXTRACTED", "date_raw": raw_date, "date_utc": normalized, "error": None}
        except (TypeError, ValueError, OverflowError) as exc:
            return {"status": "ERROR", "date_raw": raw_date, "date_utc": None, "error": f"DATE_HEADER_PARSE_ERROR: {type(exc).__name__}: {exc}"}
    except OSError as exc:
        return {"status": "ERROR", "date_raw": None, "date_utc": None, "error": f"{type(exc).__name__}: {exc}"}