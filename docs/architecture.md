# Arquitectura

El repositorio contiene dos superficies con ciclos de vida distintos:

1. `apps/web` publica una aplicación estática. TensorFlow.js carga el modelo desde `public/model` y procesa las imágenes en el navegador.
2. `ml` conserva el trabajo reproducible de entrenamiento, evaluación y exportación. Sus datasets y artefactos grandes no pertenecen al historial Git.

La separación evita que un cambio experimental del notebook altere directamente la aplicación desplegada. Un modelo pasa a producción solo después de evaluarse, documentarse y exportarse en un formato compatible con TensorFlow.js.

## Flujo de entrega

`datos versionados -> entrenamiento reproducible -> evaluación -> exportación web -> pruebas -> GitHub Pages`

El modelo web es un activo de despliegue y se mantiene junto a la aplicación para que una revisión de Git pueda reconstruir exactamente el sitio publicado.
