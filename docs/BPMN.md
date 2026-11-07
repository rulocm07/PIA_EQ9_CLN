# BPMN - proceso del Hotel Costa Azul

**Fuente original obligatoria:** `docs/references/BPMN_U2_original.pdf` (6 páginas), entregado por el equipo. Esta referencia se conserva sin modificación; es el diagrama visual BPMN que se incluirá en el reporte. El flujo que sigue sirve como apoyo de lectura, **no reemplaza la notación BPMN del original**.

```mermaid
flowchart TD
 A[Huésped solicita reservación] --> B[Consultar disponibilidad y temporada]
 B --> C{Habitación disponible?}
 C -- No --> D[Informar sin disponibilidad]
 C -- Sí --> E[Crear Pendiente y bloquear habitación]
 E --> F{Anticipo 50% o tarjeta?}
 F -- No --> G[Permanece Pendiente]
 F -- Sí --> H[Confirmada]
 H --> I{Llega el huésped?}
 I -- No a las 23:59 --> J[No-Show y penalización]
 I -- Sí --> K[Registrar identificación y garantía incidental]
 K --> L{Habitación lista?}
 L -- No --> M[No permitir check-in]
 L -- Sí --> N[Check-in y abrir folio]
 N --> O[Estancia, consumos firmados y cambios]
 O --> P[Solicitar inspección exprés]
 P --> Q[Inspección >=5 min]
 Q --> R{Folio saldado?}
 R -- No --> S[Registrar pago]
 S --> R
 R -- Sí --> T[Check-out y marcar Sucia]
 T --> U[Limpieza >=35 min]
 U --> V[Limpia/Inspeccionada]
```

**Excepciones:** avería -> cambio igual/superior sin costo; upgrade -> diferencia prorrateada; mantenimiento -> habitación fuera de inventario; cancelación -> retención/reembolso por 48 h; no-show por 23:59.

**Anotación de alcance:** en el código hay endpoints REST que representan las actividades, pero no hay motor BPMN ejecutable. El profesor solicita diagrama completo y correspondencia, no un motor BPMN.
