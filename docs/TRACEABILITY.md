# Matriz de trazabilidad verificable - PIA Hotel Costa Azul

Los PDFs de U2 y U3 se conservan íntegros en `docs/references/`. La columna **estado** distingue reglas verificadas de simulaciones y restricciones. **Las 16 User Stories están transcritas en `docs/USER_STORIES_GHERKIN.md`.**

| BR | US | Regla | Código / Endpoint | Prueba | Estado |
|---|---|---|---|---|---|
| 01 | 01 | 120 habitaciones 60/40/20 | `SQLiteRepository.initialize`, `/rooms` | `test_health_docs_and_rooms` | Verificado local |
| 02 | 01 | Capacidad 2/4/4 | `CAPACITIES`, `CapacitySpecification` | `test_value_objects_and_tariffs`, `test_overlap_includes_pending_hold` | Verificado local |
| 03 | 02 | Tarifas base | `BASE_RATES`, `/pricing/quote` | `test_value_objects_and_tariffs` | Verificado local |
| 04 | 02 | +35% julio/agosto/diciembre y Semana Santa | `nightly_rate`, `HOLY_WEEK_RANGES` | `test_value_objects_and_tariffs` | Parcial: calendario Semana Santa por confirmar |
| 05 | 03 | Anticipo 50% o tarjeta | `Reservation.confirm`, `/confirm` | `test_reservation_state_and_confirmation`, `test_rest_reservation_lifecycle_and_invalid_input` | Verificado local; tarjeta simulada |
| 06 | 04 | Cancelación y reembolso | `Reservation.cancel`, `/cancel` | `test_cancel_under_48_and_no_show`, `test_cancel_frees_room_and_duplicate_rejected` | Verificado local; reembolso simulado |
| 07 | 05 | No-show 23:59 | `Reservation.declare_no_show`, `process_no_shows`, tarea periódica | `test_no_show_next_day_releases_room` | Lógica verificada; cargos simulados |
| 08 | 06/08 | Check-in 15:00 / check-out 12:00 | `check_in`, `check_out`, `/checkout-preview` | `test_full_checkin_charges_inspection_checkout_clean` | Verificado local |
| 09 | 07 | Early antes de 12, 30% | `HotelService.check_in` | `test_full_checkin_charges_inspection_checkout_clean` | Verificado local |
| 10 | 08 | Late hasta 15, 30%; después noche | `_late_checkout_fee` | `test_late_checkout_fee` | Verificado local |
| 11 | 06 | INE/Pasaporte, acompañantes y garantía | `check_in`, `Folio` | `test_full_checkin_charges_inspection_checkout_clean` | Simula voucher sin datos sensibles |
| 12 | 09/10 | Cambio por avería/upgrade | `change_room`, `/change-room` | `test_change_room_upgrade_and_failure`, `test_change_room_due_to_failure_no_fee` | Verificado local |
| 13 | 11 | Salida anticipada 24h | `early_departure` | `test_early_departure_policy` | Verificado en caso básico; reembolso simulado |
| 14 | 12 | Consumos y firma | `Folio.add_charge`, `/consumptions` | `test_folio_requires_signature_inspection_and_payment` | Firma de prueba no legal |
| 15 | 13 | Inspección exprés 5 min | `request_inspection`, `inspect` | `test_folio_requires_signature_inspection_and_payment` | Verificado local |
| 16 | 14 | Sucia a Limpia tras limpieza | `Room.mark_dirty`, `mark_clean_inspected` | `test_room_states_and_cleaning` | Mínimo de 35 min verificado |
| 17 | 15 | Bloquear por supervisor/admin | `block_room`, `ensure_maintenance_role` | `test_block_maintenance_and_reactivate`, `test_error_api_roles_payments_and_reports` | Token académico, no IAM completo |
| 18 | 16 | PIN para >10%, condonación/anulación | `authorize_adjustment`, `verify_admin_pin` | `test_sensitive_operations_require_pin` | Pin-hash verificado; ajustes contables simulados |
| 19 | 01/03 | Cero sobreventa | `UnitOfWork`, `NoOverlapSpecification` | `test_no_overbooking_even_with_pending`, `test_atomic_parallel_booking` | Verificado SQLite; PG requiere ejecución Docker |
| 20 | — | Corte, folios abiertos, ocupación | `daily_reports`, `/reports/daily` | `test_full_checkin_charges_inspection_checkout_clean` | Consulta operativa; snapshot histórico pendiente |

## Criterios de software del PIA
- **DDD:** `Room`, `Reservation`, `Folio`, `Money`, `DateRange`; arquitectura y UML en `docs/architecture`.
- **Specification:** `CapacitySpecification`, `RoomTypeSpecification`, `BookingRoomSpecification`, `NoOverlapSpecification` llamadas desde aplicación.
- **State Machine:** `ROOM_TRANSITIONS`, `RESERVATION_TRANSITIONS` usadas en métodos de entidades.
- **REST/OpenAPI:** `src/api/main.py`, `/docs`, `docs/api/openapi.yaml` generado desde código.
- **Persistencia/DB:** SQLAlchemy + SQLite local y PostgreSQL en Docker Compose; PostgreSQL requiere prueba externa.
- **Pruebas/CI:** `tests/`, `.github/workflows/ci.yml`; resultado local registrado en `docs/RESULTADOS_PRUEBAS.txt`; CI requiere subir a GitHub.
- **Producción/Despliegue:** `docker-compose.yml`, `.env.example`, `render.yaml`, pendientes de ejecución externa y captura real.
