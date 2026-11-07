# Pendientes reales antes de declarar «PIA completado»

Los siguientes puntos **no se pueden certificar solo modificando un ZIP**, y no deben presentarse como terminados ante el profesor sin verificar:

1. **GitHub:** subir esta edición a un repositorio propiedad del equipo, crear commits reales (no fabricar historial), verificar que `Actions` quede verde. Agregar URL exacta al README.
2. **Docker/PostgreSQL:** ejecutar `docker compose up -d --build db app` y `docker compose --profile test run --rm tests`, confirmar contenedores y test PostgreSQL. El entorno de generación no dispone de Docker, así que no se valida aquí.
3. **Despliegue:** publicar en Render/Railway/Fly u otro host, proporcionar variables de entorno y BD persistente, comprobar `/health`, `/docs` y `/openapi.json` desde internet con datos ficticios. Adjuntar URL real.
4. **Evidencias:** capturas auténticas de VS Code, pytest/coverage, Swagger (caso positivo y rechazo), cambios de estado, Docker Compose, Actions y despliegue. Colocar en `docs/evidencias/` y actualizar el reporte final antes de entregar.
5. **Calendario Semana Santa:** pedir fechas oficiales/año o confirmarlas con el equipo; cargar `HOLY_WEEK_RANGES`. Sin ellas no hay cálculo automático completo para Semana Santa. Enero/febrero tampoco tienen una temporada definida explícitamente en el BRD y se aplica la tarifa base a modo de decisión provisional.
6. **Política de vencimiento de Pendiente:** consultar con el profesor/stakeholder cuándo caduca una reserva sin garantía; hoy bloquea inventario hasta intervención manual, para no generar sobreventa.
7. **Política contable/cobros:** no hay proveedor de pagos ni manejo real de tarjeta, reversos, captura de garantía o método del anticipo en la fuente. Definir tratamiento de anticipo en corte de caja si se exige precisión bancaria. No ingresar tarjetas reales.
8. **Reporte y defensa:** ajustar capturas, evidencia de GitHub y URL, conclusiones con resultados verificables; ensayar preguntas de DDD, UnitOfWork, Specification, State Machine y efectos de falla.
9. **Riesgos de producción:** autenticación multiusuario, rate limit del PIN, gestión segura de sesiones, acceso a folios, cifrado de datos y backups no están listos para exposición pública de información real.
10. **Requisito de trayectoria:** el docente exige continuidad con U2/U3 y contribuciones del equipo. Los PDFs originales están anexados, pero cada integrante debe poder explicar los cambios que realmente realizó.

**Este documento es una lista de verificación honesta.** No inventar capturas, despliegue, hechos de pagos, estados de CI o fechas de calendario.
