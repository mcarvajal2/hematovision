# Historia y baseline histórico

Este documento es la fuente de verdad sobre el proyecto histórico. Distingue lo ocurrido de su lectura actual y del trabajo futuro.

## Línea de tiempo

- **CONFIRMADO — diciembre de 2023 a enero de 2024:** desarrollo histórico principal.
- **CONFIRMADO — enero de 2024:** notebook principal `Hematologia.ipynb`; modelo final `mejor_modelo.h5`; modelos anteriores `modelo_1.h5` y `modelo_1_balanced.h5`; exportación a TensorFlow.js. Los tres `.h5` comparten arquitectura idéntica; `modelo_1_balanced.h5` es un re-guardado congelado (sin estado de optimizador) byte a byte idéntico a `modelo_1.h5`, y `mejor_modelo.h5` es un estado de entrenamiento genuinamente posterior. Procedencia exacta del proceso que generó cada uno: PENDIENTE. Evidencia completa en [Investigaciones — HIST-MODELS-004](research.md#hist-models-004-reconstrucción-de-modelo_1h5-modelo_1_balancedh5-y-mejor_modeloh5).
- **CONFIRMADO — septiembre de 2026:** modernización/publicación del repositorio versionado `mcarvajal2/hematovision`.

El notebook en `ml/notebooks/Hematologia.ipynb` tiene el mismo SHA-256 que la copia histórica inspeccionada. Se conserva sin cambios como evidencia. Los artefactos históricos locales y el dataset no se versionan ni se modifican desde este repositorio.

## Entorno histórico conocido

**CONFIRMADO:** HP OMEN by HP Laptop 17-an0xx; Intel Core i7-7700HQ; 32 GB RAM; NVIDIA GeForce GTX 1050 con 4 GiB VRAM; proyecto y dataset almacenados en `D:`. El uso efectivo de la GPU en un entrenamiento sigue **PENDIENTE**.

La metadata preservada de `Hematologia.ipynb` declara un kernel con nombre visible `tf-cpu` y Python 3.11.5. Esto documenta la configuración grabada del notebook, no demuestra por sí solo el dispositivo o versiones efectivamente usados durante el entrenamiento histórico.

## Dataset histórico reconstruido

### Antes de augmentation

| Clase | Cantidad |
| --- | ---: |
| Basófilos | 2.241 |
| Eosinófilos | 4.134 |
| Eritroblastos | 2.061 |
| Linfoblastos | 2.557 |
| Linfocitos | 4.260 |
| Mieloblastos | 2.534 |
| Monocitos | 3.460 |
| Neutrófilos | 6.629 |
| Plaquetas | 2.348 |
| **Total** | **30.224** |

**CONFIRMADO:** las carpetas históricas conocidas son `Divided`, `Labelled`, `Labelled_2`, `Labelled_mix` y `Divided_Labelled_Mix`. No se copia el dataset al repositorio.

La procedencia de las dos fuentes ya fue identificada: `Labelled` corresponde al contenido de alta resolución publicado por Bodzas, Kodytek & Zidek (2023), y `Labelled_2` a `PBC_dataset_normal_DIB` de Acevedo et al. (2020). La trazabilidad disponible y las citas están en [Procedencia de datasets](dataset-provenance.md); los archivos locales no conservan IDs de paciente/frotis/campo para un split agrupado.

### Pipeline reconstruido

`fuentes originales → mezcla → 30.224 imágenes → augmentation físico guardado en disco → ~7.000/clase → reducción aleatoria → 5.950/clase → split aleatorio por imagen 85/10/5 → augmentation online adicional sobre train → entrenamiento`

El notebook muestra augmentation físico en `Labelled_mix`, reducción aleatoria a 5.950 por clase y copias a `Divided_Labelled_Mix`. Los tamaños finales observados son 53.550 imágenes: 45.513 train, 5.355 validation y 2.682 test.

## Entrenamiento final reconstruido

**CONFIRMADO en el notebook y sus salidas:** entrada 150×150×3; nueve clases; batch size 64; 712 batches por época; máximo 100 épocas; 62 ejecutadas; mejor época 50 por `val_loss`; tiempo medio aproximado 3.227 s por época (≈53,8 min/época; ≈55,58 h totales); accuracy histórica de test aproximada 98,92 %.

Esta métrica es histórica y **NO representa validación clínica** ni debe usarse como desempeño confiable fuera de ese pipeline.

## Limitación metodológica crítica

**CONFIRMADO:** el augmentation físico ocurrió antes del split. Imágenes aumentadas se guardaron junto a originales y luego se mezclaron antes de dividir train/validation/test por archivo.

- Riesgo de leakage del pipeline: **CONFIRMADO**.
- Leakage efectivo entre imágenes concretas de distintos splits: **PROBABLE**, no demostrado par a par.
- El split fue por archivo; no hay evidencia de split por paciente, frotis o lámina.
- `random.shuffle()` se usó sin seed documentada en esa etapa del notebook.
- Que el loop haya creado derivados de imágenes ya aumentadas es **HIPÓTESIS PLAUSIBLE**, no confirmada.

Toda comunicación de la accuracy histórica debe incluir estas limitaciones. La auditoría y preguntas abiertas viven en [Investigaciones](research.md).
