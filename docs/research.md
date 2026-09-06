# Investigaciones

Registro de preguntas y evidencia. Estados permitidos: `OPEN`, `IN PROGRESS`, `RESOLVED`. Cada entrada debe incluir pregunta, contexto, evidencia revisada, hallazgos, nivel de certeza, conclusión, preguntas nuevas, impacto potencial y fecha. Use una nueva sección solo para investigación con evidencia o resultado reutilizable.

## HIST-AUDIT-001 — Auditoría del pipeline histórico

**Estado:** RESOLVED (para el alcance de la reconstrucción actual)
**Fecha:** 2026-09-05
**Pregunta:** ¿Qué pipeline produjo el baseline histórico y qué tan interpretable es su métrica?

**Contexto y evidencia revisada:** notebook histórico `Hematologia.ipynb` (idéntico a `ml/notebooks/Hematologia.ipynb`), sus salidas guardadas, scripts históricos auxiliares y estructura/conteos del dataset local histórico.

**Hallazgos:**

- **CONFIRMADO:** augmentation físico antes del split, reducción a 5.950 imágenes por clase, split 85/10/5 por archivo y augmentation online posterior solo en train.
- **CONFIRMADO:** 53.550 imágenes finales, con 45.513/5.355/2.682 en train/validation/test; entrenamiento de 62 épocas y mejor época 50.
- **CONFIRMADO:** riesgo de leakage del pipeline por mezclar originales y derivados antes del split.
- **INFERIDO:** la métrica de test histórica cercana a 98,92 % puede estar optimista y no es una estimación fiable de generalización.
- **HIPÓTESIS:** podrían existir cadenas de augmentation sobre imágenes ya aumentadas; requiere trazabilidad de archivos para demostrarlo.

**Conclusión:** conservar el baseline como evidencia y no usar su métrica como validación clínica ni como comparación definitiva. La historia detallada está en [Historia y baseline histórico](project-history.md).

**Preguntas nuevas:** cuantificar pares relacionados entre splits y recuperar metadatos de la unidad independiente.

**Impacto potencial:** alto; determina cómo debe construirse el baseline reproducible y cómo se comunica el modelo existente.

## HIST-NB-002 — Comprensión técnica del notebook histórico `Hematologia.ipynb`

**Estado:** RESOLVED (lectura estática del artefacto preservado)
**Fecha:** 2026-09-05
**Pregunta:** ¿Qué problema intentaba resolver cada etapa del notebook, cómo funcionaba técnicamente y cuáles son sus límites actuales?

**Contexto y evidencia revisada:** código, metadata y outputs guardados de `ml/notebooks/Hematologia.ipynb`; no se ejecutó ni modificó. El análisis trazable está en [Comprensión técnica del notebook histórico](notebook-analysis.md).

**Hallazgos:**

- **CONFIRMADO:** el notebook parte de `Labelled_mix`; realiza inspección, augmentation físico, reducción a 5.950 por clase, split por archivo, augmentation online solo en train, CNN, callbacks y evaluación por clase.
- **CONFIRMADO:** no contiene la integración de las fuentes que originaron `Labelled_mix`, ni creación de `Labelled`/`Labelled_2`/`Divided`, ni código de exportación TensorFlow.js.
- **CONFIRMADO:** la CNN tiene 32 convoluciones, cuatro pools, cabeza `Flatten → 512 → 1024 → 512 → 9` y 4.372.857 parámetros totales (4.370.041 entrenables).
- **CONFIRMADO:** la metadata guardada declara `tf-cpu`; no demuestra por sí sola que el entrenamiento se ejecutara en CPU, pero no hay comprobación de GPU en el notebook.
- **INFERIDO:** el orden augmentation físico→split puede explicar parte del rendimiento extremadamente alto, pero no cuantifica leakage efectivo.
- **PROBABLE:** la ausencia de aceleración GPU efectiva, junto con la CNN profunda y el pipeline de imágenes, contribuyó a las ≈55,58 horas de entrenamiento; requiere evidencia de entorno para confirmarlo.

**Conclusión:** el artefacto representa un flujo educativo de ML completo y varias de sus decisiones siguen siendo válidas, pero no permite reconstruir la procedencia de datos ni garantizar evaluación independiente. No debe modernizarse ni ejecutarse para resolver esas incógnitas.

**Preguntas nuevas:** ¿qué archivos/documentos externos registran la creación de `Labelled_mix` y la exportación TF.js? ¿Puede auditarse el árbol de archivos para reconstruir familias de originales/derivados?

**Impacto potencial:** alto; completa el primer recorrido técnico de Fase 1 y define la evidencia mínima necesaria antes de reconstruir un baseline reproducible.

## HIST-DATA-003 — Procedencia, estructura y trazabilidad de datasets históricos

**Estado:** RESOLVED (para procedencia y trazabilidad disponible en los artefactos preservados)
**Fecha:** 2026-09-05
**Pregunta:** ¿De dónde provienen `Labelled` y `Labelled_2`, qué representa `ig` y queda una unidad independiente para un split correcto?

**Contexto y evidencia revisada:** árbol local, nombres, extensiones, conteos, metadata no destructiva, hashes representativos, scripts históricos y fuentes primarias públicas. El detalle y las citas viven en [Procedencia y trazabilidad de los datasets](dataset-provenance.md).

**Hallazgos:**

- **CONFIRMADO:** `Labelled` contiene el dataset de alta resolución de Bodzas, Kodytek & Zidek (2023), convertido a PNG; `Divided` conserva los mismos nombres base como BMP en un split histórico 80/10/10.
- **CONFIRMADO:** `Labelled_2` es `PBC_dataset_normal_DIB` de Acevedo et al. (2020), con sus 17.092 imágenes JPG y ocho grupos originales.
- **CONFIRMADO:** `ig` es el grupo de immature granulocytes de PBC; sus 2.895 archivos explican exactamente la diferencia entre las 17.092 imágenes de PBC y las 30.224 que llegaron a `Labelled_mix`.
- **CONFIRMADO:** `Labelled_mix` comenzó como `16.027 + (17.092 − 2.895) = 30.224`; la suma por cada una de las nueve clases finales coincide exactamente.
- **CONFIRMADO:** ninguna copia local contiene manifiesto o IDs fiables de paciente, frotis, lámina, campo o imagen fuente.
- **INFERIDO:** `Labelled` y `Divided` son derivados paralelos de un árbol BMP común; no hay evidencia suficiente para afirmar que uno se creó directamente desde el otro.

**Conclusión:** para los artefactos preservados, la situación es **D — solo split por archivo disponible**. Aunque la publicación Bodzas registra 78 pacientes y 81 frotis, esos vínculos no se conservaron en los nombres incrementales locales. PBC tampoco expone IDs de sujeto en esta copia.

**Preguntas nuevas:** ¿se puede recuperar un manifiesto original de Bodzas que mapee crops a campo/frotis/paciente? ¿existe una copia histórica externa de la preparación de `Labelled_mix` que documente la exclusión de `ig`? ¿qué definición semántica debe usarse para una futura comparación inter-fuente de eritroblasto/normoblast?

**Impacto potencial:** alto; permite separar los dominios de origen y plantea una futura evaluación externa de cinco clases comunes, pero no autoriza aún un experimento.

## Preguntas abiertas

Todas están `OPEN` salvo que una investigación posterior indique lo contrario.

1. ¿Puede recuperarse un manifiesto que mapee los crops Bodzas a paciente, frotis, campo o imagen fuente?
2. ¿Existe una copia/release de PBC con identificadores de sujeto o adquisición, no presentes localmente?
3. ¿Por qué se excluyó `ig` de la mezcla histórica?
4. ¿Qué versión exacta de TensorFlow se usó para entrenamiento?
5. ¿Qué versión histórica de CUDA/cuDNN existía?
6. ¿Se utilizó realmente la GTX 1050 durante algún entrenamiento?
7. ¿Qué arquitectura y resultados correspondieron a `modelo_1.h5`?
8. ¿Qué arquitectura y resultados correspondieron a `modelo_1_balanced.h5`?
9. ¿Cuánto leakage efectivo existe entre train/validation/test?
10. ¿Podemos reconstruir relaciones original→imagen aumentada?
11. ¿Cuál sería el rendimiento de la CNN histórica sobre un split metodológicamente correcto?
12. ¿Qué definición semántica y protocolo serían adecuados para una futura evaluación externa de las cinco clases compartidas entre fuentes?
