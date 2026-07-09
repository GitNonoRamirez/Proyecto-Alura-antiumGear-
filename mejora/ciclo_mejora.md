# Parte 6.9 – Ciclo de Mejora Continua

## Objetivo
Definir un flujo de retroalimentación que permita mejorar la calidad de las respuestas del agente de manera iterativa.

## Flujo de mejora
1. **Preguntas recurrentes sin respuesta**
   - Detectadas en métricas (% sin respuesta).
   - Acción: añadir documentos relevantes a `documentos/`.
   - Pipeline de actualización indexa automáticamente.

2. **Respuestas mal evaluadas**
   - Detectadas en métricas (% feedback negativo).
   - Acción: ajustar prompt o lógica de recuperación.
   - Documentar cambios en bitácora.

3. **Revisión periódica**
   - Responsables de curaduría validan documentos añadidos.
   - Se revisan métricas para confirmar mejora.

## Indicadores de éxito
- Reducción del % de preguntas sin respuesta.
- Disminución del feedback negativo.
- Tiempo de respuesta estable o mejorado.

## Responsables
- Equipo de curaduría documental.
- Equipo técnico de prompts y recuperación.
