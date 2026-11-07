# ADR-002: SQLite para desarrollo y PostgreSQL en Docker
**Estado:** actualizado y aceptado en v2 (06/11/2026).

**Contexto:** BR-19 exige no sobreventa y PIA exige DB + App + Tests en Docker Compose. El ZIP inicial tenía un servicio Alpine sin motor de base de datos. `max(id)+1` y asignaciones sin transacción podían duplicarse.

**Opciones:** SQLite sin bloqueo (rechazado), SQLite con `BEGIN IMMEDIATE` local, PostgreSQL con bloqueo transaccional en Compose.

**Decisión:** SQLAlchemy con SQLite local (`hotel_v2.db` para no modificar la base anterior) y PostgreSQL 16 en `db`. UnitOfWork serializa escrituras y guarda reserva, habitación, folio y auditoría en una sola transacción.

**Consecuencias:** más dependencias y configuración, pero DB real en Compose; transacciones coherentes; el bloqueo global sacrifica paralelismo; cambiar esquema requiere migraciones planificadas. No se afirma haber desplegado ni probado Docker en un servidor remoto.
