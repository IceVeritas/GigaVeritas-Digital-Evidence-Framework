#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador de manifiesto IceVeritas para resultados Solo Lectura y Time Stamp."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import uuid
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import quote

VERSION = "Manifest — Versión 2.0"
SUPPORTED = {".png", ".mkv", ".txt"}

DOCUMENT_FIELDS = {
    "autor", "idioma", "antiguedad", "texto-resena", "texto-respuesta",
    "url-resena", "utc-timestamp", "png-last-modified-utc", "folder",
}


def normalize_source_text(value: str) -> str:
    """Normalize HTML layout whitespace while preserving paragraph boundaries."""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[\t ]+", " ", line).strip() for line in value.split("\n")]
    result: list[str] = []
    for line in lines:
        if line:
            result.append(line)
        elif result and result[-1] != "":
            result.append("")
    while result and result[-1] == "":
        result.pop()
    return "\n".join(result)


class SourceIndexParser(HTMLParser):
    """Read documentary fields from each source HTML evidence card."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.records: dict[str, dict[str, Any]] = {}
        self.current: dict[str, Any] | None = None
        self.active: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "article":
            classes = set((values.get("class") or "").split())
            audit_id = (values.get("data-audit-id") or "").strip()
            if "card" in classes and audit_id:
                self.current = {"audit_id": audit_id, "attributes": values, "values": {}, "ambiguous_fields": []}
                self.active = []
            return
        if self.current is None:
            return
        for capture in self.active:
            capture["depth"] += 1
        name = (values.get("data-field") or "").strip()
        if name not in DOCUMENT_FIELDS:
            return
        if name == "url-resena":
            href = (values.get("href") or "").strip()
            if href:
                self.current["values"].setdefault(name, []).append(href)
            return
        self.active.append({"name": name, "tag": tag.lower(), "depth": 0, "parts": []})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        for capture in self.active:
            capture["parts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        tag = tag.lower()
        for index in range(len(self.active) - 1, -1, -1):
            capture = self.active[index]
            if capture["tag"] == tag and capture["depth"] == 0:
                self.active.pop(index)
                value = normalize_source_text("".join(capture["parts"]))
                if value:
                    self.current["values"].setdefault(capture["name"], []).append(value)
                break
            if capture["depth"] > 0:
                capture["depth"] -= 1
        if tag == "article":
            self._finish_record()

    def _finish_record(self) -> None:
        if self.current is None:
            return
        record = self.current
        fields: dict[str, str] = {}
        for name, entries in record["values"].items():
            unique = list(dict.fromkeys(entries))
            if len(unique) == 1:
                fields[name] = unique[0]
            elif len(unique) > 1:
                record["ambiguous_fields"].append(name)
        self.records[record["audit_id"]] = {
            "fields": fields,
            "ambiguous_fields": record["ambiguous_fields"],
            "attributes": record["attributes"],
        }
        self.current = None
        self.active = []


def read_source_index(path: Path | None) -> tuple[dict[str, dict[str, Any]], str | None]:
    if path is None or not path.is_file():
        return {}, None
    raw = path.read_bytes()
    parser = SourceIndexParser()
    parser.feed(raw.decode("utf-8-sig", errors="replace"))
    parser.close()
    return parser.records, hashlib.sha256(raw).hexdigest()


def source_platform(url: str) -> str:
    host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", url).split("/", 1)[0]).casefold()
    if host in {"maps.app.goo.gl", "maps.google.com", "www.google.com"} or host.endswith(".google.com"):
        return "Google Maps"
    return "NO DISPONIBLE"


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError(f"{path} debe contener una lista 'records'.")
    return data


def file_kind(item: dict[str, Any], timestamp: bool = False) -> str | None:
    ext = Path(str(item.get("filename") or item.get("relative_path") or "")).suffix.lower()
    category = str(item.get("category") or "").upper()
    if ext in SUPPORTED:
        return ext[1:].upper()
    if timestamp and category == "IMAGE":
        return "PNG"
    if timestamp and category == "VIDEO":
        return "MKV"
    return None


def norm_path(item: dict[str, Any]) -> str:
    return str(item.get("relative_path") or "").replace("\\", "/").strip("/").casefold()


def norm_name(item: dict[str, Any]) -> str:
    return str(item.get("filename") or Path(norm_path(item)).name).casefold()


def correlate(solo: dict[str, Any], timestamp: dict[str, Any], source_root: str | None = None) -> list[dict[str, Any]]:
    solo_records = {str(r.get("record_id")): r for r in solo.get("records", []) if r.get("record_id") is not None}
    time_records = {str(r.get("record_id")): r for r in timestamp.get("records", []) if r.get("record_id") is not None}
    record_ids = list(dict.fromkeys([*solo_records, *time_records]))
    combined = []
    for rid in record_ids:
        sr = solo_records.get(rid)
        tr = time_records.get(rid)
        evidences = [e for e in (sr or {}).get("evidences", []) if isinstance(e, dict) and file_kind(e) in ("PNG", "MKV", "TXT")]
        artifacts = [a for a in (tr or {}).get("artifacts", []) if isinstance(a, dict) and file_kind(a, True) in ("PNG", "MKV", "TXT")]
        used: set[int] = set()
        files = []
        for e in evidences:
            kind = file_kind(e)
            match = None
            ep = norm_path(e)
            if ep:
                match = next((i for i, a in enumerate(artifacts) if i not in used and file_kind(a, True) == kind and norm_path(a) == ep), None)
            if match is None:
                en = norm_name(e)
                match = next((i for i, a in enumerate(artifacts) if i not in used and file_kind(a, True) == kind and norm_name(a) == en), None)
            a = artifacts[match] if match is not None else None
            if match is not None:
                used.add(match)
            files.append(build_file(e, a, kind, source_root))
        for i, a in enumerate(artifacts):
            if i not in used:
                files.append(build_file(None, a, file_kind(a, True), source_root))
        files.sort(key=lambda f: (f["kind"], (f.get("relative_path") or f.get("filename") or "").casefold()))
        status = record_status(files)
        combined.append({
            "record_id": rid,
            "status": status,
            "source_records": {"solo_lectura": sr, "time_stamp": tr},
            "evidences": files,
        })
    return combined


def build_file(e: dict[str, Any] | None, a: dict[str, Any] | None, kind: str, source_root: str | None) -> dict[str, Any]:
    primary = e or a or {}
    solo_hash = (e or {}).get("sha256")
    time_hash = (a or {}).get("sha256")
    solo_status = (e or {}).get("hash_status")
    time_status = (a or {}).get("hash_status")
    changed = (a or {}).get("file_changed_during_read") is True
    has_error = any(s is not None and str(s).upper() not in ("OK", "SUCCESS") for s in (solo_status, time_status))
    if changed:
        state = "CAMBIO_DURANTE_LECTURA"
    elif has_error:
        state = "ERROR"
    elif e is None or a is None:
        state = "INCOMPLETO"
    elif not solo_hash or not time_hash:
        state = "NO_VERIFICABLE"
    elif str(solo_hash).casefold() == str(time_hash).casefold():
        state = "COINCIDENTE"
    else:
        state = "DISCREPANCIA"
    details = (e or {}).get("metadata_details") or {}
    source_path = None
    if source_root and primary.get("relative_path"):
        source_path = str(Path(source_root) / Path(str(primary["relative_path"])))
    validation = details.get("png_validation") if kind == "PNG" and isinstance(details, dict) else None
    return {
        "kind": kind,
        "source_path": source_path,
        "source_href": Path(source_path).as_uri() if source_path and Path(source_path).is_absolute() else None,
        "filename": primary.get("filename") or Path(str(primary.get("relative_path") or "")).name or None,
        "relative_path": primary.get("relative_path"),
        "format": {"PNG": ".png", "MKV": ".mkv", "TXT": ".txt"}[kind],
        "category": (a or {}).get("category") or {"PNG": "IMAGE", "MKV": "VIDEO", "TXT": "DOCUMENT"}[kind],
        "size_bytes": (a or {}).get("size_bytes"),
        "sha256_solo_lectura": solo_hash,
        "sha256_time_stamp": time_hash,
        "hash_status_solo_lectura": solo_status,
        "hash_status_time_stamp": time_status,
        "integrity_status": state,
        "mtime_utc": (a or {}).get("mtime_utc") or ((e or {}).get("fs_timestamps") or {}).get("mtime_utc"),
        "ctime_utc": (a or {}).get("ctime_utc") or ((e or {}).get("fs_timestamps") or {}).get("ctime_utc"),
        "ctime_description": "Atributo del sistema de archivos",
        "file_changed_during_read": (a or {}).get("file_changed_during_read"),
        "observed_timestamp": (e or {}).get("observed_timestamp"),
        "timestamp_origin": (e or {}).get("source_origin"),
        "png_validation": validation,
        "metadata_status": (e or {}).get("metadata_status") if kind == "PNG" else "NO ANALIZADO",
        "source_data": {"solo_lectura": e, "time_stamp": a},
    }


def record_status(files: list[dict[str, Any]]) -> str:
    states = {f["integrity_status"] for f in files}
    for state in ("CAMBIO_DURANTE_LECTURA", "ERROR", "DISCREPANCIA", "INCOMPLETO", "NO_VERIFICABLE"):
        if state in states:
            return state
    return "COINCIDENTE" if files else "NO_VERIFICABLE"


def summarize(records: list[dict[str, Any]]) -> dict[str, int]:
    files = [f for r in records for f in r["evidences"]]
    states = Counter(f["integrity_status"] for f in files)
    counts = Counter(f["kind"] for f in files)
    primary_txt = sum(
        f["kind"] == "TXT"
        and str(f.get("filename") or "").casefold() == f"evidence_{r['record_id']}.txt".casefold()
        for r in records
        for f in r["evidences"]
    )
    data_files = counts["PNG"] + counts["MKV"]
    return {
        "respuestas_vinci_documentadas": len({r["record_id"] for r in records}),
        "archivos_asociados_a_respuestas": data_files + primary_txt,
        "datos_origen": data_files,
        "png": counts["PNG"],
        "mkv": counts["MKV"],
        "documentacion_auxiliar": counts["TXT"],
        "archivos_examinados": len(files),
        "comparaciones_sha256": sum(bool(f.get("sha256_solo_lectura") and f.get("sha256_time_stamp")) for f in files),
        "coincidentes": states["COINCIDENTE"],
        "discrepancias": states["DISCREPANCIA"],
        "errores": states["ERROR"],
        "incompletos": states["INCOMPLETO"],
        "cambios_durante_lectura": states["CAMBIO_DURANTE_LECTURA"],
        "no_verificables": states["NO_VERIFICABLE"],
    }

def display(value: Any) -> str:
    if value is None or value == "":
        return "NO DISPONIBLE"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    if value is True:
        return "SÍ"
    if value is False:
        return "NO"
    return str(value)


def documentary_report_text(
    record: dict[str, Any], source: dict[str, Any] | None, source_html_hash: str | None,
    audit_id: str, generated_at_utc: str,
) -> str:
    import textwrap

    width = 100
    fields = (source or {}).get("fields", {})
    ambiguous = set((source or {}).get("ambiguous_fields", []))

    def value(name: str) -> str:
        if name in ambiguous:
            return "NO DISPONIBLE (campo ambiguo en el HTML de origen)"
        return str(fields.get(name) or "NO DISPONIBLE")

    def section(title: str) -> list[str]:
        return ["", "=" * width, title, "-" * width]

    def field_line(label: str, field_value: Any) -> list[str]:
        rendered = display(field_value)
        prefix = f"{label:<34} : "
        wrapped = textwrap.wrap(rendered, width=width - len(prefix), break_long_words=True, break_on_hyphens=False) or [""]
        return [prefix + wrapped[0]] + [(" " * len(prefix)) + part for part in wrapped[1:]]

    def text_lines(text: str) -> list[str]:
        if not text.strip() or text == "NO DISPONIBLE":
            return ["NO DISPONIBLE"]
        result: list[str] = []
        for paragraph in text.split("\n"):
            if not paragraph.strip():
                if result and result[-1] != "":
                    result.append("")
            else:
                result.extend(textwrap.wrap(paragraph, width=width, break_long_words=True, break_on_hyphens=False) or [""])
        while result and result[-1] == "":
            result.pop()
        return result

    record_id = record["record_id"]
    url = value("url-resena")
    platform = source_platform(url) if url != "NO DISPONIBLE" else "NO DISPONIBLE"
    attrs = (source or {}).get("attributes", {})
    location = attrs.get("data-location") or "NO DISPONIBLE"
    highway = attrs.get("data-highway") or "NO DISPONIBLE"
    timestamp = value("utc-timestamp")
    lines = [
        "=" * width,
        "ICEVERITAS | INFORME DOCUMENTAL Y TÉCNICO CONSOLIDADO",
        "CONSOLIDATED DOCUMENTARY AND TECHNICAL EVIDENCE REPORT — AIRE DU REYRAN (A8)",
        "=" * width,
    ]
    
    lines += section("IDENTIFICACIÓN DEL PROYECTO Y LA EVIDENCIA")
    lines += field_line("Proyecto", "IceVeritas")
    lines += field_line("Tipo de documento", "INFORME DOCUMENTAL Y TÉCNICO CONSOLIDADO")
    lines += field_line("ID de auditoría", audit_id)
    lines += field_line("Generado (UTC)", generated_at_utc)
    lines += field_line("ID de evidencia / expediente", record_id)
    lines += field_line("Estado general de integridad", record.get("status"))
    lines += field_line("Fuente / plataforma", platform)
    lines += field_line("Ubicación indicada en HTML", location)
    lines += field_line("Carretera indicada en HTML", highway)
    lines += field_line("URL original", url)
    lines += field_line("Autor de la reseña", value("autor"))
    lines += field_line("Idioma", value("idioma"))
    lines += field_line("Antigüedad visible", value("antiguedad"))
    lines += field_line("Fecha exacta de publicación", "NO DISPONIBLE")
    lines += field_line("Timestamp citado en HTML (UTC)", timestamp)
    lines += field_line("Última modificación PNG (UTC)", value("png-last-modified-utc"))
    lines += field_line("Método de adquisición", "NO DISPONIBLE")

    lines += section("TEXTO ÍNTEGRO DE LA RESEÑA")
    lines += text_lines(value("texto-resena"))
    lines += section("TEXTO ÍNTEGRO DE LA RESPUESTA DEL ESTABLECIMIENTO")
    lines += text_lines(value("texto-respuesta"))

    lines += section("ARCHIVOS DE EVIDENCIA Y CUSTODIA")
    lines += field_line("HTML de origen", (source or {}).get("html_filename") or "NO DISPONIBLE")
    lines += field_line("SHA-256 del HTML de origen", source_html_hash or "NO DISPONIBLE")
    lines += section("INVENTARIO TÉCNICO Y VERIFICACIÓN DE INTEGRIDAD")
    if not record.get("evidences"):
        lines += ["NO SE HAN ASOCIADO ARCHIVOS DE EVIDENCIA A ESTE EXPEDIENTE."]
    for evidence in record.get("evidences", []):
        kind = evidence.get("kind", "ARCHIVO")
        lines += section(f"EVIDENCIA {kind} · {evidence.get('filename') or 'NOMBRE NO DISPONIBLE'}")
        lines += field_line("Ruta relativa", evidence.get("relative_path"))
        lines += field_line("Nombre de archivo", evidence.get("filename"))
        lines += field_line("Formato", evidence.get("format"))
        lines += field_line("Categoría", evidence.get("category"))
        lines += field_line("Estado de integridad", evidence.get("integrity_status"))
        lines += field_line("Estado hash · Solo Lectura", evidence.get("hash_status_solo_lectura"))
        lines += field_line("Estado hash · Time Stamp", evidence.get("hash_status_time_stamp"))
        lines += field_line(f"SHA-256 {kind} · Solo Lectura", evidence.get("sha256_solo_lectura"))
        lines += field_line(f"SHA-256 {kind} · Time Stamp", evidence.get("sha256_time_stamp"))
        lines += field_line("Tamaño (bytes)", evidence.get("size_bytes"))
        lines += field_line("mtime UTC · sistema de archivos", evidence.get("mtime_utc"))
        lines += field_line("ctime UTC · atributo del sistema de archivos", evidence.get("ctime_utc"))
        lines += field_line("Cambio durante lectura", evidence.get("file_changed_during_read"))
        if kind == "PNG":
            validation = evidence.get("png_validation") or {}
            lines += field_line("Validación estructural PNG", validation.get("structure_status"))
            lines += field_line("Firma PNG válida", validation.get("signature_valid"))
            lines += field_line("Chunks comprobados", validation.get("chunks_checked"))
            lines += field_line("Errores CRC", validation.get("crc_errors"))
            lines += field_line("Errores de validación PNG", validation.get("errors"))
            lines += field_line("Avisos de validación PNG", validation.get("warnings"))
            lines += field_line("Chunk tIME", validation.get("chunk_tIME"))
            lines += field_line("Metadatos internos de texto", validation.get("text_metadata"))
            lines += field_line("Estado de metadatos PNG", evidence.get("metadata_status"))
            lines += field_line("Timestamp observado", evidence.get("observed_timestamp"))
            lines += field_line("Origen del timestamp observado", evidence.get("timestamp_origin"))
        elif kind == "MKV":
            lines += field_line("Metadatos internos del contenedor MKV", "NO ANALIZADOS")
    lines += [  
        "",
        "=" * width,
        "OBSERVACIONES METODOLÓGICAS Y LIMITACIONES",
        "-" * width,
        "SHA-256 permite comparar los bytes examinados; por sí solo no acredita autoría, autenticidad,",
        "origen, fecha de captura ni integridad histórica. La coincidencia entre módulos es una",
        "comprobación de consistencia de resultados, no dos pruebas independientes de autenticidad.",
        "Los timestamps del sistema de archivos describen atributos del volumen y no demuestran la",
        "fecha original de captura. Los metadatos internos MKV figuran como NO ANALIZADOS.",
        "La reseña y la respuesta se transcriben del HTML de origen mediante campos separados.",
        "El HTML de origen y las evidencias originales se leen sin modificarlos.",
        "Este TXT consolidado se genera a partir de los datos recibidos de Solo Lectura y Time Stamp.",
        "=" * width,
    ]   
    margin = "    "
    lines = [margin + line if line.strip() else "" for line in lines]
    return "\n".join(lines) + "\n"


def esc(value: Any) -> str:
    return html.escape(display(value), quote=True)


def field(label: str, value: Any, css: str = "") -> str:
    return f'<div class="field"><dt>{html.escape(label)}</dt><dd class="{css}">{esc(value)}</dd></div>'


def hash_field(label: str, value: Any) -> str:
    shown = esc(value)
    button = f'<button class="copy" type="button" aria-label="Copiar {html.escape(label)}" data-copy="{shown}">Copiar</button>' if value else ""
    return f'<div class="field hash-field"><dt>{html.escape(label)}</dt><dd><code>{shown}</code>{button}</dd></div>'


def evidence_card(f: dict[str, Any]) -> str:
    kind = f["kind"]
    png = kind == "PNG"
    validation = f.get("png_validation") if png else None
    details = ""
    if png:
        v = validation or {}
        details = '<section class="detail"><h4>Validación estructural PNG</h4><dl>' + "".join([
            field("Resultado", v.get("structure_status")), field("Firma válida", v.get("signature_valid")),
            field("Chunks comprobados", v.get("chunks_checked")), field("Errores CRC", v.get("crc_errors")),
            field("Errores de validación", v.get("errors")), field("Avisos", v.get("warnings")),
            field("Chunk tIME", v.get("chunk_tIME")), field("Metadatos internos (texto)", v.get("text_metadata")),
            field("Estado de metadatos", f.get("metadata_status")),
            field("Timestamp observado", f.get("observed_timestamp")), field("Origen del timestamp", f.get("timestamp_origin")),
        ]) + '</dl><p class="muted">Los metadatos internos se distinguen de los atributos del sistema de archivos.</p></section>'
    elif kind == "MKV":
        details = '<section class="detail"><h4>Metadatos del contenedor</h4><p>NO ANALIZADO</p><p class="muted">La fecha mtime mostrada es un atributo del sistema de archivos; no representa la fecha original de grabación.</p></section>'
    else:
        details = '<section class="detail"><h4>Documento TXT</h4><p>Contenido no reproducido en el manifiesto; se informa la identificación y los controles de hash recibidos.</p></section>'
    changed = f.get("file_changed_during_read")
    link = f'<p class="source-link"><a href="{html.escape(f["source_href"], quote=True)}">Abrir archivo fuente ({kind})</a></p>' if f.get("source_href") else '<p class="muted source-link">Enlace al archivo fuente: NO DISPONIBLE</p>'
    read_state = "NO DISPONIBLE" if changed is None else ("CAMBIO DETECTADO" if changed else "SIN CAMBIO DETECTADO")
    return f'''<article class="evidence-card">
      <div class="card-head"><div><span class="kind">{kind}</span><h3>{esc(f.get('filename'))}</h3><p class="path">{esc(f.get('relative_path'))}</p></div><span class="status status-{f['integrity_status']}">{f['integrity_status'].replace('_',' ')}</span></div>{link}
      <dl class="fields">{field('Formato', f.get('format'))}{field('Categoría', f.get('category'))}{field('Tamaño (bytes)', f.get('size_bytes'))}
      {hash_field('SHA-256 · Solo Lectura', f.get('sha256_solo_lectura'))}{hash_field('SHA-256 · Time Stamp', f.get('sha256_time_stamp'))}
      {field('Estado hash · Solo Lectura', f.get('hash_status_solo_lectura'))}{field('Estado hash · Time Stamp', f.get('hash_status_time_stamp'))}
      {field('Fecha de modificación (mtime UTC)', f.get('mtime_utc'))}{field('Fecha ctime UTC · atributo del sistema de archivos', f.get('ctime_utc'))}
      {field('Estado durante el cálculo del hash', read_state)}</dl>{details}</article>'''


def html_report(doc: dict[str, Any]) -> str:
    s = doc["summary"]
    cards = "".join(f'<div class="stat"><span>{label}</span><b>{s[key]}</b></div>' for key, label in [
        ("respuestas_vinci_documentadas", "Respuestas de VINCI documentadas"),
        ("archivos_asociados_a_respuestas", "Archivos asociados a las respuestas"),
        ("datos_origen", "Datos de origen"),
        ("png", "Imágenes PNG"),
        ("mkv", "Vídeos MKV"),
        ("documentacion_auxiliar", "Documentación auxiliar"),
        ("archivos_examinados", "Archivos examinados"),
        ("coincidentes", "Hashes coincidentes"),
        ("discrepancias", "Discrepancias"),
        ("errores", "Errores"),
    ])
    sections = []
    for r in doc["records"]:
        files = "".join(evidence_card(f) for f in r["evidences"])
        report = r.get("documentary_report") or {}
        report_link = (f'<p class="source-link"><a href="../txt/{quote(report["filename"])}">Abrir informe consolidado TXT</a>'
                       f' · SHA-256: <code>{html.escape(report["sha256"])}</code></p>') if report else '<p class="muted">Informe consolidado TXT: NO DISPONIBLE</p>'
        sections.append(f'''<section class="record" id="record-{html.escape(r['record_id'], quote=True)}"><header class="record-head"><div><p class="eyebrow">RESPUESTA DOCUMENTADA</p><h2>{esc(r['record_id'])}</h2></div><span class="status status-{r['status']}">{r['status'].replace('_',' ')}</span>
                        </div>
                        <div>
                            <strong>Réf:</strong> AUD-A8-REYRAN-2026
                        </div>
                        <div>
                            <strong>Opérateur:</strong> VINCI Autoroutes (Escota)
                        </div></header>{report_link}<div class="evidence-grid">{files or '<p class="empty">Sin archivos disponibles.</p>'}</div></section>''')
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="IceVeritas es un proyecto independiente de documentación técnica, identificación y verificación de la integridad de materiales digitales mediante procedimientos reproducibles y huellas criptográficas SHA-256."> <meta name="robots" content="index, follow">
<meta name="author" content="IceVeritas">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="application-name" content="IceVeritas">
<meta name="keywords" content="IceVeritas, evidencias digitales, verificación SHA-256, integridad digital, documentación forense, auditoría digital, trazabilidad documental"><title>IceVeritas · Manifest 2.0</title>
<style>
:root {{--navy:#142b45;--blue:#244b70;--teal:#367e83;--paper:#fff;--bg:#edf1f4;--ink:#192a3a;--muted:#5e6c78;--line:#d3dce3;--ok:#246b53;--warn:#9a6500;--bad:#a33a37;--gray:#626e78}}
* {{box-sizing:border-box}}body {{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",Arial,sans-serif}}.container {{max-width:1180px;margin:auto;padding:30px 22px 44px}}.masthead {{position:relative;background:var(--navy);color:#fff;padding:30px 34px;border-bottom:5px solid var(--teal);border-radius:5px 5px 0 0}}.masthead .brand {{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#d7e5eb;font-weight:700}}.lang-selector-bar {{display:flex;align-items:center;gap:0;margin-bottom:12px}}.lang-btn {{display:inline-flex;padding:3px 6px;color:#d7e5eb;text-decoration:none}}.lang-btn:hover,.lang-btn:focus-visible {{color:#fff;text-decoration:underline}}.lang-btn.active {{color:#fff}}.lang-name {{font:700 12px ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:.06em}}.lang-divider {{color:#9fb0c0;margin:0 4px}}h1,h2,h3,.eyebrow,.mast-meta {{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;text-transform:uppercase}}h1 {{font-size:26px;font-weight:700;margin:8px 0 14px;line-height:1.25}}.mast-meta {{display:flex;gap:22px;flex-wrap:wrap;color:#e2eaf0;font-size:12px;letter-spacing:.06em}}.mast-meta b {{color:#fff}}

/* --- BLOQUE DE REFERENCIA ISO/IEC 27037 --- */
.iso-reference-badge {{position:absolute;top:30px;right:34px;text-align:right;font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;line-height:1.35;color:#d7e5eb;background:rgba(255,255,255,0.05);padding:8px 12px;border-radius:4px;border:1px solid rgba(255,255,255,0.12)}}
.iso-reference-badge .iso-title {{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;color:#fff;text-transform:uppercase}}
.iso-reference-badge .iso-ref {{display:block;font-size:13px;color:#e2eaf0;margin-top:2px}}
.iso-reference-badge .iso-operator {{display:block;font-size:12px;color:#d7e5eb}}
.iso-reference-badge b,.iso-reference-badge strong {{color:#fff}}

.panel,.record {{background:var(--paper);border:1px solid var(--line);border-radius:4px;margin-top:20px;padding:24px;box-shadow:0 2px 6px #162f4510}}h2 {{margin:0;font-size:19px;font-weight:700;color:var(--navy)}}h3 {{font-size:15px;font-weight:700;margin:16px 0 6px;color:var(--blue)}}h4 {{margin:15px 0 7px;color:var(--blue)}}.eyebrow {{font-size:11px;letter-spacing:.12em;color:var(--muted);font-weight:700;margin:0 0 4px}}.stats {{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:18px}}.stat {{border:1px solid var(--line);border-top:3px solid var(--blue);padding:11px 12px;background:#f9fbfc;min-width:0}}.stat span {{display:block;font-size:12px;line-height:1.35;color:var(--muted)}}.stat b {{font-size:23px;color:var(--navy)}}.record-head,.card-head {{display:flex;align-items:center;justify-content:space-between;gap:14px}}.record-head {{border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:18px}}.evidence-grid {{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.evidence-card {{border:1px solid var(--line);border-radius:4px;padding:18px;background:#fff;break-inside:avoid}}.kind {{font-size:10px;letter-spacing:.12em;font-weight:800;color:var(--blue)}}.source-link {{margin:10px 0}}.source-link a {{color:var(--blue);font-weight:700}}.path {{font:12px/1.4 Consolas,monospace;color:var(--muted);overflow-wrap:anywhere;margin:3px 0 0}}.status {{display:inline-block;border-radius:3px;padding:5px 9px;font-size:11px;font-weight:800;letter-spacing:.04em;white-space:nowrap;background:#eef1f3;color:var(--gray)}}.status-COINCIDENTE {{background:#e2f1eb;color:var(--ok)}}.status-DISCREPANCIA,.status-ERROR,.status-CAMBIO_DURANTE_LECTURA {{background:#f8e7e5;color:var(--bad)}}.status-INCOMPLETO,.status-NO_VERIFICABLE {{background:#fff0d5;color:var(--warn)}}dl.fields,dl.detail {{margin:13px 0 0}}.field {{display:grid;grid-template-columns:minmax(155px, .8fr) minmax(0,1.5fr);gap:10px;padding:7px 0;border-bottom:1px solid #e8edf0}}dt {{font-size:12px;color:var(--muted)}}dd {{margin:0;overflow-wrap:anywhere}}.hash-field dd {{display:flex;align-items:flex-start;gap:8px}}code {{font:12px/1.55 Consolas,"Courier New",monospace;overflow-wrap:anywhere;color:#142b45}}button.copy {{border:1px solid var(--line);background:#f7f9fa;color:var(--blue);border-radius:3px;padding:3px 7px;font-size:11px;cursor:pointer}}.detail {{border-top:1px solid var(--line);margin-top:17px;padding-top:2px}}.detail p {{margin:7px 0}}.muted,.empty {{font-size:12px;color:var(--muted)}}.methodology {{border-left:4px solid var(--teal)}}.methodology p,.intro p {{margin:8px 0}}.intro h3 {{margin-top:18px}}.footer {{font-size:12px;color:var(--muted);padding:20px 4px;text-align:center}}.contact address {{font-style:normal;display:flex;gap:18px;flex-wrap:wrap;margin-top:12px}}.contact a {{color:var(--blue);font-weight:700;text-decoration:none}}.contact a:hover {{text-decoration:underline}}.contact .contact-links {{display:flex;gap:18px;flex-wrap:wrap}}.reference-note {{margin-top:16px;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}}
@media(max-width:850px){{.stats {{grid-template-columns:repeat(3,minmax(0,1fr))}}.evidence-grid {{grid-template-columns:1fr}}}}
/* --- ADAPTACION RESPONSIVE PARA MOVILES --- */
@media(max-width:540px){{
    .container {{
        padding:12px;
    }}

    .masthead {{
        padding:20px 16px;
    }}

    /* Referencia metodologica ISO */
    .iso-reference-badge {{
        position:static;
        display:block;
        width:100%;
        max-width:100%;
        box-sizing:border-box;
        text-align:left;
        margin:0 0 16px;
        padding:11px 12px;
        overflow-wrap:anywhere;
        line-height:1.45;
    }}

    .iso-reference-badge .iso-title {{
        font-size:10px;
        line-height:1.4;
    }}

    .iso-reference-badge .iso-ref {{
        font-size:11px;
        overflow-wrap:anywhere;
    }}

    .iso-reference-badge .iso-operator {{
        font-size:11px;
        overflow-wrap:anywhere;
    }}

    /* Identidad IceVeritas */
    .masthead .brand {{
        display:block;
        font-size:11px;
        letter-spacing:.14em;
        line-height:1.5;
    }}

    .lang-selector-bar {{
        margin-bottom:14px;
    }}

    /* Titulo principal */
    h1 {{
        font-size:clamp(22px,6.5vw,27px);
        line-height:1.2;
        margin:12px 0 18px;
        overflow-wrap:anywhere;
    }}

    /* Identificacion y metadatos de auditoria */
    .mast-meta {{
        display:grid;
        grid-template-columns:1fr;
        gap:10px;
        font-size:11px;
        letter-spacing:.035em;
        line-height:1.5;
    }}

    .mast-meta span {{
        min-width:0;
        overflow-wrap:anywhere;
    }}

    /* Paneles y contenido */
    .panel,.record {{
        padding:18px;
    }}

    .stats {{
        grid-template-columns:repeat(2,minmax(0,1fr));
    }}

    .field {{
        grid-template-columns:1fr;
        gap:2px;
    }}

    .card-head {{
        align-items:flex-start;
        flex-direction:column;
    }}
}}
@media print{{@page {{size:auto;margin:13mm}}body {{background:#fff;font-size:11px}}.container {{max-width:none;padding:0}}.masthead {{print-color-adjust:exact;-webkit-print-color-adjust:exact;border-radius:0}}.panel,.record,.evidence-card {{box-shadow:none;break-inside:avoid}}.record {{break-before:auto}}.copy {{display:none}}.stats {{grid-template-columns:repeat(5,1fr)}}.evidence-grid {{grid-template-columns:1fr 1fr}}a {{color:inherit}}.iso-reference-badge {{border:none;background:none;padding:0}}}}
</style></head><body><main class="container"><header class="masthead"><nav class="lang-selector-bar mb-3" aria-label="Selector de idioma"><a href="./BG/" class="lang-btn" title="Búlgaro" target="_blank" rel="noopener noreferrer"><span class="lang-name font-monospace fw-bold">BG</span></a><span class="lang-divider text-white-50 mx-1">|</span><a href="./ES/" class="lang-btn active" title="Español" target="_blank" rel="noopener noreferrer"><span class="lang-name font-monospace text-white-50">ES</span></a><span class="lang-divider text-white-50 mx-1">|</span><a href="./RU/" class="lang-btn" title="Русский" target="_blank" rel="noopener noreferrer"><span class="lang-name font-monospace text-white-50">RU</span></a></nav><div class="iso-reference-badge">
        <div class="iso-title">ISO/IEC 27037 METHODOLOGICAL REFERENCE</div>
        <div class="iso-ref"><strong>Réf:</strong> AUD-A8-REYRAN-2026</div>
        <div class="iso-operator"><strong>Entité concernée:</strong> VINCI Autoroutes (Escota)</div>
    </div><div class="brand">IceVeritas · Informe técnico</div><h1>Manifiesto consolidado de evidencias</h1><div class="mast-meta"><span><b>Identificador de auditoría:</b> {esc(doc['audit_id'])}</span><span><b>Generado (UTC):</b> {esc(doc['generated_at_utc'])}</span><span><b>Versión:</b> Manifest — Versión 2.0</span></div>
                            </header>
<section class="panel intro"><p class="eyebrow">PRESENTACIÓN DEL PROYECTO</p><h2>Sobre el proyecto IceVeritas</h2><p>IceVeritas es un proyecto orientado a la documentación técnica, identificación y verificación de la integridad de materiales digitales.</p><p>Su metodología combina procedimientos de análisis de archivos, registro de atributos técnicos y temporales, cálculo de huellas criptográficas SHA-256 y consolidación de resultados.</p><p>El objetivo es proporcionar documentación estructurada, trazable y verificable sobre los materiales digitales examinados, facilitando su identificación, conservación y posterior evaluación por terceros.</p><p>Los informes generados documentan los controles efectivamente realizados y sus resultados, distinguiendo los datos observados de las inferencias y de los aspectos que no han podido verificarse.</p><h3>Finalidad del presente documento</h3><p>El presente manifiesto recoge los resultados consolidados del procedimiento de examen de los archivos digitales incluidos en los registros identificados.</p><p>Se documentan los archivos de origen, sus características técnicas, las huellas SHA-256 y los atributos temporales disponibles, junto con los resultados de las comprobaciones realizadas.</p></section>
<section class="panel"><p class="eyebrow">RESUMEN EJECUTIVO</p><h2>Alcance de la revisión</h2><div class="stats">{cards}</div><p class="muted">Las piezas asociadas se calculan como datos de origen más un TXT principal por respuesta. Los TXT de respaldo se contabilizan como documentación auxiliar adicional. Cada archivo se cuenta una sola vez en el total de archivos examinados.</p></section>
{''.join(sections)}
<section class="panel methodology"><p class="eyebrow">METODOLOGÍA Y ALCANCE</p><h2>Transparencia metodológica</h2><p>Intervinieron tres módulos: <b>Módulo de Análisis y Verificación de Datos Digitales</b> (Solo Lectura — Versión 9.2); <b>Módulo de Análisis de Trazabilidad Temporal</b> (Time Stamp — Versión 2.0.0); y <b>Módulo de Consolidación y Documentación Forense</b> (Manifest — Versión 2.0).</p><p>Los registros se correlacionaron por identificador de respuesta. Dentro de cada registro, los archivos se emparejaron primero por ruta relativa y, como alternativa, por nombre y tipo de archivo. Las comparaciones SHA-256 se cuentan por pareja de archivos correlacionada con ambos hashes disponibles; los estados se derivan de los hashes y de los estados de lectura recibidos. En esta ejecución se compararon {s['comparaciones_sha256']} parejas: {s['coincidentes']} coincidencias, {s['discrepancias']} discrepancias y {s['errores']} errores.</p><p>En los PNG se registraron la validez de la firma, el número de chunks comprobados, los errores CRC, errores de validación, avisos, el chunk tIME y los metadatos de texto disponibles. Para los MKV se registraron atributos del sistema de archivos, incluidos mtime y ctime; los metadatos internos del contenedor figuran como <b>NO ANALIZADOS</b>.</p><p>Los timestamps del sistema de archivos no acreditan por sí solos la fecha original de captura. La coincidencia de hashes entre módulos acredita consistencia de resultados, pero no constituye dos pruebas independientes de autenticidad. Estos controles tampoco demuestran por sí solos autoría ni integridad histórica.</p><div class="reference-note"><h3>Marco de referencia internacional</h3><p>El procedimiento toma como referencia metodológica determinados principios de identificación, recopilación, adquisición y preservación de información digital contemplados en la norma internacional ISO/IEC 27037:2012.</p><p>Esta referencia se utiliza como orientación metodológica y no constituye una declaración de certificación, acreditación ni conformidad integral con los requisitos de dicha norma.</p></div></section>
<section class="panel contact" aria-labelledby="contact-title"><p class="eyebrow">CONTACTO</p><h2 id="contact-title">{esc(doc['contact']['name'])}</h2><address class="contact-links"><a href="{html.escape(doc['contact']['email_href'], quote=True)}" title="Enviar correo electrónico a Atanas Atanasov" aria-label="Enviar correo electrónico a Atanas Atanasov: {esc(doc['contact']['email'])}">{esc(doc['contact']['email'])}</a><a href="{html.escape(doc['contact']['whatsapp_url'], quote=True)}" title="Contactar con Atanas Atanasov por WhatsApp" aria-label="Abrir conversación de WhatsApp con Atanas Atanasov al {esc(doc['contact']['whatsapp'])}" target="_blank" rel="noopener noreferrer">WhatsApp: {esc(doc['contact']['whatsapp'])}</a><span>{esc(doc['contact']['profile'])}</span></address></section><footer class="footer">IceVeritas · Documento derivado de los JSON de entrada · Auditoría {esc(doc['audit_id'])}</footer></main><script>document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(b.dataset.copy);b.textContent='Copiado';setTimeout(()=>b.textContent='Copiar',1200)}}catch(e){{b.textContent='No disponible'}}}}));</script></body></html>'''


def unique_stem(audit_id: str, dirs: list[Path]) -> str:
    base = re.sub(r"[^A-Za-z0-9_-]", "_", audit_id)
    stem = base
    n = 1
    while any(any(d.glob(f"*_{stem}.*")) for d in dirs):
        n += 1
        stem = f"{base}_{n}"
    return stem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="IceVeritas: consolida Solo Lectura y Time Stamp en un manifiesto de PNG y MKV.")
    project = Path(__file__).resolve().parent.parent
    parser.add_argument("--solo_json", type=Path, help="JSON de Solo Lectura (por defecto, el más reciente en json/).")
    parser.add_argument("--timestamp_json", type=Path, help="JSON de Time Stamp (por defecto, el más reciente en json/).")
    parser.add_argument("--output_dir", type=Path, default=project, help="Raíz del proyecto; las salidas van a json/, manifest_html/ y txt/.")
    args = parser.parse_args(argv)
    json_dir = args.output_dir / "json"
    solo_path = args.solo_json or next(iter(sorted(json_dir.glob("solo_lectura*.json"), key=lambda p: p.stat().st_mtime, reverse=True)), None)
    time_path = args.timestamp_json or next(iter(sorted(json_dir.glob("time_stamp*.json"), key=lambda p: p.stat().st_mtime, reverse=True)), None)
    if solo_path is None or time_path is None:
        parser.error("Indique --solo_json y --timestamp_json o deje ambos informes en json/.")
    for p in (solo_path, time_path):
        if not p.is_file() or p.suffix.lower() != ".json":
            parser.error(f"No es un archivo JSON existente: {p}")
    try:
        solo, timestamp = read_json(solo_path), read_json(time_path)
    except ValueError as exc:
        parser.error(str(exc))
    records = correlate(solo, timestamp, solo.get("input_directory"))
    source_index_path = None
    if solo.get("input_directory") and solo.get("index_filename"):
        source_index_path = Path(str(solo["input_directory"])) / str(solo["index_filename"])
    source_records, source_index_hash = read_source_index(source_index_path)
    for source_record in source_records.values():
        source_record["html_filename"] = source_index_path.name if source_index_path else "NO DISPONIBLE"
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    audit_id = "IV-" + now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8].upper()
    doc = {
        "schema": "iceveritas.manifest/2.0",
        "generator": VERSION,
        "audit_id": audit_id,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "inputs": {"solo_lectura": str(solo_path.resolve()), "time_stamp": str(time_path.resolve()), "source_html": str(source_index_path.resolve()) if source_index_path and source_index_path.is_file() else None},
        "modules": {"solo_lectura": {"version": solo.get("program_version"), "run_id": solo.get("run_id"), "run_timestamp_utc": solo.get("run_timestamp_utc")}, "time_stamp": {"version": timestamp.get("version"), "generated_at_utc": timestamp.get("generated_at_utc")}},
        "summary": summarize(records),
        "contact": {"name": "Atanas Atanasov", "email": "icedux@icloud", "email_href": "mailto:icedux@icloud", "whatsapp": "+34653583521", "whatsapp_url": "https://wa.me/34653583521", "profile": "icedux.art"},
        "records": records,
        "source_html_sha256": source_index_hash,
        "documentary_reports": [],
        "consolidated_reports": [],
        "methodology": "Los SHA-256 identifican y comparan bytes; la coincidencia comprueba consistencia de resultados y no prueba por sí sola autenticidad, autoría, fecha original de captura ni integridad histórica.",
    }
    output_root = args.output_dir
    output_json, output_html, output_txt = output_root / "json", output_root / "manifest_html", output_root / "txt"
    for folder in (output_json, output_html, output_txt):
        folder.mkdir(parents=True, exist_ok=True)
    stem = unique_stem(audit_id, [output_json, output_html, output_txt])
    json_path = output_json / f"manifest_{stem}.json"
    html_path = output_html / f"manifest_{stem}.html"
    documentary_reports = []
    for record in records:
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", record["record_id"])
        report_name = f"EVIDENCE_{safe_id}_{stem}.txt"
        report_path = output_txt / report_name
        report_source = source_records.get(record["record_id"])
        report_text = documentary_report_text(
            record, report_source, source_index_hash, audit_id, doc["generated_at_utc"]
        )
        with report_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(report_text)
        report_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
        report_info = {
            "filename": report_name,
            "relative_path": f"txt/{report_name}",
            "sha256": report_hash,
            "document_type": "CONSOLIDATED_DOCUMENTARY_AND_TECHNICAL_REPORT",
        }
        record["documentary_report"] = report_info
        documentary_reports.append({
            "record_id": record["record_id"], **report_info,
            "review_text_status": "PRESENT" if report_source and report_source.get("fields", {}).get("texto-resena") else "NO DISPONIBLE",
            "response_status": "PRESENT" if report_source and report_source.get("fields", {}).get("texto-respuesta") else "NO DISPONIBLE",
        })
    doc["documentary_reports"] = documentary_reports
    doc["consolidated_reports"] = documentary_reports
    doc["summary"]["informes_consolidados_generados"] = len(documentary_reports)
    json_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(html_report(doc), encoding="utf-8")
    print(f"Auditoría: {audit_id}")
    print(f"JSON consolidado: {json_path}")
    print(f"HTML: {html_path}")
    print(f"Informes TXT consolidados: {output_txt} ({len(documentary_reports)} expedientes; EVIDENCE_*.txt)")
    print("Resumen: " + json.dumps(doc["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
