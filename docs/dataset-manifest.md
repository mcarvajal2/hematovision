# Manifiesto de originales (Fase 2) — inventario auditable

**Estado:** inventario construido y verificado de forma independiente (dos rondas). Miguel aprobó la cuarentena del grupo conflictivo, la proporción 80/10/10 y la semilla `20260907`, y aprobó el manifiesto como base de trabajo. **El test sigue SIN congelar** — esta ronda entrega la propuesta definitiva de split, no su congelamiento. Este documento no autoriza entrenamiento, DVC ni ningún cambio de modelo.

**Fuente de verdad relacionada:** [Procedencia de datasets](dataset-provenance.md) (de dónde vienen `Labelled`/`Labelled_2`, por qué se excluye `ig`) y [Plan de Fase 2](phase2-plan.md) (diseño completo, del que este documento ejecuta las tareas 1-4, sin congelar el test). No se duplica esa evidencia aquí, solo se referencia.

**Método:** script `ml/scripts/build_manifest.py` (solo lectura; sin TensorFlow/Keras/DVC), ejecutado sobre `D:\Datasets\dataset_hematologia\Labelled` y `Labelled_2` (excluyendo `ig`, como ya documentaba `dataset-provenance.md`). Ningún archivo original fue movido, modificado, eliminado ni aumentado. Verificado de forma independiente por un segundo agente: relectura completa de la lógica, reagrupación completa del CSV por hash, y recálculo de SHA-256 sobre una muestra estratificada de 250 archivos (0 discrepancias) más los dos archivos del conflicto de etiqueta (ver abajo), byte a byte.

## 1. Conteos reales por fuente y clase

**CONFIRMADO** — coinciden exactamente con `dataset-provenance.md`, sin discrepancias:

| Clase final | Total | Aporte Bodzas (`Labelled`) | Aporte PBC (`Labelled_2`) |
| --- | ---: | ---: | ---: |
| Basófilos | 2.241 | 1.023 (Basophile) | 1.218 (basophil) |
| Eosinófilos | 4.134 | 1.017 (Eosinophile) | 3.117 (eosinophil) |
| Eritroblastos | 2.061 | 510 (Normoblast) | 1.551 (erythroblast) |
| Linfoblastos | 2.557 | 2.557 (Lymphoblast) | — |
| Linfocitos | 4.260 | 3.046 (Lymphocyte) | 1.214 (lymphocyte) |
| Mieloblastos | 2.534 | 2.534 (Myeloblast) | — |
| Monocitos | 3.460 | 2.040 (Monocyte) | 1.420 (monocyte) |
| Neutrófilos | 6.629 | 99+3.201 (Band+Segment) | 3.329 (neutrophil) |
| Plaquetas | 2.348 | — | 2.348 (platelet) |
| **Total** | **30.224** | **16.027** | **14.197** |

`Labelled_2/ig` (2.895 archivos) queda fuera del manifiesto por diseño — no se recorrió esa carpeta, replicando la exclusión ya documentada en `dataset-provenance.md`. Su motivo histórico sigue `PENDIENTE-evidencia-agotada` (HIST-ENV-005); este manifiesto no reabre esa pregunta.

## 2. Duplicados exactos y conflictos

**CONFIRMADO, verificado dos veces de forma independiente:** 15 grupos de archivos con SHA-256 idéntico (30 archivos), de los cuales **14 son duplicados sin conflicto** (incluidos vía prefijos numéricos consecutivos, todos dentro de la misma clase) y **1 es un conflicto de etiqueta**:

> **Conflicto de etiqueta (sha256 `5c7c2002…6ec68c7`):** `Labelled_2/eosinophil/EO_225902.jpg` y `Labelled_2/neutrophil/BNE_191112.jpg` son **bytes idénticos** (15.885 bytes, JPEG 360×363, mismo `SOF0`) pero están archivados bajo dos clases distintas del dataset público PBC: Eosinófilos y Neutrófilos. Esto no se resolvió automáticamente.

Los otros 14 grupos son pares dentro de una misma clase (Basófilos ×6 pares, Eosinófilos ×5 pares, Monocitos ×1 par, Linfocitos ×1 par), todos con clases consistentes entre sí — no representan un problema de etiquetado, solo contenido duplicado en el release público, y se tratan como una sola unidad indivisible para el split.

**Implicación práctica:** el dataset público PBC contiene al menos una imagen archivada simultáneamente (o accidentalmente) bajo dos categorías celulares distintas. Esto es evidencia externa al proyecto (del dataset público), no un error de este repositorio ni de HematoVision 2024.

## 2.1 Registro de cuarentena

**Decisión:** [DEC-002](decisions.md#dec-002-cuarentena-del-grupo-de-hash-conflictivo-en-lugar-de-elegir-etiqueta) — Miguel decidió poner el grupo en cuarentena en vez de elegir una etiqueta automáticamente.

| Campo | Valor |
| --- | --- |
| SHA-256 del grupo | `5c7c2002b0fec1f34093f672961aa13e3880fb5db0075e6a211d91f4e6ec68c7` |
| Archivos | `Labelled_2/eosinophil/EO_225902.jpg` (PBC, etiquetado Eosinófilos); `Labelled_2/neutrophil/BNE_191112.jpg` (PBC, etiquetado Neutrófilos) |
| Motivo | Bytes idénticos entre dos archivos del dataset público PBC archivados bajo clases distintas; ninguna evidencia local permite determinar cuál etiqueta es correcta |
| Decisión | Excluidos de train/validation/test ("cuarentena"). No se eliminaron ni modificaron los originales. No se eligió una etiqueta automáticamente |
| Estado en el manifiesto | `split_propuesto = 'cuarentena'` en `manifest_v2.csv`, para ambas filas, verificado de forma independiente (dos veces) |
| Fecha | 2026-09-07 |
| Reversibilidad | Reversible: si en el futuro se resuelve la etiqueta correcta (p. ej. contactando a los autores de PBC o revisión experta), se puede reincorporar el grupo a una nueva versión del manifiesto |

## 3. Esquema y ubicación del manifiesto

- **`ml/data/manifest_v1.csv`** — inventario crudo (paths/hashes/clases/tamaños, sin split definitivo). Generado por [`ml/scripts/build_manifest.py`](../ml/scripts/build_manifest.py).
- **`ml/data/manifest_v2.csv`** — **propuesta definitiva de split** (esta ronda), con la cuarentena aplicada y el split 80/10/10 aprobado. Generado por [`ml/scripts/build_split.py`](../ml/scripts/build_split.py) a partir de `manifest_v1.csv` (no vuelve a leer ni hashear ninguna imagen). Mismas columnas que v1; `split_propuesto` ahora toma valores `train`/`val`/`test`/`cuarentena` (nunca vacío).
- Ambos **fuera de Git** (`ml/data/` en `.gitignore`), consistente con `ml/README.md` mientras no exista DVC. Los scripts que los generan sí están versionados.
- **Identificador reproducible de esta propuesta:** SHA-256 de `manifest_v2.csv` = `010a820d46cb2bf43c4d922405da61003087215dc8315ceb284d08624acf31e1` (4.273.600 bytes, 30.224 filas). Verificado de forma independiente de dos maneras: (a) recalculando el hash del archivo existente, (b) re-ejecutando `build_split.py` en un **proceso Python nuevo** (no solo una segunda corrida dentro del mismo script) y confirmando el mismo SHA-256 exacto.

## 4. Propuesta de split definitiva (aprobada por Miguel, NO congelada)

**Unidad de asignación:** grupo de SHA-256 idéntico (no el archivo individual) — así los 14 grupos duplicados sin conflicto no pueden terminar repartidos entre splits distintos, y el grupo en cuarentena no puede aparecer en ninguno. **Verificado independientemente dos veces: 0 grupos cruzan splits.**

**Proporción y semilla aprobadas:** 80/10/10 (train/val/test), estratificada por `clase_final_9` a nivel de grupo de hash, `random.Random(20260907)`. Aprobado por Miguel como configuración inicial.

| Clase | Train | Val | Test | Cuarentena | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Basófilos | 1.793 | 224 | 224 | 0 | 2.241 |
| Eosinófilos | 3.306 | 413 | 414 | 1 | 4.134 |
| Eritroblastos | 1.649 | 206 | 206 | 0 | 2.061 |
| Linfoblastos | 2.046 | 256 | 255 | 0 | 2.557 |
| Linfocitos | 3.408 | 426 | 426 | 0 | 4.260 |
| Mieloblastos | 2.027 | 253 | 254 | 0 | 2.534 |
| Monocitos | 2.768 | 346 | 346 | 0 | 3.460 |
| Neutrófilos | 5.302 | 663 | 663 | 1 | 6.629 |
| Plaquetas | 1.878 | 235 | 235 | 0 | 2.348 |
| **Total** | **24.177** | **3.022** | **3.023** | **2** | **30.224** |

Por fuente: Bodzas — train 12.783, val 1.602, test 1.642, cuarentena 0 (total 16.027, sin cuarentena porque el conflicto es exclusivamente PBC). PBC — train 11.394, val 1.420, test 1.381, cuarentena 2 (total 14.197).

**Reproducibilidad verificada dos veces de forma independiente:** (1) dos corridas de la función de asignación dentro del script de Terra, resultado idéntico fila por fila; (2) re-ejecución completa de Luna en un proceso Python nuevo, mismo SHA-256 exacto del CSV resultante. **Sigue sin congelarse** — es la propuesta definitiva, pendiente de tu revisión final antes de fijarla como test inmóvil.

## 5. Validaciones ejecutadas

1. Conteo total y por clase contra `dataset-provenance.md`: **0 discrepancias** (construcción y verificación independiente, dos veces).
2. Conteo por fuente/carpeta de origen contra la misma tabla: **0 discrepancias**.
3. `ig` no aparece como `clase_carpeta_origen` en ninguna fila (búsqueda exacta, no substring): **confirmado independientemente**.
4. 30.224 `path_original` únicos; 0 archivos ausentes en disco; 0 rutas fuera de `Labelled`/`Labelled_2`.
5. Recálculo independiente de SHA-256 sobre una muestra estratificada de 250 archivos (130 Bodzas / 120 PBC, las 9 clases representadas): **250/250 coincidencias**.
6. Reagrupación completa e independiente del CSV por `sha256`: **15 grupos duplicados, 1 conflicto — coincide exactamente** con el resultado original.
7. Verificación byte a byte independiente del conflicto de etiqueta (tamaño, SHA-256, dimensiones JPEG): **confirmado, bytes idénticos**.
8. Ningún grupo de hash duplicado quedó repartido entre dos splits distintos (revisión completa, no muestral).
9. 0 errores de lectura/hash (ningún archivo protegido, corrupto o inaccesible).
10. Cuarentena: exactamente 2 filas con `split_propuesto='cuarentena'`, confirmado de forma independiente dos veces, coincidiendo con el grupo conflictivo documentado.
11. Reproducibilidad de `manifest_v2.csv`: dos corridas internas idénticas fila por fila (Terra) + una re-ejecución en proceso Python nuevo con SHA-256 de archivo idéntico (Luna) — reproducibilidad confirmada más allá de la duda de "quizás solo funciona una vez".
12. 0 filas con `split_propuesto` vacío o fuera de `{train, val, test, cuarentena}`.
13. Ningún grupo de hash (incluida la cuarentena) aparece repartido entre dos valores distintos de `split_propuesto` — revisión completa de las 30.224 filas, no muestral, confirmada dos veces.

## 6. Riesgos que impiden congelar el test todavía

- **El split no logra independencia biológica.** Es una mejora real sobre 2024 (corrige el mecanismo de leakage por augmentation-antes-de-split y agrupa duplicados exactos), pero no hay ID de paciente/frotis/campo en ninguna copia local (`dataset-provenance.md`, "Situación D"). No debe comunicarse como split independiente a secas.
- **Duplicados no exactos no están cubiertos.** Solo se detectan duplicados con SHA-256 idéntico; recortes ligeramente distintos de la misma célula/campo (si existieran) no se detectan con este método y quedan como límite conocido, no resuelto.
- **El conflicto de etiqueta permanece sin resolver a nivel de anotación** (solo se puso en cuarentena, no se investigó su causa en la fuente pública) — no bloquea congelar el resto del split, pero sí bloquea usar esas dos imágenes específicas para cualquier propósito hasta una decisión de anotación.
- **La congelación del test sigue pendiente de tu revisión final** de esta propuesta (conteos, proporción, semilla, identificador SHA-256) — no se congela automáticamente por haber sido verificada.

## 7. Archivos modificados y estado de Git

- **Nuevo, versionado:** `ml/scripts/build_manifest.py` (construye `manifest_v1.csv` desde las imágenes).
- **Nuevo, versionado:** `ml/scripts/build_split.py` (construye `manifest_v2.csv`, la propuesta definitiva, desde `manifest_v1.csv` — no vuelve a tocar imágenes).
- **Nuevo/actualizado, versionado:** `docs/dataset-manifest.md` (este documento).
- **Nuevo, versionado:** [DEC-002](decisions.md#dec-002-cuarentena-del-grupo-de-hash-conflictivo-en-lugar-de-elegir-etiqueta) en `docs/decisions.md`.
- **Modificado, versionado:** `.gitignore` (+`ml/data/`, ya cubre ambos manifiestos).
- **Nuevo, NO versionado (gitignored):** `ml/data/manifest_v1.csv` (4.273.580 bytes) y `ml/data/manifest_v2.csv` (4.273.600 bytes) — permanecen solo en disco local hasta que se inicialice DVC (no autorizado todavía).
- Ningún dataset, notebook histórico, modelo ni código de producción fue tocado. Ninguna imagen original fue movida, modificada o eliminada.

## 8. Confirmación explícita

**El test NO está congelado.** `manifest_v2.csv` es la propuesta definitiva de split (cuarentena aplicada, proporción y semilla aprobadas, reproducibilidad verificada dos veces de forma independiente), pero congelarla como test inmóvil para entrenamiento/evaluación es un paso posterior, explícitamente no autorizado en esta ronda.

## 9. Decisiones que necesitas aprobar antes de congelar

1. **Confirmar esta propuesta definitiva** (conteos, proporción 80/10/10, semilla `20260907`, identificador SHA-256 `010a820d…acf31e1`) como la que se congelará, o pedir cambios.
2. **Autorizar el congelamiento del test** — es decir, pasar de "propuesta verificada" a "congelado" (tarea 4 de `phase2-plan.md`), incluyendo decidir cómo se registra/publica el hash del listado de test (¿en `docs/experiments.md`, en un archivo `.dvc` cuando exista, o ambos?).
3. Si en algún momento aparece evidencia que permita resolver la etiqueta del grupo en cuarentena (Sección 2.1), decidir si se reincorpora a una `manifest_v3.csv` o queda cuarentenado indefinidamente.
