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

## DEC-003 -- Congelamiento del split de Fase 2 (train/val/test) sin DVC

**Estado:** ACCEPTED
**Fecha:** 2026-09-07

**Contexto:** el manifiesto de originales entregó una propuesta definitiva de split (80/10/10, semilla 20260907, cuarentena DEC-002) verificada independientemente dos veces, con identificador SHA-256 010a820d46cb2bf43c4d922405da61003087215dc8315ceb284d08624acf31e1 sobre manifest_v2.csv. Miguel aprobó explícitamente congelarla. DVC no está inicializado todavía.

**Decisión:** congelar el split registrando su identificador SHA-256 y metadatos (conteos, semilla, cuarentena, política de uso del test) en un archivo pequeño versionado en Git (ml/split_freeze.json), en vez de esperar a DVC. ml/scripts/build_split.py y ml/scripts/verify_split_freeze.py leen ese archivo y abortan si una asignación recalculada no coincide exactamente con el hash congelado, en vez de sobrescribir manifest_v2.csv en silencio. El manifiesto grande sigue fuera de Git.

**Alternativas consideradas:** esperar a inicializar DVC antes de congelar nada (bloquearía Fase 2 sin justificación real, ya que DVC es una decisión de infraestructura/costo separada); congelar solo de forma informal en un documento sin ningún mecanismo ejecutable que lo verifique.

**Razones:** un identificador de hash commiteado más un guard ejecutable da inmutabilidad práctica y verificable sin requerir infraestructura remota todavía no autorizada.

**Consecuencias:** el test queda disponible para EXP-REPRO cuando se autorice el entrenamiento, bajo la política de uso único y de no calibrar hiperparámetros/umbrales sobre él. Congelar el split no autoriza DVC, entrenamiento, augmentation ni cambios al modelo publicado -- cada uno sigue requiriendo su propia autorización explícita. Si se resuelve la etiqueta del grupo en cuarentena, se generaría una manifest_v3.csv y una nueva decisión, no se modificaría este freeze retroactivamente.
