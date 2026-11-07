# ADR-004: bloqueo de inventario desde la creación de la reserva
**Estado:** aceptado.

**Contexto:** BR-19 impide reservar una habitación que otra solicitud ya apartó; el proyecto original no asignaba habitación.

**Alternativas:** reservar únicamente en Confirmada (riesgo de solicitudes pendientes simultáneas), contador por tipo (sin identidad de habitación), asignación transaccional concreta.

**Decisión:** asignar `room_number` al crear `Pendiente` dentro de UnitOfWork y considerar Pendiente, Confirmada y Checked-in como intervalos ocupantes. Confirmar requiere garantía, pero no cambia la habitación asignada.

**Consecuencias:** se evita overbooking; una reserva Pendiente bloquea inventario indefinidamente hasta definirse un plazo de expiración con el responsable del negocio. Esta decisión no inventa una caducidad.
