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

## HIST-MODELS-004 — Reconstrucción de `modelo_1.h5`, `modelo_1_balanced.h5` y `mejor_modelo.h5`

**Estado:** RESOLVED (para arquitectura y relación entre archivos); PENDIENTE la procedencia exacta del proceso/corrida que generó cada uno
**Fecha:** 2026-09-07
**Pregunta:** ¿Qué arquitectura y resultados corresponden a `modelo_1.h5` y `modelo_1_balanced.h5`, y cómo se relacionan con `mejor_modelo.h5`? (preguntas 7 y 8, más abajo)

**Contexto y evidencia revisada:** inspección de solo lectura de los tres `.h5` (`D:\Datasets\dataset_hematologia\Modelos\modelo_1.h5`, `modelo_1_balanced.h5`, y `artifacts/keras/mejor_modelo.h5`) vía metadatos HDF5 (`h5py`, sin cargar los modelos en un runtime Keras/TensorFlow) y comparación numérica exacta de los 184 tensores de `model_weights`; hashes SHA-256, tamaños y fechas de sistema de archivos calculados de forma independiente dos veces; búsqueda de referencias en `Hematologia.ipynb` (copia histórica y la preservada en este repositorio) y en el repositorio histórico `Proyecto Hematología` (sin historial Git recuperable: `git` rechaza el directorio por "dubious ownership" y nadie cambió esa configuración sin autorización).

**Hallazgos:**

- **CONFIRMADO:** los tres archivos comparten topología idéntica (77 capas: 1 InputLayer, 32 Conv2D, 32 BatchNormalization, 4 MaxPooling2D, 1 Flatten, 4 Dense, 3 Dropout), misma entrada `(None,150,150,3)`, misma salida softmax de 9 clases y 4.372.857 parámetros totales — coincide con la arquitectura de `mejor_modelo.h5` ya documentada en [notebook-analysis.md](notebook-analysis.md).
- **CONFIRMADO:** la diferencia de tamaño en disco entre `modelo_1_balanced.h5` (17,7 MB) y los otros dos (~53 MB) no refleja una arquitectura distinta; se debe a que `modelo_1_balanced.h5` no tiene estado de optimizador Adam guardado (sus 76 capas no-`InputLayer` están marcadas `trainable=false`), mientras que `modelo_1.h5` y `mejor_modelo.h5` sí lo tienen completo.
- **CONFIRMADO** (comparación byte a byte de los 184 tensores de pesos): `modelo_1_balanced.h5` es un re-guardado, congelado y sin estado de optimizador, de exactamente los mismos pesos que `modelo_1.h5`. No es el resultado de un reentrenamiento sobre datos "balanceados" distintos.
- **CONFIRMADO:** `mejor_modelo.h5` no es una copia ni una continuación trivial de `modelo_1.h5`: sus 184 tensores difieren en su totalidad (diferencia absoluta máxima 33,12; media por tensor 0,42), una magnitud compatible con progreso real de entrenamiento.
- **INFERIDO** (coincidencia numérica exacta, no lectura directa de un log por época): el learning rate registrado en `modelo_1.h5` (~0,0004) es el valor inicial de Adam; el de `mejor_modelo.h5` (~0,0000032) coincide exactamente con el cuarto valor de la secuencia de `ReduceLROnPlateau` ya documentada en [notebook-analysis.md](notebook-analysis.md#10-callbacks-y-duración) (`0,0004→0,00008→0,000016→0,0000032→0,000001`). Esto sugiere que `modelo_1.h5` es un punto temprano del entrenamiento y `mejor_modelo.h5` uno tardío, cercano al mínimo de `val_loss` en la época 50.
- **HIPÓTESIS:** `modelo_1.h5` no fue guardado por el único `ModelCheckpoint` presente en el notebook preservado (que escribe solo a `mejor_modelo.h5`); probablemente proviene de una versión distinta del notebook, un `model.save()` manual no preservado, o una corrida separada. No hay evidencia para elegir entre estas opciones.
- **PENDIENTE:** si `modelo_1.h5` y `mejor_modelo.h5` pertenecen a la misma corrida continua de entrenamiento o a corridas separadas; el propósito funcional de congelar `modelo_1_balanced.h5`; y si el historial Git de `Proyecto Hematología` (actualmente inaccesible) contendría evidencia adicional.

**Conclusión:** la relación estructural entre los tres archivos queda confirmada (mismo backbone; `modelo_1_balanced.h5` es un congelado de `modelo_1.h5`; `mejor_modelo.h5` es un estado de entrenamiento genuinamente posterior). La procedencia exacta del proceso que generó cada checkpoint permanece abierta.

**Preguntas nuevas:** ¿existen logs de entrenamiento (`history.json` u equivalente) que registren val_loss/LR por época y permitan confirmar si `modelo_1.h5` y `mejor_modelo.h5` son la misma corrida? Si se autoriza resolver el bloqueo de Git en `Proyecto Hematología`, ¿su historial menciona `modelo_1.h5`/`modelo_1_balanced.h5`?

**Impacto potencial:** medio; completa la arquitectura y relación entre los tres artefactos históricos, pero no cambia el estado de preservación (siguen siendo evidencia de solo lectura) ni el roadmap de un baseline reproducible.

## HIST-ENV-005 — Búsqueda exhaustiva de entorno de entrenamiento, logs y exclusión de `ig`

**Estado:** RESOLVED (evidencia local agotada; preguntas quedan PENDIENTE por ausencia de evidencia, no por falta de búsqueda)
**Fecha:** 2026-09-07
**Pregunta:** ¿Puede determinarse la versión de TensorFlow/CUDA/cuDNN, el uso real de GPU, un log/historial de entrenamiento, o el motivo de exclusión de `ig`, a partir de los artefactos locales? (preguntas 3, 4, 5, 6 y 13)

**Contexto y evidencia revisada:** metadata completa (`metadata` raíz) y las 33 celdas de salida de `Hematologia.ipynb` (no el código); atributos HDF5 completos —raíz y descendientes— de `modelo_1.h5` y `mejor_modelo.h5`; lectura completa de los seis scripts de `Proyecto Hematología/Proyecto/utils/`; enumeración recursiva por extensión de los 156.252 archivos de `D:\Datasets\dataset_hematologia`.

**Hallazgos:**

- **CONFIRMADO:** el notebook solo declara `kernelspec.display_name="tf-cpu"` y `language_info.version="3.11.5"`; no hay otro campo de metadata. Ninguna de las 33 celdas de salida contiene texto sobre GPU, CUDA, cuDNN, NVIDIA, dispositivos físicos o versión de TensorFlow (0 coincidencias en una búsqueda exhaustiva case-insensitive).
- **CONFIRMADO:** los atributos HDF5 de `modelo_1.h5` y `mejor_modelo.h5` (raíz y descendientes, incluidos `layer_names`/`weight_names`) no contienen `tensorflow_version`, CUDA, cuDNN, GPU ni ningún dato de hardware; solo `backend='tensorflow'` y `keras_version='2.10.0'`, ya conocidos.
- **CONFIRMADO:** de 156.252 archivos en todo `D:\Datasets\dataset_hematologia`, 156.250 son imágenes y los 2 restantes son `modelo_1.h5`/`modelo_1_balanced.h5`. No existe ningún `.log`, `.json`, `.csv`, `.txt`, `.yaml/.yml` ni archivo de historial de entrenamiento en esa carpeta.
- **CONFIRMADO:** ninguno de los seis scripts de `utils/` (`convert_images.py`, `delete_images.py`, `limit_samples_per_class.py`, `split_data.py`, `visualizar_result.py`, `__init__.py`) ni el notebook mencionan `ig`/`immature granulocytes` como motivo de exclusión, ni generan/referencian `modelo_1.h5` o `modelo_1_balanced.h5`, ni serializan el `history` de `model_1.fit(...)` a disco (`visualizar_result.py` solo grafica el objeto en memoria).
- **CONFIRMADO:** `limit_samples_per_class.py` (límite genérico de 50 archivos/clase) y `split_data.py` (split 80/10/10 con semilla 123) son utilitarios genéricos disponibles en el repositorio histórico, pero no están conectados al pipeline final del notebook (que usa reducción a 5.950/clase y split manual 85/10/5) ni explican el término "balanced".
- Una búsqueda adicional de palabras clave (cuda/cudnn/nvidia/gpu/tensorflow-gpu/history.json/requirements/environment.yml) en ambas raíces históricas solo produjo un falso positivo (contenido binario de imagen codificado en base64 dentro del notebook).

**Conclusión:** la evidencia local disponible está agotada para estas preguntas. No es que falte buscar más: se recorrió el 100% de las salidas del notebook, el 100% de los atributos HDF5, el 100% de los scripts históricos y el 100% de los archivos del dataset por extensión, sin resultado positivo en ningún caso. Las preguntas 3 (exclusión de `ig`), 4-6 (TensorFlow/CUDA/cuDNN/GPU) y 13 (logs de entrenamiento) permanecen `PENDIENTE`, pero como PENDIENTE-evidencia-agotada: solo se resolverían con una fuente externa a este dataset y este repositorio (memoria del desarrollador, otra máquina, u otro respaldo no localizado).

**Preguntas nuevas:** ninguna nueva; esto cierra el espacio de búsqueda local para estas preguntas.

**Impacto potencial:** medio; permite cerrar la Fase 0 (preservación y arqueología) del roadmap con una base de evidencia explícita y completa, distinguiendo claramente "no investigado" de "investigado y sin evidencia local".

## Preguntas abiertas

Todas están `OPEN` salvo que una investigación posterior indique lo contrario.

1. ¿Puede recuperarse un manifiesto que mapee los crops Bodzas a paciente, frotis, campo o imagen fuente?
2. ¿Existe una copia/release de PBC con identificadores de sujeto o adquisición, no presentes localmente?
3. ¿Por qué se excluyó `ig` de la mezcla histórica? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)): ningún script ni el notebook lo explican; requeriría una fuente externa.
4. ¿Qué versión exacta de TensorFlow se usó para entrenamiento? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)): ni el notebook ni los `.h5` la registran.
5. ¿Qué versión histórica de CUDA/cuDNN existía? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)).
6. ¿Se utilizó realmente la GTX 1050 durante algún entrenamiento? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)): solo hay evidencia indirecta e insuficiente (`kernelspec` "tf-cpu").
7. ¿Qué arquitectura y resultados correspondieron a `modelo_1.h5`? — **PARCIALMENTE RESUELTA**: arquitectura confirmada, idéntica a `mejor_modelo.h5` ([HIST-MODELS-004](#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5)); resultados (accuracy/loss de esa corrida específica) siguen PENDIENTES por falta de logs.
8. ¿Qué arquitectura y resultados correspondieron a `modelo_1_balanced.h5`? — **PARCIALMENTE RESUELTA**: es un re-guardado congelado, byte a byte idéntico a `modelo_1.h5` ([HIST-MODELS-004](#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5)); su propósito funcional sigue PENDIENTE.
9. ¿Cuánto leakage efectivo existe entre train/validation/test?
10. ¿Podemos reconstruir relaciones original→imagen aumentada?
11. ¿Cuál sería el rendimiento de la CNN histórica sobre un split metodológicamente correcto?
12. ¿Qué definición semántica y protocolo serían adecuados para una futura evaluación externa de las cinco clases compartidas entre fuentes?
13. ¿Existen logs de entrenamiento (`history.json` u equivalente) que permitan confirmar si `modelo_1.h5` y `mejor_modelo.h5` pertenecen a la misma corrida de entrenamiento? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)): censo completo de `dataset_hematologia` (156.252 archivos) no encontró ningún log/historial.
14. ¿Cuál era el propósito funcional de congelar `modelo_1_balanced.h5` (transfer learning, exportación, rama de entrenamiento distinta)? — **EVIDENCIA LOCAL AGOTADA** ([HIST-ENV-005](#hist-env-005-búsqueda-exhaustiva-de-entorno-de-entrenamiento-logs-y-exclusión-de-ig)): ningún script lo explica ni conecta con el nombre "balanced".
