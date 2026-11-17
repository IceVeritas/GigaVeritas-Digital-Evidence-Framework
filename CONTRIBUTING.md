<div align="right">
<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>
</div>

---

<a id="bg"></a>

# Ръководство за принос към проекта (Contributing)

Благодарим за интереса към проекта **GigaVeritas Digital Evidence Framework**.

GigaVeritas е проект, разработван от **IceVeritas**, предназначен за техническо изследване, документиране и консолидиране на предварително придобити цифрови доказателства.

Настоящият документ определя правилата и условията за участие в развитието на проекта.

> Документът подлежи на одобрение от поддържащия проекта.

## 1. Обхват на проекта

Всички приноси трябва да съответстват на текущия технически обхват на GigaVeritas.

Към настоящия момент рамката е насочена към обработката на локални доказателствени файлове и предварително придобити и документирани записи, представени като произхождащи от Google Maps.

Проектът към момента не претендира да предоставя:

- Придобиване на данни в реално време от Google Maps.
- Автоматизирано извличане (scraping) от онлайн платформи.
- Универсално придобиване на данни от други платформи.
- Независима проверка на първоначалното авторство или произхода на цифровото съдържание.
- Сертифицирано съхранение на цифрови доказателства.

Всяко предложено разширяване извън настоящия обхват трябва да бъде изрично описано, имплементирано, прегледано и тествано, преди да бъде представено като налична функционалност.

## 2. Видове приноси

Могат да бъдат предлагани следните видове подобрения:

- Отстраняване на програмни грешки.
- Подобрения на съществуващите модули.
- Подобрения в сигурността и надеждността.
- Корекции и допълнения в документацията.
- Синтетични тестови случаи.
- Подобрения в обработката на грешки.
- Подобрения в съвместимостта с поддържаните операционни системи и версии на Python.
- Подобрения в съгласуваността на генерираните отчети.

Всяка нова функционалност трябва да бъде придружена от описание на нейното предназначение, реализация и ограничения.

## 3. Изисквания преди изпращане на промени

Преди изпращане на принос:

1. Опишете проблема или предложеното подобрение.
2. Представете наблюдаваното поведение чрез синтетичен пример.
3. Посочете засегнатите модули и файлове.
4. Ограничете промените до ясно определена функционална област.
5. Актуализирайте съответната документация, когато се променят функционалности, изходни формати или технически договорености.
6. Добавете синтетични тестове за новите функционалности и съответните гранични случаи.
7. Посочете реално изпълнените команди и действително получените резултати.

Препоръчително е рефакторингът и функционалните промени да се изпращат отделно.

Това улеснява прегледа на промените, засягащи идентификацията на файловете, изчисляването на SHA-256 и генерираните отчети.

## 4. Цифрови доказателства, поверителност и чувствителна информация

**Не изпращайте реални доказателствени файлове или лична информация от конкретни случаи.**

Приносите не трябва да съдържат:

- Реални доказателствени материали или досиета.
- Лични имена или идентифицираща информация.
- Частни URL адреси или връзки към индивидуални записи.
- Реални идентификатори на одити.
- Екранни снимки с лична или чувствителна информация.
- Лични пътища до директории и файлове.
- Отчети, генерирани от реални разследвания.
- Хешове, свързани с реални доказателствени случаи.
- Пароли, API ключове, токени или други секретни данни.

За примери, документация и тестове използвайте синтетични записи и изкуствено генерирани файлове.

Преди изпращане на промени проверявайте всички модифицирани файлове, за да се уверите, че не е включена чувствителна информация.

## 5. Технически и методологични изисквания

Промените трябва да запазват разграничението между техническите наблюдения и форензичните заключения.

По-специално:

- Съвпадащият SHA-256 хеш доказва бинарна съгласуваност между сравняваните файлове.
- Съвпадението на хешовете само по себе си не доказва автентичност, авторство или произход.
- Времевите атрибути на файловата система, като `mtime` и `ctime`, са локални характеристики на файловете.
- Тези атрибути не установяват независимо първоначалната дата на създаване или заснемане.
- Успешната техническа проверка не трябва да се представя като сертификация.
- Една функционалност не трябва да се описва като реализирана, ако действително не присъства в кода.

Промените, засягащи генерираните JSON, HTML или TXT отчети, трябва да запазват съгласуваността между съответните изходни структури.

## 6. Качество на кода и съвместимост

Предложеният код трябва:

- Да следва съществуващите конвенции за програмиране на Python.
- Да предпочита стандартната библиотека на Python, когато това е подходящо.
- Да избягва ненужни външни зависимости.
- Да запазва предвидената обработка на оригиналните доказателствени файлове в режим само за четене.
- Да прилага подходяща проверка на входните и изходните пътища.
- Да обработва безопасно липсващи файлове и невалидни входни данни.
- Да не въвежда недокументирано поведение.
- Да запазва ясно разделение между отговорностите на отделните модули.

Промените, засягащи операциите с файловата система, трябва да бъдат преглеждани за рискове, свързани с:

- Излизане извън разрешената директория (path traversal).
- Символни връзки.
- Непреднамерен достъп до файлове извън предназначената директория на досието.

## 7. Тестване

Новата функционалност трябва да включва синтетични тестове, когато е приложимо, за:

- Валидни входни файлове.
- Липсващи входни файлове.
- Невалидни JSON документи.
- Липсващи или непълни записи.
- Резултати от сравненията SHA-256.
- Промени във файловете по време на четене.
- Невалидни пътища.
- Неочаквани файлови разширения.
- Генериране на изходни документи.
- Съгласуваност между JSON, HTML и TXT отчетите.

Като успешни могат да бъдат представяни единствено тестове, които действително са изпълнени.

Документацията трябва ясно да разграничава:

- Реализирана функционалност.
- Функционалност, тествана при определени условия.
- Планирана или експериментална функционалност.

Успешният синтетичен тест не доказва автентичността или произхода на реални доказателства.

## 8. Pull Requests

Всеки Pull Request трябва да съдържа:

- Ясно описание на предложената промяна.
- Причината за нейното въвеждане.
- Засегнатите модули и файлове.
- Съответните синтетични примери или тестове.
- Командите, изпълнени по време на тестването.
- Реално получените резултати.
- Известни ограничения или съображения за съвместимост.

Промените в изходните формати трябва да бъдат придружени от съответните актуализации на документацията.

Промените, засягащи форензичната интерпретация на резултатите, трябва да обясняват своите методологични последици.

## 9. Процес на преглед

Всички приноси подлежат на преглед от поддържащия проекта.

При прегледа могат да бъдат оценявани:

- Коректността на реализацията.
- Проверка на входните и изходните данни.
- Сигурност на файловата система.
- Поверителност и защита на данните.
- Съгласуваност между генерираните JSON, HTML и TXT файлове.
- Съвместимост със съществуващите изходни структури.
- Покритие и възпроизводимост на тестовете.
- Точност на техническите и методологичните твърдения.

Един принос може да бъде върнат за корекции или отхвърлен, ако въвежда неподкрепени функционалности, отслабва мерките за сигурност или представя неправилно обхвата на проекта.

Изпращането на Pull Request не гарантира неговото приемане.

## 10. Стандарти и методологични референции

GigaVeritas използва ISO/IEC 27037:2012 като методологична отправна точка за идентифициране, събиране, придобиване и съхраняване на цифрови доказателства.

Позоваването на този стандарт не означава сертификация, акредитация или пълно съответствие на софтуера с неговите изисквания.

Приносите трябва да запазват това разграничение в кода, документацията и публичните представяния на проекта.

## 11. Лиценз и собственост

Условията за лицензиране и собственост върху хранилището трябва да бъдат потвърдени от носителя на съответните права.

Участниците не трябва да приемат, че проектът е лицензиран за неограничено използване, разпространение или търговска експлоатация.

Не трябва да се добавя или обявява лиценз без разрешение от носителя на правата.

## 12. Заключителна бележка

Целта на GigaVeritas не е просто да генерира хешове или отчети.

Проектът има за цел да предостави структурирана и технически прозрачна рамка за изследване, документиране и консолидиране на предварително придобити цифрови доказателства.

Точността, възпроизводимостта, поверителността и методологичната коректност имат приоритет пред броя на функционалностите или привидната сложност на софтуера.

---

**IceVeritas**  
GigaVeritas Digital Evidence Framework

---

<a id="es"></a>

# Guía de contribución al proyecto (Contributing)

Gracias por tu interés en contribuir al proyecto **GigaVeritas Digital Evidence Framework**.

GigaVeritas es un proyecto desarrollado por **IceVeritas**, destinado al examen técnico, la documentación y la consolidación de evidencias digitales previamente adquiridas.

Este documento establece las normas y condiciones para participar en el desarrollo del proyecto.

> Documento pendiente de aprobación por el mantenedor del proyecto.

## 1. Alcance del proyecto

Todas las contribuciones deben respetar el alcance técnico actual de GigaVeritas.

En su estado actual, el framework se centra en el procesamiento de archivos locales de evidencia y registros previamente adquiridos y documentados como procedentes de Google Maps.

El proyecto no declara actualmente disponer de:

- Adquisición de datos en vivo desde Google Maps.
- Extracción automatizada (scraping) de plataformas en línea.
- Adquisición generalizada desde otras plataformas.
- Verificación independiente de la autoría o procedencia original del contenido digital.
- Preservación certificada de evidencias digitales.

Cualquier ampliación propuesta fuera del alcance actual deberá describirse, implementarse, revisarse y probarse expresamente antes de documentarse como una capacidad disponible.

## 2. Tipos de contribuciones

Se pueden proponer las siguientes mejoras:

- Corrección de errores de programación.
- Mejoras de los módulos existentes.
- Mejoras de seguridad y fiabilidad.
- Correcciones y ampliaciones de la documentación.
- Casos de prueba sintéticos.
- Mejoras en el tratamiento de errores.
- Mejoras de compatibilidad con los sistemas operativos y versiones de Python admitidos.
- Mejoras de consistencia de los informes generados.

Toda nueva funcionalidad deberá acompañarse de una explicación de su finalidad, implementación y limitaciones.

## 3. Requisitos antes de enviar cambios

Antes de enviar una contribución:

1. Explica el problema o la mejora propuesta.
2. Describe el comportamiento observado mediante un ejemplo sintético.
3. Identifica los módulos y archivos afectados.
4. Mantén los cambios limitados a un ámbito funcional claramente definido.
5. Actualiza la documentación correspondiente cuando cambien las funcionalidades, los formatos de salida o los contratos técnicos.
6. Añade pruebas sintéticas para las nuevas funcionalidades y los casos de error pertinentes.
7. Indica los comandos realmente ejecutados y los resultados efectivamente obtenidos.

Es recomendable presentar por separado las refactorizaciones y los cambios funcionales.

Esto facilita la revisión de modificaciones que afectan a la identificación de archivos, el cálculo de SHA-256 y los informes generados.

## 4. Evidencias digitales, privacidad e información sensible

**No envíes archivos reales de evidencia ni información privada de casos concretos.**

Las contribuciones no deben contener:

- Expedientes o materiales de evidencia reales.
- Nombres personales o información identificativa.
- URL privadas o enlaces a registros individuales.
- Identificadores reales de auditoría.
- Capturas de pantalla con información personal o sensible.
- Rutas personales de directorios y archivos.
- Informes generados a partir de investigaciones reales.
- Hashes asociados a casos reales de evidencia.
- Contraseñas, claves API, tokens u otros secretos.

Utiliza registros sintéticos y archivos generados artificialmente para los ejemplos, la documentación y las pruebas.

Antes de enviar cambios, revisa todos los archivos modificados para asegurarte de que no se haya incluido información sensible accidentalmente.

## 5. Requisitos técnicos y metodológicos

Los cambios deben preservar la distinción entre las observaciones técnicas y las conclusiones forenses.

En particular:

- Una huella SHA-256 coincidente demuestra consistencia binaria entre los archivos comparados.
- La coincidencia de hashes no demuestra por sí sola autenticidad, autoría o procedencia.
- Los atributos temporales del sistema de archivos, como `mtime` y `ctime`, son características locales de los archivos.
- Estos atributos no establecen de forma independiente la fecha original de creación o captura.
- Una comprobación técnica satisfactoria no debe presentarse como una certificación.
- Una funcionalidad no debe documentarse como implementada si realmente no está presente en el código.

Los cambios que afecten a los informes JSON, HTML o TXT generados deben preservar la consistencia entre las correspondientes estructuras de salida.

## 6. Calidad del código y compatibilidad

Las contribuciones deben:

- Seguir las convenciones de programación Python existentes.
- Preferir la biblioteca estándar de Python cuando resulte apropiado.
- Evitar dependencias externas innecesarias.
- Preservar el tratamiento previsto de los archivos originales de evidencia en modo de solo lectura.
- Aplicar validaciones adecuadas a las rutas de entrada y salida.
- Gestionar de forma segura los archivos inexistentes y las entradas no válidas.
- Evitar introducir comportamientos no documentados.
- Mantener claramente separadas las responsabilidades de los distintos módulos.

Los cambios relacionados con operaciones del sistema de archivos deben revisarse para detectar riesgos asociados a:

- Acceso fuera de la ruta permitida (*path traversal*).
- Enlaces simbólicos.
- Acceso no previsto a archivos fuera del directorio destinado al expediente.

## 7. Pruebas

Las nuevas funcionalidades deben incluir pruebas sintéticas que cubran, cuando corresponda:

- Archivos de entrada válidos.
- Archivos de entrada inexistentes.
- Documentos JSON malformados.
- Registros inexistentes o incompletos.
- Resultados de comparaciones SHA-256.
- Cambios en archivos durante su lectura.
- Rutas no válidas.
- Extensiones de archivo inesperadas.
- Generación de documentos de salida.
- Consistencia entre los informes JSON, HTML y TXT.

Únicamente pueden presentarse como satisfactorias las pruebas que hayan sido ejecutadas realmente.

La documentación debe distinguir claramente entre:

- Funcionalidad implementada.
- Funcionalidad probada bajo condiciones definidas.
- Funcionalidad planificada o experimental.

Una prueba sintética satisfactoria no demuestra la autenticidad ni la procedencia de evidencias reales.

## 8. Pull Requests

Cada Pull Request debe incluir:

- Una descripción clara del cambio propuesto.
- El motivo de su introducción.
- Los módulos y archivos afectados.
- Los ejemplos sintéticos o pruebas correspondientes.
- Los comandos ejecutados durante las pruebas.
- Los resultados realmente obtenidos.
- Las limitaciones conocidas o consideraciones de compatibilidad.

Los cambios en los formatos de salida deben incluir las correspondientes actualizaciones de documentación.

Los cambios que afecten a la interpretación forense de los resultados deben explicar sus implicaciones metodológicas.

## 9. Proceso de revisión

Todas las contribuciones estarán sujetas a revisión por parte del mantenedor del proyecto.

Durante la revisión podrán evaluarse:

- Corrección de la implementación.
- Validación de las entradas y salidas.
- Seguridad del sistema de archivos.
- Privacidad y protección de datos.
- Consistencia entre los archivos JSON, HTML y TXT generados.
- Compatibilidad con las estructuras de salida existentes.
- Cobertura y reproducibilidad de las pruebas.
- Precisión de las afirmaciones técnicas y metodológicas.

Una contribución podrá devolverse para su corrección o rechazarse si introduce capacidades no respaldadas, debilita los controles de seguridad o representa incorrectamente el alcance del proyecto.

El envío de un Pull Request no garantiza su aceptación.

## 10. Normas y referencias metodológicas

GigaVeritas utiliza ISO/IEC 27037:2012 como referencia metodológica para la identificación, recopilación, adquisición y preservación de evidencias digitales.

La referencia a esta norma no implica certificación, acreditación ni conformidad integral del software con sus requisitos.

Las contribuciones deben preservar esta distinción en el código, la documentación y las comunicaciones públicas del proyecto.

## 11. Licencia y propiedad

Las condiciones de licencia y propiedad del repositorio deben ser confirmadas por el titular de los derechos correspondientes.

Los participantes no deben asumir que el proyecto está autorizado para su uso, redistribución o explotación comercial sin restricciones.

No debe añadirse ni declararse una licencia sin autorización del titular de los derechos.

## 12. Nota final

El objetivo de GigaVeritas no consiste simplemente en generar hashes o informes.

El proyecto pretende proporcionar un framework estructurado y técnicamente transparente para examinar, documentar y consolidar evidencias digitales previamente adquiridas.

La precisión, la reproducibilidad, la privacidad y la honestidad metodológica tienen prioridad sobre el número de funcionalidades o la aparente complejidad del software.

---

**IceVeritas**  
GigaVeritas Digital Evidence Framework

---

<a id="ru"></a>

# Руководство по участию в проекте (Contributing)

Благодарим за интерес к участию в развитии проекта **GigaVeritas Digital Evidence Framework**.

GigaVeritas — это проект, разрабатываемый **IceVeritas** и предназначенный для технического исследования, документирования и консолидации ранее полученных цифровых доказательств.

Настоящий документ устанавливает правила и условия участия в развитии проекта.

> Документ подлежит утверждению сопровождающим проекта.

## 1. Область действия проекта

Все предложения и изменения должны соответствовать текущей технической области применения GigaVeritas.

В настоящее время framework ориентирован на обработку локальных файлов доказательств и предварительно полученных и документированных записей, представленных как происходящие из Google Maps.

На данный момент проект не заявляет о наличии следующих возможностей:

- Получение данных в реальном времени из Google Maps.
- Автоматизированное извлечение данных (scraping) с онлайн-платформ.
- Универсальное получение данных с других платформ.
- Независимая проверка первоначального авторства или происхождения цифрового содержимого.
- Сертифицированное хранение цифровых доказательств.

Любое предлагаемое расширение за пределы текущей области применения должно быть явно описано, реализовано, проверено и протестировано до того, как оно будет представлено как доступная функциональность.

## 2. Виды вклада

Могут предлагаться следующие виды улучшений:

- Исправление программных ошибок.
- Улучшение существующих модулей.
- Повышение безопасности и надёжности.
- Исправление и дополнение документации.
- Синтетические тестовые сценарии.
- Улучшение обработки ошибок.
- Повышение совместимости с поддерживаемыми операционными системами и версиями Python.
- Улучшение согласованности формируемых отчётов.

Каждая новая функциональность должна сопровождаться объяснением её назначения, реализации и ограничений.

## 3. Требования перед отправкой изменений

Перед отправкой вклада необходимо:

1. Описать проблему или предлагаемое улучшение.
2. Представить наблюдаемое поведение на синтетическом примере.
3. Указать затронутые модули и файлы.
4. Ограничить изменения чётко определённой функциональной областью.
5. Обновить соответствующую документацию при изменении функциональности, форматов выходных данных или технических соглашений.
6. Добавить синтетические тесты для новых функций и соответствующих ошибочных сценариев.
7. Указать фактически выполненные команды и реально полученные результаты.

Рекомендуется отправлять рефакторинг и функциональные изменения отдельно.

Это упрощает проверку изменений, затрагивающих идентификацию файлов, вычисление SHA-256 и формируемые отчёты.

## 4. Цифровые доказательства, конфиденциальность и чувствительная информация

**Не отправляйте реальные файлы доказательств или личную информацию из конкретных дел.**

Вклады не должны содержать:

- Реальные материалы доказательств или дела.
- Личные имена или идентифицирующую информацию.
- Закрытые URL-адреса или ссылки на отдельные записи.
- Реальные идентификаторы аудита.
- Снимки экрана с личной или чувствительной информацией.
- Личные пути к каталогам и файлам.
- Отчёты, сформированные в ходе реальных расследований.
- Хеши, связанные с реальными делами и доказательствами.
- Пароли, API-ключи, токены или другие секретные данные.

Для примеров, документации и тестирования используйте синтетические записи и искусственно созданные файлы.

Перед отправкой изменений проверьте все изменённые файлы, чтобы убедиться, что в них случайно не включена чувствительная информация.

## 5. Технические и методологические требования

Изменения должны сохранять разграничение между техническими наблюдениями и криминалистическими выводами.

В частности:

- Совпадающий SHA-256-хеш подтверждает бинарную согласованность сравниваемых файлов.
- Совпадение хешей само по себе не доказывает подлинность, авторство или происхождение.
- Временные атрибуты файловой системы, такие как `mtime` и `ctime`, являются локальными характеристиками файлов.
- Эти атрибуты самостоятельно не устанавливают первоначальную дату создания или съёмки.
- Успешная техническая проверка не должна представляться как сертификация.
- Функциональность не должна документироваться как реализованная, если её фактически нет в коде.

Изменения, затрагивающие формируемые JSON-, HTML- или TXT-отчёты, должны сохранять согласованность соответствующих выходных структур.

## 6. Качество кода и совместимость

Предлагаемый код должен:

- Следовать существующим соглашениям программирования на Python.
- По возможности использовать стандартную библиотеку Python.
- Избегать ненужных внешних зависимостей.
- Сохранять предусмотренную обработку исходных файлов доказательств в режиме только для чтения.
- Обеспечивать надлежащую проверку входных и выходных путей.
- Безопасно обрабатывать отсутствующие файлы и некорректные входные данные.
- Не вводить недокументированное поведение.
- Сохранять чёткое разделение обязанностей между отдельными модулями.

Изменения, затрагивающие операции с файловой системой, должны проверяться на наличие рисков, связанных с:

- Выходом за пределы разрешённого пути (*path traversal*).
- Символическими ссылками.
- Непредусмотренным доступом к файлам за пределами предназначенного каталога дела.

## 7. Тестирование

Новая функциональность должна сопровождаться синтетическими тестами, охватывающими, где это применимо:

- Корректные входные файлы.
- Отсутствующие входные файлы.
- Некорректные JSON-документы.
- Отсутствующие или неполные записи.
- Результаты сравнения SHA-256.
- Изменения файлов во время чтения.
- Некорректные пути.
- Неожиданные расширения файлов.
- Формирование выходных документов.
- Согласованность JSON-, HTML- и TXT-отчётов.

В качестве успешных могут указываться только тесты, которые действительно были выполнены.

Документация должна чётко разграничивать:

- Реализованную функциональность.
- Функциональность, протестированную в определённых условиях.
- Запланированную или экспериментальную функциональность.

Успешный синтетический тест не доказывает подлинность или происхождение реальных доказательств.

## 8. Pull Requests

Каждый Pull Request должен содержать:

- Чёткое описание предлагаемого изменения.
- Причину его внесения.
- Затронутые модули и файлы.
- Соответствующие синтетические примеры или тесты.
- Команды, выполненные во время тестирования.
- Фактически полученные результаты.
- Известные ограничения или особенности совместимости.

Изменения форматов выходных данных должны сопровождаться соответствующим обновлением документации.

Изменения, затрагивающие криминалистическую интерпретацию результатов, должны объяснять свои методологические последствия.

## 9. Процесс проверки

Все вклады подлежат проверке сопровождающим проекта.

В процессе проверки могут оцениваться:

- Корректность реализации.
- Проверка входных и выходных данных.
- Безопасность файловой системы.
- Конфиденциальность и защита данных.
- Согласованность формируемых JSON-, HTML- и TXT-файлов.
- Совместимость с существующими структурами выходных данных.
- Полнота и воспроизводимость тестов.
- Точность технических и методологических утверждений.

Вклад может быть возвращён на доработку или отклонён, если он вводит неподтверждённые возможности, ослабляет меры безопасности или неправильно описывает область применения проекта.

Отправка Pull Request не гарантирует его принятие.

## 10. Стандарты и методологические ссылки

GigaVeritas использует ISO/IEC 27037:2012 в качестве методологического ориентира для идентификации, сбора, получения и сохранения цифровых доказательств.

Ссылка на данный стандарт не означает сертификацию, аккредитацию или полное соответствие программного обеспечения его требованиям.

Вклады должны сохранять это разграничение в коде, документации и публичных материалах проекта.

## 11. Лицензия и права собственности

Условия лицензирования и права собственности на репозиторий должны быть подтверждены соответствующим правообладателем.

Участники не должны предполагать, что проект разрешён для неограниченного использования, распространения или коммерческой эксплуатации.

Добавление или объявление лицензии без разрешения правообладателя не допускается.

## 12. Заключительное замечание

Цель GigaVeritas заключается не просто в генерации хешей или отчётов.

Проект стремится предоставить структурированный и технически прозрачный framework для исследования, документирования и консолидации ранее полученных цифровых доказательств.

Точность, воспроизводимость, конфиденциальность и методологическая добросовестность имеют приоритет над количеством функций или кажущейся сложностью программного обеспечения.

---

**IceVeritas**  
GigaVeritas Digital Evidence Framework