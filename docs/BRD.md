# BRD refinado — Hotel Costa Azul

## Objetivo
Centralizar la operación de las 120 habitaciones, reservaciones, estancia, folios, limpieza, mantenimiento y reportes; reducir errores de asignación, fugas de cobro y tiempos de atención.

## Contexto y actores
Hotel de 120 habitaciones: 60 Estándar (2 adultos, $1,200/noche), 40 Dobles (4 personas, $1,800/noche), 20 Suites (4 personas, $3,000/noche). Actores: Huésped, Reservaciones, Recepción, Limpieza/Ama de llaves, Administración y Supervisor de Mantenimiento.

## Alcance incluido
Inventario/disponibilidad en tiempo real; tarifas estacionales; reserva/garantía; cancelación/no-show; check-in y garantía incidental; early/late check-out; cambio por avería/upgrade; salida anticipada; consumos al folio; inspección exprés; limpieza; fuera de servicio/reactivación; PIN administrativo; reportes diarios.

## Fuera de alcance
Motor externo de reservas, integraciones contables, facturación electrónica detallada, proveedores específicos de pago y gestión técnica de usuarios no están definidos por U2; no se implementan como política.

## Reglas BR
- BR-01 inventario 120: 60 Estándar, 40 Doble, 20 Suite.
- BR-02 capacidades 2/4/4.
- BR-03 tarifas $1,200/$1,800/$3,000 MXN por noche.
- BR-04 temporada alta aumenta 35%; baja marzo-junio y septiembre-noviembre; alta julio-agosto, diciembre y Semana Santa.
- BR-05 confirmar con anticipo ≥50% o tarjeta en garantía.
- BR-06 cancelación >48h reembolso 100%; <48h retiene 50% del anticipo.
- BR-07 no-show a 23:59 día de llegada; cobrar primera noche completa a tarjeta y liberar para el día siguiente.
- BR-08 check-in 15:00; check-out 12:00.
- BR-09 early check-in antes de 12:00, habitación lista, cargo 30%; después de 12:00 sin cargo.
- BR-10 late check-out hasta 15:00 cargo 30%; después, noche completa.
- BR-11 INE/Pasaporte del titular, acompañantes; garantía incidental $1,000 voucher o $500 efectivo.
- BR-12 avería: igual o superior sin diferencia; upgrade voluntario: diferencia prorrateada noches restantes.
- BR-13 salida anticipada con ≥24h: noches ocupadas + media noche; mismo día: noche completa sin reembolso.
- BR-14 consumos restaurante/bar, lavandería, estacionamiento con habitación y firma, cargados inmediatamente.
- BR-15 inspección exprés de 5 minutos antes de cierre/liberación de garantía.
- BR-16 limpieza estándar 35–45 minutos; estado Sucia→Limpia/Inspeccionada en tiempo real.
- BR-17 Administración/Supervisor puede poner Fuera de Servicio con motivo y fecha; descontar inventario.
- BR-18 descuentos >10%, condonaciones y anulación de cargos requieren PIN de Administración.
- BR-19 overbooking cero; inventario bloqueado al reservar.
- BR-20 a medianoche disponibles Corte de Caja Diario, Folios Abiertos y Ocupación diaria.

## Criterios de éxito
Habitaciones asignadas sin limpiar: 0. Check-in promedio: <3 minutos. Fugas por consumos no reportados: <1% mensual.

## Supuestos y pendientes
Semana Santa depende de calendario anual; debe configurarse con fechas oficiales. La implementación de demostración calcula temporada alta por julio/agosto/diciembre y marca Semana Santa como pendiente configurable. La integración real de tarjeta/PIN no se simula como pasarela bancaria; se representa el indicador de garantía. Las reglas no definidas en U2/U3 permanecen fuera del alcance.
