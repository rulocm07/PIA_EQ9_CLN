# Registro de cambios respecto al ZIP inicial

## v2 - Revisión para PIA
- [x] Reservas pendientes con habitación asignada en transacción, bloqueo de inventario por intervalos y máximo real de habitaciones.
- [x] SQLite local con esquema nuevo no destructivo; PostgreSQL real para Compose.
- [x] Specification y State Machine aplicadas en los casos de uso.
- [x] Check-in, check-out, folios, consumos, pagos registrados para demo, garantías incidentales, inspección, limpieza y mantenimiento.
- [x] No-show ejecutado periódicamente y recuperación al reiniciar servicio.
- [x] Early / late checkout, cambios por avería/upgrade, salida anticipada, ajustes/PIN.
- [x] Roles de mantenimiento con tokens de demostración; PIN PBKDF2 desde .env.
- [x] Reportes operativos de caja, folios abiertos y ocupación; auditoría de eventos.
- [x] Tests y cobertura automatizada; OpenAPI exportado desde FastAPI.
- [x] CI/CD como configuración en `.github/workflows/ci.yml` y Docker Compose con DB/App/Tests.
- [x] Actualización de documentos, ADRs, trazabilidad, reporte y slides.
- [ ] **No verificado**: ejecutar Compose/PostgreSQL/CI en el equipo; validar despliegue público real.
- [ ] **Por acordar**: calendario Semana Santa, vencimiento reservas Pendientes, criterio contable de anticipos.

El ZIP inicial se conserva como respaldo independiente fuera de esta edición. No se inventa el historial de commits del equipo.
