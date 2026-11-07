# Guion de demostración - Hotel Costa Azul

Requiere API activa, Swagger en `/docs` y base de datos de pruebas/ejemplo. Usar **datos completamente ficticios**. Para demo del flujo completo, elegir llegada igual a la fecha real del día y salida posterior (2 noches) o ejecutar la suite de tests con reloj de prueba.

## 1. Conceptos para defensa
- Explicar entidades y Value Objects (`Money`, `DateRange`), por qué `Reservation` no permite confirmar 2 veces.
- Explicar combinación `RoomTypeSpecification AND CapacitySpecification AND BookingRoomSpecification AND NoOverlapSpecification`.
- Explicar UoW: asignación y bloqueo hechos en misma transacción; en 60 habitaciones solo 60 reservas del mismo tipo/fecha.
- Explicar `ROOM_TRANSITIONS` / `RESERVATION_TRANSITIONS` y transiciones inválidas.
- Diferenciar una prueba del **código** de una validación del **despliegue en Docker/Render**.

## 2. Reservaciones
1. `GET /availability` con tipo Estándar, huéspedes 2 y fechas del ejemplo.
2. `POST /reservations` con `guest_name: Ana Ejemplo`, `check_in` y `check_out`, `room_type: Estándar`, `guests: 2`.
3. Anotar `id`, `room_number` y `total_mxn`. Repetir disponibilidad: la habitación ya no aparece, aunque estado Pendiente.
4. `POST /reservations/{id}/confirm` enviando depósito del 50%. Repetir: debe devolver error 400 de transición.
5. En una base aislada de pruebas, repetir 60 veces; la 61.ª debe ser rechazada (test automatizado, no es necesario usar la API 61 veces).

## 3. Estancia y folio
6. Durante día de llegada, `POST .../check-in` con tipo `INE` (sin número), nombres ficticios de acompañantes y `voucher`; guardar `folio_id`.
7. `POST /folios/{folio_id}/consumptions`: categoría `lavandería`, descripción `Lavado`, monto `100`, `signature: firma-demo`, habitación asignada.
8. `POST /folios/{folio_id}/payments`: monto del saldo, método `efectivo`, `terminal` o `transferencia` (son registros simulados).
9. Solicitar inspección, revisar que antes de 5 min falla, al cumplir 5 min completar. Mostrar `GET /reservations/{id}/checkout-preview` para late checkout.
10. `POST .../check-out`: si saldo o inspección pendientes da error; si está saldado cierra y habitación pasa a Sucia. Tras 35 min, `POST /rooms/{num}/clean` pasa a Limpia/Inspeccionada.

## 4. Excepciones
- Solicitar cambio a habitación superior con `reason: upgrade` y mostrar diferencia de noches restantes.
- Solicitar cambio con `reason: avería` y cargo cero.
- Bloquear habitación con rol Recepción: falla. Con `X-Role-Token` configurado + actor Administración/Supervisor: funciona si no hay reservas previas.
- Descuento mayor al 10% sin `admin_pin`: rechazo; con PIN correcto: se registra ajuste.
- No-show automático con reserva confirmada que no hizo check-in a las 23:59; mostrar el test `test_no_show_next_day_releases_room` si no conviene esperar a la hora real.

## 5. Evidencia final
- `python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80`
- `docker compose --profile test run --rm tests`
- captura verde de GitHub Actions
- Swagger `/docs` desde URL pública verificada
- matrices de trazabilidad, UML, ADR, BPMN visual original.

**Nota:** no enviar información bancaria ni imágenes de INE/pasaporte; aquí solo se procesa el tipo documental para demostración.
