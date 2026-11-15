 <div align="right">

<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

<a id="es"></a>

# Formatos de archivo admitidos y capacidades de procesamiento

## 1. Catálogo de extensiones

El núcleo de GigaVeritas (`forensic_core.py`) define un catálogo de **27 extensiones**, distribuidas en cinco categorías.

| Categoría | Extensiones |
|---|---|
| Imágenes | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Vídeo | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Documentos | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Correo electrónico | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

## 2. Uso del catálogo por los módulos

- **`forensic_core.py` — Forensic Core 2.3.0:** define el catálogo central de extensiones y proporciona funciones compartidas para el procesamiento técnico.
- **`solo_lectura.py` — Solo Lectura V9.3:** importa el catálogo centralizado del Core para identificar los archivos que incorpora a sus operaciones de inventario.
- **`time_stamp.py` — Time Stamp:** mantiene actualmente un catálogo propio equivalente para identificar y procesar los archivos contemplados por este módulo.

La presencia de una extensión en el catálogo significa que el sistema puede reconocerla dentro de los criterios de inventario correspondientes. **No significa que todos los formatos dispongan de un analizador interno específico, extracción completa de metadatos o validación estructural.**

## 3. Diferencias entre reconocimiento y análisis

Es importante distinguir tres niveles de capacidad:

1. **Reconocimiento e inventario:** identificación de archivos mediante su extensión y aplicación de los criterios de inclusión del módulo.
2. **Identificación binaria:** cálculo de huellas SHA-256 para documentar la identidad de los bytes procesados.
3. **Inspección específica:** lectura de estructuras internas, extracción de determinados metadatos o validaciones técnicas propias de un formato.

Estos niveles no son equivalentes. El reconocimiento de una extensión y el cálculo de su hash no acreditan que el contenido haya sido interpretado o validado estructuralmente.

## 4. Alcance del flujo consolidado actual

En su estado documentado, el flujo consolidado de extremo a extremo tiene un alcance más limitado que el catálogo general:

| Formato | Capacidad documentada |
|---|---|
| `.png` | Validación estructural de chunks y CRC32. |
| `.mkv` | Verificación de hash SHA-256 y registro de atributos del sistema de archivos. |
| `.txt` | Documentación auxiliar asociada a cada registro. |

La inclusión de otros formatos en el catálogo no debe interpretarse como compatibilidad integral de extremo a extremo. La incorporación de nuevos formatos a ese flujo requiere implementar y verificar las operaciones específicas que correspondan.

## 5. Alcance metodológico y limitaciones

GigaVeritas está concebido para el tratamiento **post-adquisición** de expedientes digitales locales previamente recopilados y organizados por identificador de registro.

El sistema no realiza captura ni scraping en vivo desde Google Maps u otras plataformas. Tampoco acredita por sí solo la autoría, autenticidad o procedencia original de los archivos.

El cálculo SHA-256 permite comprobar la identidad binaria entre los bytes comparados. Por su parte, los atributos temporales del sistema de archivos, como `mtime` y `ctime`, describen información registrada localmente y no constituyen un sellado de tiempo confiable.

La referencia a ISO/IEC 27037:2012 constituye un marco metodológico de orientación y no implica certificación ni conformidad integral del software con dicha norma.

---

<a id="bg"></a>

# Поддържани файлови формати и възможности за обработка

## 1. Каталог на файловите разширения

Техническото ядро на GigaVeritas (`forensic_core.py`) определя каталог от **27 файлови разширения**, разпределени в пет категории.

| Категория | Разширения |
|---|---|
| Изображения | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Видео | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Аудио | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Документи | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Електронна поща | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

## 2. Използване на каталога от модулите

- **`forensic_core.py` — Forensic Core 2.3.0:** определя централния каталог с разширения и предоставя споделени функции за техническа обработка.
- **`solo_lectura.py` — Solo Lectura V9.3:** използва централния каталог на Core за идентифициране на файловете, включвани в операциите по инвентаризация.
- **`time_stamp.py` — Time Stamp:** към момента поддържа собствен еквивалентен каталог за идентифициране и обработка на файловете, обхванати от този модул.

Наличието на дадено разширение в каталога означава, че системата може да го разпознае в рамките на съответните критерии за инвентаризация. **Това не означава, че всички формати разполагат със специфичен вътрешен анализатор, пълно извличане на метаданни или структурна проверка.**

## 3. Разлика между разпознаване и анализ

Важно е да се разграничават три нива на функционалност:

1. **Разпознаване и инвентаризация:** идентифициране на файлове по разширение и прилагане на критериите за включване на съответния модул.
2. **Бинарна идентификация:** изчисляване на SHA-256 хешове за документиране на идентичността на обработените байтове.
3. **Специфична проверка:** прочитане на вътрешни структури, извличане на определени метаданни или технически проверки, специфични за даден формат.

Тези нива не са взаимозаменяеми. Разпознаването на разширение и изчисляването на хеш не доказват, че съдържанието е интерпретирано или структурно валидирано.

## 4. Обхват на настоящия консолидиран процес

В настоящото си документирано състояние консолидираният процес от край до край има по-ограничен обхват от общия каталог:

| Формат | Документирана функционалност |
|---|---|
| `.png` | Структурна проверка на chunks и CRC32. |
| `.mkv` | Проверка на SHA-256 хеш и регистриране на атрибутите на файловата система. |
| `.txt` | Допълнителна документация, свързана със съответния запис. |

Включването на други формати в каталога не трябва да се тълкува като пълна съвместимост на целия процес от край до край. Включването на нови формати в този процес изисква разработване и проверка на съответните специфични операции.

## 5. Методологичен обхват и ограничения

GigaVeritas е предназначен за **обработка след придобиване (post-acquisition)** на локални цифрови досиета, които вече са събрани и организирани по идентификатор на запис.

Системата не извършва заснемане или scraping в реално време от Google Maps или други платформи. Тя също така не удостоверява сама по себе си авторството, автентичността или първоначалния произход на файловете.

Изчисляването на SHA-256 позволява проверка на бинарната идентичност между сравняваните байтове. Времевите атрибути на файловата система, като `mtime` и `ctime`, описват локално регистрирана информация и не представляват надежден времеви печат.

Позоваването на ISO/IEC 27037:2012 представлява методологична отправна рамка и не означава сертифициране или пълно съответствие на софтуера с този стандарт.

---

<a id="ru"></a>

# Поддерживаемые форматы файлов и возможности обработки

## 1. Каталог расширений файлов

Техническое ядро GigaVeritas (`forensic_core.py`) определяет каталог из **27 расширений файлов**, распределённых по пяти категориям.

| Категория | Расширения |
|---|---|
| Изображения | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Видео | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Аудио | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Документы | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Электронная почта | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

## 2. Использование каталога модулями

- **`forensic_core.py` — Forensic Core 2.3.0:** определяет центральный каталог расширений и предоставляет общие функции для технической обработки.
- **`solo_lectura.py` — Solo Lectura V9.3:** использует централизованный каталог Core для определения файлов, включаемых в операции инвентаризации.
- **`time_stamp.py` — Time Stamp:** в настоящее время поддерживает собственный эквивалентный каталог для определения и обработки файлов, охватываемых этим модулем.

Наличие расширения в каталоге означает, что система может распознать его в рамках соответствующих критериев инвентаризации. **Это не означает, что для всех форматов реализованы специализированный внутренний анализатор, полное извлечение метаданных или структурная проверка.**

## 3. Различия между распознаванием и анализом

Важно различать три уровня возможностей:

1. **Распознавание и инвентаризация:** определение файлов по расширению и применение критериев включения соответствующего модуля.
2. **Бинарная идентификация:** вычисление хешей SHA-256 для документирования идентичности обработанных байтов.
3. **Специализированная проверка:** чтение внутренних структур, извлечение отдельных метаданных или технические проверки, специфичные для конкретного формата.

Эти уровни не являются взаимозаменяемыми. Распознавание расширения и вычисление хеша не подтверждают, что содержимое было интерпретировано или прошло структурную проверку.

## 4. Область действия текущего консолидированного процесса

В своём текущем документированном состоянии консолидированный процесс от начала до конца имеет более ограниченную область действия, чем общий каталог:

| Формат | Документированные возможности |
|---|---|
| `.png` | Структурная проверка chunks и CRC32. |
| `.mkv` | Проверка хеша SHA-256 и регистрация атрибутов файловой системы. |
| `.txt` | Вспомогательная документация, связанная с соответствующей записью. |

Включение других форматов в каталог не следует трактовать как полную совместимость со всем процессом от начала до конца. Включение новых форматов в этот процесс требует реализации и проверки соответствующих специализированных операций.

## 5. Методологическая область действия и ограничения

GigaVeritas предназначен для **обработки после получения (post-acquisition)** локальных цифровых материалов, которые уже были собраны и организованы по идентификатору записи.

Система не выполняет сбор данных или scraping в реальном времени из Google Maps и других платформ. Она также сама по себе не подтверждает авторство, подлинность или первоначальное происхождение файлов.

Вычисление SHA-256 позволяет проверить бинарную идентичность сравниваемых байтов. Временные атрибуты файловой системы, такие как `mtime` и `ctime`, отражают локально зарегистрированную информацию и не являются надёжной временной меткой.

Ссылка на ISO/IEC 27037:2012 используется в качестве методологической основы и не означает сертификацию или полное соответствие программного обеспечения данному стандарту.