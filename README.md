# HematoVision

Aplicación web educativa para explorar la clasificación de células sanguíneas mediante un modelo de visión artificial ejecutado en el navegador.

> **Advertencia:** no es un dispositivo médico. No debe utilizarse para diagnóstico, tratamiento ni toma de decisiones clínicas.

## Estructura

- `apps/web`: interfaz web Vite y modelo TensorFlow.js publicado.
- `ml`: código, notebook y configuración de entrenamiento.
- `artifacts`: modelos de entrenamiento y experimentos locales; no se suben a Git.
- `docs`: arquitectura, protocolo de actualización y documentación del modelo.

## Inicio rápido

Requiere Node.js 20.19 o superior.

```powershell
npm --prefix apps/web ci
npm run web:dev
```

Validar antes de abrir un cambio:

```powershell
npm run check
```

## Versionado

El código y el modelo web publicado se versionan en Git. Los datasets, modelos Keras y resultados de entrenamiento se gestionarán con DVC antes de su primera actualización; véase [ml/README.md](ml/README.md).

## Despliegue

GitHub Actions compila `apps/web` y publica `apps/web/dist` en GitHub Pages al integrar cambios en `main`. En la configuración del repositorio de GitHub, seleccionar **Pages → Source: GitHub Actions**.

## Documentación

- [Punto de entrada para agentes](AGENTS.md)
- [Índice de conocimiento del proyecto](docs/index.md)
- [Estado del proyecto](docs/project-status.md)
- [Arquitectura](docs/architecture.md)
- [Protocolo de actualización](docs/update-protocol.md)
- [Ficha del modelo](docs/model-card.md)
- [Guía de contribución](CONTRIBUTING.md)
