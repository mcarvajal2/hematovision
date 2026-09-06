# Decisiones

Registro liviano de decisiones no triviales. Estados: `PROPOSED`, `ACCEPTED`, `SUPERSEDED`, `RETIRED`. Al añadir una decisión, use un ID estable `DEC-NNN` y registre contexto, decisión, alternativas, razones, consecuencias, fecha y estado.

## DEC-001 — Preservar el baseline histórico

**Estado:** ACCEPTED
**Fecha:** 2026-09-05

**Contexto:** el notebook y modelo de 2024 contienen resultados históricos, pero el pipeline reconstruido tiene riesgo confirmado de leakage y no existe validación clínica.

**Decisión:** preservar modelo y notebook históricos como baseline y evidencia; no corregirlos silenciosamente. Las mejoras futuras se implementarán como una nueva evolución reproducible y se compararán contra el baseline cuando corresponda.

**Alternativas consideradas:** modificar el notebook/modelo existente para corregir el pipeline; reemplazar el baseline sin conservar su contexto.

**Razones:** protege la trazabilidad de lo ocurrido y evita que una corrección actual se confunda con evidencia de 2024.

**Consecuencias:** los defectos históricos se documentan explícitamente; una evaluación confiable exige un dataset, split y ejecución nuevos. Véanse [Historia](project-history.md) y [Roadmap](roadmap.md).
