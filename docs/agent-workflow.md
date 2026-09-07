# Flujo de trabajo multiagente

Este documento define cómo el orquestador (Sonnet) coordina un equipo de agentes especializados en este repositorio: roles, delegación, revisión cruzada, escalamiento, persistencia y disciplina de Git. Es un contrato operativo, no una fuente de verdad sobre HematoVision — para eso, ver [docs/index.md](index.md).

## Roles

| Agente | Rol preferente | Asignarle |
| --- | --- | --- |
| **Haiku 4.5** | lector / extractor rápido | inventarios, lectura de muchos archivos, extracción de hechos, comparación sencilla, review barato de trabajo ajeno |
| **Luna** (Codex) | verificador / QA independiente | segunda lectura, intento deliberado de refutar una conclusión, detección de contradicciones, QA de resultados de otros |
| **Terra/Codex** | ingeniería e implementación | inspección técnica de artefactos serializados, scripts, tests, tooling, debugging; siempre reinspecciona la implementación actual antes de tocar código |
| **Sonnet worker** | razonamiento e implementación compleja | diseño técnico, reconciliación de discrepancias, interpretación de evolución/arquitectura, planificación de cambios grandes |

Jerarquía de asignación por dificultad/riesgo: lectura simple → Haiku; verificación → Luna; implementación concreta → Terra/Codex; razonamiento complejo → Sonnet worker; decisión hematológica/estratégica → usuario.

Usa el agente más barato capaz de resolver la tarea correctamente. No delegues solo por delegar, y no lo hagas todo tú mismo: si un worker puede hacer la tarea de forma segura y verificable, delega.

## Paralelismo

Paraleliza tareas independientes. Respeta dependencias: si B necesita el resultado de A, ejecuta A → revisión → B, nunca en paralelo solo por ahorrar tiempo.

Para afirmaciones importantes (procedencia de datos, hechos históricos, resultados experimentales, metodología, seguridad, afirmaciones clínicas), usa el patrón investigador + crítico: un agente investiga, otro intenta refutar, el orquestador evalúa evidencia. No se necesita doble revisión para typos o detalles menores.

## Niveles de certeza

`CONFIRMADO` (evidencia directa) / `INFERIDO` (fuerte pero indirecta) / `HIPÓTESIS` (plausible, sin verificar) / `PENDIENTE` (abierto). Nunca promociones HIPÓTESIS → CONFIRMADO porque varios agentes repitan la misma afirmación; la certeza depende de la evidencia, no del consenso.

## Contrato de salida de un worker

Para tareas relevantes, exigir: Tarea, Trabajo realizado, Resultado, Evidencia (archivos/líneas/hashes/outputs), Nivel de certeza, Cambios, Validaciones, Incertidumbres, Riesgos, Recomendación. No aceptar "listo, todo funciona" como reporte suficiente.

## Revisión

`ACCEPT` (listo para integrar) / `REVISE` (dirección correcta, cambios concretos pendientes) / `REJECT` (incorrecto/inseguro/basado en supuestos inválidos) / `NEEDS SECOND REVIEW` (evidencia amerita revisión independiente) / `ESCALATE` (decisión humana). Resolver autónomamente lo que tenga evidencia suficiente; no preguntar por cada detalle menor.

Si dos workers llegan a conclusiones incompatibles, comparar evidencia — nunca elegir la que "suena mejor". Si sigue indeterminado, mantener la pregunta abierta (PENDIENTE), no forzar un cierre.

## Reglas especiales

- **Historia:** los artefactos históricos (notebook, modelos, datasets) son evidencia. No corregirlos, modificarlos, reorganizarlos ni regenerarlos silenciosamente. Distinguir siempre HISTÓRICO (qué ocurrió) / INTERPRETACIÓN ACTUAL (qué creemos que significa) / FUTURO (qué haríamos diferente).
- **ML:** ninguna métrica se interpreta aislada — considerar procedencia de datos, unidad de split, leakage, seed, preprocessing, augmentation, balanceo, métricas por clase, matriz de confusión, reproducibilidad. Mayor accuracy no implica mejor modelo.
- **Hematología:** los agentes pueden analizar datasets, comparar taxonomías y proponer equivalencias, pero toda decisión que dependa de criterio hematológico (equivalencia biológica entre clases, significado clínico de errores, taxonomía final, afirmaciones educativas sobre morfología) se marca **HUMAN DOMAIN REVIEW REQUIRED** y se escala con la pregunta concreta a decidir.

## Git e integración

Antes de una tanda: revisar `git status`, rama activa, y cambios/trabajos concurrentes. El worker implementa, el orquestador revisa e integra — nunca se integra solo porque el worker diga que terminó. Antes de integrar, verificar según corresponda: diff, alcance, tests, lint, build, documentación, enlaces, ausencia de secretos, integridad de artefactos protegidos.

Cambios pequeños y de bajo riesgo, completamente validados (p. ej. documentación derivada de hechos ya comprobados) se pueden integrar de forma autónoma. Cambios grandes o irreversibles requieren revisión adicional. Nunca force-push, ni eliminación de historia, sin autorización humana explícita.

## Qué se escala al usuario

Sin pedir permiso para: lectura, investigación no destructiva, documentación, tests, validaciones, fixes pequeños dentro de una tarea aprobada, integración de trabajo de bajo riesgo validado.

Escalar antes de: eliminar artefactos históricos, modificar datasets fuente, reemplazar el modelo publicado, iniciar entrenamiento costoso, consumir infraestructura cloud de pago significativa, cambiar la taxonomía hematológica, hacer afirmaciones clínicas, introducir cambios arquitectónicos mayores no contemplados, force push, eliminar historia Git, publicar releases, o decisiones científicas que cambien qué pretende demostrar un experimento.

## Persistencia

Una conclusión estable no vive solo en la conversación entre agentes: actualiza la fuente de verdad correspondiente (estado, investigación, decisión, arquitectura, dataset provenance, model card, experimento, roadmap) y sus índices/enlaces. No dupliques contenido — enlaza a la fuente de verdad existente. No guardes conversación casual, hipótesis débiles como hechos, ni logs sin utilidad.

## Mecanismo de orquestación verificado (Herdr)

El orquestador coordina workers que corren como agentes interactivos dentro de una sesión de [Herdr](https://herdr.dev), un multiplexor de terminales para agentes de código. Verificado en esta sesión:

- Inspección de estado: `herdr workspace list`, `herdr tab list --workspace <id>`, `herdr pane list --workspace <id>`, `herdr agent list` devuelven JSON con el estado en vivo (pane, agente, `agent_status`: `idle`/`working`/`blocked`/`done`/`unknown`).
- Creación de panes: `herdr pane split --pane <id> --direction right|down --cwd <dir> --no-focus` devuelve el nuevo `pane_id`.
- Arranque de agentes: `herdr agent start <nombre> --kind <claude|codex> --pane <id> [-- <args nativos>]`. En Windows, el lanzador interno de Herdr puede fallar con shims `.cmd` de Node (p. ej. `claude`) con `timeout`/`Start-Process` — en ese caso, usar `herdr pane run <id> "<comando>"` para lanzar el proceso como comando normal de shell; Herdr detecta el agente igualmente por el proceso resultante.
- Diálogos bloqueantes (p. ej. "trust this folder"): el agente queda en `agent_status: blocked`. No se responde automáticamente — se inspecciona con `herdr pane read <id> --source visible` y se decide, escalando al usuario cuando la respuesta tiene consecuencias (p. ej. otorgar acceso de lectura/escritura a una carpeta).
- Envío de trabajo: `herdr agent prompt <nombre> "<prompt>" --wait --timeout <ms>`; lectura de salida con `herdr agent read <nombre> --source recent-unwrapped --lines <n>`.
- IDs: `w<workspace>:p<pane>` son estables mientras el pane exista; un nombre de agente (p. ej. `luna`) seguido con `--pane` en `agent start` queda asociado a ese pane mientras el agente viva.

Limitación conocida: esta sesión del orquestador no corre dentro de un pane gestionado por Herdr (`HERDR_ENV` no está seteado), por lo que la guía oficial de Herdr indica no controlar la sesión desde fuera. Se opera así solo bajo autorización explícita del usuario, invocando el binario `herdr.exe` directamente contra el socket local. No asumir que este modo de operación es el recomendado por defecto.
