# ADR-005: datos simulados, tokens de rol y hash de PIN
**Estado:** aceptado exclusivamente para demostración académica.

**Contexto:** BR-18 requiere PIN para operaciones sensibles y BR-17 limita bloqueo de habitaciones a dos roles. U2 deja fuera la gestión técnica de usuarios, proveedor de pagos y firma digital real.

**Alternativas:** PIN plano en código (rechazado), sesión/login completo (no definido), variables de entorno + hash PBKDF2 + tokens temporales de demostración.

**Decisión:** almacenar solo `ADMIN_PIN_HASH`, comparar con PBKDF2 y `hmac.compare_digest`; autorizar mantenimiento con `X-Role-Token`. Sin tarjetas ni números de INE reales. Las operaciones financieras son asientos de simulación.

**Consecuencias:** útil para demostrar reglas; no es autenticación multiusuario suficiente para servicio público. Pendiente gestión de usuarios, rotación, rate limit, TLS, CSRF y proceso real de pagos si se amplía el alcance.
