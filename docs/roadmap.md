# Roadmap

El roadmap ordena la evolución; no autoriza por sí mismo a modificar el baseline histórico. Estado actual: **Fase 0**.

## Fase 0 — Preservación y arqueología (CERRADA 2026-09-07)

- [x] Preservar artefactos históricos y documentar pipeline ([evidencia](research.md#hist-audit-001-auditoría-del-pipeline-histórico), [notebook-analysis.md](notebook-analysis.md)).
- [x] Identificar orígenes públicos y límite de trazabilidad de los datasets ([evidencia](dataset-provenance.md)).
- [x] Investigar arquitectura y relación de los modelos anteriores ([evidencia](research.md#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5)).
- [x] Investigar entorno de entrenamiento (TensorFlow/CUDA/GPU), logs de entrenamiento y exclusión de `ig` — evidencia local agotada sin resultado positivo ([evidencia](research.md#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)).

Cierre: no queda ninguna pregunta arqueológica local por investigar con los artefactos disponibles en este repositorio y en los datasets/directorios históricos locales. Las preguntas sin respuesta (procedencia exacta de cada checkpoint, versión de TensorFlow/CUDA/cuDNN, uso real de GPU, motivo de exclusión de `ig`, manifiesto paciente/frotis) quedan como PENDIENTE-evidencia-agotada en [Investigaciones](research.md#preguntas-abiertas); resolverlas requeriría una fuente externa a este repositorio. Avanzar a Fase 1/2 es una decisión de alcance a tomar con el usuario.

## Fase 1 — Comprensión

- [x] Recorrer el notebook histórico por etapas técnicas ([análisis](notebook-analysis.md)).
- Distinguir decisiones correctas, limitaciones y conocimiento reutilizable.
- Documentar arquitectura y entrenamiento.

## Fase 2 — Baseline reproducible

- Definir dataset versionado fuera de Git.
- Eliminar leakage y definir split reproducible.
- Usar paciente/lámina como unidad independiente si los datos lo permiten.
- Considerar evaluación externa separada por fuente para las cinco clases compatibles, sin sustituir un split agrupado si se recuperan IDs.
- Reconstruir la CNN histórica en entorno moderno y obtener un baseline confiable.

## Fase 3 — Modelos modernos

Comparar de forma controlada CNN histórica, transfer learning y modelos ligeros aptos para navegador. No hay arquitectura definitiva decidida.

## Fase 4 — Evaluación

Métricas por clase, macro F1, matriz de confusión, análisis de errores, OOD/negativos y calibración de confianza.

## Fase 5 — Web

Medir tamaño, latencia, memoria y compatibilidad; evaluar TensorFlow.js frente a alternativas modernas solo después de medir.

## Fase 6 — Producto educativo

UX, explicabilidad, limitaciones, documentación, demo y seguridad del mensaje educativo/no diagnóstico.
