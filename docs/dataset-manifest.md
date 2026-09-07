# Manifiesto de originales (Fase 2) — inventario auditable

**Estado:** inventario construido y verificado de forma independiente. **El split propuesto NO está congelado** — pendiente de revisión y de resolver el conflicto de etiqueta antes de usarse para entrenar. Este documento no autoriza entrenamiento, DVC ni ningún cambio de modelo.

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

> **Conflicto de etiqueta (sha256 `5c7c2002…6ec68c7`):** `Labelled_2/eosinophil/EO_225902.jpg` y `Labelled_2/neutrophil/BNE_191112.jpg` son **bytes idénticos** (15.885 bytes, JPEG 360×363, mismo `SOF0`) pero están archivados bajo dos clases distintas del dataset público PBC: Eosinófilos y Neutrófilos. Esto no se resolvió automáticamente — no hay base en esta auditoría para decidir cuál etiqueta es correcta. Ambos registros quedan **sin `split_propuesto`** en el manifiesto hasta que se decida.

Los otros 14 grupos son pares dentro de una misma clase (Basófilos ×6 pares, Eosinófilos ×5 pares, Monocitos ×1 par, Linfocitos ×1 par), todos con clases consistentes entre sí — no representan un problema de etiquetado, solo contenido duplicado en el release público, y se tratan como una sola unidad indivisible para el split.

**Implicación práctica:** el dataset público PBC contiene al menos una imagen archivada simultáneamente (o accidentalmente) bajo dos categorías celulares distintas. Esto es evidencia externa al proyecto (del dataset público), no un error de este repositorio ni de HematoVision 2024.

## 3. Esquema y ubicación del manifiesto

- **Ubicación:** `ml/data/manifest_v1.csv` — **fuera de Git** (`.gitignore`), consistente con `ml/README.md` ("los datos de entrenamiento... no se suben a Git") mientras no exista DVC.
- **Tamaño:** 4.273.580 bytes, 30.224 filas + cabecera.
- **Columnas:** `path_original` (relativo a `D:\Datasets\dataset_hematologia\`), `fuente` (`Bodzas`/`PBC`), `clase_carpeta_origen` (nombre real de carpeta), `clase_final_9`, `sha256`, `tamano_bytes`, `split_propuesto` (vacío para las 2 filas del conflicto).
- **Script generador (versionado):** [`ml/scripts/build_manifest.py`](../ml/scripts/build_manifest.py) — reproducible, solo lectura, sin dependencias externas a la librería estándar de Python.

## 4. Propuesta de split (NO congelada)

**Unidad de asignación:** grupo de SHA-256 idéntico (no el archivo individual) — así los 14 grupos duplicados sin conflicto no pueden terminar repartidos entre splits distintos. **Verificado independientemente: 0 grupos cruzan splits.**

**Proporción propuesta:** 80/10/10 (train/val/test), estratificada por `clase_final_9`, con semilla fija `random.Random(20260907)`. Se propone 80/10/10 en vez del histórico 85/10/5 porque el augmentation ahora será solo online (no física), así que no hace falta reservar tanto material de train para compensar augmentation en disco; un val/test relativamente más grandes dan más estabilidad a la curva de rechazo (Sección 4 de `phase2-plan.md`) y al reporte final. **Esto es una propuesta, no una decisión — la proporción y la semilla pueden cambiarse antes de congelar.**

| Clase | Train | Val | Test | Sin asignar (conflicto) |
| --- | ---: | ---: | ---: | ---: |
| Basófilos | 1.793 | 224 | 224 | 0 |
| Eosinófilos | 3.306 | 413 | 414 | 1 |
| Eritroblastos | 1.649 | 206 | 206 | 0 |
| Linfoblastos | 2.046 | 256 | 255 | 0 |
| Linfocitos | 3.408 | 426 | 426 | 0 |
| Mieloblastos | 2.027 | 253 | 254 | 0 |
| Monocitos | 2.768 | 346 | 346 | 0 |
| Neutrófilos | 5.302 | 663 | 663 | 1 |
| Plaquetas | 1.878 | 235 | 235 | 0 |

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

## 6. Riesgos que impiden congelar el test todavía

- **El conflicto de etiqueta no está resuelto.** Congelar el test sin decidir qué hacer con esas dos filas dejaría un hueco de datos no documentado o un split inconsistente si un cargador asumiera que todas las filas tienen `split_propuesto`.
- **El split no logra independencia biológica.** Es una mejora real sobre 2024 (corrige el mecanismo de leakage por augmentation-antes-de-split y agrupa duplicados exactos), pero no hay ID de paciente/frotis/campo en ninguna copia local (`dataset-provenance.md`, "Situación D"). No debe comunicarse como split independiente a secas.
- **Duplicados no exactos no están cubiertos.** Solo se detectan duplicados con SHA-256 idéntico; recortes ligeramente distintos de la misma célula/campo (si existieran) no se detectan con este método y quedan como límite conocido, no resuelto.
- **La proporción 80/10/10 y la semilla son una propuesta**, no una decisión — deben confirmarse (o cambiarse) antes de congelar cualquier archivo de test.

## 7. Archivos modificados y estado de Git

- **Nuevo, versionado:** `ml/scripts/build_manifest.py` (código, reproducible).
- **Nuevo, versionado:** `docs/dataset-manifest.md` (este documento).
- **Modificado, versionado:** `.gitignore` (+`ml/data/`).
- **Nuevo, NO versionado (gitignored):** `ml/data/manifest_v1.csv` (4.273.580 bytes) — permanece solo en disco local hasta que se inicialice DVC (no autorizado todavía).
- Ningún dataset, notebook histórico, modelo ni código de producción fue tocado.

## 8. Decisiones que necesitas aprobar antes del siguiente paso

1. **Conflicto de etiqueta:** ¿cómo resolver `EO_225902.jpg`/`BNE_191112.jpg`? Opciones sin decidir aquí: excluir ambos registros del manifiesto con la razón documentada, investigar más en la fuente pública de PBC, o alguna otra resolución — no hay base técnica en esta auditoría para elegir una etiqueta sobre la otra.
2. **Proporción y semilla del split:** ¿80/10/10 con semilla `20260907` tal como se propone, o preferís otra proporción/semilla?
3. **Confirmación de que este manifiesto (una vez resuelto el punto 1) es la base aceptada** para congelar el test — es decir, pasar de "propuesta" a "congelado" (tarea 4 de `phase2-plan.md`), lo cual sigue sin autorizarse en esta ronda.
