<div align="right">

<a href="../README.md#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="../README.md#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

<a id="es"></a>

# Arquitectura del Sistema

## Límite del sistema

El flujo procesa carpetas de evidencia ya organizadas y un HTML de índice cuyos registros incluyen identificadores estructurados. Está orientado actualmente al tratamiento documental de expedientes de reseñas de Google Maps. **La adquisición o captura en vivo desde plataformas externas no forma parte de estos cuatro módulos.**

## Flujo de datos

```text
HTML de origen + carpetas de registros/archivos
       ├── solo_lectura.py ──> JSON de Solo Lectura + log
       │       └── forensic_core.py (validación, recorrido, hashes, parsers)
       └── time_stamp.py ────> HTML derivado + JSON de artefactos + log
                                  │
JSON de Solo Lectura ────────────┴──> manifest.py
HTML fuente ─────────────────────────> lectura de campos documentales
                                        └── JSON manifiesto + HTML + TXT por registro