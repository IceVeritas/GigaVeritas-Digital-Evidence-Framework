<div align="right">
<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>
</div>

---

<a id="bg"></a>

# Manifest — Консолидиране и документално представяне на цифрови доказателства

**IceVeritas Manifest 2.0** (`manifest.py`) е Python модул, предназначен за консолидиране на резултатите, генерирани от модулите **Solo Lectura** и **Time Stamp**.

Основната му функция е да обедини техническите резултати от двата JSON източника, да съпостави съответните записи и файлове и да генерира структуриран манифест с допълнителни HTML и TXT отчети.

Модулът използва оригиналния HTML индекс като допълнителен документален източник за извличане на информация, която не се съдържа в двата JSON отчета.

## 1. Отговорности на модула

Модулът извършва следните операции:

- Зареждане на JSON отчетите от Solo Lectura и Time Stamp.
- Проверка на структурата на входните JSON документи.
- Корелация на записите чрез идентификатора `record_id`.
- Съпоставяне на файловете по относителен път, име и тип.
- Сравнение на SHA-256 хешовете от двата модула.
- Оценка на състоянието на съпоставените файлове.
- Консолидиране на техническите резултати.
- Извличане на допълнителна документална информация от оригиналния HTML индекс.
- Генериране на JSON манифест.
- Генериране на HTML отчет.
- Генериране на индивидуални TXT отчети за обработените записи.
- Изчисляване на SHA-256 хешове за генерираните TXT отчети.

## 2. Структура на входните данни

Manifest използва два основни входни източника:

- **Solo Lectura JSON** — съдържа резултатите от техническата инвентаризация, информация за файловете, SHA-256 хешовете и наличните резултати от структурните проверки.
- **Time Stamp JSON** — съдържа откритите файлове, техните SHA-256 хешове, размери, времеви атрибути и информация за евентуални промени по време на четене.

Тези два JSON документа представляват основните източници за техническото консолидиране.

### Допълнителен документален източник

Модулът може да използва и оригиналния HTML индекс на досието.

Пътят до него се определя чрез полетата:

- `input_directory`
- `index_filename`

Те се получават от JSON отчета на Solo Lectura.

HTML индексът се използва единствено за извличане на допълнителни документални полета и изчисляване на SHA-256 на самия HTML документ.

Той не участва в корелацията на файловете или в сравнението на SHA-256 между Solo Lectura и Time Stamp.

Ако HTML документът не е наличен, модулът може да продължи обработката. В този случай съответната документална информация се отбелязва като недостъпна.

## 3. Корелация на записите и файловете

Записите от двата JSON източника се съпоставят чрез идентификатора `record_id`.

Модулът обединява идентификаторите, налични в двата отчета, като запазва реда на първоначалното им откриване.

В рамките на всеки запис файловете се съпоставят последователно:

1. По относителен път (`relative_path`).
2. При липса на съвпадение — по име и тип на файла.

Поддържаните от Manifest файлови типове са:

| Категория | Разширение |
|---|---|
| Изображение | `.png` |
| Видео | `.mkv` |
| Документ | `.txt` |

Файлове, които не попадат в тези три категории, не се включват в файловата корелация на Manifest.

Файловете, открити само в единия JSON източник, също се включват в резултата, когато отговарят на поддържаните типове. Те се маркират като непълни, когато липсва съответстващ файл от другия източник.

## 4. Извличане на документална информация

За допълнителната документална информация модулът анализира оригиналния HTML индекс.

Идентифицират се елементите `article`, които съдържат класа `card` и атрибута `data-audit-id`.

Извличат се следните полета, когато са налични:

- `autor`
- `idioma`
- `antiguedad`
- `texto-resena`
- `texto-respuesta`
- `url-resena`
- `utc-timestamp`
- `png-last-modified-utc`
- `folder`

Допълнително се запазват атрибутите:

- `data-location`
- `data-highway`

За полето `url-resena` се използва стойността на HTML атрибута `href`.

Текстовите стойности се нормализират, като се премахват излишните интервали и се запазват границите между абзаците.

Когато за едно поле бъдат открити няколко различни стойности, то се маркира като двусмислено чрез `ambiguous_fields`.

Това предотвратява произволния избор на една от различаващите се стойности.

**Важно:** HTML индексът е допълнителен документален източник. Техническата корелация и сравненията SHA-256 се извършват въз основа на двата JSON отчета.

## 5. Сравнение на SHA-256 и оценка на състоянието

Manifest сравнява SHA-256 хешовете, получени от Solo Lectura и Time Stamp за съпоставените файлове.

Възможните състояния са:

| Статус | Значение |
|---|---|
| `COINCIDENTE` | Наличните SHA-256 хешове съвпадат. |
| `DISCREPANCIA` | Наличните SHA-256 хешове се различават. |
| `CAMBIO_DURANTE_LECTURA` | Регистрирана е промяна по време на четене на файла. |
| `ERROR` | Регистрирана е грешка при обработката или изчисляването на хеша. |
| `INCOMPLETO` | Липсва съответстващ файл в един от двата източника. |
| `NO_VERIFICABLE` | Няма достатъчно данни за извършване на сравнението. |

При оценката се вземат предвид:

- Наличието на съответстващи файлове.
- Наличието на SHA-256 хешове.
- Статусите на операциите по хеширане.
- Индикаторът `file_changed_during_read`.

Общият статус на всеки запис се определя въз основа на състоянията на включените в него файлове.

Приоритетът на състоянията е:

1. `CAMBIO_DURANTE_LECTURA`
2. `ERROR`
3. `DISCREPANCIA`
4. `INCOMPLETO`
5. `NO_VERIFICABLE`
6. `COINCIDENTE`

Съвпадението на SHA-256 хешовете показва съгласуваност между резултатите на двата модула. То не представлява независимо доказателство за автентичност или историческа цялост на цифровото съдържание.

## 6. Консолидиране на техническата информация

За всеки обработен запис Manifest обединява:

- Идентификатора на записа.
- Статуса на записа.
- Информацията от Solo Lectura.
- Информацията от Time Stamp.
- Данните за съпоставените файлове.
- SHA-256 хешовете от двата източника.
- Статусите на хеширането.
- Размерите на файловете.
- Времевите атрибути `mtime` и `ctime`.
- Информацията за промени по време на четене.
- Наличните резултати от структурните проверки на PNG.

За PNG файловете се включват наличните резултати от структурната проверка, извършена от Solo Lectura.

Те могат да съдържат информация за:

- Валидност на PNG сигнатурата.
- Проверени chunks.
- Грешки CRC.
- Грешки при валидация.
- Предупреждения.
- Chunk `tIME`.
- Вътрешни текстови метаданни.

За MKV файловете вътрешните метаданни на контейнера се обозначават като `NO ANALIZADO`.

Модулът не извършва самостоятелно нов структурен анализ на оригиналните файлове.

## 7. Генериране на JSON манифест

Manifest създава структуриран JSON документ, който обединява резултатите от обработката.

Използваната схема е:

`iceveritas.manifest/2.0`

Манифестът съдържа:

- Идентификатор на одита.
- Дата и час на генериране в UTC.
- Пътища към входните JSON файлове.
- Път към HTML източника, когато е наличен.
- Информация за версиите на използваните модули.
- Обобщена статистика.
- Корелирани записи.
- Информация за свързаните файлове.
- Резултати от сравненията SHA-256.
- Индивидуални статуси на файловете.
- Информация за генерираните TXT отчети.
- SHA-256 на HTML източника, когато е наличен.
- Методологични бележки.

Идентификаторът на одита се генерира с времеви компонент UTC и уникален суфикс.

## 8. Генериране на HTML отчет

Модулът създава HTML отчет за визуално представяне на консолидираните резултати.

Отчетът включва:

- Идентификатор на одита.
- Дата и час на генериране.
- Обобщение на обработените записи.
- Статистика за файловете.
- Резултати от SHA-256 сравненията.
- Статуси на проверките.
- Информация за отделните записи.
- Карти с информация за файловете.
- Връзки към индивидуалните TXT отчети.
- Възможност за копиране на SHA-256 стойностите.
- Методологични бележки и ограничения.

За PNG файловете HTML отчетът представя наличните резултати от структурната валидация.

За MKV файловете вътрешните метаданни на контейнера се обозначават като неанализирани.

HTML отчетът е производен документ и не замества оригиналните файлове или входните JSON отчети.

## 9. Индивидуални TXT отчети

За всеки обработен запис се генерира отделен TXT документ.

Документът съдържа структурирана информация за конкретния запис и свързаните с него файлове.

Сред включените данни са:

- Идентификатор на одита.
- Идентификатор на записа.
- Общ статус на целостта.
- Документална информация от HTML индекса, когато е налична.
- URL на оригиналния запис, когато е наличен.
- Текст на отзива и отговора, когато са налични.
- Информация за свързаните файлове.
- SHA-256 хешове от двата модула.
- Размери и времеви атрибути.
- Резултати от структурната проверка на PNG.
- Методологични ограничения.

При двусмислени документални полета информацията се отбелязва като недостъпна поради установена двусмисленост.

След генерирането на всеки TXT документ се изчислява неговият SHA-256 хеш.

Тази стойност се включва в JSON манифеста за идентифициране на генерирания отчет.

## 10. Статистика и обобщени резултати

Manifest генерира обобщена статистика за обработените записи и файлове.

Сред показателите са:

- Брой документирани записи.
- Брой файлове, свързани със записите.
- Брой PNG файлове.
- Брой MKV файлове.
- Брой TXT документи.
- Брой изследвани файлове.
- Брой SHA-256 сравнения.
- Брой съвпадения.
- Брой несъответствия.
- Брой грешки.
- Брой непълни резултати.
- Брой промени по време на четене.
- Брой непроверими файлове.
- Брой генерирани индивидуални TXT отчети.

Статистиката отразява резултатите от конкретното изпълнение и не представлява постоянна характеристика на системата.

## 11. Структура на резултатите

Manifest организира генерираните резултати в три отделни директории:

```text
Project/
│
├── json/
│   └── manifest_*.json
│
├── manifest_html/
│   └── manifest_*.html
│
└── txt/
    └── EVIDENCE_*.txt
```

Входните JSON файлове също могат да се намират в поддиректорията `json/`.

Генерираните резултати се записват в съответните директории под основната изходна директория.

## 12. Изпълнение

Модулът се стартира от командния ред.

Основна команда:

```bash
python manifest.py
```

По подразбиране модулът използва основната директория на проекта и търси най-новите подходящи JSON отчети в поддиректорията `json/`.

За изрично задаване на входните JSON файлове и отделна директория за резултатите:

```bash
python manifest.py --solo_json .\json\solo_lectura.json --timestamp_json .\json\time_stamp.json --output_dir .\Output
```

Поддържани аргументи:

| Аргумент | Функция |
|---|---|
| `--solo_json` | Път до JSON отчета на Solo Lectura. |
| `--timestamp_json` | Път до JSON отчета на Time Stamp. |
| `--output_dir` | Основна директория за генерираните резултати. |

**Важно:** `--output_dir` определя както директорията за търсене на входните JSON файлове в поддиректорията `json/`, така и мястото за генериране на резултатите.

Ако входните JSON файлове се намират извън `--output_dir/json/`, техните пътища трябва да бъдат зададени изрично чрез `--solo_json` и `--timestamp_json`.

## 13. Методологичен обхват и ограничения

Manifest е модул за консолидиране и документално представяне на резултати, генерирани от предходните компоненти.

Той не извършва самостоятелно:

- Първоначално придобиване на цифрови доказателства.
- Заснемане или извличане на данни в реално време от онлайн платформи.
- Пълно повторно изследване на оригиналните файлове.
- Независима проверка на авторството или произхода.
- Удостоверяване на първоначалния момент на създаване или заснемане.

Съвпадението на SHA-256 хешовете между Solo Lectura и Time Stamp показва съгласуваност между резултатите, но не представлява две независими доказателства за автентичност.

Времевите атрибути `mtime` и `ctime` са характеристики на файловата система и не удостоверяват сами по себе си първоначалната дата на създаване или заснемане.

Документалната информация зависи от наличните полета в HTML индекса. При липса на HTML източник техническата консолидация може да продължи, но съответните документални полета ще бъдат отбелязани като недостъпни.

## 14. Методологична референция

Проектът използва като методологична отправна точка:

**ISO/IEC 27037:2012** — Guidelines for identification, collection, acquisition and preservation of digital evidence.

Позоваването на този стандарт представлява методологична ориентация. То не означава сертификация, акредитация или пълно съответствие на софтуера с изискванията на стандарта.

---

<a id="es"></a>

# Manifest — Consolidación y documentación de evidencias digitales

**IceVeritas Manifest 2.0** (`manifest.py`) es un módulo Python destinado a consolidar los resultados generados por los módulos **Solo Lectura** y **Time Stamp**.

Su función principal consiste en reunir los resultados técnicos de ambas fuentes JSON, correlacionar los registros y archivos correspondientes y generar un manifiesto estructurado acompañado de informes HTML y TXT.

El módulo utiliza el índice HTML original como fuente documental complementaria para extraer información que no está incorporada en los dos informes JSON.

## 1. Responsabilidades del módulo

El módulo realiza las siguientes operaciones:

- Carga de los informes JSON de Solo Lectura y Time Stamp.
- Validación de la estructura de los documentos JSON de entrada.
- Correlación de registros mediante el identificador `record_id`.
- Emparejamiento de archivos por ruta relativa, nombre y tipo.
- Comparación de las huellas SHA-256 de ambos módulos.
- Evaluación del estado de los archivos correlacionados.
- Consolidación de los resultados técnicos.
- Extracción de información documental complementaria del índice HTML original.
- Generación de un manifiesto JSON.
- Generación de un informe HTML.
- Generación de informes TXT individuales para los registros procesados.
- Cálculo de huellas SHA-256 de los informes TXT generados.

## 2. Estructura de entrada

Manifest utiliza dos fuentes principales de entrada:

- **Solo Lectura JSON:** contiene los resultados del inventario técnico, información de los archivos, huellas SHA-256 y resultados disponibles de las comprobaciones estructurales.
- **Time Stamp JSON:** contiene los archivos descubiertos, sus huellas SHA-256, tamaños, atributos temporales e información sobre posibles cambios durante la lectura.

Estos dos documentos JSON constituyen las fuentes principales para la consolidación técnica.

### Fuente documental complementaria

El módulo también puede utilizar el índice HTML original del expediente.

Su ruta se determina mediante los campos:

- `input_directory`
- `index_filename`

Estos valores proceden del informe JSON de Solo Lectura.

El índice HTML se utiliza exclusivamente para extraer campos documentales complementarios y calcular la huella SHA-256 del propio documento HTML.

No interviene en la correlación de archivos ni en la comparación SHA-256 entre Solo Lectura y Time Stamp.

Si el documento HTML no está disponible, el módulo puede continuar el procesamiento. En ese caso, la información documental correspondiente se identifica como no disponible.

## 3. Correlación de registros y archivos

Los registros de ambas fuentes JSON se correlacionan mediante el identificador `record_id`.

El módulo reúne los identificadores disponibles en ambos informes, conservando el orden de su primera aparición.

Dentro de cada registro, los archivos se emparejan siguiendo este orden:

1. Por ruta relativa (`relative_path`).
2. Si no existe coincidencia, por nombre y tipo de archivo.

Manifest procesa los siguientes tipos de archivo:

| Categoría | Extensión |
|---|---|
| Imagen | `.png` |
| Vídeo | `.mkv` |
| Documento | `.txt` |

Los archivos que no pertenecen a estas tres categorías no se incorporan a la correlación de archivos de Manifest.

Los archivos encontrados únicamente en uno de los dos JSON también se incluyen en el resultado cuando pertenecen a los tipos admitidos. Se identifican como incompletos cuando falta el archivo correspondiente en la otra fuente.

## 4. Extracción de información documental

Para obtener información documental complementaria, el módulo analiza el índice HTML original.

Identifica los elementos `article` que contienen la clase `card` y el atributo `data-audit-id`.

Se extraen los siguientes campos, cuando están disponibles:

- `autor`
- `idioma`
- `antiguedad`
- `texto-resena`
- `texto-respuesta`
- `url-resena`
- `utc-timestamp`
- `png-last-modified-utc`
- `folder`

Adicionalmente, se conservan los atributos:

- `data-location`
- `data-highway`

Para el campo `url-resena` se utiliza el valor del atributo HTML `href`.

Los valores de texto se normalizan eliminando los espacios innecesarios y conservando los límites entre párrafos.

Cuando se encuentran varios valores diferentes para un mismo campo, este se identifica como ambiguo mediante `ambiguous_fields`.

Esto evita seleccionar arbitrariamente uno de los valores discrepantes.

**Importante:** el índice HTML es una fuente documental complementaria. La correlación técnica y las comparaciones SHA-256 se realizan a partir de los dos informes JSON.

## 5. Comparación SHA-256 y evaluación de estados

Manifest compara las huellas SHA-256 proporcionadas por Solo Lectura y Time Stamp para los archivos que han podido correlacionarse.

Los estados posibles son:

| Estado | Significado |
|---|---|
| `COINCIDENTE` | Las huellas SHA-256 disponibles coinciden. |
| `DISCREPANCIA` | Las huellas SHA-256 disponibles son diferentes. |
| `CAMBIO_DURANTE_LECTURA` | Se ha registrado un cambio durante la lectura del archivo. |
| `ERROR` | Se ha registrado un error durante el procesamiento o el cálculo del hash. |
| `INCOMPLETO` | Falta el archivo correspondiente en una de las dos fuentes. |
| `NO_VERIFICABLE` | No existen datos suficientes para realizar la comparación. |

La evaluación tiene en cuenta:

- La existencia de archivos correspondientes.
- La disponibilidad de huellas SHA-256.
- Los estados de las operaciones de hash.
- El indicador `file_changed_during_read`.

El estado general de cada registro se determina a partir de los estados de los archivos que contiene.

La prioridad aplicada a los estados es:

1. `CAMBIO_DURANTE_LECTURA`
2. `ERROR`
3. `DISCREPANCIA`
4. `INCOMPLETO`
5. `NO_VERIFICABLE`
6. `COINCIDENTE`

La coincidencia de las huellas SHA-256 demuestra consistencia entre los resultados de ambos módulos. No constituye una prueba independiente de autenticidad ni de integridad histórica del contenido digital.

## 6. Consolidación de información técnica

Para cada registro procesado, Manifest reúne:

- Identificador del registro.
- Estado del registro.
- Información procedente de Solo Lectura.
- Información procedente de Time Stamp.
- Datos de los archivos correlacionados.
- Huellas SHA-256 de ambas fuentes.
- Estados de las operaciones de hash.
- Tamaños de los archivos.
- Atributos temporales `mtime` y `ctime`.
- Información sobre cambios durante la lectura.
- Resultados disponibles de las comprobaciones estructurales PNG.

Para los archivos PNG se incorporan los resultados disponibles de la validación estructural realizada por Solo Lectura.

Estos pueden incluir información sobre:

- Validez de la firma PNG.
- Chunks comprobados.
- Errores CRC.
- Errores de validación.
- Advertencias.
- Chunk `tIME`.
- Metadatos internos de texto.

Para los archivos MKV, los metadatos internos del contenedor se identifican como `NO ANALIZADO`.

El módulo no realiza por sí mismo un nuevo análisis estructural de los archivos originales.

## 7. Generación del manifiesto JSON

Manifest crea un documento JSON estructurado que reúne los resultados del procesamiento.

El esquema utilizado es:

`iceveritas.manifest/2.0`

El manifiesto contiene:

- Identificador de auditoría.
- Fecha y hora de generación en UTC.
- Rutas de los archivos JSON de entrada.
- Ruta del HTML de origen, cuando está disponible.
- Información de las versiones de los módulos utilizados.
- Estadísticas consolidadas.
- Registros correlacionados.
- Información de los archivos asociados.
- Resultados de las comparaciones SHA-256.
- Estados individuales de los archivos.
- Información de los informes TXT generados.
- SHA-256 del HTML de origen, cuando está disponible.
- Observaciones metodológicas.

El identificador de auditoría se genera mediante un componente temporal UTC y un sufijo único.

## 8. Generación del informe HTML

El módulo genera un informe HTML para la presentación visual de los resultados consolidados.

El informe incluye:

- Identificador de auditoría.
- Fecha y hora de generación.
- Resumen de los registros procesados.
- Estadísticas de los archivos.
- Resultados de las comparaciones SHA-256.
- Estados de las comprobaciones.
- Información de los registros individuales.
- Tarjetas con información de los archivos.
- Enlaces a los informes TXT individuales.
- Funciones para copiar valores SHA-256.
- Observaciones metodológicas y limitaciones.

Para los archivos PNG, el informe HTML presenta los resultados disponibles de la validación estructural.

Para los archivos MKV, los metadatos internos del contenedor se identifican como no analizados.

El informe HTML es un documento derivado y no sustituye a los archivos originales ni a los informes JSON de entrada.

## 9. Informes TXT individuales

Para cada registro procesado se genera un documento TXT independiente.

El documento contiene información estructurada del registro y de los archivos asociados.

Entre los datos incluidos se encuentran:

- Identificador de auditoría.
- Identificador del registro.
- Estado general de integridad.
- Información documental procedente del índice HTML, cuando está disponible.
- URL del registro original, cuando está disponible.
- Texto de la reseña y de la respuesta, cuando están disponibles.
- Información de los archivos asociados.
- Huellas SHA-256 de ambos módulos.
- Tamaños y atributos temporales.
- Resultados de la validación estructural PNG.
- Limitaciones metodológicas.

Cuando existen campos documentales ambiguos, la información se identifica como no disponible debido a la ambigüedad detectada.

Después de generar cada documento TXT, se calcula su huella SHA-256.

Este valor se incorpora al manifiesto JSON para identificar el informe generado.

## 10. Estadísticas y resultados consolidados

Manifest genera estadísticas resumidas de los registros y archivos procesados.

Entre los indicadores se encuentran:

- Número de registros documentados.
- Número de archivos asociados a los registros.
- Número de archivos PNG.
- Número de archivos MKV.
- Número de documentos TXT.
- Número de archivos examinados.
- Número de comparaciones SHA-256.
- Número de coincidencias.
- Número de discrepancias.
- Número de errores.
- Número de resultados incompletos.
- Número de cambios durante la lectura.
- Número de archivos no verificables.
- Número de informes TXT individuales generados.

Las estadísticas representan los resultados de una ejecución concreta y no deben interpretarse como características permanentes del sistema.

## 11. Estructura de resultados

Manifest organiza los resultados generados en tres directorios independientes:

```text
Project/
│
├── json/
│   └── manifest_*.json
│
├── manifest_html/
│   └── manifest_*.html
│
└── txt/
    └── EVIDENCE_*.txt
```

Los JSON de entrada también pueden encontrarse en el subdirectorio `json/`.

Los resultados generados se almacenan en los directorios correspondientes dentro del directorio principal de salida.

## 12. Ejecución

El módulo se ejecuta desde la línea de comandos.

Comando básico:

```bash
python manifest.py
```

Por defecto, el módulo utiliza el directorio principal del proyecto y busca los informes JSON adecuados más recientes en el subdirectorio `json/`.

Para especificar explícitamente los JSON de entrada y utilizar un directorio independiente para los resultados:

```bash
python manifest.py --solo_json .\json\solo_lectura.json --timestamp_json .\json\time_stamp.json --output_dir .\Output
```

Argumentos disponibles:

| Argumento | Función |
|---|---|
| `--solo_json` | Ruta del informe JSON de Solo Lectura. |
| `--timestamp_json` | Ruta del informe JSON de Time Stamp. |
| `--output_dir` | Directorio principal de los resultados generados. |

**Importante:** `--output_dir` determina tanto el directorio donde se buscan los JSON dentro de la subcarpeta `json/` como la ubicación donde se generan los resultados.

Si los JSON de entrada están fuera de `--output_dir/json/`, sus rutas deben especificarse explícitamente mediante `--solo_json` y `--timestamp_json`.

## 13. Alcance y limitaciones metodológicas

Manifest es un módulo de consolidación y presentación documental de resultados generados por los componentes anteriores.

No realiza por sí mismo:

- La adquisición inicial de evidencias digitales.
- La captura o extracción de datos en vivo desde plataformas en línea.
- Un nuevo examen completo de los archivos originales.
- La verificación independiente de la autoría o procedencia.
- La acreditación del momento original de creación o captura.

La coincidencia de las huellas SHA-256 entre Solo Lectura y Time Stamp demuestra consistencia entre los resultados recibidos, pero no constituye dos pruebas independientes de autenticidad.

Los atributos temporales `mtime` y `ctime` son características del sistema de archivos y no acreditan por sí solos la fecha original de creación o captura.

La información documental depende de los campos disponibles en el índice HTML. Cuando no existe una fuente HTML accesible, la consolidación técnica puede continuar, pero los campos documentales correspondientes se identificarán como no disponibles.

## 14. Referencia metodológica

El proyecto utiliza como referencia metodológica:

**ISO/IEC 27037:2012** — Guidelines for identification, collection, acquisition and preservation of digital evidence.

La referencia a esta norma constituye una orientación metodológica. No implica certificación, acreditación ni conformidad integral del software con los requisitos de dicha norma.

---

<a id="ru"></a>

# Manifest — Консолидация и документирование цифровых доказательств

**IceVeritas Manifest 2.0** (`manifest.py`) — это модуль Python, предназначенный для консолидации результатов, сформированных модулями **Solo Lectura** и **Time Stamp**.

Его основная функция заключается в объединении технических результатов двух JSON-источников, сопоставлении соответствующих записей и файлов, а также создании структурированного манифеста с дополнительными HTML- и TXT-отчётами.

Модуль использует исходный HTML-индекс в качестве дополнительного документального источника для извлечения информации, которая не содержится в двух JSON-отчётах.

## 1. Назначение модуля

Модуль выполняет следующие операции:

- Загрузка JSON-отчётов Solo Lectura и Time Stamp.
- Проверка структуры входных JSON-документов.
- Сопоставление записей посредством идентификатора `record_id`.
- Сопоставление файлов по относительному пути, имени и типу.
- Сравнение SHA-256-хешей обоих модулей.
- Оценка состояния сопоставленных файлов.
- Консолидация технических результатов.
- Извлечение дополнительной документальной информации из исходного HTML-индекса.
- Создание JSON-манифеста.
- Создание HTML-отчёта.
- Создание отдельных TXT-отчётов для обработанных записей.
- Вычисление SHA-256-хешей созданных TXT-отчётов.

## 2. Входная структура

Manifest использует два основных входных источника:

- **Solo Lectura JSON** — содержит результаты технической инвентаризации, сведения о файлах, SHA-256-хеши и доступные результаты структурных проверок.
- **Time Stamp JSON** — содержит обнаруженные файлы, их SHA-256-хеши, размеры, временные атрибуты и сведения о возможных изменениях во время чтения.

Эти два JSON-документа являются основными источниками для технической консолидации.

### Дополнительный документальный источник

Модуль также может использовать исходный HTML-индекс дела.

Его путь определяется полями:

- `input_directory`
- `index_filename`

Эти значения извлекаются из JSON-отчёта Solo Lectura.

HTML-индекс используется исключительно для извлечения дополнительных документальных полей и вычисления SHA-256 самого HTML-документа.

Он не участвует в сопоставлении файлов или сравнении SHA-256 между Solo Lectura и Time Stamp.

Если HTML-документ недоступен, модуль может продолжить обработку. В этом случае соответствующая документальная информация обозначается как недоступная.

## 3. Сопоставление записей и файлов

Записи из двух JSON-источников сопоставляются посредством идентификатора `record_id`.

Модуль объединяет идентификаторы, доступные в обоих отчётах, сохраняя порядок их первоначального обнаружения.

Внутри каждой записи файлы сопоставляются последовательно:

1. По относительному пути (`relative_path`).
2. При отсутствии совпадения — по имени и типу файла.

Manifest обрабатывает следующие типы файлов:

| Категория | Расширение |
|---|---|
| Изображение | `.png` |
| Видео | `.mkv` |
| Документ | `.txt` |

Файлы, не относящиеся к этим трём категориям, не включаются в файловое сопоставление Manifest.

Файлы, обнаруженные только в одном из двух JSON-источников, также включаются в результат, если относятся к поддерживаемым типам. При отсутствии соответствующего файла во втором источнике они отмечаются как неполные.

## 4. Извлечение документальной информации

Для получения дополнительной документальной информации модуль анализирует исходный HTML-индекс.

Он идентифицирует элементы `article`, содержащие класс `card` и атрибут `data-audit-id`.

Извлекаются следующие поля, если они доступны:

- `autor`
- `idioma`
- `antiguedad`
- `texto-resena`
- `texto-respuesta`
- `url-resena`
- `utc-timestamp`
- `png-last-modified-utc`
- `folder`

Дополнительно сохраняются атрибуты:

- `data-location`
- `data-highway`

Для поля `url-resena` используется значение HTML-атрибута `href`.

Текстовые значения нормализуются путём удаления лишних пробелов с сохранением границ между абзацами.

Если для одного поля обнаружено несколько различных значений, оно отмечается как неоднозначное посредством `ambiguous_fields`.

Это предотвращает произвольный выбор одного из противоречащих друг другу значений.

**Важно:** HTML-индекс является дополнительным документальным источником. Техническое сопоставление и сравнение SHA-256 выполняются на основании двух JSON-отчётов.

## 5. Сравнение SHA-256 и оценка состояния

Manifest сравнивает SHA-256-хеши, предоставленные Solo Lectura и Time Stamp, для файлов, которые удалось сопоставить.

Возможные статусы:

| Статус | Значение |
|---|---|
| `COINCIDENTE` | Доступные SHA-256-хеши совпадают. |
| `DISCREPANCIA` | Доступные SHA-256-хеши различаются. |
| `CAMBIO_DURANTE_LECTURA` | Зарегистрировано изменение во время чтения файла. |
| `ERROR` | Зарегистрирована ошибка при обработке или вычислении хеша. |
| `INCOMPLETO` | В одном из двух источников отсутствует соответствующий файл. |
| `NO_VERIFICABLE` | Недостаточно данных для выполнения сравнения. |

При оценке учитываются:

- Наличие соответствующих файлов.
- Доступность SHA-256-хешей.
- Статусы операций хеширования.
- Индикатор `file_changed_during_read`.

Общий статус каждой записи определяется на основании состояний входящих в неё файлов.

Приоритет статусов следующий:

1. `CAMBIO_DURANTE_LECTURA`
2. `ERROR`
3. `DISCREPANCIA`
4. `INCOMPLETO`
5. `NO_VERIFICABLE`
6. `COINCIDENTE`

Совпадение SHA-256-хешей свидетельствует о согласованности результатов двух модулей. Оно не является независимым доказательством подлинности или исторической целостности цифрового содержимого.

## 6. Консолидация технической информации

Для каждой обработанной записи Manifest объединяет:

- Идентификатор записи.
- Статус записи.
- Информацию из Solo Lectura.
- Информацию из Time Stamp.
- Данные сопоставленных файлов.
- SHA-256-хеши из обоих источников.
- Статусы операций хеширования.
- Размеры файлов.
- Временные атрибуты `mtime` и `ctime`.
- Сведения об изменениях во время чтения.
- Доступные результаты структурных проверок PNG.

Для PNG-файлов включаются доступные результаты структурной проверки, выполненной Solo Lectura.

Они могут содержать сведения о:

- Валидности сигнатуры PNG.
- Проверенных chunks.
- Ошибках CRC.
- Ошибках валидации.
- Предупреждениях.
- Chunk `tIME`.
- Внутренних текстовых метаданных.

Для MKV-файлов внутренние метаданные контейнера обозначаются как `NO ANALIZADO`.

Модуль самостоятельно не выполняет повторный структурный анализ исходных файлов.

## 7. Создание JSON-манифеста

Manifest создаёт структурированный JSON-документ, объединяющий результаты обработки.

Используемая схема:

`iceveritas.manifest/2.0`

Манифест содержит:

- Идентификатор аудита.
- Дату и время формирования в UTC.
- Пути к входным JSON-файлам.
- Путь к HTML-источнику, если он доступен.
- Информацию о версиях использованных модулей.
- Сводную статистику.
- Сопоставленные записи.
- Сведения о связанных файлах.
- Результаты сравнений SHA-256.
- Индивидуальные статусы файлов.
- Информацию о созданных TXT-отчётах.
- SHA-256 HTML-источника, если он доступен.
- Методологические замечания.

Идентификатор аудита формируется с использованием временного компонента UTC и уникального суффикса.

## 8. Создание HTML-отчёта

Модуль создаёт HTML-отчёт для визуального представления консолидированных результатов.

Отчёт включает:

- Идентификатор аудита.
- Дату и время формирования.
- Сводку обработанных записей.
- Статистику файлов.
- Результаты сравнений SHA-256.
- Статусы проверок.
- Информацию по отдельным записям.
- Карточки с информацией о файлах.
- Ссылки на индивидуальные TXT-отчёты.
- Возможность копирования значений SHA-256.
- Методологические замечания и ограничения.

Для PNG-файлов HTML-отчёт представляет доступные результаты структурной проверки.

Для MKV-файлов внутренние метаданные контейнера обозначаются как не исследованные.

HTML-отчёт является производным документом и не заменяет исходные файлы или входные JSON-отчёты.

## 9. Индивидуальные TXT-отчёты

Для каждой обработанной записи создаётся отдельный TXT-документ.

Документ содержит структурированную информацию о записи и связанных с ней файлах.

Включаемые данные могут содержать:

- Идентификатор аудита.
- Идентификатор записи.
- Общий статус целостности.
- Документальную информацию из HTML-индекса, если она доступна.
- URL исходной записи, если он доступен.
- Текст отзыва и ответа, если они доступны.
- Сведения о связанных файлах.
- SHA-256-хеши обоих модулей.
- Размеры и временные атрибуты.
- Результаты структурной проверки PNG.
- Методологические ограничения.

Если документальные поля неоднозначны, информация обозначается как недоступная из-за обнаруженной неоднозначности.

После создания каждого TXT-документа вычисляется его SHA-256-хеш.

Это значение включается в JSON-манифест для идентификации созданного отчёта.

## 10. Статистика и сводные результаты

Manifest формирует сводную статистику по обработанным записям и файлам.

Среди показателей:

- Количество документированных записей.
- Количество файлов, связанных с записями.
- Количество PNG-файлов.
- Количество MKV-файлов.
- Количество TXT-документов.
- Количество исследованных файлов.
- Количество сравнений SHA-256.
- Количество совпадений.
- Количество расхождений.
- Количество ошибок.
- Количество неполных результатов.
- Количество изменений во время чтения.
- Количество непроверяемых файлов.
- Количество созданных индивидуальных TXT-отчётов.

Статистика отражает результаты конкретного запуска и не должна интерпретироваться как постоянная характеристика системы.

## 11. Структура результатов

Manifest организует сформированные результаты в трёх отдельных каталогах:

```text
Project/
│
├── json/
│   └── manifest_*.json
│
├── manifest_html/
│   └── manifest_*.html
│
└── txt/
    └── EVIDENCE_*.txt
```

Входные JSON-файлы также могут находиться в подкаталоге `json/`.

Сформированные результаты сохраняются в соответствующих каталогах внутри основной выходной директории.

## 12. Запуск

Модуль запускается из командной строки.

Основная команда:

```bash
python manifest.py
```

По умолчанию модуль использует основную директорию проекта и ищет наиболее новые подходящие JSON-отчёты в подкаталоге `json/`.

Для явного указания входных JSON-файлов и использования отдельного каталога для результатов:

```bash
python manifest.py --solo_json .\json\solo_lectura.json --timestamp_json .\json\time_stamp.json --output_dir .\Output
```

Доступные аргументы:

| Аргумент | Назначение |
|---|---|
| `--solo_json` | Путь к JSON-отчёту Solo Lectura. |
| `--timestamp_json` | Путь к JSON-отчёту Time Stamp. |
| `--output_dir` | Основной каталог для сформированных результатов. |

**Важно:** `--output_dir` определяет как каталог для поиска входных JSON-файлов в подкаталоге `json/`, так и место формирования результатов.

Если входные JSON-файлы находятся вне `--output_dir/json/`, их пути необходимо явно указать через `--solo_json` и `--timestamp_json`.

## 13. Методологическая область действия и ограничения

Manifest является модулем консолидации и документального представления результатов, сформированных предыдущими компонентами.

Он самостоятельно не выполняет:

- Первоначальное получение цифровых доказательств.
- Захват или извлечение данных в реальном времени с онлайн-платформ.
- Полное повторное исследование исходных файлов.
- Независимую проверку авторства или происхождения.
- Подтверждение первоначального момента создания или съёмки.

Совпадение SHA-256-хешей между Solo Lectura и Time Stamp свидетельствует о согласованности полученных результатов, но не является двумя независимыми доказательствами подлинности.

Временные атрибуты `mtime` и `ctime` являются характеристиками файловой системы и сами по себе не подтверждают первоначальную дату создания или съёмки.

Документальная информация зависит от полей, доступных в HTML-индексе. При отсутствии доступного HTML-источника техническая консолидация может продолжаться, однако соответствующие документальные поля будут обозначены как недоступные.

## 14. Методологическая ссылка

Проект использует в качестве методологического ориентира:

**ISO/IEC 27037:2012** — Guidelines for identification, collection, acquisition and preservation of digital evidence.

Ссылка на данный стандарт служит методологической основой. Она не означает сертификацию, аккредитацию или полное соответствие программного обеспечения требованиям данного стандарта.

---

**IceVeritas — GigaVeritas Digital Evidence Framework**  
*Manifest · Consolidation and Documentary Reporting · Version 2.0*