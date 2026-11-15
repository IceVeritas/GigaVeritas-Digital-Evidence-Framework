<div align="right">

<a href="../README.md#bg"><img src="https://img.shields.io/badge/BG-Български-lightgrey?style=flat-square" alt="BG"></a>
<a href="#es"><img src="https://img.shields.io/badge/ES-Español-142b45?style=flat-square" alt="ES"></a>
<a href="../README.md#ru"><img src="https://img.shields.io/badge/RU-Русский-lightgrey?style=flat-square" alt="RU"></a>

</div>

---

<a id="es"></a>

# Documentación Técnica — GigaVeritas Digital Evidence Framework

Esta carpeta centraliza las especificaciones técnicas, contratos de esquemas, requisitos operativos y directrices de seguridad del proyecto **GigaVeritas-Digital-Evidence-Framework** (**IceVeritas**).

> **Nota de estado:** La documentación de este directorio describe el comportamiento implementado en los cuatro módulos de procesamiento local (`forensic_core.py`, `solo_lectura.py`, `time_stamp.py` y `manifest.py`) y distingue explícitamente las funciones actuales frente a las propuestas en desarrollo[cite: 12, 13].

## Índice de documentos

| Documento | Contenido y alcance |
| :--- | :--- |
| **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** | Flujo de datos entre módulos, responsabilidades técnicas, contratos de esquemas JSON (`iceveritas.solo_lectura.report.v1`, `iceveritas.manifest/2.0`), acoplamiento y orden de ejecución[cite: 12]. |
| **[`REQUISITOS.md`](./REQUISITOS.md)** | Requisitos de entorno Python, estructura esperada del HTML índice (`<article class="card">`), organización de carpetas por ID, compatibilidad actual (`.png`, `.mkv`, `.txt`), controles de ejecución y criterios de demostración[cite: 13]. |
| **[`SECURITY.md`](./SECURITY.md)** | Manejo seguro de expedientes, reglas de privacidad y anonimización antes de publicar, controles frente a enlaces simbólicos/traversal y riesgos técnicos pendientes de prueba[cite: 14]. |

---

← [Volver al `README.md` principal](../README.md#es)