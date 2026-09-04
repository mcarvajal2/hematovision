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

Antes de sustituir este modelo, registrar versión del dataset, partición de evaluación, métricas por clase, matriz de confusión, semilla, parámetros y hash del artefacto exportado.
