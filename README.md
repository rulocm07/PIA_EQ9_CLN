# PIA - Hotel Costa Azul | Equipo 9 | Edición corregida v2

Sistema académico de **Componentes de Lógica de Negocios** para el Hotel Costa Azul. Implementado a partir del BRD, BPMN, glosario, 16 historias/Gherkin y arquitectura de las Unidades 2 y 3, conservados sin cambios en `docs/references/`.

**No es un PMS hotelero listo para producción.** Las operaciones bancarias, firmas, PIN y roles se demuestran de manera académica; no manejar información ni tarjetas reales. Para exponerlo en internet se requieren controles adicionales de autenticación, TLS, privacidad y pagos.

## Equipo
Equipo 9: integrantes indicados en documentos originales de U2/U3. Curso: Componentes de Lógica de Negocios. Caso: Hotel Costa Azul.

## Qué se corrigió
- Asignación de habitación **dentro de transacción**, bloquea desde que se crea una reserva pendiente; 61.ª reserva simultánea del tipo Estándar, para iguales fechas, es rechazada.
- Specification combinable para categoría, capacidad, estado y reservas solapadas; State Machine aplicada al dominio.
- Restricción de doble confirmación y estados inválidos.
- Check-in con tipo documental, acompañantes, garantía incidental de 1000/500, folio, early check-in, consumos firmados, pagos simulados, inspección de 5 min, check-out, limpieza de 35 min y mantenimiento.
- No-show automático cada 30 segundos mientras el servidor corre (incluye reintento después de reinicio), penalización y auditoría; si no hay tarjeta registrada, documenta cargo pendiente en lugar de fingir cobro.
- Upgrade/avería, salida anticipada, descuentos y condonaciones con PIN verificable, reportes por fecha.
- Base local SQLite nueva `hotel_v2.db`; Docker Compose utiliza **PostgreSQL real** con otra base separada para tests.
- Tests unitarios y de integración, CI de GitHub Actions, contrato OpenAPI generado desde FastAPI.

## Requisitos
- Python **3.12** (en Windows se verificó que Python 3.14 puede fallar con las dependencias fijadas).
- VS Code, Git y, para contenedores, Docker Desktop.

## Instalación local (Windows PowerShell)
Abrir esta carpeta en VS Code, luego:

```powershell
# Si no tienes el lanzador py, usar el Python 3.12 instalado en tu carpeta local:
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH='.'
$env:DATABASE_PATH='./hotel_v2.db'
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80
python -m uvicorn src.api.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs  -  OpenAPI: http://127.0.0.1:8000/openapi.json

> **Datos previos:** esta versión no sobrescribe `hotel.db` del ZIP original. Usa `hotel_v2.db` porque el esquema se amplió. Si hubiera datos reales en `hotel.db`, respaldarlos y planificar una migración; no renombrar un archivo antiguo para que la aplicación lo lea como v2.

## Docker (DB + App + Tests)
Copiar `.env.example` a `.env`, cambiar `POSTGRES_PASSWORD`, configurar hash PIN y tokens de roles. Nunca hacer commit de `.env`:

```powershell
Copy-Item .env.example .env
docker compose up --build -d db app
docker compose --profile test run --rm tests
docker compose ps
```

Ver http://localhost:8000/docs y http://localhost:8000/health.

**PIN administrativo:** `python scripts/generate_admin_pin.py` pide PIN sin eco y entrega `ADMIN_PIN_HASH=...`. Copiar al `.env` **con comillas simples** (así Docker Compose no interpreta los `$` dentro del hash). Los tokens `ROLE_TOKEN_ADMIN` y `ROLE_TOKEN_MAINTENANCE` son valores distintos, largos y aleatorios, usados en encabezado `X-Role-Token` con el rol correspondiente. En ejecución local sin Docker, exportar estas variables al ambiente de PowerShell antes de iniciar la API.

**IMPORTANTE:** en `docker-compose.yml`, la contraseña se interpola en la URL. Para el prototipo usa una contraseña alfanumérica sin `@`, `:`, `/`, `#` o `%`; para producción usar URL-encoding y un gestor de secretos.

## Endpoints por área
| Área | Rutas principales |
|---|---|
| Salud/API | `GET /health`, `/docs`, `/openapi.json` |
| Inventario | `GET /rooms`, `GET /availability`, `GET /pricing/quote` |
| Reservas | `POST /reservations`, `POST /reservations/{id}/confirm`, `POST .../cancel`, `GET /reservations` |
| Estancia | `POST .../check-in`, `POST .../change-room`, `POST .../early-departure`, `GET .../checkout-preview`, `POST .../check-out` |
| Folios | `GET /folios`, `GET /folios/{id}`, `POST .../consumptions`, `POST .../payments`, `POST .../inspection/request`, `POST .../inspection/complete` |
| Housekeeping | `POST /rooms/{number}/clean`, `POST .../out-of-service`, `POST .../reactivate` |
| Control | `POST /folios/{id}/adjustments`, `POST /jobs/process-no-shows` |
| Administración | `GET /reports/daily?day=AAAA-MM-DD` |

Las solicitudes y campos están detallados en Swagger. En producción real nunca confiar en roles declarados por el cliente sin identidad autenticada.

## Caso rápido en Swagger
1. `POST /reservations` con fechas de llegada/hospedaje vigentes, tipo Estándar y 2 huéspedes. Respuesta incluye el número de habitación bloqueada.
2. `POST /reservations/{id}/confirm` con anticipo de al menos 50% o `card_guarantee: true`.
3. En el **día de llegada**, `POST .../check-in` con `INE`, un acompañante y garantía `voucher` (solo registrar tipo documental, no números reales).
4. `POST /folios/{id}/consumptions` con categoría, monto, habitación y firma de prueba; `POST /folios/{id}/payments` para pagar saldo simulado.
5. Día de salida: solicitar y completar inspección después de 5 minutos; consultar `GET .../checkout-preview` para cualquier recargo; pagar; hacer `POST .../check-out`. Luego la habitación queda Sucia y puede limpiarse tras 35 min.
6. Reporte `GET /reports/daily` para entradas, salidas, caja y folios abiertos.

Para demostrar los 20 requerimientos y casos de excepción, seguir `docs/DEMO.md` y `docs/TRACEABILITY.md`.

## Pruebas, arquitectura y documentación
- `tests/`: unitarias, API, integración SQLite y test PostgreSQL cuando se ejecuta con Compose (`POSTGRES_TEST_URL`). El test PG se omite localmente sin servidor (no afirmar que fue ejecutado).
- `docs/BRD.md`, `docs/USER_STORIES_GHERKIN.md`, `docs/GLOSARIO.md`: análisis.
- `docs/architecture/ARCHITECTURE.md` y `ADR-00*.md`: DDD, UML, patrones, SOLID, decisiones.
- `docs/BPMN.md`, `docs/references/BPMN_U2_original.pdf`: proceso.
- `docs/TRACEABILITY.md`: requisito → código → prueba → evidencias.
- `docs/api/openapi.yaml`: contrato generado por `python scripts/export_openapi.py`.
- `docs/PENDIENTES_PARA_ENTREGA.md`: puntos que requieren verificación/cuenta/decisión humana.
- `Reporte_Final_PIA_Hotel_Costa_Azul.pdf` y `Presentacion_Defensa_PIA_Hotel_Costa_Azul.pptx`: materiales de apoyo preparados; completar evidencias y URL real antes de entregar.

## Repositorio y URL pública
GitHub: **PENDIENTE** — configurar remoto propio y realizar commits auténticos del equipo. Despliegue: **PENDIENTE** — URL pública no verificada. En `docs/PENDIENTES_PARA_ENTREGA.md` están los pasos; no se inventan enlaces ni historial.
