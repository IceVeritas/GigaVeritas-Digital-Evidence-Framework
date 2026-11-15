<div align="right">

<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

<a id="es"></a>

# GigaVeritas Digital Evidence Framework

**GigaVeritas-Digital-Evidence-Framework** (identificado en código e informes como **IceVeritas**) es un conjunto de herramientas en Python de biblioteca estándar diseñado para el **tratamiento post-adquisición, inventario técnico, cálculo de huellas SHA-256 y consolidación documental** de archivos digitales organizados por identificador de registro.

En su versión actual, el flujo consolidado de extremo a extremo es compatible con archivos de evidencia **`.png`** (con validación estructural de chunks y CRC32) y **`.mkv`** (con verificación de hash SHA-256 y atributos del sistema de archivos), además de archivos **`.txt`** como documentación auxiliar asociada a cada registro.

> **Alcance y limitaciones metodológicas:** Este software procesa expedientes locales ya recopilados (estructurados mediante un HTML de índice y carpetas asociadas a cada ID). **No realiza captura ni scraping en vivo desde Google Maps u otras plataformas**, ni acredita por sí solo la autoría, autenticidad o procedencia original de los archivos. Una coincidencia SHA-256 demuestra exclusivamente la identidad binaria entre los bytes comparados en cada ejecución; las marcas temporales registradas (`mtime`, `ctime`) reflejan atributos del sistema de archivos local y no constituyen un sellado de tiempo confiable.
>
## Formatos de archivo y compatibilidad

El núcleo de GigaVeritas (`forensic_core.py`) define un catálogo de **27 extensiones**, agrupadas en cinco categorías: imágenes, vídeo, audio, documentos y correo electrónico. `solo_lectura.py` utiliza el catálogo centralizado del Core, mientras que `time_stamp.py` mantiene actualmente un catálogo propio equivalente. Estas extensiones permiten reconocer los archivos que pueden incorporarse al inventario y al cálculo de huellas SHA-256. No obstante, la compatibilidad de inventario no implica que todos los formatos dispongan de inspección interna de metadatos o análisis estructural específico. Asimismo, el flujo consolidado de extremo a extremo tiene actualmente un alcance más limitado, centrado en archivos `.png` y `.mkv`, con archivos `.txt` como documentación auxiliar. Para consultar las extensiones reconocidas, sus categorías y las capacidades de procesamiento de cada formato, véase la documentación técnica: **[Formatos de archivo admitidos y capacidades de procesamiento](docs/FILE_FORMATS.md)**.

---

<a id="bg"></a>
> 🇧🇬 **Български (BG):** *Документацията на български език е в процес на подготовка. Моля, използвайте версията на испански по-горе.*

<a id="ru"></a>
> 🇷🇺 **Русский (RU):** *Документация на русском языке находится в стадии подготовки. Пожалуйста, используйте версию на испанском языке выше.*