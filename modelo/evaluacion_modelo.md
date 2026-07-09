# Parte 6.10 – Política de Evaluación y Actualización del Modelo

## Objetivo
Definir un proceso para evaluar nuevas versiones del LLM y decidir su incorporación al entorno de producción.

## Flujo de evaluación
1. **Detección de nuevas versiones**
   - Monitorear lanzamientos oficiales del proveedor del LLM.
   - Registrar fecha y características principales.

2. **Pruebas A/B controladas**
   - Seleccionar un conjunto de preguntas representativas.
   - Dividir tráfico de prueba: 50% modelo actual, 50% modelo nuevo.
   - Comparar métricas: % sin respuesta, feedback negativo, tiempo de respuesta.

3. **Análisis de resultados**
   - Si el nuevo modelo mejora métricas sin empeorar tiempos, se considera apto.
   - Documentar hallazgos en bitácora técnica.

4. **Decisión de actualización**
   - Equipo técnico valida migración.
   - Equipo de curaduría revisa coherencia.
   - Se actualiza entorno de producción.

5. **Revisión periódica**
   - Repetir cada trimestre o cuando haya nueva versión relevante.
   - Mantener registro histórico en `modelo/evaluacion_modelo.md`.

## Indicadores de éxito
- Menor % de preguntas sin respuesta.
- Menor % de feedback negativo.
- Tiempo de respuesta estable o mejorado.
- Consistencia en citas de fuentes.

## Responsables
- Equipo técnico de IA.
- Equipo de curaduría documental.

