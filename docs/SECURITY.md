# SECURITY.md
# Сигурност и поверителност / Seguridad y privacidad / Безопасность и конфиденциальность

<div align="right">
<a href="#bg">BG</a> | <a href="#es">ES</a> | <a href="#ru">RU</a>
</div>

---

<a id="bg"></a>
# Български — Сигурност и поверителност

> **Статус:** Документът определя препоръчителни практики за сигурност на хранилището. Той не представлява сертификат или независима оценка на сигурността.

## Обхват и ограничения

Софтуерът на този етап обработва локално HTML файлове и файлове, свързани с вече придобити записи от Google Maps. Той не извършва придобиване на данни от Google Maps и не определя автентичността или законността на обработваните материали.

Хешът служи за сравняване на байтове. Той не представлява цифров подпис, надежден времеви печат или доказателство за произход.

## Работа с доказателствени материали

- HTML файловете, екранните снимки, видеоклиповете, текстовете на отзиви, имената, връзките, идентификаторите на досиета и отговорите на трети страни трябва да се третират като чувствителна информация.
- Оригиналите трябва да се съхраняват в хранилище с контролиран достъп. Инструментите следва да се изпълняват върху проверени копия, като входните и изходните данни се съхраняват отделно.
- В публични issues, pull requests, екранни снимки, примери или публичната Git история не трябва да се включват реални досиета, потребителски пътища, логове, хешове на случаи, реални идентификатори или производни доклади.
- Логовете и генерираните резултати трябва да бъдат защитени със същите правила за достъп като самото досие. Пътищата и времевите атрибути могат да разкрият информация дори когато текстът на отзива е премахнат.
- Примерите за публично разпространение трябва да бъдат създавани изцяло със синтетични данни. Преди публикуване трябва да се проверят HTML съдържанието, връзките, метаданните на изображенията, имената на файловете, хешовете и генерираните резултати.

## Публикуване

Наличните материали, разгледани при проверката, съдържат идентифициращи данни и конкретна информация за местоположение.

Съществуващите HTML/JSON/TXT/HTML файлове на манифеста, логовете, екранните снимки и `index_input.html` трябва да останат частни или да бъдат подложени на стриктна анонимизация преди публикуване.

Визуалното скриване на имена не премахва данните, вградени в HTML, атрибутите, връзките или метаданните.

Генераторът на манифести съдържа данни за контакт в кода и в генерираните резултати. Преди публично разпространение те трябва да бъдат премахнати или заменени с незадължителна конфигурация, описана в документацията.

Не трябва да се публикуват реални контактни данни или реални доказателствени досиета с цел тестване на генератора.

## Докладване на уязвимости

Докато не бъде потвърден канал за връзка със сигурността, не трябва да се посочва измислен имейл адрес.

Частен канал за докладване и срокове за реакция трябва да бъдат добавени само след като поддържащият проекта ги е определил.

Лицата, които докладват проблеми, трябва да бъдат помолени да не прикачват лични доказателствени досиета и да използват синтетичен пример.

## Технически рискове, изискващи изпитване

- Символни връзки и reparse points, traversal атаки, твърди връзки, състезателни условия между проверката и прочитането, както и ограничения за размер и дълбочина.
- Колизии или дублиране на идентификатори и имена, злонамерени имена, непортируеми пътища, неправилно форматиран HTML и екранирано HTML съдържание.
- Файлове, които се променят по време на прочитане, отказани права за достъп и изходни директории, разположени във входните директории.
- Безопасност на генерирания HTML спрямо недоверено съдържание, контрол на външните връзки и зареждането на отдалечени ресурси.
- Поведение при JSON с неочаквана структура, липсващи идентификатори, липсващи хешове и несъответствия между резултатите.

Видимите защитни механизми в кода не заменят специализираните негативни тестове или независимия преглед на сигурността.

---

<a id="es"></a>
# Español — Seguridad y privacidad

> **Estado:** Este documento define prácticas recomendadas para la seguridad del repositorio. No constituye una certificación ni una auditoría independiente de seguridad.

## Alcance y limitaciones

El software de esta etapa procesa localmente archivos HTML y ficheros asociados a registros de Google Maps previamente adquiridos. No realiza adquisición desde Google Maps ni determina la autenticidad o legalidad del material procesado.

Un hash sirve para comparar bytes. No es una firma digital, un sello de tiempo de confianza ni una prueba de procedencia.

## Manejo de expedientes

- Tratar HTML, capturas, vídeos, texto de reseñas, nombres, enlaces, identificadores de expediente y respuestas de terceros como información sensible.
- Mantener los originales en almacenamiento de acceso controlado. Ejecutar las herramientas sobre copias verificadas y separar los datos de entrada de los resultados.
- No incluir expedientes reales, rutas de usuario, logs, hashes de casos, identificadores reales ni informes derivados en issues, pull requests, capturas, ejemplos o en el historial público de Git.
- Mantener los logs y los resultados generados bajo las mismas reglas de acceso que el expediente. Las rutas y los atributos temporales pueden revelar información incluso cuando se elimina el texto de una reseña.
- Crear los ejemplos públicos desde cero utilizando datos sintéticos. Antes de publicarlos, revisar el HTML, los enlaces, los metadatos de las imágenes, los nombres de archivo, los hashes y los resultados generados.

## Publicación

El material disponible durante la revisión contiene datos identificables y localización concreta.

Los archivos HTML/JSON/TXT/HTML del manifiesto existentes, los logs, las capturas y `index_input.html` deben permanecer privados o someterse a una anonimización rigurosa antes de cualquier publicación.

Ocultar visualmente los nombres no elimina los datos incrustados en el HTML, los atributos, los enlaces o los metadatos.

El generador de manifiestos incluye datos de contacto dentro del código y en los resultados generados. Antes de publicar, deben retirarse o sustituirse por una configuración opcional documentada.

No publicar datos reales de contacto ni expedientes reales para probar el generador.

## Divulgación de vulnerabilidades

Hasta que exista un canal de contacto de seguridad confirmado, no debe inventarse ni publicarse una dirección de correo electrónico.

Un canal privado de comunicación y unos plazos de respuesta solo deben añadirse cuando el mantenedor los haya acordado.

Se debe solicitar a quien informe de un problema que evite adjuntar expedientes personales y utilice un caso sintético.

## Riesgos técnicos que requieren pruebas

- Rutas simbólicas y reparse points, ataques de traversal, enlaces duros, condiciones de carrera entre la comprobación y la lectura, y límites de tamaño y profundidad.
- Colisiones o duplicación de identificadores y nombres, nombres maliciosos, rutas no portables, HTML malformado y contenido HTML escapado.
- Archivos que cambian durante la lectura, permisos denegados y directorios de salida ubicados dentro de los directorios de entrada.
- Seguridad del HTML generado frente a contenido no confiable, control de enlaces externos y carga de recursos remotos.
- Comportamiento ante JSON con esquemas inesperados, identificadores ausentes, hashes ausentes y discrepancias entre resultados.

Las defensas visibles en el código no sustituyen las pruebas negativas específicas ni una revisión de seguridad independiente.

---

<a id="ru"></a>
# Русский — Безопасность и конфиденциальность

> **Статус:** Документ определяет рекомендуемые практики обеспечения безопасности репозитория. Он не является сертификатом или независимым аудитом безопасности.

## Область применения и ограничения

Программное обеспечение на данном этапе локально обрабатывает HTML-файлы и файлы, связанные с ранее полученными записями Google Maps. Оно не осуществляет сбор данных непосредственно из Google Maps и не определяет подлинность или законность обрабатываемых материалов.

Хеш используется для сравнения байтов. Он не является цифровой подписью, доверенной меткой времени или доказательством происхождения.

## Обращение с доказательственными материалами

- HTML-файлы, снимки экрана, видео, тексты отзывов, имена, ссылки, идентификаторы дел и ответы третьих лиц следует рассматривать как конфиденциальную информацию.
- Оригиналы необходимо хранить в хранилище с контролируемым доступом. Инструменты следует запускать на проверенных копиях, отделяя входные данные от результатов обработки.
- Не включать реальные дела, пользовательские пути, журналы, хеши дел, реальные идентификаторы и производные отчёты в публичные issues, pull requests, снимки экрана, примеры или публичную историю Git.
- Журналы и сгенерированные результаты должны защищаться теми же правилами доступа, что и само дело. Пути и временные атрибуты могут раскрывать информацию даже после удаления текста отзыва.
- Публичные примеры необходимо создавать с нуля, используя синтетические данные. Перед публикацией следует проверять HTML, ссылки, метаданные изображений, имена файлов, хеши и результаты обработки.

## Публикация

Материалы, доступные на этапе проверки, содержат идентифицирующие данные и конкретную информацию о местоположении.

Существующие файлы HTML/JSON/TXT/HTML манифеста, журналы, снимки экрана и `index_input.html` должны оставаться закрытыми либо проходить строгую анонимизацию перед публикацией.

Визуальное скрытие имён не удаляет данные, встроенные в HTML, атрибуты, ссылки или метаданные.

Генератор манифестов содержит контактные данные в исходном коде и в создаваемых результатах. Перед публикацией их необходимо удалить либо заменить документированной необязательной конфигурацией.

Не следует публиковать реальные контактные данные или реальные доказательственные дела для тестирования генератора.

## Раскрытие уязвимостей

До подтверждения канала связи по вопросам безопасности не следует указывать вымышленный адрес электронной почты.

Частный канал для сообщений и сроки реагирования следует добавлять только после согласования с сопровождающим проекта.

Лицам, сообщающим о проблемах, следует рекомендовать не прикреплять персональные доказательственные материалы и использовать синтетические примеры.

## Технические риски, требующие тестирования

- Символические ссылки и reparse points, атаки обхода путей (traversal), жёсткие ссылки, гонки между проверкой и чтением, а также ограничения размера и глубины.
- Коллизии или дублирование идентификаторов и имён, вредоносные имена, непереносимые пути, некорректный HTML и экранированное HTML-содержимое.
- Файлы, изменяющиеся во время чтения, отказ в доступе и выходные каталоги, расположенные внутри входных каталогов.
- Безопасность генерируемого HTML при обработке недоверенного содержимого, контроль внешних ссылок и загрузки удалённых ресурсов.
- Поведение при обработке JSON с неожиданной структурой, отсутствующими идентификаторами, отсутствующими хешами и расхождениями между результатами.

Защитные механизмы, видимые в исходном коде, не заменяют специальные негативные тесты или независимую проверку безопасности.