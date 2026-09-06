# Procedencia y trazabilidad de los datasets históricos

**Investigación:** `HIST-DATA-003` en [Investigaciones](research.md).
**Método:** inspección local de árbol, nombres, conteos, una muestra pequeña de metadata/imagen y hashes representativos; contraste con publicaciones y repositorios públicos. No se modificó ni procesó ningún dataset.

## Dictamen breve

El corpus histórico no era una fuente única. La evidencia permite identificar dos datasets públicos diferentes:

| Carpeta local | Fuente probable/original | Certeza | Evidencia combinada |
| --- | --- | --- | --- |
| `Labelled` y probablemente `Divided` | Bodzas, Kodytek & Zidek (2023), *A high-resolution large-scale dataset of pathological and normal white blood cells* | **CONFIRMADO** como origen del contenido | 16.027 imágenes, nueve clases y conteos idénticos; BMP 1.200×1.200, nombres numéricos y clases coinciden con la descripción primaria. |
| `Labelled_2` | Acevedo et al. (2020), `PBC_dataset_normal_DIB` | **CONFIRMADO** | 17.092 imágenes, ocho grupos, mismos conteos exactos, nombres de carpetas/prefijos, JPG 360×363 y metadata de codificación compatibles. |
| `Labelled_mix` | Mezcla histórica de las dos anteriores, sin `ig` | **CONFIRMADO** para la composición inicial | `16.027 + (17.092 − 2.895) = 30.224`, igual al output histórico; las sumas por clase cuadran exactamente y hashes muestrales coinciden. |
| `Divided_Labelled_Mix` | Split histórico de `Labelled_mix` | **CONFIRMADO** | Código del notebook copia archivos 85/10/5; conteos actuales 45.513/5.355/2.682. |

Esta identificación no convierte el modelo histórico en validado: ambos orígenes fueron mezclados y divididos por archivo después de augmentation físico. Véase [Historia](project-history.md) y [análisis del notebook](notebook-analysis.md).

## Evidencia local

### `Labelled`: dataset de alta resolución Bodzas et al.

`Labelled` contiene 16.027 PNG RGB de 1.200×1.200 en nueve clases: Basophile 1.023, Eosinophile 1.017, Lymphoblast 2.557, Lymphocyte 3.046, Monocyte 2.040, Myeloblast 2.534, Neutrophile Band 99, Neutrophile Segment 3.201 y Normoblast 510. Los archivos son números incrementales (`0.png`, `1.png`, …).

El artículo de Bodzas et al. describe exactamente 16.027 crops individuales BMP 24-bit de 1.200×1.200, en las mismas nueve clases y con nombres incrementales, extraídos de imágenes de campo de 5.472×3.648. Por convergencia de tamaño, formato de origen, taxonomía y los nueve conteos exactos, la correspondencia es **CONFIRMADA**. La publicación primaria documenta también el instrumento, preparación y contexto clínico. [Bodzas et al., 2023](https://www.nature.com/articles/s41597-023-02378-7)

`Divided` contiene el mismo conjunto de nombres base como BMP, repartido en `train`/`val`/`test` con 80/10/10 por clase: sus nueve conjuntos de nombres coinciden exactamente con los de `Labelled` al retirar extensión. Las dimensiones y píxeles muestrales de pares BMP/PNG coinciden. Esto confirma una relación 1:1 de identidad de muestra entre ambos árboles, pero **no confirma la dirección exacta de creación**.

El script histórico `utils/split_data.py` define `splitfolders.ratio(..., seed=123, ratio=(0.8, 0.1, 0.1))`, consistente con `Divided`, aunque no contiene rutas ni un registro de ejecución que pruebe que fue el comando concreto utilizado. `utils/convert_images.py` convierte BMP a PNG, pero apunta a un directorio ausente llamado `Limited_Labelled`, no a estas rutas. Además, el timestamp de `Labelled` antecede al de `Divided`. Por ello:

- **CONFIRMADO:** `Divided` y `Labelled` representan las mismas muestras por nombre/clase; uno conserva BMP y el otro PNG.
- **MUY PROBABLE:** `Labelled` es una conversión PNG del contenido público de Bodzas y `Divided` es un split 80/10/10 de ese contenido BMP.
- **PENDIENTE:** demostrar si `Labelled` fue convertido directamente desde `Divided`, o si ambos se crearon en paralelo desde un árbol predecesor ya no conservado.

### `Labelled_2`: PBC_dataset_normal_DIB de Acevedo et al.

`Labelled_2` tiene exactamente 17.092 JPG RGB organizados como `basophil`, `eosinophil`, `erythroblast`, `ig`, `lymphocyte`, `monocyte`, `neutrophil` y `platelet`. Sus conteos son 1.218, 3.117, 1.551, 2.895, 1.214, 1.420, 3.329 y 2.348, respectivamente. El artículo de datos de Acevedo et al. reporta exactamente esos ocho grupos, 17.092 imágenes individuales JPG de 360×363, anotadas por patólogos, obtenidas con CellaVision DM96 en el Hospital Clínic de Barcelona. [Acevedo et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32346559/), [artículo abierto](https://upcommons.upc.edu/server/api/core/bitstreams/9faee873-304c-42e7-9878-9758db3357a4/content)

Los prefijos locales refuerzan la identificación: `BA_`, `EO_`, `ERB_`, `LY_`, `MO_`, `BNE_`, `SNE_` y `PLATELET_`; los JPG muestrales miden 360×363. La clase `ig` incluye prefijos `MY` (1.137), `MMY` (1.015), `PMY` (592) e `IG` (151). La publicación define el grupo de immature granulocytes como promyelocytes, myelocytes y metamyelocytes; por tanto, que **la carpeta `ig` representa immature granulocytes está CONFIRMADO**. La expansión individual de cada abreviatura de archivo es **INFERIDA**, aunque es compatible con esa definición; el subgrupo `IG_` no está explicado por la evidencia encontrada.

La evidencia externa también establece que estas muestras eran de individuos sin infección, enfermedad hematológica/oncológica ni tratamiento farmacológico al recolectar la sangre. No se encontró número de sujetos ni IDs por individuo en el release público; fuentes secundarias lo reportan como `N/A` a ese nivel. [Acevedo et al., 2020](https://pubmed.ncbi.nlm.nih.gov/32346559/)

### `Labelled_mix`: mezcla y normalización de etiquetas

El notebook observó 30.224 archivos antes de augmentation. Esa cifra es la suma exacta de `Labelled` (16.027) y `Labelled_2` sin `ig` (17.092 − 2.895 = 14.197).

| Clase final histórica | Aporte `Labelled` / Bodzas | Aporte `Labelled_2` / PBC | Total inicial |
| --- | ---: | ---: | ---: |
| Basófilos | 1.023 | 1.218 | 2.241 |
| Eosinófilos | 1.017 | 3.117 | 4.134 |
| Eritroblastos | Normoblast 510 | 1.551 | 2.061 |
| Linfoblastos | 2.557 | — | 2.557 |
| Linfocitos | 3.046 | 1.214 | 4.260 |
| Mieloblastos | 2.534 | — | 2.534 |
| Monocitos | 2.040 | 1.420 | 3.460 |
| Neutrófilos | Band 99 + Segment 3.201 | 3.329 | 6.629 |
| Plaquetas | — | 2.348 | 2.348 |
| **Total** | **16.027** | **14.197** | **30.224** |

Esta tabla no es una nueva fuente para cantidades históricas; explica la tabla ya consolidada en [Historia](project-history.md#antes-de-augmentation). Muestras de ambos árboles aparecen en `Labelled_mix` con el mismo SHA-256. Las colisiones de nombres numéricos al unificar `Neutrophile Band` y `Neutrophile Segment` dejan nombres como `0.png` y `0 (2).png`; por ello, los nombres de `Labelled_mix` no son un manifiesto limpio de origen.

**CONFIRMADO:** `ig` fue excluida antes de la mezcla, porque la diferencia aritmética es exacta. **PENDIENTE:** la razón histórica de exclusión; no aparece en notebook, scripts ni archivos auxiliares.

Después, el notebook escribió augmentation físico en esa misma carpeta y redujo cada clase a 5.950. Por ello, el árbol actual de `Labelled_mix` contiene originales retenidos, JPG/Png de ambas fuentes y derivados `img_...`; ya no es una representación preservada de la mezcla inicial.

### `Divided_Labelled_Mix`

El notebook copia, sin recodificar, archivos de `Labelled_mix` a `train` (85 %), `val` (10 %) y `test` (5 %) después del augmentation y de la reducción. La estructura y los conteos actuales son compatibles exactamente con ese código. Los directorios son el resultado final de entrenamiento histórico, no una fuente primaria.

## Metadata e inspección visual

La inspección no destructiva de una muestra por clase encontró:

- `Labelled`: PNG RGB 24-bit, 1.200×1.200; solo propiedades PNG de resolución, sin EXIF, comentario, software o ID clínico recuperable.
- `Labelled_2`: JPG RGB, normalmente 360×363 en la muestra; la muestra `ig` inspeccionada fue 360×360. El único texto recuperable fue una marca del codificador `Intel(R) JPEG Library, version [1.51.13.45]`; no contiene paciente, lámina, fecha de adquisición ni campo microscópico.

La comparación visual de muestras de basófilo y neutrófilo muestra diferencias claras de tamaño de crop, encuadre, fondo y apariencia cromática. **INFERIDO:** son compatibles con dominios de adquisición distintos. **CONFIRMADO externamente:** proceden de instituciones e instrumentos diferentes (Ostrava/Olympus-Basler frente a Barcelona/CellaVision), con protocolos de tinción descritos en sus publicaciones. La observación visual no prueba por sí misma microscopio, tinción ni calidad clínica.

## Trazabilidad biológica y posibilidad de split

La fuente Bodzas sí tenía una unidad superior durante adquisición: 12.986 campos microscópicos de 81 frotis de 78 pacientes anonimizados, recolectados entre 2020–2022; los crops públicos fueron aplanados a carpetas por clase y nombre incremental. El artículo no proporciona en el release local una tabla que relacione número de archivo con paciente, frotis, campo o imagen cruda. [Bodzas et al., 2023](https://www.nature.com/articles/s41597-023-02378-7)

PBC/Acevedo declara imágenes individuales de sujetos sanos, pero el release local tampoco contiene identificadores de sujeto, lámina, frotis o campo. Sus prefijos nombran categorías celulares, no una gramática demostrada de agrupación biológica. No hay README, CSV, JSON, XML, licencia local, URL ni manifiesto auxiliar en `dataset_hematologia`.

**Clasificación para los artefactos preservados: D — solo split por archivo disponible.** Se conoce que Bodzas tuvo pacientes/frotis, pero la correspondencia fue removida o no llegó a la copia local; no puede reconstruirse honestamente desde los nombres incrementales. No se encontró evidencia de que el número posterior al prefijo PBC codifique un paciente, lámina o campo. Recuperar un split A/B/C requeriría manifiestos externos no presentes, una versión del dataset que conserve IDs o coordinación con autores; no debe inferirse mediante agrupamiento visual.

## Implicación metodológica y evaluación entre dominios

Los dos orígenes son dominios distintos y el historial los mezcló. Una futura evaluación separada por fuente podría ser más informativa que un split aleatorio mezclado, pero no resuelve por sí sola la falta de grupo paciente/frotis dentro de cada origen.

Existe una intersección razonable de cinco etiquetas para una futura pregunta de generalización externa: basófilo, eosinófilo, linfocito, monocito y neutrófilo (en Bodzas habría que unificar Band+Segment; en PBC ya existe `neutrophil`). Las otras clases no son compatibles uno-a-uno: `lymphoblast` y `myeloblast` solo están en Bodzas; plaqueta solo en PBC; y eritroblasto/normoblast requiere una decisión semántica explícita. Por tanto:

- **POSIBLE:** experimento futuro source-separated de cinco clases, entrenar en un origen y evaluar en el otro, con resolución/label mapping predefinidos y sin mezclar familias.
- **NO DEMOSTRADO AÚN:** que las etiquetas tengan equivalencia clínica suficiente para una comparación definitiva, ni que las particiones internas puedan ser por paciente/frotis.
- **Valor potencial:** medir cambio de dominio por institución, instrumento, preparación y crop, no reclamar rendimiento clínico.

## Fuentes externas

- Bodzas, A., Kodytek, P. & Zidek, J. (2023). *A high-resolution large-scale dataset of pathological and normal white blood cells*. Scientific Data 10, 466. [Artículo y datos metodológicos](https://www.nature.com/articles/s41597-023-02378-7). Licencia CC BY 4.0.
- Acevedo, A. et al. (2020). *A dataset of microscopic peripheral blood cell images for development of automatic recognition systems*. Data in Brief 30, 105474. [PubMed](https://pubmed.ncbi.nlm.nih.gov/32346559/), [artículo abierto](https://upcommons.upc.edu/server/api/core/bitstreams/9faee873-304c-42e7-9878-9758db3357a4/content). Licencia CC BY 4.0.

Estas fuentes externas sustentan la identificación y el contexto de captura; los hechos sobre las copias locales provienen de la inspección descrita arriba.
