# Protocolo de actualización

## Cambios de aplicación

1. Crear issue y rama desde `main`.
2. Implementar el cambio con pruebas proporcionadas o actualizadas.
3. Ejecutar `npm run check`.
4. Abrir pull request, revisar y fusionar solo con CI exitoso.
5. Publicar una versión semántica: `patch` para correcciones, `minor` para funcionalidades compatibles y `major` para cambios incompatibles.

## Cambios de modelo

1. Confirmar que los datos están anonimizados, autorizados y versionados fuera de Git.
2. Ejecutar el entrenamiento con parámetros y semilla registrados.
3. Evaluar contra un conjunto de prueba inmóvil y comparar métricas por clase con la versión actual.
4. Actualizar `docs/model-card.md` y guardar métricas, matriz de confusión y hash del modelo.
5. Exportar el modelo a TensorFlow.js, verificar que la app lo carga y probar una predicción de humo.
6. Solicitar revisión antes de publicar.

No se publica un modelo que reduzca una métrica acordada sin una justificación y aprobación explícita.
