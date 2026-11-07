# ADR-003: CQRS básico para consultas
- Estado: Aceptado.
- Contexto: disponibilidad y reportes no necesitan mutar agregados (NB-01, NB-10).
- Alternativas: reutilizar entidades completas para toda lectura; separar consultas en DTOs.
- Decisión: endpoints GET devuelven proyecciones simples; POST ejecuta comandos y valida dominio.
- Consecuencias: lectura clara y eficiente; se debe evitar duplicar reglas de negocio en query handlers.
