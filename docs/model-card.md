# Ficha del modelo

## Estado

Modelo heredado, pendiente de validación reproducible. Uso exclusivamente educativo y demostrativo.

## Entrada y salida

- Entrada: imagen RGB normalizada de 150 × 150 píxeles.
- Salida: probabilidades para Basófilos, Eosinófilos, Eritroblastos, Linfoblastos, Linfocitos, Mieloblastos, Monocitos, Neutrófilos y Plaquetas.

## Limitaciones

- No existe evidencia de validación clínica en este repositorio.
- El rendimiento puede variar según microscopio, tinción, iluminación y población.
- Una predicción no equivale a un diagnóstico.
- El modelo no detecta ni segmenta células dentro de un cuadro: clasifica la imagen completa como una de las nueve clases. El modo automático de la app puede volver a contar la misma célula varias veces; el total mostrado es demostrativo, no un conteo hematológico.
- Es un clasificador softmax cerrado: siempre reparte 100% de probabilidad entre las nueve clases, incluso ante imágenes fuera de dominio (una cara, un objeto cualquiera). Una confianza alta no garantiza que la imagen sea una célula válida.
- La app aplica un umbral mínimo de confianza (`MIN_CONFIDENCE` en `apps/web/src/constants.js`, actualmente 0.6) para descartar predicciones obviamente ambiguas. Es provisional: no fue calibrado contra un set de validación negativo (fondos, piel, caras, otras tinciones). Antes de confiar en ese valor, medir la tasa de falsos positivos sobre ese set y ajustar en consecuencia.

## Compatibilidad de deserialización (TF.js)

El artefacto publicado fue exportado con `keras v2.10.0` / `TensorFlow.js Converter v4.16.0` y serializa capas `Conv2D` con `kernel_regularizer: L2`. `apps/web/src/classifier.js` registra una clase `L2` de paso (no una capa real) solo para que `tf.loadLayersModel()` pueda deserializar ese regularizer; no afecta la inferencia. Si se reexporta el modelo, verificar primero si sigue haciendo falta este shim (por ejemplo, quitando `kernel_regularizer` antes de convertir, o si el nuevo converter serializa los regularizers distinto). `tests/classifier.test.js` carga el artefacto real contra el código actual para detectar si el shim deja de ser suficiente.

## Reproducibilidad del entrenamiento

Pendiente. `ml/pyproject.toml` declara un entorno moderno (Python ≥3.11, Keras ≥3.0), pero el artefacto publicado viene de Keras 2.10 y no hay `uv.lock` ni script de exportación en el repo — reentrenar hoy no necesariamente reproduce este artefacto ni el mismo shim de deserialización. Antes de reentrenar: documentar la procedencia del dataset, fijar un entorno histórico reproducible (o una estrategia de migración probada a Keras 3), escribir un script de exportación versionado, y validar la carga en TF.js antes de publicar.

Antes de sustituir este modelo, registrar versión del dataset, partición de evaluación, métricas por clase, matriz de confusión, semilla, parámetros y hash del artefacto exportado.
