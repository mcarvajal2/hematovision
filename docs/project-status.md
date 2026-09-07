# Estado del proyecto

**Actualizado:** 2026-09-07
**Fase actual:** Fase 0 — preservación y arqueología, **cerrada**: evidencia local agotada para todas sus preguntas prioritarias. Comprensión técnica inicial de Fase 1 también completada. Ver [Roadmap](roadmap.md) para el detalle por ítem.

## Dónde estamos

- **Último hito:** el repositorio moderno fue inicializado/publicado en septiembre de 2026, conservando el notebook histórico y la aplicación web con el modelo exportado.
- **Último trabajo:** cierre de la Fase 0. Se reconstruyó la arquitectura y relación entre `modelo_1.h5`, `modelo_1_balanced.h5` y `mejor_modelo.h5` (mismo backbone; `modelo_1_balanced.h5` es un congelado de `modelo_1.h5`; `mejor_modelo.h5` es un estado de entrenamiento posterior), y se agotó la búsqueda local de entorno de entrenamiento (TensorFlow/CUDA/cuDNN/GPU), logs/historial de entrenamiento y motivo de exclusión de `ig` — sin resultado positivo en ningún caso, mediante un flujo multiagente documentado en [Flujo de trabajo multiagente](agent-workflow.md). Resultados persistidos en [Investigaciones — HIST-MODELS-004](research.md#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5) y [HIST-ENV-005](research.md#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig).
- **Trabajo activo:** ninguno abierto en Fase 0. Las preguntas sin resolver (procedencia exacta de `modelo_1.h5`, motivo de "balanced", versión de TensorFlow/CUDA/cuDNN, uso real de GPU, exclusión de `ig`, manifiesto paciente/frotis) quedan documentadas como PENDIENTE-evidencia-agotada: solo se resolverían con una fuente externa a este repositorio y este dataset. Decidir si avanzar a Fase 1/2 del roadmap es una decisión a tomar con el usuario, no autónoma.
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
3. Avanzar a Fase 1 (comprensión, ya mayormente cubierta por [notebook-analysis.md](notebook-analysis.md)) o Fase 2 (baseline reproducible) es la siguiente decisión de alcance/roadmap; no se inició ningún trabajo de modernización o entrenamiento.
