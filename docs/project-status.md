# Estado del proyecto

**Actualizado:** 2026-09-08
**Fase actual:** Fase 0 — preservación y arqueología, **cerrada**: evidencia local agotada para todas sus preguntas prioritarias. Comprensión técnica inicial de Fase 1 también completada. Fase 2 — baseline reproducible, **en preparación**: dataset/split congelados (DEC-003), scaffolding de `ml/src`/`ml/tests` implementado, y remoto DVC en GCS creado y probado (`gs://hematovision-ml-dvc`, proyecto `hematovision-ml`) sin subir todavía los datasets reales; entrenamiento/EXP-REPRO siguen sin autorizar. Ver [Roadmap](roadmap.md) para el detalle por ítem.

## Dónde estamos

- **Último hito:** remoto DVC real conectado a Google Cloud Storage (2026-09-08) — proyecto GCP `hematovision-ml`, bucket `gs://hematovision-ml-dvc` (`southamerica-west1`, Standard, sin acceso público), probado end-to-end con un archivo descartable (push/pull con hash idéntico). Ver [DVC y remoto GCS](dvc-plan.md).
- **Último trabajo:** conexión del remoto GCS — sin mover ni subir los datasets originales (~24-25 GiB), sin claves JSON, autenticación vía Application Default Credentials con la cuenta personal de Miguel.
- **Trabajo activo:** Fase 2 no está completa: subir los datasets reales, entrenamiento/EXP-REPRO siguen sin autorizar. Las preguntas históricas sin resolver permanecen documentadas como PENDIENTE-evidencia-agotada y solo se resolverían con una fuente externa a este repositorio y este dataset.
- **Hallazgo principal:** el pipeline histórico aumentó imágenes y las mezcló antes de dividir por archivo. El riesgo de leakage del pipeline es **CONFIRMADO**; leakage efectivo entre pares concretos de splits es **PROBABLE**, aún no demostrado par a par.
- **Decisión vigente:** el notebook y modelo históricos se preservan como baseline/evidencia; las mejoras serán una evolución nueva y reproducible. Véase [DEC-001](decisions.md#dec-001-preservar-el-baseline-histórico).
- **Hallazgo nuevo:** el notebook documenta desde `Labelled_mix` hasta evaluación, pero no la integración de fuentes, los modelos previos ni la exportación TensorFlow.js. Su metadata dice `tf-cpu`, aunque no prueba el dispositivo real de entrenamiento.
- **Procedencia resuelta:** `Labelled` deriva del dataset Bodzas et al. (2023) y `Labelled_2` de PBC/Acevedo et al. (2020); `ig` es immature granulocytes y fue excluida de la mezcla. Las copias locales solo permiten split por archivo, no por paciente/frotis.

## Hitos completados

- Auditoría inicial del equipo histórico HP OMEN y de la metadata del notebook,
  sin atribuir todavía el uso efectivo de GPU.
- Reconstrucción técnica del notebook y del pipeline histórico.
- Identificación de los datasets fuente y documentación de su procedencia.
- Documentación del riesgo estructural de leakage.
- Reconstrucción de arquitectura y relación entre `modelo_1.h5`, `modelo_1_balanced.h5` y `mejor_modelo.h5` (ver HIST-MODELS-004).
- Búsqueda exhaustiva y cierre de las preguntas de entorno (TensorFlow/CUDA/GPU), logs de entrenamiento y exclusión de `ig` (ver HIST-ENV-005).

No hay modernización ni entrenamiento nuevo en curso.

## Preguntas abiertas prioritarias

Todas las preguntas locales de Fase 0 (manifiestos de paciente/lámina/frotis, motivo de exclusión de `ig`, entornos TensorFlow/CUDA/GPU, procedencia exacta de los modelos anteriores) están investigadas hasta agotar la evidencia disponible en este repositorio y estos datasets; permanecen como PENDIENTE-evidencia-agotada, no como preguntas sin investigar. Lista completa: [Investigaciones](research.md#preguntas-abiertas).

## Siguiente paso recomendado

La arqueología local está cerrada. Los próximos pasos requieren una decisión del usuario, no son autónomos:

1. Si se quiere seguir la pista de manifiestos externos (releases originales de Bodzas/PBC con IDs de paciente/sujeto), es una búsqueda fuera de este repositorio y estos discos — decidir si vale la pena antes de invertir tiempo.
2. Si se autoriza resolver el bloqueo de "dubious ownership" en `D:\Proyectos\Proyecto Hematología` (cambiar configuración Git), podría recuperarse historial adicional — no se hizo sin autorización explícita.
3. Fase 2 (baseline reproducible) ya está en marcha: dataset y split congelados (DEC-003), scaffolding de `ml/src`/`ml/tests` implementado, y remoto DVC en GCS creado y probado (sin subir los datasets reales todavía) -- ver [Plan de Fase 2](phase2-plan.md) y [DVC y remoto GCS](dvc-plan.md). No se inició ningún entrenamiento.
