# User Stories y criterios de aceptación (fuente U2)

## US-01 Consultar disponibilidad — Reservaciones
Como Reservaciones quiero consultar habitaciones por fechas, huéspedes y tipo para confirmar sin duplicidades.
```gherkin
Given existen habitaciones registradas
When consulto rango de fechas, huéspedes y tipo
Then solo aparecen habitaciones compatibles y disponibles
```
## US-02 Aplicar tarifa por temporada — Reservaciones
Como Reservaciones quiero calcular tarifa por tipo y temporada para cotizar correctamente.
```gherkin
Given una reserva con fechas y tipo
When las fechas son temporada baja o alta
Then aplicar tarifa base o incremento automático del 35%
```
## US-03 Confirmar reserva — Reservaciones
Como Reservaciones quiero confirmar con anticipo o tarjeta en garantía.
```gherkin
Given una reserva con total calculado
When registro anticipo del 50% o tarjeta en garantía
Then la reserva pasa a Confirmada
```
## US-04 Cancelar reserva — Huésped
Como huésped quiero cancelar y conocer el reembolso.
```gherkin
Given reserva confirmada
When cancelo con más de 48 horas
Then reembolso 100%
When cancelo con menos de 48 horas
Then retener 50% del anticipo
```
## US-05 No-show — Recepción
Como Recepción quiero declarar no-show a las 23:59 y aplicar política.
```gherkin
Given reserva confirmada y llegada hoy sin check-in
When son las 23:59
Then declarar No-Show, liberar habitación al día siguiente y cobrar primera noche a garantía
```
## US-06 Check-in — Recepción
Como Recepción quiero registrar identidad, acompañantes y garantía incidental.
```gherkin
Given reserva confirmada
When registro INE/Pasaporte, acompañantes y voucher de $1,000 o efectivo $500
Then completar check-in y abrir estancia/folio
```
## US-07 Early check-in — Recepción
```gherkin
Given huésped llega antes de las 12:00
When hay habitación lista
Then permitir entrada y cobrar 30% de tarifa diaria
When llega después de las 12:00
Then no agregar cargo early
```
## US-08 Late check-out — Recepción
```gherkin
Given salida oficial 12:00
When sale hasta 15:00
Then cobrar 30%
When sale después de 15:00
Then cobrar noche completa
```
## US-09 Cambio por avería — Recepción
```gherkin
Given falla técnica no subsanable de inmediato
When Recepción solicita cambio
Then reubicar en categoría igual o superior sin diferencia
```
## US-10 Upgrade voluntario — Huésped
```gherkin
Given huésped solicita categoría superior
When se autoriza y hay disponibilidad
Then prorratear diferencia por noches restantes
```
## US-11 Salida anticipada — Recepción
```gherkin
Given estancia vigente
When aviso con al menos 24 horas
Then cobrar noches hospedadas más media noche
When aviso el mismo día
Then cobrar noche completa sin reembolso
```
## US-12 Consumos al folio — Recepción
```gherkin
Given huésped tiene habitación asignada
When registro consumo con número de habitación y firma
Then cargar inmediatamente al folio
```
## US-13 Inspección de check-out — Recepción/Limpieza
```gherkin
Given huésped inicia check-out
When Recepción solicita inspección
Then Limpieza recibe solicitud y reporta resultado
When inspección confirma estado
Then generar cuenta desglosada y liberar garantía según corresponda
```
## US-14 Actualizar habitación limpia — Limpieza
```gherkin
Given habitación Sucia después del check-out
When Limpieza termina y revisa
Then actualizar a Limpia/Inspeccionada en tiempo real
And Recepción no asigna llave antes de ese estado
```
## US-15 Fuera de servicio — Administración/Mantenimiento
```gherkin
Given habitación con avería o mantenimiento mayor
When Administración o Supervisor la marca Fuera de Servicio
Then registrar motivo/fecha estimada y descontar del inventario
```
## US-16 Operaciones sensibles — Administración
```gherkin
Given operación sensible
When Recepción intenta descuento >10%, condonación o anulación
Then solicitar PIN de Administración
When PIN válido
Then permitir operación autorizada
```
