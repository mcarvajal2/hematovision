# HematoVision: guía para agentes

HematoVision es una aplicación web educativa que clasifica imágenes de nueve tipos de células sanguíneas en el navegador. No es un producto de diagnóstico ni un dispositivo médico.

## Empieza aquí

1. Lee el [README](README.md) y el [índice de conocimiento](docs/index.md).
2. Lee [Estado del proyecto](docs/project-status.md) antes de planificar trabajo.
3. Inspecciona el código y la documentación relevante **antes de asumir** cómo está implementada una parte del proyecto.

## Router documental

- Contexto histórico, dataset y limitaciones: [Historia y baseline histórico](docs/project-history.md).
- Hallazgos auditados, incertidumbres y cómo investigar: [Investigaciones](docs/research.md).
- Motivos de decisiones de alcance: [Decisiones](docs/decisions.md).
- Protocolo para registrar ejecuciones futuras de ML: [Experimentos](docs/experiments.md).
- Orden de evolución: [Roadmap](docs/roadmap.md).
- Cómo se coordina un equipo multiagente en este repositorio (roles, delegación, revisión, escalamiento): [Flujo de trabajo multiagente](docs/agent-workflow.md).
- Implementación y despliegue actuales: [Arquitectura](docs/architecture.md), [ficha del modelo](docs/model-card.md) y [protocolo de actualización](docs/update-protocol.md).

## Preservación

- `ml/notebooks/Hematologia.ipynb` es una copia idéntica del notebook histórico. Es evidencia, no un lugar para modernizar código ni corregir resultados.
- Los modelos Keras, datasets y directorios locales históricos no pertenecen al repositorio. No los copies, muevas, regeneres ni modifiques.
- No presentes la métrica histórica cercana al 99 % sin su limitación de leakage; consulta primero la historia y la ficha del modelo.
- La fuente de verdad para la aplicación publicada es el código y los activos versionados bajo `apps/web`; los documentos describen, no sustituyen, esa evidencia.

## Persistir conocimiento

Al descubrir información reutilizable y suficientemente estable, evalúa si debe actualizarse el estado, una investigación, una decisión, documentación técnica, un experimento o el roadmap. Distingue siempre `CONFIRMADO`, `INFERIDO`, `HIPÓTESIS` y `PENDIENTE`; no conviertas conjeturas en hechos ni guardes conversación casual o resultados efímeros.

Usa las convenciones de [Investigaciones](docs/research.md), [Decisiones](docs/decisions.md) y [Experimentos](docs/experiments.md). Al crear una entrada, actualiza su índice o puntero correspondiente y evita duplicar una fuente de verdad existente.
