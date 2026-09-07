# Plan de Fase 2 — baseline reproducible

**Estado del documento:** PROPUESTA, no ejecutada. No autoriza por sí sola a entrenar, descargar datos grandes, cambiar la taxonomía publicada ni modificar el modelo en producción. Requiere las autorizaciones marcadas explícitamente en cada sección y en [Decisiones pendientes de Miguel](#decisiones-pendientes-de-miguel).

Convención de certeza: `CONFIRMADO` / `INFERIDO` / `HIPÓTESIS` / `PENDIENTE`, igual que en [research.md](research.md). `HUMAN DOMAIN REVIEW REQUIRED` marca una decisión que depende de criterio hematológico y no debe cerrarse por ingeniería.

## Resumen ejecutivo

HematoVision tiene hoy una app funcional (modo manual y automático) sobre un modelo heredado de 2024 con **riesgo estructural de leakage confirmado** (el orden augmentation-antes-de-split), aunque la inflación efectiva de su accuracy sigue sin cuantificarse (INFERIDO, no CONFIRMADO — ver matiz en la Sección 3). El repositorio no tiene ninguna infraestructura de entrenamiento/evaluación reproducible (`ml/src` está vacío, no hay DVC, no hay manifiesto de datos). Este plan separa seis preocupaciones que hoy están mezcladas implícitamente en el código y en la conversación — taxonomía del modelo, taxonomía de reporte, aceptación/rechazo, conteo, evaluación del clasificador y evaluación del diferencial acumulado — y propone, para cada una, un diseño concreto, su validación y su criterio de salida, sin implementar nada todavía. El baseline propuesto reproduce la CNN histórica (misma arquitectura, mismas 9 clases) sobre un split nuevo que corrige el *mecanismo* de leakage por augmentation física (augmentation solo después del split, con una política explícita de duplicados exactos), explícitamente sin buscar superar la accuracy histórica ni afirmar independencia biológica. La ejecución real (construir el manifiesto, inicializar DVC, entrenar) requiere autorización separada porque implica cómputo no trivial sobre datos locales.

## Taxonomías y capas (marco para todo lo que sigue)

| Capa | Qué es | Estado hoy |
| --- | --- | --- |
| **A. Taxonomía interna del modelo** | Las 9 clases que el softmax predice: Basófilos, Eosinófilos, Eritroblastos, Linfoblastos, Linfocitos, Mieloblastos, Monocitos, Neutrófilos, Plaquetas. | **CONFIRMADO, existe** — `apps/web/src/constants.js:1`, idéntica a la CNN histórica. |
| **B. Taxonomía hematológica de reporte** | Mapeo de las 9 clases a categorías de reporte (p. ej. Linfoblastos+Mieloblastos → "Blast"), conservando la predicción original. | **No existe.** Propuesto abajo; su validez clínica es `HUMAN DOMAIN REVIEW REQUIRED`. |
| **C. Reglas de aceptación/rechazo** | Umbral de confianza → predicción concluyente o inconclusa. | **Existe parcialmente**: `MIN_CONFIDENCE=0.6` (`constants.js:9`) descarta la predicción sin contarla como estado; no hay un estado "inconcluso" rastreado. |
| **D. Reglas de conteo** | Qué entra en qué denominador (WBC, NRBC, plaquetas, blastos). | **Existe parcialmente y con un gap concreto**: `counter.js:3` excluye solo "Plaquetas" del denominador (`totalWithoutPlatelets`); **no excluye "Eritroblastos" (NRBC)**, que hematológicamente tampoco es un leucocito. |
| **E. Evaluación del clasificador** | Métricas del modelo sobre imágenes individuales aisladas. | **No existe de forma reproducible** — solo la evaluación no reproducible del notebook histórico (leakage confirmado). |
| **F. Evaluación del diferencial acumulado** | Métricas de la cuenta de 100 (o más) células simuladas. | **No existe.** |

Esta tabla es la referencia para todo el documento: cada sección de abajo pertenece a una o más de estas capas y no las mezcla.

## 1. Estado actual (evidencia, no propuesta)

Inspección directa de código el 2026-09-07 (no reconstruida de memoria de conversación):

- **App (`apps/web/src`):** `classifier.js` carga el modelo TF.js y devuelve `{label, confidence}` sobre las 9 clases (capa A). `constants.js` define `MIN_CONFIDENCE=0.6` y `isConclusive()` (capa C). `counter.js` es un contador plano de las 9 clases con un único ajuste: excluye "Plaquetas" del total (`totalWithoutPlatelets`) y del cap de 100 (`MAX_NON_PLATELET_COUNT`) — **no excluye "Eritroblastos"**. `app.js` implementa modo manual (un botón, una predicción) y modo automático (`setInterval(analyze, 2000)`, sin tracking ni deduplicación entre capturas — limitación ya documentada en `model-card.md`). Todo esto es real, funcional y probado (`apps/web/tests/*.test.js` cubre los cinco módulos + activos del modelo).
- **ML (`ml/`):** `pyproject.toml` declara un entorno **moderno** (TensorFlow ≥2.16,<2.20; Keras ≥3.0,<4.0) — distinto del entorno histórico del `.h5` publicado (Keras 2.10.0, confirmado por HDF5, ver `model-card.md` y HIST-MODELS-004). `ml/src/hematovision_ml/utils` existe como carpeta pero está **vacía** (sin archivos `.py`). No hay `ml/tests`. No hay DVC inicializado (no existe `.dvc/`). El único artefacto de entrenamiento reproducible es el notebook histórico, preservado como evidencia, no como punto de partida ejecutable (ver `AGENTS.md`).
- **Documentación de proceso ya existente y reutilizable** (no hace falta reinventarla): `docs/update-protocol.md` ya define el checklist de "Cambios de modelo" (semilla registrada, test inmóvil, actualizar model-card, exportar y probar antes de publicar) y `docs/experiments.md` ya define la plantilla `EXP-NNN`. Este plan se apoya en ambos en vez de duplicarlos.
- **Investigación histórica reutilizada sin repetir** (Fase 0, cerrada): arquitectura de las 32 convoluciones y 4.372.857 parámetros (`notebook-analysis.md`), relación `modelo_1.h5`→`modelo_1_balanced.h5`→`mejor_modelo.h5` (HIST-MODELS-004), leakage estructural confirmado por augmentation-antes-de-split (HIST-AUDIT-001), procedencia de datasets y "Situación D — solo split por archivo disponible" (`dataset-provenance.md`), ausencia total de logs/entorno GPU-CUDA local (HIST-ENV-005). Ninguna de estas auditorías se repite aquí.

## 2. Dataset y split

**Estado de ejecución (2026-09-07):** tareas 1-4 de la Sección 7 ejecutadas y verificadas de forma independiente — inventario completo en [Manifiesto de originales](dataset-manifest.md). El manifiesto y la propuesta de split existen; **el test NO está congelado** (bloqueado por un conflicto de etiqueta sin resolver y por decisiones de proporción/semilla pendientes de aprobación — ver ese documento). Tareas 5 en adelante (scaffolding, DVC, EXP-REPRO) siguen sin autorizar.

**Restricción de partida (ya confirmada, no se re-investiga):** ninguna copia local conserva ID de paciente, frotis o campo (`dataset-provenance.md`, "Situación D"). Cualquier split que afirme independencia por paciente sería inventado. Este plan no lo hace.

**Punto de partida correcto — no es `Labelled_mix`.** `Labelled_mix`, tal como existe hoy en disco, ya fue contaminado por el augmentation físico histórico (contiene originales y derivados `img_...` mezclados; `dataset-provenance.md` línea 64). Reutilizarlo como fuente de "originales" heredaría el problema. El manifiesto nuevo debe construirse desde las dos carpetas **nunca aumentadas**: `Labelled` (16.027, Bodzas) y `Labelled_2` excluyendo `ig` (14.197, PBC) — 30.224 originales, replicando la unión aritmética ya documentada, sin repetir la decisión de exclusión de `ig` (que queda igual, con su motivo aún PENDIENTE-evidencia-agotada).

**Diseño propuesto:**

1. **Manifiesto** (`ml/data/manifest.csv` o `.parquet`, fuera de Git salvo un `.dvc`/puntero, según `ml/README.md`): una fila por imagen original con columnas mínimas `path_original`, `fuente` (Bodzas/PBC), `clase_carpeta_origen`, `clase_final_9` (tras el mapeo Band+Segment→Neutrófilos y Normoblast→Eritroblastos ya usado históricamente — se mantiene igual para permitir comparación, no se re-decide aquí), `sha256`, `split` (asignado en el paso 2). El hash SHA-256 sirve para detectar corrupción/duplicados exactos y para que el manifiesto sea auditable sin re-leer las imágenes.
2. **Política de duplicados exactos (antes de asignar split):** `dataset-provenance.md` (línea 60) ya registra que muestras de ambos árboles aparecen en `Labelled_mix` con el mismo SHA-256. Antes de asignar split, agrupar el manifiesto por `sha256` y tratar cada grupo de hashes idénticos como una sola unidad indivisible (todo el grupo va al mismo split); registrar cuántos grupos/colisiones aparecen. Esto es necesario pero no suficiente: no cubre duplicados *no exactos* (recortes ligeramente distintos de la misma célula/campo), que quedan fuera de alcance de este plan y deben declararse como límite conocido, no como caso resuelto.
3. **Unidad de split:** el **grupo de archivo original idéntico** (paso 2), no el paciente (no disponible) y no el archivo aumentado (no existe todavía en este punto, porque el split ocurre *antes* de augmentar). Esto corrige el mecanismo de leakage por augmentation física documentado en HIST-AUDIT-001, sujeto a la auditoría de duplicados del paso 2 — pero **no** logra independencia biológica ni descarta duplicados no exactos; debe comunicarse siempre así, nunca como "split independiente" a secas.
4. **Asignación:** partición aleatoria estratificada por `clase_final_9` (para conservar proporciones por clase), con semilla fija registrada, sobre los grupos del paso 2 (30.224 originales antes de agrupar duplicados). Proporción a decidir con el usuario (el histórico usó 85/10/5; con augmentation ahora solo online y no física, se puede permitir un train más chico relativo sin perder tantas imágenes por augmentation física redundante — a discutir, no decidido aquí).
5. **Test final:** un subconjunto de grupos-de-originales, congelado (hash del listado completo commiteado o registrado en el manifiesto), usado **una sola vez** para el reporte final de cada experimento. No se reutiliza para elegir hiperparámetros ni el umbral de aceptación (eso usa validación, ver Sección 4). Explícitamente **no** es `Divided_Labelled_Mix/test` (ese conjunto es un split de material ya aumentado, contaminado por diseño).
6. **Augmentation:** solo online, solo sobre `train`, generada en el pipeline de entrada durante el entrenamiento — nunca físicamente pre-guardada en disco antes del split. Esto, junto con la política de duplicados del paso 2, es lo que corrige el mecanismo de leakage documentado, sin necesidad de "demostrar" leakage caso por caso.
7. **Trazabilidad por fuente:** conservar la columna `fuente` permite, sin trabajo adicional futuro, una evaluación separada Bodzas-vs-PBC (capa E) y deja la puerta abierta al experimento "POSIBLE" de 5 clases inter-fuente que ya proponía `dataset-provenance.md`, sin comprometerse a ejecutarlo ahora.

**Validación de este paso:** el manifiesto debe reproducir exactamente los conteos ya confirmados (30.224 total, conteos por clase de la tabla en `dataset-provenance.md`); cualquier discrepancia bloquea el resto del plan hasta explicarse.

**Riesgo/costo:** construir el manifiesto implica leer y hashear ~30.224 imágenes (dos datasets completos). Es de solo lectura (no mueve ni modifica nada), pero no es instantáneo — requiere autorización antes de ejecutarse por el volumen de I/O, no por el riesgo.

## 3. Baseline ML

Dos experimentos, deliberadamente separados y nunca conflados:

### EXP-REPRO (esta fase) — reproducción metodológica, no mejora

- **Objetivo:** un número de accuracy/F1 honesto y reproducible para la arquitectura histórica, sobre el split limpio de la Sección 2. **No se espera ni se promete igualar o superar el ~98,92% histórico.** El riesgo estructural de leakage está `CONFIRMADO` (augmentation antes del split, HIST-AUDIT-001), pero cuánto infló efectivamente esa accuracy sigue sin cuantificarse — es `INFERIDO` que puede estar optimista, no un hecho demostrado. Un número más bajo aquí sería consistente con el riesgo conocido, no una prueba adicional de cuánto se infló.
- **Alcance exacto de "reproducción":** este experimento es una **reproducción metodológica de arquitectura y pipeline** (misma CNN, mismas 9 clases, mismo espíritu de entrenamiento), **no** una reproducción bit-exacta del artefacto `mejor_modelo.h5` (Keras 2.10.0). No debe leerse ni reportarse como si igualara el artefacto histórico a nivel de pesos, serialización o entorno.
- **Arquitectura:** la misma CNN reconstruida en `notebook-analysis.md` §7-8 (32 Conv2D + BatchNorm, 4 MaxPool, cabeza Flatten→512→1024→512→9, ≈4.372.857 parámetros), no una arquitectura nueva.
- **Entorno:** el declarado en `ml/pyproject.toml` (TensorFlow ≥2.16, Keras ≥3.0) — **no** se intenta recrear el entorno de 2024 (Keras 2.10), porque esa reconstrucción exacta ya se investigó y su evidencia está agotada (HIST-ENV-005: no hay versión de TF/CUDA/cuDNN registrada en ningún artefacto local). Antes de dar por aceptable esta migración, ejecutar una prueba mínima de compatibilidad (construir el modelo con la arquitectura documentada en Keras 3 y verificar que serializa/exporta a TF.js sin sorpresas nuevas más allá del shim de `L2` ya conocido) — no asumir que Keras 3 es un reemplazo transparente de Keras 2.10 solo porque ambos son Keras.
- **Semillas:** una semilla para la asignación del split (Sección 2, ya fija en el manifiesto) y una semilla distinta para la inicialización/entrenamiento del modelo, registradas por separado — responden preguntas distintas de reproducibilidad.
- **Checkpoints y registro:** a diferencia del histórico (que nunca serializó `history` a disco — confirmado en HIST-ENV-005), este experimento debe guardar `history.json`/CSV por época, el checkpoint de mejor `val_loss`, y la configuración completa (arquitectura, hiperparámetros, versiones de librerías) en una carpeta de experimento versionada por fecha/hash, fuera de Git (según `ml/README.md`, vía DVC cuando se inicialice).
- **Registro documental:** una entrada `EXP-001` en `docs/experiments.md` con la plantilla ya definida ahí — no se inventa un formato nuevo.
- **Exportación:** solo después de que la evaluación (Sección 4) se revise y apruebe, siguiendo el checklist ya existente en `docs/update-protocol.md` ("Cambios de modelo"). No se reemplaza el modelo publicado como parte de este plan.

### EXP-COMPARE (futuro, explícitamente fuera de esta fase)

Comparar arquitecturas alternativas (transfer learning, modelos ligeros para navegador) contra el baseline de EXP-REPRO. No se decide arquitectura aquí; no se inicia sin que EXP-REPRO exista primero.

**Validación de esta sección:** EXP-REPRO no se ejecuta sin autorización explícita (ver [Plan de ejecución](#7-plan-de-ejecución)) — es cómputo de entrenamiento real, no lectura.

## 4. Evaluación individual (capa E)

Sobre el test congelado de la Sección 2, una sola vez por experimento registrado:

- **Métricas:** accuracy, macro-F1, precision/recall/F1 por clase, matriz de confusión (cruda y normalizada) — sobre las 9 clases (taxonomía A).
- **Vista agrupada de reporte:** las mismas predicciones, agregadas según la taxonomía B propuesta (Sección 6) — p. ej. recall/precision de "Blast" como unión de Linfoblastos+Mieloblastos. Es una relectura de las mismas predicciones, no un modelo nuevo.
- **Evaluación por fuente:** el mismo conjunto de métricas separado por `fuente` (Bodzas vs PBC) usando la columna del manifiesto — permite ver si el modelo generaliza igual entre dominios de adquisición, sin necesitar una nueva investigación.
- **Estudio de rechazo/inconclusos, sin asumir 0.6:** construir una curva riesgo-cobertura (accuracy vs. % de predicciones aceptadas) variando el umbral de confianza **sobre validación**, nunca sobre el test congelado — así el umbral final se elige sin haber tocado el número que se reporta como resultado. El histórico 0.6 se trata como un candidato a verificar, no como una referencia válida por defecto (ya documentado como no calibrado en `model-card.md`).
- **Límite explícito:** esta evaluación no incluye ejemplos fuera de dominio (caras, fondos) — el modelo es un softmax cerrado que siempre reparte 100% entre las 9 clases (`model-card.md`). Calibrar el umbral contra falsos-positivos-fuera-de-dominio requeriría un set negativo que hoy no existe; se deja como PENDIENTE, no se inventa.

## 5. Evaluación del diferencial simulado (capa F)

**Objetivo:** medir qué tan bien la capa de conteo/agregación reconstruye una composición porcentual conocida a partir de predicciones ya evaluadas en la Sección 4 — no evalúa detección, tracking, selección de campo ni desempeño clínico sobre un frotis real. Esta limitación se declara aquí explícitamente y debe repetirse en cualquier reporte de resultados.

**Diseño:**

1. **Composición(es) de referencia:** una o más distribuciones porcentuales objetivo por clase (p. ej. un diferencial "normal" de referencia). **La composición de referencia es `HUMAN DOMAIN REVIEW REQUIRED`** — no se define aquí un porcentaje "normal" por clase; debe venir de Miguel o de literatura hematológica citada explícitamente.
2. **Muestreo:** para una composición objetivo y un tamaño de panel (100, y como análisis adicional 200/400), muestrear del **test congelado** (no de train/val) un conjunto de imágenes por clase verdadera que respete esa proporción, aplicar el clasificador ya evaluado (mismo umbral fijado en la Sección 4, sin re-tunearlo aquí) y tabular el diferencial predicho.
3. **Repetición y semillas:** repetir el muestreo con múltiples semillas registradas (no una sola corrida) para obtener una distribución de error por clase, no un único número.
4. **Métricas:** error absoluto medio por clase (con desviación), sesgo (dirección sistemática de sobre/sub-conteo por clase), y la distribución completa de errores entre repeticiones — no solo el promedio.
5. **200/400 células:** un análisis adicional para ver si el error se reduce con paneles más grandes, explícitamente exploratorio, **no** un requisito clínico ya aprobado.
6. **Protección contra fuga de decisiones:** el umbral de aceptación y cualquier otro hiperparámetro se fijan en la Sección 4 usando validación; esta sección solo *usa* esas decisiones ya congeladas sobre test, no las ajusta. Si algún resultado de esta simulación sugiriera cambiar el umbral, ese cambio se re-evaluaría en un experimento nuevo con su propio ciclo validación→test, no ajustando retroactivamente este.

## 6. Contrato del contador (propuesta, no implementada)

Separación explícita de capas (sin escribir código todavía):

1. **Predicción ML** (ya existe): una de las 9 clases + confianza.
2. **Mapeo hematológico** (propuesto): las 9 clases se agrupan para reporte — Linfoblastos+Mieloblastos → "Blast"; el resto se reporta 1:1. La predicción original de 9 clases se conserva siempre (nunca se descarta al agrupar), para no perder trazabilidad ni bloquear una futura re-agrupación.
3. **Aceptación** (existe parcialmente): confianza ≥ umbral → concluyente; si no, hoy la predicción no se cuenta y se muestra un mensaje ("Imagen no concluyente · enfoca una célula aislada", `app.js`), pero no queda registrada como estado del contador — desaparece del *conteo*, no de la UI. Propuesta: convertir "inconcluso" en un **estado rastreado del contador** (visible en el conteo acumulado, no solo como mensaje transitorio de la última captura).
4. **Conteo** (existe parcialmente, con el gap ya señalado en la Sección 1): estados propuestos —
   - **WBC:** las 7 clases leucocitarias (incluyendo Blast agrupado para el denominador de reporte, y Linfoblastos/Mieloblastos por separado para la vista detallada).
   - **NRBC** (Eritroblastos): tratado aparte del denominador WBC — **hoy no lo está** (gap confirmado en Sección 1). Convención de reporte (¿cuenta absoluto, por-100-WBC, o ambos?) es `HUMAN DOMAIN REVIEW REQUIRED`.
   - **Plaquetas:** ya separado del denominador hoy; mantener.
   - **Blastos:** vista agregada de reporte (ver mapeo #2); si su presencia debe disparar automáticamente un estado de "pendiente de revisión" es una decisión abierta (ver más abajo).
   - **Inconclusos:** predicciones bajo el umbral, contadas como estado propio en vez de descartadas.
   - **Duplicados:** no existe ningún mecanismo de deduplicación en modo automático hoy (cada intervalo de 2s es independiente, limitación ya documentada en `model-card.md`); este contrato no lo resuelve — requiere tracking/detección, fuera de alcance de este plan — pero lo deja nombrado como estado pendiente en vez de invisible.
   - **Pendientes de revisión:** estado para conteos/hallazgos que un flujo humano futuro debería revisar (p. ej. presencia de Blast o NRBC). Criterio exacto: decisión abierta.

**No se implementa nada de esto en este plan.** Es el contrato a validar con Miguel antes de tocar `counter.js`/`app.js`.

## 7. Plan de ejecución

Tareas pequeñas, en orden de dependencia. Cada una indica qué necesita para arrancar y qué la cierra.

| # | Tarea | Depende de | Recursos | Autorización requerida |
| --- | --- | --- | --- | --- |
| 1 | Diseñar el esquema exacto del manifiesto (columnas, formato de archivo) | Este plan | Ninguno (solo diseño) | No — puede iterarse en docs |
| 2 | Construir el manifiesto real (leer + hashear `Labelled` + `Labelled_2`) | 1 | I/O sobre ~30.224 imágenes, solo lectura | **Sí** — volumen de trabajo, aunque sea de solo lectura |
| 3 | Validar el manifiesto contra los conteos ya confirmados en `dataset-provenance.md` | 2 | Cómputo trivial | No |
| 4 | Agrupar duplicados exactos por `sha256`, asignar split train/val/test estratificado sobre esos grupos, congelar test (hash del listado) | 3 | Cómputo trivial | No |
| 5 | Scaffolding de `ml/src` (pipeline de augmentation online, carga desde manifiesto) — código, sin entrenar | 4 | Ninguno | No |
| 6 | Inicializar DVC y configurar un remoto compartido (S3/GCS/Azure Blob), versionar el manifiesto y la asignación de split — **requisito explícito de `ml/README.md` antes de una nueva ronda de entrenamiento**, no opcional | 4, 5 | Configuración de infraestructura (cuenta/credenciales de almacenamiento remoto) | **Sí** — decisión de infraestructura/costo distinta de "solo cómputo local" |
| 7 | **EXP-REPRO**: entrenar la CNN histórica sobre el split nuevo, en el entorno moderno declarado en `ml/pyproject.toml` (reproducción metodológica de arquitectura/pipeline, no reproducción bit-exacta del artefacto Keras 2.10 — ver riesgo en Sección 3) | 5, 6 | Cómputo de entrenamiento; el histórico tardó ≈55,58h y no hay evidencia local de qué dispositivo lo ejecutó (CPU-únicamente es solo PROBABLE, no CONFIRMADO — `research.md`). No hay base para proyectar una duración en hardware moderno sin un benchmark corto previo | **Sí, explícita** — es el punto de no-retorno de "iniciar entrenamiento" que pediste no cruzar sin permiso |
| 8 | Evaluación individual (capa E), 9 clases, sobre el test congelado | 7 | Cómputo trivial | No (una vez autorizado 7) |
| 9 | Vista agrupada de reporte (taxonomía B, p. ej. "Blast") sobre las mismas predicciones de la tarea 8 | 8, **y aprobación de la taxonomía B en la tarea 13** | Cómputo trivial | Bloqueada por decisión humana (no por cómputo): no se reporta la vista agrupada hasta que la Sección 6/tarea 13 esté aprobada |
| 10 | Curva riesgo-cobertura sobre validación para revisar el umbral 0.6 | 7 | Cómputo trivial | No |
| 11 | Simulación de diferencial (capa F) | 8, 10, y definir composición(es) de referencia con Miguel | Cómputo trivial | Necesita la decisión de composición de referencia (Sección 5) antes de poder ejecutarse con sentido |
| 12 | Registrar `EXP-001` en `docs/experiments.md`, actualizar `model-card.md` si corresponde | 7-11 | Ninguno | No (documentación) |
| 13 | Diseñar (no implementar) el contrato del contador con Miguel, cerrando las decisiones abiertas de la Sección 6 (incluida la aprobación de la taxonomía B) | Independiente del resto | Ninguno | No (es conversación/decisión, no código) |
| 14 | Implementar el contrato del contador en código | 13 aprobada | Desarrollo normal | No debería requerir autorización especial si 13 ya está cerrada — pero es un cambio de producto visible, así que se revisa como cualquier PR |
| 15 | EXP-COMPARE (arquitecturas alternativas) | 7-12 completos | Cómputo de entrenamiento adicional, potencialmente varias corridas | **Sí, explícita**, y por separado de la autorización de la tarea 7 |

**Qué puede avanzar ya sin más autorización:** tareas 1 y 5 (diseño y scaffolding, sin tocar datos ni entrenar) y la conversación de la tarea 13.
**Qué está bloqueado en autorización de cómputo/infraestructura:** 2 (construir el manifiesto), 6 (DVC/remoto), 7 (EXP-REPRO) y 15 (EXP-COMPARE).
**Qué está bloqueado en una decisión humana, no en cómputo:** 9 (necesita aprobación de taxonomía B), 11 (necesita composición de referencia) y 14 (necesita el contrato aprobado).

## Matriz requisito → implementación propuesta → validación → criterio de salida

| Requisito | Implementación propuesta | Validación | Criterio de salida |
| --- | --- | --- | --- |
| A. Taxonomía del modelo | Mantener las 9 clases históricas sin cambios | Manifiesto reproduce conteos por clase ya confirmados | Conteos exactos, 0 discrepancias |
| B. Taxonomía de reporte | Mapeo 9→reporte (incl. "Blast"), prediction original conservada | Revisión hematológica del mapeo | Mapeo aprobado por Miguel/revisión de dominio |
| C. Aceptación/rechazo | Curva riesgo-cobertura sobre validación; "inconcluso" como estado | Curva calculada sin tocar test | Umbral elegido y justificado con la curva, no heredado sin revisar |
| D. Conteo | Estados WBC/NRBC/Plaquetas/Blast/Inconcluso/Duplicado/Pendiente-revisión (contrato, Sección 6) | Contrato revisado con Miguel antes de programarlo | Contrato aprobado explícitamente, por escrito, antes de tocar `counter.js` |
| E. Evaluación del clasificador | Accuracy/macro-F1/P-R-F1 por clase/matriz de confusión, 9 clases (sin dependencia humana) + vista agrupada por fuente (dependiente de aprobar B) | Ejecutada una sola vez sobre test congelado | Métricas de 9 clases registradas en `EXP-001`/`model-card.md`; vista agrupada solo se publica tras aprobar B |
| F. Evaluación del diferencial | Simulación de 100(+200/400) WBC, repetida con semillas, error/sesgo por clase | Reutiliza predicciones/umbral ya fijados, no retunea sobre test | Reporte con distribución de error, explícitamente no-clínico, no-diagnóstico |
| Dataset/split | Manifiesto de originales + agrupación de duplicados exactos + split pre-augmentation | Conteos verificados contra evidencia existente | Test congelado y hasheado, sin duplicados exactos cruzando splits, augmentation solo online en train |
| Baseline ML | Reproducción metodológica (no bit-exacta) de la CNN histórica en entorno moderno, con DVC/remoto ya configurado, sin buscar superar 98,92% | Prueba de compatibilidad Keras 3 + historia de entrenamiento persistida (a diferencia del histórico) | `EXP-001` completo y documentado, comparación honesta contra el baseline heredado, con su alcance metodológico explícito |

## Decisiones pendientes de Miguel

1. Equivalencia `Normoblast` (Bodzas) = `Eritroblastos`/`erythroblast` (PBC): ¿fue deliberada en 2024 o heredada del nombre de carpeta? (ya preguntado en el tramo "Datos", sigue sin respuesta).
2. ¿La agrupación "Blast" = Linfoblastos+Mieloblastos es hematológicamente apropiada para reporte, conservando siempre la predicción original? — `HUMAN DOMAIN REVIEW REQUIRED`.
3. Convención de reporte de NRBC (Eritroblastos): ¿conteo absoluto, "por 100 WBC", o ambos? — `HUMAN DOMAIN REVIEW REQUIRED`.
4. ¿Qué hacer con la ausencia de deduplicación en modo automático mientras no exista tracking: aceptar la limitación documentada, o restringir el modo automático? — decisión de producto, no bloquea este plan pero sí el contrato del contador (tarea 13).
5. Composición(es) de referencia hematológica para la simulación de diferencial (Sección 5) — `HUMAN DOMAIN REVIEW REQUIRED`, sin esto la tarea 11 no puede ejecutarse con sentido.
6. Tasa de falsos-positivos-fuera-de-dominio aceptable para el umbral de "inconcluso" — afecta confianza del usuario en una app educativa, no es diagnóstico, pero conviene decidirlo conscientemente en vez de heredar 0.6 sin revisar.
7. Autorización explícita y separada para: (a) construir el manifiesto real (tarea 2, cómputo de I/O sobre ~30.224 imágenes), (b) inicializar DVC y un remoto compartido (tarea 6, implica elegir y posiblemente pagar infraestructura de almacenamiento), (c) ejecutar EXP-REPRO (tarea 7, entrenamiento real), (d) más adelante, EXP-COMPARE (tarea 15).
8. Confirmación de que la búsqueda de manifiestos externos de paciente/frotis sigue diferida (ya lo decidiste; solo se registra aquí para que quede junto al plan que depende de ella).
9. Si "reproducción metodológica en entorno moderno (Keras 3)" es aceptable como alcance de EXP-REPRO, o si se prefiere invertir primero en recrear el entorno histórico (Keras 2.10) pese a que su evidencia de versión/CUDA ya se dio por agotada (HIST-ENV-005) — ver Sección 3.

## Riesgos y limitaciones científicas

- **El nuevo split no logra independencia biológica.** Solo corrige el mecanismo de leakage por augmentation-antes-de-split, y solo agrupa duplicados *exactos* (mismo SHA-256); duplicados no exactos (recortes distintos de la misma célula/campo) quedan sin resolver. Sin ID de paciente/frotis, sigue siendo posible que imágenes muy similares del mismo origen terminen en splits distintos por azar. Cualquier métrica resultante debe comunicarse con esta limitación, siempre.
- **Brecha de entorno Keras 2.10 → Keras 3.0.** No hay garantía de que la arquitectura se reproduzca sin ajustes de API; el shim de `L2` ya conocido en TF.js es una señal de que estas transiciones de versión no son triviales en este proyecto. Por eso EXP-REPRO se define como reproducción metodológica, no bit-exacta.
- **Sin estimación de cómputo confiable.** El histórico tardó ≈55,58h; el dispositivo real (CPU vs GPU) no está confirmado (solo es PROBABLE que fuera predominantemente CPU — `research.md`), y no hay base local para proyectar cuánto tardaría EXP-REPRO en hardware actual sin un benchmark corto previo.
- **Dependencia de infraestructura nueva (DVC + remoto).** `ml/README.md` ya exige esto antes de entrenar; implica una decisión de costo/proveedor que este plan no resuelve por sí solo (tarea 6).
- **La simulación de diferencial no valida un flujo clínico.** Mide solo la matemática de agregación sobre imágenes ya aisladas y correctamente etiquetadas; no dice nada sobre detección, selección de campo, tracking ni desempeño sobre un frotis real.
- **El umbral de aceptación sigue sin calibrar contra negativos fuera de dominio** (caras, fondos, otras tinciones) incluso después de la curva riesgo-cobertura propuesta, porque esa curva usa el mismo dominio de imágenes de células — calibrar contra falsos positivos "no-célula" requeriría un dataset negativo que no existe hoy.
- **Ninguna decisión de este plan reemplaza revisión hematológica profesional** para las taxonomías de reporte, agrupaciones clínicas o afirmaciones educativas sobre morfología.
