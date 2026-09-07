# Estado del proyecto

**Actualizado:** 2026-09-07
**Fase actual:** Fase 0 — preservación y arqueología; procedencia de datasets, comprensión técnica inicial de Fase 1, y arquitectura/relación de los tres modelos históricos completadas.

## Dónde estamos

- **Último hito:** el repositorio moderno fue inicializado/publicado en septiembre de 2026, conservando el notebook histórico y la aplicación web con el modelo exportado.
- **Último trabajo:** reconstrucción de la arquitectura y relación entre `modelo_1.h5`, `modelo_1_balanced.h5` y `mejor_modelo.h5` mediante inspección de solo lectura (HDF5 + comparación byte a byte de pesos), ejecutada con un flujo multiagente documentado en [Flujo de trabajo multiagente](agent-workflow.md). Resultado persistido en [Investigaciones — HIST-MODELS-004](research.md#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5).
- **Trabajo activo:** recuperar, si existe, una relación crop→campo/frotis/paciente y documentar el entorno histórico (CUDA/GPU); la procedencia exacta del proceso que generó cada uno de los tres modelos sigue pendiente por falta de logs de entrenamiento.
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

No hay modernización ni entrenamiento nuevo en curso.

## Preguntas abiertas prioritarias

Recuperación de manifiestos de paciente/lámina/frotis, motivo de exclusión de `ig`, entornos TensorFlow/CUDA/GPU, modelos anteriores y cuantificación del leakage. Lista completa: [Investigaciones](research.md#preguntas-abiertas).

## Siguiente paso recomendado

Buscar manifiestos o releases originales que puedan mapear crops a paciente/frotis/campo, empezando por el dataset Bodzas; en paralelo, localizar evidencia del entorno TensorFlow/CUDA/GPU y de los modelos anteriores. Si no aparecen IDs, documentar definitivamente la limitación antes de diseñar el baseline reproducible.
