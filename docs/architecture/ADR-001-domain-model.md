# ADR-001: Domain Model como patrón principal
- Estado: Aceptado para el prototipo.
- Contexto: BR-04, BR-06, BR-07, BR-10, BR-11, BR-16, BR-17 y BR-19 exigen reglas cruzadas, temporales y estados.
- Alternativas: Transaction Script (simple, pero duplicaría reglas por pantalla); Table Module (útil en operaciones tabulares, insuficiente para ciclo de vida); Domain Model.
- Decisión: Domain Model para Reserva, Habitación y Folio; consultas de reportes pueden ser proyecciones.
- Consecuencias: reglas encapsuladas y testables; mayor inversión inicial y necesidad de mantener agregados consistentes.
