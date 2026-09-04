# Machine learning

El notebook histórico se conserva en `notebooks/Hematologia.ipynb` como referencia. La lógica nueva debe migrar gradualmente a módulos bajo `src/` y pruebas bajo `tests/`.

## Entorno

Se recomienda `uv` para crear entornos y bloquear dependencias:

```powershell
cd ml
uv sync
```

## Datos y artefactos

Los datos de entrenamiento, modelos Keras y experimentos no se suben a Git. La carpeta `artifacts/keras` contiene una copia local del modelo heredado. Antes de una nueva ronda de entrenamiento se debe inicializar DVC y configurar un remoto compartido (por ejemplo, un bucket S3, GCS o Azure Blob) para guardar datos y artefactos de forma versionada.
