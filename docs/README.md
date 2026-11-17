<div align="right">

<a href="#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

# Technical Documentation — GigaVeritas Digital Evidence Framework

This folder centralizes the technical specifications, schema contracts, operational requirements, and security guidelines of the **GigaVeritas-Digital-Evidence-Framework** (**IceVeritas**) project.

> **Status note:** The documentation in this directory describes the behavior implemented across the four local processing modules (`forensic_core.py`, `solo_lectura.py`, `time_stamp.py`, and `manifest.py`) and explicitly distinguishes current features from proposals under development.

## Document Index

| Document | Content and Scope |
| :--- | :--- |
| **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Data flow between modules, technical responsibilities, JSON schema contracts (`iceveritas.solo_lectura.report.v1`, `iceveritas.manifest/2.0`), coupling, and execution order. |
| **[`REQUISITOS.md`](./REQUISITOS.md)** | Python environment requirements, expected index HTML structure (`<article class="card">`), folder organization by ID, current compatibility (`.png`, `.mkv`, `.txt`), execution controls, and demonstration criteria. |
| **[`SECURITY.md`](./SECURITY.md)** | Secure handling of case files, privacy and anonymization rules prior to publication, controls against symbolic links/traversal, and technical risks pending testing. |
| **[`time_stamp.md`](./time_stamp.md)** | Descriptive evidence synchronization (`time_stamp.py`), recursive discovery across 27 extensions, SHA-256 computation with read-time control (`os.fstat()`), UTC file system timestamp recording, derived HTML generation (`*_FIXED.html`), and JSON reporting. |
| **[`manifest.md`](./manifest.md)** | Consolidation and documentary reporting (`manifest.py`), cross-correlation of JSON reports from Solo Lectura and Time Stamp, SHA-256 comparison and integrity status evaluation, complementary HTML index extraction, and generation of the `iceveritas.manifest/2.0` manifest alongside HTML and individual TXT reports. |

---

← [Back to main `README.md`](../README.md)

---

<a id="es"></a>

# Documentación Técnica — GigaVeritas Digital Evidence Framework

Esta carpeta centraliza las especificaciones técnicas, contratos de esquemas, requisitos operativos y directrices de seguridad del proyecto **GigaVeritas-Digital-Evidence-Framework** (**IceVeritas**).

> **Nota de estado:** La documentación de este directorio describe el comportamiento implementado en los cuatro módulos de procesamiento local (`forensic_core.py`, `solo_lectura.py`, `time_stamp.py` y `manifest.py`) y distingue explícitamente las funciones actuales frente a las propuestas en desarrollo.

## Índice de documentos

| Documento | Contenido y alcance |
| :--- | :--- |
| **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Flujo de datos entre módulos, responsabilidades técnicas, contratos de esquemas JSON (`iceveritas.solo_lectura.report.v1`, `iceveritas.manifest/2.0`), acoplamiento y orden de ejecución. |
| **[`REQUISITOS.md`](./REQUISITOS.md)** | Requisitos de entorno Python, estructura esperada del HTML índice (`<article class="card">`), organización de carpetas por ID, compatibilidad actual (`.png`, `.mkv`, `.txt`), controles de ejecución y criterios de demostración. |
| **[`SECURITY.md`](./SECURITY.md)** | Manejo seguro de expedientes, reglas de privacidad y anonimización antes de publicar, controles frente a enlaces simbólicos/traversal y riesgos técnicos pendientes de prueba. |
| **[`time_stamp.md`](./time_stamp.md)** | Sincronización descriptiva de evidencias (`time_stamp.py`), descubrimiento recursivo en 27 extensiones, cálculo SHA-256 con control durante la lectura (`os.fstat()`), registro de atributos temporales UTC, generación de HTML derivado (`*_FIXED.html`) e informe JSON. |
| **[`manifest.md`](./manifest.md)** | Consolidación y documentación de evidencias (`manifest.py`), correlación entre informes JSON de Solo Lectura y Time Stamp, comparación SHA-256 y evaluación de estados, extracción documental complementaria del índice HTML y generación del manifiesto `iceveritas.manifest/2.0` junto con informes HTML y TXT individuales. |

---

← [Volver al `README.md` principal](../README.md#es)

---

<a id="bg"></a>

# Техническа документация — GigaVeritas Digital Evidence Framework

Тази папка централизира техническите спецификации, договорите за схеми, оперативните изисквания и насоките за сигурност на проекта **GigaVeritas-Digital-Evidence-Framework** (**IceVeritas**).

> **Бележка за статуса:** Документацията в тази директория описва поведението, внедрено в четирите модула за локална обработка (`forensic_core.py`, `solo_lectura.py`, `time_stamp.py` и `manifest.py`), и изрично разграничава текущите функционалности от предложенията в процес на разработка.

## Индекс на документите

| Документ | Съдържание и обхват |
| :--- | :--- |
| **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Поток от данни между модулите, технически отговорности, договори за JSON схеми (`iceveritas.solo_lectura.report.v1`, `iceveritas.manifest/2.0`), свързаност и ред на изпълнение. |
| **[`REQUISITOS.md`](./REQUISITOS.md)** | Изисквания към Python средата, очаквана структура на индексния HTML (`<article class="card">`), организация на папките по ID, текуща съвместимост (`.png`, `.mkv`, `.txt`), контроли при изпълнение и критерии за демонстрация. |
| **[`SECURITY.md`](./SECURITY.md)** | Сигурна работа с досиета, правила за поверителност и анонимизиране преди публикуване, защити срещу символни връзки/traversal и технически рискове, подлежащи на тестване. |
| **[`time_stamp.md`](./time_stamp.md)** | Описателна синхронизация на доказателства (`time_stamp.py`), рекурсивно откриване в 27 разширения, изчисляване на SHA-256 с контрол по време на четене (`os.fstat()`), регистриране на времеви атрибути в UTC, генериране на производен HTML (`*_FIXED.html`) и JSON отчет. |
| **[`manifest.md`](./manifest.md)** | Консолидиране и документиране на доказателства (`manifest.py`), корелация между JSON отчетите на Solo Lectura и Time Stamp, сравнение на SHA-256 и оценка на състоянията, допълнително документално извличане от HTML индекса и генериране на манифест `iceveritas.manifest/2.0` заедно с HTML и индивидуални TXT отчети. |

---

← [Обратно към основния `README.md`](../README.md#bg)

---

<a id="ru"></a>

# Техническая документация — GigaVeritas Digital Evidence Framework

Эта папка централизует технические спецификации, контракты схем, эксплуатационные требования и рекомендации по безопасности проекта **GigaVeritas-Digital-Evidence-Framework** (**IceVeritas**).

> **Примечание о статусе:** Документация в этом каталоге описывает поведение, реализованное в четырёх модулях локальной обработки (`forensic_core.py`, `solo_lectura.py`, `time_stamp.py` и `manifest.py`), и чётко разграничивает текущие функции и предложения, находящиеся в разработке.

## Указатель документов

| Документ | Содержание и область охвата |
| :--- | :--- |
| **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Поток данных между модулями, технические задачи, контракты JSON-схем (`iceveritas.solo_lectura.report.v1`, `iceveritas.manifest/2.0`), связанность компонентов и порядок выполнения. |
| **[`REQUISITOS.md`](./REQUISITOS.md)** | Требования к среде Python, ожидаемая структура индексного HTML (`<article class="card">`), организация папок по ID, текущая совместимость (`.png`, `.mkv`, `.txt`), проверки при выполнении и критерии демонстрации. |
| **[`SECURITY.md`](./SECURITY.md)** | Безопасная работа с делами, правила конфиденциальности и анонимизации перед публикацией, защита от символических ссылок/traversal и технические риски, требующие тестирования. |
| **[`time_stamp.md`](./time_stamp.md)** | Описательная синхронизация доказательств (`time_stamp.py`), рекурсивный поиск по 27 расширениям, вычисление SHA-256 с контролем во время чтения (`os.fstat()`), регистрация временных атрибутов в UTC, создание производного HTML (`*_FIXED.html`) и JSON-отчёта. |
| **[`manifest.md`](./manifest.md)** | Консолидация и документирование доказательств (`manifest.py`), сопоставление JSON-отчётов Solo Lectura и Time Stamp, сравнение SHA-256 и оценка статусов, дополнительное извлечение документальных данных из HTML-индекса и создание манифеста `iceveritas.manifest/2.0` вместе с HTML- и отдельными TXT-отчётами. |

---

← [Вернуться к основному `README.md`](../README.md#ru)