# Decisiones

Registro liviano de decisiones no triviales. Estados: `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, `RETIRED`. Al añadir una decisión, use un ID estable `DEC-NNN` y registre contexto, decisión, alternativas, razones, consecuencias, fecha y estado.

## DEC-001 — Preservar el baseline histórico

**Estado:** ACCEPTED
**Fecha:** 2026-09-05

**Contexto:** el notebook y modelo de 2024 contienen resultados históricos, pero el pipeline reconstruido tiene riesgo confirmado de leakage y no existe validación clínica.

**Decisión:** preservar modelo y notebook históricos como baseline y evidencia; no corregirlos silenciosamente. Las mejoras futuras se implementarán como una nueva evolución reproducible y se compararán contra el baseline cuando corresponda.

**Alternativas consideradas:** modificar el notebook/modelo existente para corregir el pipeline; reemplazar el baseline sin conservar su contexto.

**Razones:** protege la trazabilidad de lo ocurrido y evita que una corrección actual se confunda con evidencia de 2024.

**Consecuencias:** los defectos históricos se documentan explícitamente; una evaluación confiable exige un dataset, split y ejecución nuevos. Véanse [Historia](project-history.md) y [Roadmap](roadmap.md).

## DEC-002 — Cuarentena del grupo de hash conflictivo en lugar de elegir etiqueta

**Estado:** ACCEPTED
**Fecha:** 2026-09-07

**Contexto:** al construir el manifiesto de originales para el baseline reproducible de Fase 2, se encontró que dos archivos del dataset público PBC (`Labelled_2/eosinophil/EO_225902.jpg` y `Labelled_2/neutrophil/BNE_191112.jpg`) son bytes idénticos (mismo SHA-256) pero están archivados bajo dos clases distintas (Eosinófilos y Neutrófilos). No existe evidencia local que permita determinar cuál etiqueta es correcta. Detalle técnico completo en [Manifiesto de originales §2.1](dataset-manifest.md#21-registro-de-cuarentena).

**Decisión:** poner ambos registros en cuarentena — excluidos de train/validation/test — en vez de elegir una etiqueta automáticamente o descartar uno de los dos archivos. Los originales no se eliminan, mueven ni modifican.

**Alternativas consideradas:** elegir una de las dos etiquetas por heurística (p. ej. la carpeta con más muestras); descartar aleatoriamente uno de los dos archivos; ignorar el conflicto y dejar que un archivo "gane" silenciosamente según el orden del script.

**Razones:** ninguna de las alternativas tiene respaldo técnico — inventar una resolución para un conflicto de anotación de un dataset público de terceros no es una decisión de ingeniería, y silenciarlo contradice el principio de este proyecto de no ocultar discrepancias.

**Consecuencias:** el split pierde 2 imágenes (de 30.224) hasta que se resuelva la etiqueta; el manifiesto documenta la cuarentena como reversible si en el futuro aparece evidencia (p. ej. de los autores de PBC) que permita resolverla. No bloquea el resto del split ni el resto de Fase 2.
