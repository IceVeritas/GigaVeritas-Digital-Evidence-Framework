<div align="right">

<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

# GigaVeritas Digital Evidence Framework

**GigaVeritas-Digital-Evidence-Framework** (identified in code and reports as **IceVeritas**) is a standard-library Python toolkit designed for **post-acquisition processing, technical inventory, SHA-256 hash computation, and documentary consolidation** of digital files organized by record identifier.

In its current version, the end-to-end consolidated workflow supports **`.png`** evidence files (with structural chunk and CRC32 validation) and **`.mkv`** files (with SHA-256 hash verification and file system attributes), in addition to **`.txt`** files as auxiliary documentation associated with each record.

> **Methodological Scope and Limitations:** This software processes previously collected local case files (structured via an HTML index and folders associated with each ID). **It does not perform live capture or scraping from Google Maps or other platforms**, nor does it independently certify the authorship, authenticity, or original provenance of files. A SHA-256 match exclusively demonstrates binary identity between the bytes compared during each execution; recorded timestamps (`mtime`, `ctime`) reflect local file system attributes and do not constitute trusted timestamping.

## File Formats and Compatibility

The GigaVeritas core (`forensic_core.py`) defines a catalog of **27 extensions**, grouped into five categories: images, video, audio, documents, and email. `solo_lectura.py` uses the centralized Core catalog, whereas `time_stamp.py` currently maintains its own equivalent catalog. These extensions identify the files that can be incorporated into the inventory and SHA-256 hash computation. However, inventory compatibility does not imply that all formats undergo internal metadata inspection or specific structural analysis. Furthermore, the end-to-end consolidated workflow currently has a narrower scope, focused on `.png` and `.mkv` files, with `.txt` files serving as auxiliary documentation. To review recognized extensions, their categories, and the processing capabilities for each format, see the technical documentation: **[Supported File Formats and Processing Capabilities](docs/FILE_FORMATS.md)**.

---

<a id="es"></a>

# GigaVeritas Digital Evidence Framework

**GigaVeritas-Digital-Evidence-Framework** (identificado en código e informes como **IceVeritas**) es un conjunto de herramientas en Python de biblioteca estándar diseñado para el **tratamiento post-adquisición, inventario técnico, cálculo de huellas SHA-256 y consolidación documental** de archivos digitales organizados por identificador de registro.

En su versión actual, el flujo consolidado de extremo a extremo es compatible con archivos de evidencia **`.png`** (con validación estructural de chunks y CRC32) y **`.mkv`** (con verificación de hash SHA-256 y atributos del sistema de archivos), además de archivos **`.txt`** como documentación auxiliar asociada a cada registro.

> **Alcance y limitaciones metodológicas:** Este software procesa expedientes locales ya recopilados (estructurados mediante un HTML de índice y carpetas asociadas a cada ID). **No realiza captura ni scraping en vivo desde Google Maps u otras plataformas**, ni acredita por sí solo la autoría, autenticidad o procedencia original de los archivos. Una coincidencia SHA-256 demuestra exclusivamente la identidad binaria entre los bytes comparados en cada ejecución; las marcas temporales registradas (`mtime`, `ctime`) reflejan atributos del sistema de archivos local y no constituyen un sellado de tiempo confiable.

## Formatos de archivo y compatibilidad

El núcleo de GigaVeritas (`forensic_core.py`) define un catálogo de **27 extensiones**, agrupadas en cinco categorías: imágenes, vídeo, audio, documentos y correo electrónico. `solo_lectura.py` utiliza el catálogo centralizado del Core, mientras que `time_stamp.py` mantiene actualmente un catálogo propio equivalente. Estas extensiones permiten reconocer los archivos que pueden incorporarse al inventario y al cálculo de huellas SHA-256. No obstante, la compatibilidad de inventario no implica que todos los formatos dispongan de inspección interna de metadatos o análisis estructural específico. Asimismo, el flujo consolidado de extremo a extremo tiene actualmente un alcance más limitado, centrado en archivos `.png` y `.mkv`, con archivos `.txt` como documentación auxiliar. Para consultar las extensiones reconocidas, sus categorías y las capacidades de procesamiento de cada formato, véase la documentación técnica: **[Formatos de archivo admitidos y capacidades de procesamiento](docs/FILE_FORMATS.md)**.

---

<a id="bg"></a>

# GigaVeritas Digital Evidence Framework

**GigaVeritas-Digital-Evidence-Framework** (идентифициран в кода и отчетите като **IceVeritas**) е набор от инструменти на Python от стандартната библиотека, проектиран за **обработка след придобиване (post-acquisition), техническа инвентаризация, изчисляване на SHA-256 хешове и документално консолидиране** на цифрови файлове, организирани по идентификатор на запис.

В текущата си версия консолидираният работен поток от край до край поддържа файлове с доказателства **`.png`** (със структурна валидация на chunks и CRC32) и **`.mkv`** (с проверка на SHA-256 хеш и атрибути на файловата система), както и **`.txt`** файлове като спомагателна документация, свързана с всеки запис.

> **Методологичен обхват и ограничения:** Този софтуер обработва предварително събрани локални досиета (структурирани чрез HTML индекс и папки, свързани с всеки идентификатор). **Той не извършва заснемане или извличане на данни (scraping) в реално време от Google Maps или други платформи**, нито удостоверява сам по себе си авторството, автентичността или първоначалния произход на файловете. Съвпадението на SHA-256 доказва единствено двоичната идентичност между сравняваните байтове при всяко изпълнение; регистрираните времеви маркери (`mtime`, `ctime`) отразяват атрибути на локалната файлова система и не представляват надежден времеви печат.

## Файлови формати и съвместимост

Ядрото на GigaVeritas (`forensic_core.py`) дефинира каталог от **27 разширения**, групирани в пет категории: изображения, видео, аудио, документи и електронна поща. `solo_lectura.py` използва централизирания каталог на Core, докато `time_stamp.py` понастоящем поддържа собствен еквивалентен каталог. Тези разширения позволяват разпознаването на файловете, които могат да бъдат включени в инвентаризацията и изчисляването на SHA-256 хешове. Въпреки това съвместимостта за инвентаризация не означава, че всички формати разполагат с вътрешна проверка на метаданни или специфичен структурен анализ. Освен това консолидираният работен поток от край до край понастоящем има по-ограничен обхват, фокусиран върху файлове `.png` и `.mkv`, като файловете `.txt` служат за спомагателна документация. За справка относно разпознаваните разширения, техните категории и възможностите за обработка на всеки формат вижте техническата документация: **[Поддържани файлови формати и възможности за обработка](docs/FILE_FORMATS.md)**.

---

<a id="ru"></a>

# GigaVeritas Digital Evidence Framework

**GigaVeritas-Digital-Evidence-Framework** (обозначаемый в коде и отчётах как **IceVeritas**) — это набор инструментов на базе стандартной библиотеки Python, предназначенный для **обработки после получения данных (post-acquisition), технической инвентаризации, вычисления хешей SHA-256 и документальной консолидации** цифровых файлов, организованных по идентификатору записи.

В текущей версии сквозной консолидированный рабочий процесс поддерживает файлы доказательств **`.png`** (со структурной проверкой чанков и CRC32) и **`.mkv`** (с проверкой хеша SHA-256 и атрибутов файловой системы), а также файлы **`.txt`** в качестве вспомогательной документации, связанной с каждой записью.

> **Методологическая область действия и ограничения:** Данное программное обеспечение обрабатывает предварительно собранные локальные цифровые дела (структурированные посредством HTML-индекса и папок, связанных с каждым идентификатором). **Оно не выполняет захват или сбор данных (scraping) в реальном времени из Google Maps или других платформ**, а также само по себе не подтверждает авторство, подлинность или первоначальное происхождение файлов. Совпадение SHA-256 доказывает исключительно двоичную идентичность между сравниваемыми байтами при каждом запуске; регистрируемые временные метки (`mtime`, `ctime`) отражают атрибуты локальной файловой системы и не являются надёжной меткой времени.

## Форматы файлов и совместимость

Ядро GigaVeritas (`forensic_core.py`) определяет каталог из **27 расширений**, сгруппированных в пять категорий: изображения, видео, аудио, документы и электронная почта. Модуль `solo_lectura.py` использует централизованный каталог ядра Core, тогда как `time_stamp.py` в настоящее время поддерживает собственный эквивалентный каталог. Эти расширения позволяют распознавать файлы, которые могут быть включены в инвентаризацию и вычисление хешей SHA-256. Тем не менее совместимость на уровне инвентаризации не означает, что для всех форматов выполняется внутренняя проверка метаданных или специализированный структурный анализ. Кроме того, сквозной консолидированный рабочий процесс в настоящее время имеет более узкую область применения, сосредоточенную на файлах `.png` и `.mkv`, при этом файлы `.txt` используются в качестве вспомогательной документации. Чтобы ознакомиться с распознаваемыми расширениями, их категориями и возможностями обработки каждого формата, обратитесь к технической документации: **[Поддерживаемые форматы файлов и возможности обработки](docs/FILE_FORMATS.md)**.