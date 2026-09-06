# Comprensión técnica del notebook histórico

**Objeto analizado:** `ml/notebooks/Hematologia.ipynb`
**Método:** lectura estática de celdas, metadatos y outputs guardados; no se ejecutó ni modificó el notebook.
**Alcance:** explicar qué hace el artefacto conservado. Para la historia, cantidades y limitación de leakage, la fuente de verdad sigue siendo [Historia y baseline histórico](project-history.md).

## Mapa conceptual

| Etapa | Celdas | Qué evidencia aporta |
| --- | ---: | --- |
| Entorno e imports | 0–4 | Proyecto, librerías y reinicio de sesión Keras. |
| Inspección del dataset ya mezclado | 5–8 | `Labelled_mix`, una muestra por clase, conteos y gráfico de desbalance. |
| Balanceo físico en disco | 10–11 | Augmentation hasta ~7.000 por clase y reducción aleatoria a 5.950. |
| Split por archivo | 12 | Copias 85/10/5 hacia `Divided_Labelled_Mix`. |
| Entrada y augmentation online | 13–15 | Generadores, normalización, augmentations y etiquetas one-hot. |
| CNN, compilación y callbacks | 17–20 | Arquitectura, función de pérdida, optimizador y entrenamiento. |
| Seguimiento y evaluación | 21–32 | Curvas, test, métricas agregadas, informe, matriz de confusión y errores. |

## Lo que el notebook no documenta

**CONFIRMADO:** no hay celdas que creen `Labelled`, `Labelled_2` o `Labelled_mix` a partir de fuentes originales; tampoco hay conversión de formatos, unificación semántica de clases, creación de `Divided` ni exportación TensorFlow.js. `mejor_modelo.h5` se guarda indirectamente mediante `ModelCheckpoint`, pero no existe un `model.save()` explícito. Por tanto, las procedencias de esas carpetas, los modelos previos y la exportación siguen **PENDIENTES**; no deben inferirse a partir de este notebook.

## Etapas de datos

### 1. Entorno e intención inicial

**Qué hizo y para qué servía.** El título declara un clasificador de células sanguíneas en frotis. Importó utilidades de archivos, visualización, NumPy/Pandas, TensorFlow/Keras y scikit-learn; después usa `K.clear_session()` antes de datos y antes de modelar. Esto libera el grafo/estado global de Keras de ejecuciones anteriores, algo útil en un notebook interactivo.

**Cómo funcionaba.** `ImageDataGenerator` construye lotes de imágenes transformadas; `Sequential` encadena capas; Keras entrena mediante un bucle de gradientes ya implementado. Se importaron varias APIs que no terminan usadas (`Path`, `sns`, `layers`, `Rescaling`, `Conv2D`, `MaxPooling2D`, `Flatten`, `Dense`, `Dropout`, `optimizers`, `visualkeras`), señal normal de exploración, no de una etapa ejecutada.

**Razonable en 2024.** Usar Keras y herramientas de visualización fue una elección accesible y apropiada para un proyecto educativo. Reiniciar sesión evitaba acumulación de modelos en memoria.

**Hoy.** Como mejora de código/reproducibilidad se reducirían imports, se separaría configuración de lógica y se fijaría un entorno bloqueado. La metadata del notebook declara kernel `tf-cpu` y Python 3.11.5; eso **CONFIRMA la configuración guardada**, no prueba por sí solo el hardware de la ejecución histórica.

### 2. Exploración, clases y desbalance

**Qué hizo.** Definió `total_dir` como `D:/Datasets/dataset_hematologia/Labelled_mix`, mostró la primera imagen de cada subcarpeta, contó archivos y generó un gráfico circular. Los outputs guardados muestran 30.224 archivos iniciales y nueve carpetas/clases. La tabla detallada ya está en [Historia](project-history.md#antes-de-augmentation).

**Para qué y cómo.** Ver ejemplos permite detectar rápidamente carpetas erróneas, formatos inesperados o etiquetas obvias incorrectas. Contar archivos mide el desbalance: si una clase tiene muchas más muestras, una optimización de accuracy puede favorecerla. Las clases se deducen de nombres de directorio; `flow_from_directory` las ordenará alfabéticamente y producirá índices 0–8.

**Razonable.** Inspección visual, conteo y un gráfico son un buen primer control de calidad. El conjunto final conservó nombres consistentes y las salidas confirman nueve clases.

**Hoy.** Se añadirían validaciones programáticas (archivo legible, dimensiones, duplicados, distribución, procedencia y metadatos), una muestra estratificada reproducible y una revisión experta de etiquetas. Es una mejora científica/metodológica; el notebook no permite afirmar que esas verificaciones ocurrieron.

### 3. Significado observable de las carpetas

**CONFIRMADO por el código:** `Labelled_mix` es el directorio de entrada de este notebook y después el lugar donde se escriben derivados físicos. `Divided_Labelled_Mix` es la salida de su split, con `train`, `val` y `test`. El nombre `Divided` no se usa en el notebook; `Labelled` y `Labelled_2` tampoco.

**INFERIDO con cautela:** los nombres sugieren que `Labelled_mix` era una mezcla previa de fuentes etiquetadas. No sabemos qué transformaciones previas se hicieron ni si hubo duplicados entre fuentes. La cadena conceptual demostrable es:

`fuentes no documentadas en este notebook → Labelled_mix (30.224) → augmentation físico → reducción a 5.950 × 9 = 53.550 → copias aleatorias 85/10/5 a Divided_Labelled_Mix → generadores → CNN`

**Hoy.** La mejora de reproducibilidad es registrar manifiestos, hashes, versiones y transformaciones entre cada flecha, sin depender de nombres de carpetas locales.

### 4. Augmentation físico y balanceo en disco

**Qué hizo.** La celda 10 creó un `ImageDataGenerator` con rotación ±20°, desplazamientos horizontal/vertical de hasta 20 %, shear 0,2, zoom 0,2, flips horizontal/vertical y relleno `nearest`. Para cada clase generó un PNG por iteración con `save_to_dir` hasta que el conteo corriente alcanzara 7.000. La celda 11 mezcló nombres con `random.shuffle()` y eliminó archivos hasta `max_images = 5950` (el comentario dice 5.900, pero el código ejecutado define 5.950).

**Para qué servía.** Intentaba compensar la escasez relativa de clases y enseñar al modelo variaciones geométricas de una célula que idealmente no cambian su etiqueta. La reducción posterior igualó las clases a 5.950 y produjo un conjunto balanceado de 53.550 imágenes.

**Cómo funcionaba.** `datagen.flow(x, batch_size=1)` produce variantes aleatorias de la imagen `x`; el primer lote se guarda como PNG y el bucle se corta. Al recalcular `os.listdir()` dentro de `range`, la cantidad de iteraciones se fija al entrar en cada clase, pero los archivos de origen se indexan sobre un directorio que va creciendo. Por ello, que algunos originales de `img...` puedan reutilizarse como origen es una **HIPÓTESIS PLAUSIBLE**, no una relación demostrada imagen a imagen.

**Qué era razonable.** Augmentation geométrico y balancear la exposición de clases eran decisiones comunes y didácticas en 2024. Guardar variantes facilitaba inspeccionarlas y reutilizarlas sin regeneración.

**Qué mejoraríamos hoy.** Como mejora metodológica, se dividiría antes de toda transformación derivada y se aplicaría augmentation solo al train; como rendimiento/almacenamiento, se generaría online o bajo demanda. Antes habría que validar si flips verticales, shear y desplazamientos preservan la plausibilidad biológica y óptica de cada clase: eso es una pregunta científica, no resuelta por el notebook.

### 5. Split train/validation/test y leakage

**Qué hizo.** La celda 12 listó cada clase ya balanceada, aplicó `random.shuffle(images)` sin fijar semilla, calculó `int(0.85*n)`, `int(0.10*n)` y el resto, y copió los archivos a `Divided_Labelled_Mix/train`, `val` y `test`. Con 5.950 por clase, produjo 5.057 train, 595 validation y 298 test por clase; los totales guardados son 45.513, 5.355 y 2.682.

**Qué intentaba resolver y por qué parecía razonable.** Separar 85/10/5 mantiene datos para aprender, ajustar decisiones durante entrenamiento y medir al final. Dado que cada archivo es una imagen distinta, mezclar los nombres y repartirlos parece intuitivamente una partición aleatoria justa; además preserva el mismo número de muestras por clase.

**Por qué el contexto cambia la conclusión.** La unidad de split fue el archivo, no el origen biológico. Si una imagen original `A` y un derivado aumentado `A'` coexisten en `Labelled_mix`, el shuffle puede enviar `A` a train y `A'` a test. Son archivos distintos pero estadísticamente muy dependientes: comparten contenido, textura, tinción, fondo y morfología; solo cambia una transformación. Matemáticamente, el test deja de aproximar muestras independientes de la población objetivo y se parece parcialmente a datos ya vistos bajo otra vista. Un clasificador puede reconocer señales específicas del origen en vez de aprender características que generalicen a nuevas láminas/pacientes; por eso su métrica puede inflarse.

**Nivel de certeza.** El riesgo estructural de leakage es **CONFIRMADO** por el orden de operaciones. Que un par concreto original/derivado haya cruzado splits es **PROBABLE**, pero no está verificado completamente: faltan manifiestos y una auditoría par a par. Tampoco hay evidencia de separación por paciente, frotis o lámina.

**Qué haríamos hoy.** Definir primero la unidad independiente más fuerte disponible (idealmente paciente; si no, lámina/frotis), asignarla de manera reproducible a un único split y recién entonces derivar o aumentar solo train. La evaluación usaría validation/test sin augmentation geométrico y un test inmóvil. Esto es una mejora metodológica futura, no una modificación propuesta al artefacto histórico.

### 6. Generadores y augmentation online

**Qué hizo.** `image_size=(150,150)` y `batch_size=64`. El generador de train reescala píxeles a [0,1] con `1./255` y repite las mismas transformaciones geométricas; validation y test solo reescalan. `flow_from_directory` redimensiona, lee subcarpetas como clases y devuelve lotes de etiquetas one-hot (`class_mode='categorical'`). Train/validation usan `shuffle=True, seed=42`; test usa `shuffle=False`, lo que permite alinear `test_ds.labels` con `model.predict(test_ds)`.

**Para qué y cómo.** El generador evita cargar todas las imágenes redimensionadas a RAM. En cada lote de train entrega 64 imágenes transformadas y su vector de nueve posiciones; en test entrega el mismo orden de archivos para comparar predicción y etiqueta. Los outputs confirman los tamaños 45.513/5.355/2.682 y el mapeo alfabético: Basofilos=0 … Plaquetas=8.

**Razonable.** Normalizar, transformar solo train y desactivar el shuffle de test son decisiones técnicamente correctas que siguen vigentes. El uso simultáneo de augmentation físico y online buscaba mayor diversidad, aunque no elimina la dependencia creada antes del split.

**Hoy.** Se considerarían pipelines de entrada más actuales, deterministas y medibles, con semilla global y trazabilidad de transformaciones. `ImageDataGenerator` sigue siendo comprensible, pero es una API heredada frente a pipelines de datos y capas de augmentation modernas. No se selecciona una alternativa en esta investigación.

## Modelo y optimización

### 7. CNN: qué aprende y arquitectura real

**Qué hizo.** Construyó una CNN `Sequential` desde cero con 32 convoluciones 3×3 (ocho con 16 filtros, ocho con 32 y dieciséis con 64), Batch Normalization tras cada convolución, cuatro `MaxPool2D(2,2)`, `Flatten`, densas 512→1024→512 con regularización L2=0,0001 y `Dropout(0.3)`, y una salida densa de nueve unidades con `softmax`.

**Para qué servía.** Una CNN aprende filtros espaciales compartidos: capas tempranas suelen responder a bordes, color y textura; capas intermedias combinan esos elementos en patrones más complejos; capas profundas construyen representaciones útiles para separar categorías. Es una explicación conceptual: **no sabemos** qué rasgo biológico concreto aprendió cada filtro ni que lo haya hecho de manera clínicamente válida.

**Cómo funcionaba.** Una convolución 3×3 desplaza filtros sobre la imagen y genera mapas de activación. `padding='same'` conserva alto/ancho dentro de cada bloque; ReLU introduce no linealidad. Al aumentar 16→32→64 filtros, la red dispone de más canales para describir patrones progresivamente ricos mientras el pooling reduce resolución. Batch Normalization aprende escala y desplazamiento de activaciones y mantiene estadísticas móviles, lo que suele estabilizar gradientes. Max pooling conserva la activación local más fuerte y reduce coste/ sensibilidad a pequeños desplazamientos.

| Bloque | Capas y salida aproximada |
| --- | --- |
| Entrada | 150×150×3 RGB |
| B1 | 8 × Conv 3×3, 16 filtros + BN; MaxPool → 75×75×16 |
| B2 | 8 × Conv 3×3, 32 filtros + BN; MaxPool → 37×37×32 |
| B3 | 8 × Conv 3×3, 64 filtros + BN; MaxPool → 18×18×64 |
| B4 | 8 × Conv 3×3, 64 filtros + BN; MaxPool → 9×9×64 |
| Cabeza | Flatten 5.184 → Dense 512 → 1.024 → 512 → softmax 9 |

`Flatten` convierte los 9×9×64 activaciones en un vector de 5.184 valores. Las densas combinan globalmente esas evidencias; Dropout desactiva aleatoriamente 30 % de unidades durante train para reducir coadaptación. Softmax transforma nueve logits en probabilidades que suman uno.

**Qué era razonable.** Convoluciones pequeñas, normalización, pooling, regularización L2, dropout y una salida softmax eran elecciones sólidas para una clasificación multiclase desde cero en 2024. La progresión de canales es convencional y sigue siendo un patrón válido.

**Qué mejoraríamos hoy.** Como posibilidades de análisis: comparar una cabeza de pooling global frente a `Flatten`+densas para reducir parámetros; contrastar una CNN desde cero con representaciones preentrenadas bajo un protocolo controlado; y medir coste de navegador. Son hipótesis de evolución futura, no decisiones tecnológicas.

### 8. Los 4.372.857 parámetros

Un parámetro entrenable es un número que el optimizador ajusta para reducir la pérdida: los pesos de cada conexión/filtro y, cuando existe, su bias. En Batch Normalization, gamma y beta son entrenables; medias y varianzas móviles se guardan pero no reciben gradiente.

**Reconstrucción CONFIRMADA por cálculo directo del código:**

| Sección | Parámetros totales | Entrenables | No entrenables |
| --- | ---: | ---: | ---: |
| Bloque 16 + BN | 17.136 | 16.880 | 256 |
| Bloque 32 + BN | 70.272 | 69.760 | 512 |
| Bloque 64 inicial + BN | 278.784 | 277.760 | 1.024 |
| Bloque 64 final + BN | 297.216 | 296.192 | 1.024 |
| Dense 5.184→512 | 2.654.720 | 2.654.720 | 0 |
| Dense 512→1.024 | 525.312 | 525.312 | 0 |
| Dense 1.024→512 | 524.800 | 524.800 | 0 |
| Dense 512→9 | 4.617 | 4.617 | 0 |
| **Total** | **4.372.857** | **4.370.041** | **2.816** |

Por ejemplo, la primera densa aporta `5.184×512 + 512`: más del 60 % del total. Esto explica por qué una arquitectura con convoluciones relativamente modestas termina con millones de pesos: Flatten conserva todas las posiciones espaciales y cada una se conecta con cada unidad densa. Más parámetros aumentan expresividad, memoria de pesos y coste de operaciones; también pueden elevar riesgo de sobreajuste si la independencia efectiva del dataset es baja.

### 9. Compilación y entrenamiento

**Qué hizo.** Compiló con `categorical_crossentropy`, `Adam(0.0004)` y métricas accuracy, Precision, Recall y AUC. Entrenó hasta 100 épocas con validation; los outputs guardados muestran 62 épocas y 712 batches por época.

**Cómo funciona un batch.** Las 64 imágenes pasan por la CNN (*forward pass*), que devuelve nueve probabilidades por imagen. La crossentropy compara cada distribución con su etiqueta one-hot y penaliza asignar poca probabilidad a la clase verdadera. Backpropagation calcula cómo cambiar cada peso para reducir esa pérdida; Adam combina una estimación de dirección y magnitud adaptativa, escalada por el learning rate 0,0004. Tras 712 lotes —los necesarios para cubrir aproximadamente 45.513 muestras— se completa una época. Varias épocas permiten aprendizaje progresivo; validation estima el comportamiento sobre sus 5.355 archivos sin actualización de pesos.

**Métricas.** Accuracy es la fracción correctamente clasificada. Precision mide cuán fiables son las predicciones positivas bajo la agregación de Keras; Recall mide cuántos positivos se recuperan. AUC mide capacidad de ordenar positivos sobre negativos; en multiclase Keras la calcula sobre salidas por clase y no sustituye métricas por clase. La posterior evaluación de scikit-learn usa precision/recall ponderados y AUC one-vs-rest.

**Razonable.** Crossentropy + softmax y Adam son una pareja estándar; mantener validation y varias métricas fue una decisión cuidadosa. El batch 64 era una elección práctica sujeta a memoria y rendimiento.

**Hoy.** Se registraría la semilla completa, versiones, hardware, curvas y artefactos como experimento reproducible; se añadirían macro F1, calibración y métricas por clase desde el inicio. No se puede concluir que el conjunto de métricas histórico valide desempeño clínico.

### 10. Callbacks y duración

**Qué hizo.** `ModelCheckpoint('mejor_modelo.h5', save_best_only=True)` guardó solamente el modelo que mejoró el monitor por defecto (`val_loss`). `ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=6, min_lr=1e-6)` redujo el learning rate a una quinta parte tras seis épocas sin mejora. `EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True)` detuvo tras doce épocas sin mejora y restauró pesos del mínimo `val_loss`.

**Para qué servía.** El checkpoint evita conservar solo el último modelo, que puede ser peor. Reducir learning rate al estancarse cambia de pasos grandes a ajustes más finos. Early stopping evita seguir optimizando cuando validation ya no mejora y conserva el mejor estado observado.

**Evidencia.** El learning rate registrado cae 0,0004→0,00008→0,000016→0,0000032→0,000001. El mínimo `val_loss` guardado es 0,0493 en época 50; la ejecución termina en época 62, coherente con paciencia 12 y restauración de esa época. Frente a 100 épocas a ~3.227 s/época, evitó aproximadamente 38 épocas o **34,06 horas**; es una estimación basada en el promedio histórico, no una medición de un contrafactual.

**Razonable y hoy.** Los tres callbacks son prácticas válidas hoy. Se mejoraría reproducibilidad declarando monitores/modos explícitos, guardando configuración e historial fuera del notebook y definiendo por adelantado el criterio de selección; esto no cuestiona su utilidad histórica.

## Evaluación y resultados guardados

### 11. Curvas, métricas y test

**Qué hizo.** Promedió las métricas históricas de train/validation y dibujó accuracy, loss, precision, recall y AUC por época. Luego predijo los 2.682 archivos de test en 42 batches (130 s históricos), aplicó `argmax` a probabilidades, calculó accuracy, precision/recall ponderados y AUC OVR, imprimió `classification_report`, construyó matriz de confusión y localizó 29 índices mal clasificados para visualizarlos.

**Cómo funcionaba.** `argmax` elige la clase de mayor probabilidad. El report muestra precision, recall y F1 por clase; la matriz muestra filas reales y columnas predichas. `shuffle=False` fue crucial: preserva la correspondencia entre predicciones y `test_ds.labels`. La visualización de errores solo titula la etiqueta real, no la predicción, por lo que ayuda a mirar fallos pero no explica por sí sola qué confusión ocurrió.

**Resultados históricos confirmados.** Accuracy 0,989187; precision ponderada 0,989245; recall ponderado 0,989187; AUC OVR 0,999929; 29 errores. El report tiene soporte 298 por clase y macro/weighted F1 cercano a 0,99. Son resultados del split histórico, no validación independiente/ clínica.

**Razonable.** Usar test sin transforms aleatorias, report por clase, matriz de confusión y revisión visual de errores fue más completo que usar accuracy sola. Estas técnicas siguen siendo válidas.

**Hoy.** Se conservarían predicciones, IDs de muestras, matriz normalizada, macro F1, intervalos de incertidumbre y una taxonomía de errores; se evaluaría OOD/negativos y calibración. Antes de comparar modelos se corregiría el protocolo de split.

## Rendimiento extremadamente lento

Los logs guardados muestran aproximadamente 3.227 segundos por época (≈53,8 minutos), 55,58 horas para 62 épocas y 130 segundos para el test. La explicación causal no está completamente registrada.

- **CONFIRMADO:** la CNN es profunda (32 convoluciones), procesa imágenes 150×150, ejecuta 712 batches por época y aplica lectura, resize y augmentation online en cada batch. Todo ello consume cálculo y entrada/salida.
- **CONFIRMADO:** la metadata del notebook declara `tf-cpu`; no contiene una comprobación de GPU ni logs de dispositivo.
- **PROBABLE:** que el entrenamiento se haya ejecutado solo en CPU o sin aceleración efectiva. En ese caso, convoluciones, BatchNorm y la cabeza densa de 4,37 M parámetros explicarían gran parte del tiempo en un i7-7700HQ.
- **PROBABLE:** que la carga desde SSD SATA, decodificación/redimensionamiento y augmentation Python/CPU hayan contribuido, incluso con GPU; el generador realiza trabajo por lote.
- **POSIBLE:** que limitaciones de versiones históricas de TensorFlow/Keras, configuración de hilos, formato de imágenes o transferencia CPU→GPU afectaran rendimiento.
- **PENDIENTE:** demostrar qué dispositivo ejecutó cada operación, versiones de TensorFlow/CUDA/cuDNN y perfil de cuello de botella. La GTX 1050 de 4 GiB existía, pero su uso real en este entrenamiento no está probado.

## 2024 frente a posibilidades actuales

| Aspecto | 2024 en el notebook | Hoy, sin decisión tomada |
| --- | --- | --- |
| Datos | carpetas locales y nombres de directorio | manifiestos, versionado externo, metadatos y trazabilidad |
| Augmentation | físico antes del split + online en train | split por unidad independiente antes de derivar; augmentation de train bajo demanda |
| Entrada | `ImageDataGenerator` | pipelines más deterministas y observables |
| Modelo | CNN desde cero con Flatten+densas | comparar cabezas más compactas, transferencia y coste de despliegue |
| Reproducibilidad | semillas parciales; shuffle sin seed | semillas, dependencias, hardware, datos y artefactos registrados |
| Seguimiento | outputs/plots del notebook | experimentos identificables y comparables |
| Web | la exportación TF.js ocurrió fuera del notebook | medir tamaño, latencia, memoria y compatibilidad antes de elegir formato |

Estas son posibilidades de investigación futura, no un plan de migración ni una selección de tecnología.

## Conclusión de comprensión

El notebook representa un flujo educativo completo y técnicamente coherente para entrenar una CNN: inspecciona, balancea, separa, genera lotes, entrena con regularización/callbacks y evalúa con varias vistas. Sus puntos fuertes reutilizables son la separación conceptual train/validation/test, normalización, augmentation solo online en train, callbacks y evaluación por clase. Su limitación decisiva es el orden histórico de augmentation físico y split, junto con falta de procedencia y unidad biológica independiente. La siguiente investigación debe recuperar procedencia/metadatos y trazabilidad de imágenes antes de intentar un baseline reproducible.
