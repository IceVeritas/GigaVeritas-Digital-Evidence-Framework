<div align="right">

<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

<a id="es"></a>

# Time Stamp — Sincronización descriptiva de evidencias

**IceVeritas Time Stamp 2.0.0** (`time_stamp.py`) es un módulo Python destinado al descubrimiento de archivos asociados a registros de un expediente digital, el cálculo de huellas criptográficas SHA-256 y el registro de atributos temporales del sistema de archivos.

Su función principal consiste en incorporar información técnica descriptiva a una copia derivada del HTML original y generar un informe JSON independiente con los resultados del procesamiento.

## 1. Responsabilidades del módulo

El módulo realiza las siguientes operaciones:

- Identificación de registros dentro de un documento HTML.
- Localización de las carpetas asociadas a cada registro.
- Descubrimiento recursivo de archivos de evidencia.
- Clasificación de archivos por categorías y extensiones.
- Cálculo de huellas criptográficas SHA-256.
- Registro del tamaño y de los atributos temporales del sistema de archivos.
- Detección de determinados cambios de tamaño o tiempo de modificación durante la lectura.
- Incorporación de información descriptiva en una copia derivada del HTML.
- Generación de un informe JSON independiente.
- Registro de eventos y operaciones mediante logs.

## 2. Estructura de entrada

El módulo trabaja sobre un expediente local previamente recopilado.

La estructura esperada comprende:

La estructura de entrada debe incluir:

- Un documento HTML de índice situado directamente en el directorio raíz del expediente.
- Registros de datos integrados en el documento HTML, estructurados mediante campos identificadores (`data-field`) y agrupados en sus correspondientes elementos contenedores.
- Identificadores de registro con la nomenclatura del expediente, cuyo prefijo de referencia es `AUD-` (por ejemplo, `AUD-...`).
- Carpetas asociadas a los identificadores de registro, que contienen los archivos correspondientes a cada expediente.

Cuando no encuentra una carpeta con guiones en el identificador, el módulo contempla una alternativa de búsqueda sustituyendo los guiones por guiones bajos.

## 3. Descubrimiento y clasificación de archivos

El módulo realiza un recorrido recursivo de las carpetas asociadas a los registros.

Utiliza un catálogo propio de **27 extensiones**, agrupadas en cinco categorías:

| Categoría | Extensiones |
|---|---|
| Imágenes | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Vídeo | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Documentos | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Correo electrónico | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

La clasificación se realiza mediante la extensión del archivo. La inclusión en este catálogo no implica análisis interno, extracción de metadatos específicos ni validación estructural de todos los formatos.

**Nota arquitectónica:** el catálogo de `time_stamp.py` es actualmente independiente del catálogo definido en `forensic_core.py`, aunque ambos contienen las mismas extensiones.

## 4. Cálculo SHA-256 y control durante la lectura

Para cada archivo admitido, el módulo calcula una huella SHA-256 mediante lectura binaria en bloques de **1 MiB**.

El cálculo se realiza utilizando un descriptor de archivo abierto. Antes y después de la lectura se obtienen atributos mediante `os.fstat()`.

El resultado contempla los siguientes campos:

| Campo | Descripción |
|---|---|
| `sha256` | Huella criptográfica SHA-256. |
| `hash_status` | Estado de la operación de cálculo. |
| `size_bytes` | Tamaño del archivo en bytes. |
| `mtime_utc` | Fecha de modificación del sistema de archivos en UTC. |
| `ctime_utc` | Atributo temporal `ctime` expresado en UTC. |
| `file_changed_during_read` | Indicador de cambios detectados en tamaño o `mtime` durante la lectura. |

Si se produce un error de lectura, el módulo registra el estado `ERROR` y los datos de error correspondientes.

La comparación de atributos permite detectar determinados cambios durante la operación, pero no constituye una garantía absoluta de que el archivo haya permanecido inalterado durante todo el proceso.

## 5. Atributos temporales

El módulo registra los atributos temporales proporcionados por el sistema de archivos:

- `mtime`: fecha de última modificación.
- `ctime`: atributo temporal cuyo significado depende del sistema operativo.

Los valores se convierten a formato UTC.

Estos datos describen los atributos observados durante la ejecución. No representan necesariamente la fecha de creación original, el momento de captura ni el momento real de incorporación del archivo al expediente.

## 6. Generación del HTML derivado

El módulo procesa los elementos `article.card` identificados en el HTML original.

Para cada registro:

1. Identifica el expediente correspondiente.
2. Descubre los archivos asociados.
3. Calcula sus huellas y registra sus atributos.
4. Construye un bloque descriptivo de artefactos.
5. Incorpora el bloque a una copia derivada del HTML.

El bloque generado contiene información como:

- Categoría del archivo.
- Nombre del archivo.
- Huella SHA-256.
- Estado del cálculo del hash.
- Fecha de modificación del sistema de archivos en UTC.

Si el HTML contiene un bloque anterior identificado como `forensic-artifacts-block`, el módulo intenta retirarlo antes de incorporar el nuevo resultado.

El documento original se utiliza como entrada; el HTML enriquecido se escribe en el directorio de salida.

## 7. Informe JSON

Además del HTML derivado, el módulo genera un informe JSON independiente.

El documento incluye:

| Campo | Descripción |
|---|---|
| `tool` | Identificación de la herramienta. |
| `version` | Versión del módulo. |
| `generated_at_utc` | Fecha de generación del informe. |
| `source_html` | Nombre del HTML de entrada. |
| `records_processed` | Número de registros procesados. |
| `records` | Resultados asociados a cada registro. |

Cada registro contiene información sobre la carpeta asociada, el número de archivos descubiertos y los datos técnicos de cada archivo.

## 8. Logs y trazabilidad de ejecución

Cada ejecución utiliza un identificador temporal UTC con microsegundos y un sufijo único.

El módulo genera un archivo de log independiente y también registra información en la salida de consola.

Los logs permiten consultar operaciones, advertencias, errores de acceso y resultados del descubrimiento de archivos.

## 9. Controles de rutas y lectura

El código incorpora controles destinados a reducir el riesgo de procesar rutas no previstas:

- Comprueba que el directorio de entrada exista y sea un directorio.
- Rechaza nombres de índice que representen rutas o subdirectorios.
- Impide que el directorio de salida coincida con el directorio de entrada o esté dentro de él.
- Comprueba que el HTML de entrada sea un archivo regular dentro de la raíz.
- Omite enlaces simbólicos detectados durante el descubrimiento.
- Comprueba que los archivos descubiertos permanezcan dentro de la carpeta correspondiente al registro.

Estos controles forman parte de la validación de rutas y del recorrido de archivos. No deben interpretarse como una garantía absoluta frente a todas las condiciones de carrera o modificaciones concurrentes del sistema de archivos.

## 10. Ejecución

El módulo se ejecuta desde la línea de comandos mediante tres argumentos:

```bash
python time_stamp.py --input "/ruta/expediente" --output "/ruta/resultados" --index "index.html"
```

| Argumento | Función |
|---|---|
| `--input` | Directorio raíz del expediente original. |
| `--output` | Directorio independiente para los resultados derivados. |
| `--index` | Nombre del HTML original situado directamente en el directorio de entrada. |

El argumento `--index` es opcional y utiliza `index.html` como valor predeterminado.

## 11. Archivos generados

El módulo genera los siguientes artefactos:

| Archivo | Contenido |
|---|---|
| `*_FIXED.html` | Copia derivada del HTML con los bloques descriptivos incorporados. |
| `time_stamp_sync_<run_stamp>.json` | Informe estructurado de los registros y archivos descubiertos. |
| `time_stamp_sync_<run_stamp>.log` | Registro de la ejecución. |

Los resultados se escriben en el directorio independiente indicado mediante `--output`.

## 12. Alcance y limitaciones metodológicas

Time Stamp es un módulo de documentación técnica **post-adquisición**. No realiza captura ni scraping en vivo desde Google Maps u otras plataformas.

El cálculo SHA-256 identifica los bytes leídos durante una ejecución y permite comparar posteriormente huellas criptográficas. Por sí solo no demuestra autenticidad histórica, autoría, procedencia ni integridad desde el momento original de adquisición.

Los atributos `mtime` y `ctime` reflejan información proporcionada por el sistema de archivos y no constituyen un sellado de tiempo confiable.

El módulo no realiza análisis estructural completo de los 27 formatos reconocidos ni certifica la autenticidad de los archivos procesados.

La referencia a ISO/IEC 27037:2012 constituye una orientación metodológica y no implica certificación ni conformidad integral del software con dicha norma.

---

<a id="bg"></a>

# Time Stamp — Описателна синхронизация на цифрови доказателства

**IceVeritas Time Stamp 2.0.0** (`time_stamp.py`) е Python модул, предназначен за откриване на файлове, свързани със записи в цифрово досие, изчисляване на криптографски SHA-256 хешове и регистриране на времевите атрибути на файловата система.

Основната му функция е да добавя описателна техническа информация към производно копие на оригиналния HTML документ и да генерира отделен JSON отчет с резултатите от обработката.

## 1. Отговорности на модула

Модулът извършва следните операции:

- Идентифициране на записи в HTML документ.
- Откриване на папките, свързани със съответните записи.
- Рекурсивно откриване на файлове с доказателствено съдържание.
- Класифициране на файловете по категории и разширения.
- Изчисляване на криптографски SHA-256 хешове.
- Регистриране на размера и времевите атрибути на файловата система.
- Откриване на определени промени в размера или времето на модификация по време на четене.
- Добавяне на описателна информация към производно копие на HTML документа.
- Генериране на отделен JSON отчет.
- Регистриране на събития и операции чрез логове.

## 2. Входна структура

Модулът работи с предварително събрано локално досие.

Очакваната структура включва:

- HTML индексен документ, разположен директно в основната директория.
- HTML елементи `<article>`, идентифицирани чрез класа `card`.
- Идентификатори на записи по шаблона `AUD-A8-REYRAN-####`.
- Папки, свързани с идентификаторите, съдържащи съответните файлове.

Когато не бъде намерена папка с тирета в идентификатора, модулът предвижда алтернативно търсене чрез замяна на тиретата с долни черти.

## 3. Откриване и класифициране на файлове

Модулът извършва рекурсивно обхождане на папките, свързани със записите.

Използва собствен каталог от **27 разширения**, разпределени в пет категории:

| Категория | Разширения |
|---|---|
| Изображения | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Видео | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Аудио | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Документи | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Електронна поща | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

Класифицирането се извършва въз основа на файловото разширение. Включването в този каталог не означава вътрешен анализ, извличане на специфични метаданни или структурна проверка на всички формати.

**Архитектурна бележка:** каталогът на `time_stamp.py` понастоящем е независим от каталога, дефиниран във `forensic_core.py`, въпреки че двата съдържат едни и същи разширения.

## 4. Изчисляване на SHA-256 и контрол по време на четене

За всеки поддържан файл модулът изчислява SHA-256 хеш чрез двоично четене на блокове от **1 MiB**.

Изчислението се извършва чрез отворен файлов дескриптор. Преди и след прочитането се извличат атрибути чрез `os.fstat()`.

Резултатът включва следните полета:

| Поле | Описание |
|---|---|
| `sha256` | Криптографски SHA-256 хеш. |
| `hash_status` | Статус на операцията по изчисляване. |
| `size_bytes` | Размер на файла в байтове. |
| `mtime_utc` | Време на последна модификация на файловата система в UTC. |
| `ctime_utc` | Времевият атрибут `ctime`, изразен в UTC. |
| `file_changed_during_read` | Индикатор за открити промени в размера или `mtime` по време на четенето. |

При грешка при четене модулът регистрира статус `ERROR` и съответните данни за грешката.

Сравнението на атрибутите позволява откриване на определени промени по време на операцията, но не представлява абсолютна гаранция, че файлът е останал непроменен през целия процес.

## 5. Времеви атрибути

Модулът регистрира времевите атрибути, предоставени от файловата система:

- `mtime`: време на последна модификация.
- `ctime`: времеви атрибут, чието значение зависи от операционната система.

Стойностите се преобразуват във формат UTC.

Тези данни описват атрибутите, наблюдавани по време на изпълнението. Те не представляват непременно първоначалната дата на създаване, момента на заснемане или реалния момент на включване на файла в досието.

## 6. Генериране на производен HTML документ

Модулът обработва идентифицираните в оригиналния HTML елементи `article.card`.

За всеки запис:

1. Идентифицира съответното досие.
2. Открива свързаните файлове.
3. Изчислява техните хешове и регистрира атрибутите им.
4. Създава описателен блок с артефактите.
5. Добавя блока към производно копие на HTML документа.

Генерираният блок съдържа информация като:

- Категория на файла.
- Име на файла.
- SHA-256 хеш.
- Статус на изчисляването на хеша.
- Време на модификация на файловата система в UTC.

Ако HTML документът съдържа предишен блок, идентифициран като `forensic-artifacts-block`, модулът се опитва да го премахне, преди да добави новия резултат.

Оригиналният документ се използва като вход; обогатеният HTML се записва в изходната директория.

## 7. JSON отчет

Освен производния HTML модулът генерира и отделен JSON отчет.

Документът включва:

| Поле | Описание |
|---|---|
| `tool` | Идентификация на инструмента. |
| `version` | Версия на модула. |
| `generated_at_utc` | Дата на генериране на отчета. |
| `source_html` | Име на входния HTML документ. |
| `records_processed` | Брой обработени записи. |
| `records` | Резултати за всеки запис. |

Всеки запис съдържа информация за свързаната папка, броя на откритите файлове и техническите данни за всеки файл.

## 8. Логове и проследимост на изпълнението

Всяко изпълнение използва уникален времеви идентификатор UTC с микросекунди и допълнителен уникален суфикс.

Модулът генерира отделен лог файл и регистрира информация и в конзолния изход.

Логовете позволяват преглед на операциите, предупрежденията, грешките при достъп и резултатите от откриването на файлове.

## 9. Проверки на пътища и четене

Кодът включва проверки, предназначени да намалят риска от обработване на непредвидени пътища:

- Проверява дали входната директория съществува и е директория.
- Отхвърля имена на индекс, които представляват пътища или поддиректории.
- Не допуска изходната директория да съвпада с входната или да се намира в нея.
- Проверява дали входният HTML е обикновен файл в основната директория.
- Пропуска откритите символни връзки по време на откриването.
- Проверява дали откритите файлове остават в рамките на папката на съответния запис.

Тези проверки са част от валидирането на пътищата и обхождането на файловете. Те не трябва да се разглеждат като абсолютна защита срещу всички състезателни условия или едновременни промени във файловата система.

## 10. Изпълнение

Модулът се стартира от командния ред чрез три аргумента:

```bash
python time_stamp.py --input "/path/to/case" --output "/path/to/results" --index "index.html"
```

| Аргумент | Функция |
|---|---|
| `--input` | Основна директория на оригиналното досие. |
| `--output` | Независима директория за производните резултати. |
| `--index` | Име на оригиналния HTML файл, разположен директно във входната директория. |

Аргументът `--index` е незадължителен и по подразбиране използва `index.html`.

## 11. Генерирани файлове

Модулът генерира следните артефакти:

| Файл | Съдържание |
|---|---|
| `*_FIXED.html` | Производно копие на HTML с добавени описателни блокове. |
| `time_stamp_sync_<run_stamp>.json` | Структуриран отчет за записите и откритите файлове. |
| `time_stamp_sync_<run_stamp>.log` | Регистър на изпълнението. |

Резултатите се записват в независимата директория, посочена чрез `--output`.

## 12. Методологичен обхват и ограничения

Time Stamp е модул за техническа документация **след придобиване (post-acquisition)**. Той не извършва заснемане или scraping в реално време от Google Maps или други платформи.

Изчисляването на SHA-256 идентифицира байтовете, прочетени по време на изпълнението, и позволява последващо сравняване на криптографски хешове. Само по себе си то не доказва историческа автентичност, авторство, произход или цялост от момента на първоначалното придобиване.

Атрибутите `mtime` и `ctime` отразяват информация, предоставена от файловата система, и не представляват надежден времеви печат.

Модулът не извършва пълен структурен анализ на 27-те разпознавани формата и не удостоверява автентичността на обработваните файлове.

Позоваването на ISO/IEC 27037:2012 представлява методологична отправна рамка и не означава сертифициране или пълно съответствие на софтуера с този стандарт.

---

<a id="ru"></a>

# Time Stamp — Описательная синхронизация цифровых доказательств

**IceVeritas Time Stamp 2.0.0** (`time_stamp.py`) — это модуль Python, предназначенный для обнаружения файлов, связанных с записями цифрового дела, вычисления криптографических хешей SHA-256 и регистрации временных атрибутов файловой системы.

Его основная функция заключается в добавлении описательной технической информации в производную копию исходного HTML-документа и создании отдельного JSON-отчёта с результатами обработки.

## 1. Назначение модуля

Модуль выполняет следующие операции:

- Идентификация записей в HTML-документе.
- Поиск папок, связанных с соответствующими записями.
- Рекурсивное обнаружение файлов с доказательственным содержимым.
- Классификация файлов по категориям и расширениям.
- Вычисление криптографических хешей SHA-256.
- Регистрация размера и временных атрибутов файловой системы.
- Обнаружение определённых изменений размера или времени модификации во время чтения.
- Добавление описательной информации в производную копию HTML-документа.
- Создание отдельного JSON-отчёта.
- Регистрация событий и операций с помощью логов.

## 2. Входная структура

Модуль работает с предварительно собранным локальным цифровым делом.

Ожидаемая структура включает:

- HTML-документ индекса, расположенный непосредственно в корневом каталоге.
- HTML-элементы `<article>`, идентифицируемые классом `card`.
- Идентификаторы записей по шаблону `AUD-A8-REYRAN-####`.
- Папки, связанные с идентификаторами и содержащие соответствующие файлы.

Если папка с дефисами в идентификаторе не найдена, модуль предусматривает альтернативный поиск с заменой дефисов на символы подчёркивания.

## 3. Обнаружение и классификация файлов

Модуль выполняет рекурсивный обход папок, связанных с записями.

Он использует собственный каталог из **27 расширений**, распределённых по пяти категориям:

| Категория | Расширения |
|---|---|
| Изображения | `.png`, `.jpg`, `.jpeg`, `.heic`, `.heif`, `.gif` |
| Видео | `.mp4`, `.mkv`, `.avi`, `.mov` |
| Аудио | `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac` |
| Документы | `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.odt`, `.txt`, `.html`, `.mht` |
| Электронная почта | `.eml`, `.msg`, `.pst`, `.ost`, `.mbox` |

Классификация выполняется на основании расширения файла. Наличие формата в этом каталоге не означает внутреннего анализа, извлечения специфических метаданных или структурной проверки всех форматов.

**Архитектурное примечание:** каталог `time_stamp.py` в настоящее время независим от каталога, определённого в `forensic_core.py`, хотя оба содержат одинаковые расширения.

## 4. Вычисление SHA-256 и контроль во время чтения

Для каждого поддерживаемого файла модуль вычисляет хеш SHA-256 посредством бинарного чтения блоками по **1 MiB**.

Вычисление выполняется с использованием открытого файлового дескриптора. До и после чтения атрибуты извлекаются с помощью `os.fstat()`.

Результат содержит следующие поля:

| Поле | Описание |
|---|---|
| `sha256` | Криптографический хеш SHA-256. |
| `hash_status` | Статус операции вычисления хеша. |
| `size_bytes` | Размер файла в байтах. |
| `mtime_utc` | Время последней модификации файловой системы в UTC. |
| `ctime_utc` | Временной атрибут `ctime`, выраженный в UTC. |
| `file_changed_during_read` | Индикатор обнаруженных изменений размера или `mtime` во время чтения. |

При ошибке чтения модуль регистрирует статус `ERROR` и соответствующие сведения об ошибке.

Сравнение атрибутов позволяет обнаруживать определённые изменения во время операции, но не является абсолютной гарантией того, что файл оставался неизменным на протяжении всего процесса.

## 5. Временные атрибуты

Модуль регистрирует временные атрибуты, предоставляемые файловой системой:

- `mtime`: время последней модификации.
- `ctime`: временной атрибут, значение которого зависит от операционной системы.

Значения преобразуются в формат UTC.

Эти данные описывают атрибуты, наблюдаемые во время выполнения. Они не обязательно представляют первоначальную дату создания, момент съёмки или фактический момент включения файла в цифровое дело.

## 6. Создание производного HTML-документа

Модуль обрабатывает идентифицированные в исходном HTML элементы `article.card`.

Для каждой записи:

1. Определяет соответствующее дело.
2. Обнаруживает связанные файлы.
3. Вычисляет их хеши и регистрирует атрибуты.
4. Формирует описательный блок артефактов.
5. Добавляет этот блок в производную копию HTML-документа.

Создаваемый блок содержит такую информацию, как:

- Категория файла.
- Имя файла.
- Хеш SHA-256.
- Статус вычисления хеша.
- Время модификации файловой системы в UTC.

Если HTML содержит предыдущий блок с идентификатором `forensic-artifacts-block`, модуль пытается удалить его перед добавлением нового результата.

Исходный документ используется в качестве входных данных; дополненный HTML записывается в выходной каталог.

## 7. JSON-отчёт

Помимо производного HTML модуль создаёт отдельный JSON-отчёт.

Документ включает:

| Поле | Описание |
|---|---|
| `tool` | Идентификация инструмента. |
| `version` | Версия модуля. |
| `generated_at_utc` | Дата создания отчёта. |
| `source_html` | Имя входного HTML-документа. |
| `records_processed` | Количество обработанных записей. |
| `records` | Результаты по каждой записи. |

Каждая запись содержит сведения о соответствующей папке, количестве обнаруженных файлов и технических данных каждого файла.

## 8. Логи и отслеживаемость выполнения

Каждое выполнение использует уникальный временной идентификатор UTC с микросекундами и дополнительным уникальным суффиксом.

Модуль создаёт отдельный файл лога и одновременно выводит информацию в консоль.

Логи позволяют просматривать операции, предупреждения, ошибки доступа и результаты обнаружения файлов.

## 9. Проверки путей и чтения

Код содержит проверки, предназначенные для снижения риска обработки непредусмотренных путей:

- Проверяет существование входного каталога и то, что он является каталогом.
- Отклоняет имена индексов, представляющие собой пути или подкаталоги.
- Не допускает совпадения выходного каталога с входным или его размещения внутри него.
- Проверяет, что входной HTML является обычным файлом внутри корневого каталога.
- Пропускает обнаруженные символические ссылки во время поиска.
- Проверяет, что обнаруженные файлы находятся внутри папки соответствующей записи.

Эти проверки являются частью валидации путей и обхода файлов. Их не следует рассматривать как абсолютную защиту от всех условий гонки или одновременных изменений файловой системы.

## 10. Запуск

Модуль запускается из командной строки с помощью трёх аргументов:

```bash
python time_stamp.py --input "/path/to/case" --output "/path/to/results" --index "index.html"
```

| Аргумент | Назначение |
|---|---|
| `--input` | Корневой каталог исходного дела. |
| `--output` | Отдельный каталог для производных результатов. |
| `--index` | Имя исходного HTML-файла, расположенного непосредственно во входном каталоге. |

Аргумент `--index` является необязательным; по умолчанию используется `index.html`.

## 11. Создаваемые файлы

Модуль создаёт следующие артефакты:

| Файл | Содержимое |
|---|---|
| `*_FIXED.html` | Производная копия HTML с добавленными описательными блоками. |
| `time_stamp_sync_<run_stamp>.json` | Структурированный отчёт о записях и обнаруженных файлах. |
| `time_stamp_sync_<run_stamp>.log` | Журнал выполнения. |

Результаты записываются в отдельный каталог, указанный через `--output`.

## 12. Методологическая область действия и ограничения

Time Stamp является модулем технического документирования **после получения данных (post-acquisition)**. Он не выполняет сбор данных или scraping в реальном времени из Google Maps и других платформ.

Вычисление SHA-256 идентифицирует байты, прочитанные во время выполнения, и позволяет впоследствии сравнивать криптографические хеши. Само по себе оно не доказывает историческую подлинность, авторство, происхождение или целостность с момента первоначального получения файла.

Атрибуты `mtime` и `ctime` отражают сведения, предоставляемые файловой системой, и не являются надёжной временной меткой.

Модуль не выполняет полный структурный анализ 27 распознаваемых форматов и не удостоверяет подлинность обрабатываемых файлов.

Ссылка на ISO/IEC 27037:2012 используется в качестве методологической основы и не означает сертификацию или полное соответствие программного обеспечения данному стандарту.