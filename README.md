# 🏨 Hotel Costa Azul — PIA de Componentes de Lógica de Negocios

**Equipo 9 · Proyecto Integrador de Aprendizaje · 2026**

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docs.docker.com/compose/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-4169E1)](https://www.postgresql.org/)

**API pública:** https://pia-eq9-cln.onrender.com/docs  
**Estado de salud:** https://pia-eq9-cln.onrender.com/health  
**Repositorio:** https://github.com/rulocm07/PIA_EQ9_CLN

> **Proyecto académico.** Los cobros, garantías y roles de demostración son simulados. No introducir datos bancarios, documentos de identidad ni secretos reales. La disponibilidad del despliegue gratuito y su base de datos puede cambiar.

## 1. Descripción general

Sistema de gestión de operaciones hoteleras que implementa reglas de negocio para habitaciones, disponibilidad, reservaciones, check-in, consumos, folios, pagos simulados, inspecciones, check-out, limpieza, mantenimiento y reportes. La solución utiliza una **API REST con FastAPI**, separa dominio, aplicación e infraestructura, y puede ejecutarse con SQLite localmente o PostgreSQL mediante Docker Compose y despliegue en Render.

La implementación toma como referencia los documentos de análisis y diseño del proyecto, incluidas las reglas de negocio, historias de usuario, BPMN y decisiones arquitectónicas conservadas en `docs/`.

## 2. Funcionalidades principales

- **Habitaciones:** consulta, disponibilidad por fechas, capacidad, estado, limpieza, bloqueo por mantenimiento y reactivación.
- **Reservaciones:** cotización, creación, confirmación, cancelación, prevención de sobreventa y asignación transaccional.
- **Estancias:** check-in, cambio de habitación, salida anticipada y check-out sujeto a reglas y estados.
- **Folios:** cargos de consumos, pagos y garantías **simulados**, ajustes autorizados e inspección de salida.
- **Automatización:** procesamiento de no-shows y actualización de estados según reglas implementadas.
- **Reportes:** consulta de información operativa diaria.
- **Calidad:** pruebas automatizadas, cobertura mínima configurada del 80 %, integración con Docker y GitHub Actions.

## 3. Tecnologías

| Capa / función | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| API y documentación | FastAPI, Uvicorn, Swagger UI / OpenAPI |
| Persistencia | SQLAlchemy, SQLite (local), PostgreSQL (Docker/Render) |
| Pruebas | pytest, pytest-cov |
| Contenedores | Docker, Docker Compose |
| Integración continua | GitHub Actions |
| Despliegue | Render |
| Control de versiones | Git, GitHub |

## 4. Arquitectura

La organización real de la versión corregida del proyecto separa responsabilidades:

- **Dominio (`src/domain/`)**: entidades, reglas, especificaciones y máquina de estados.
- **Aplicación (`src/application/`)**: coordinación de casos de uso mediante servicios.
- **Infraestructura (`src/infrastructure/`)**: repositorio, persistencia y transacciones.
- **API (`src/api/`)**: endpoints HTTP, validaciones de entrada y documentación OpenAPI.
- **Pruebas (`tests/`)**: verificaciones de dominio, servicios, API y PostgreSQL.

Flujo simplificado:

```text
Cliente / Swagger UI
        |
        v
   FastAPI (API)
        |
        v
Servicios de aplicación
        |
        v
  Dominio y reglas
        |
        v
Repositorio SQLAlchemy
        |
        v
SQLite local / PostgreSQL
```

## 5. Estructura del proyecto

La siguiente estructura corresponde a los **archivos reales de la edición corregida**, no a la estructura conceptual de ejemplo de la imagen:

```text
hotel_costa_azul_pia/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Integración continua: pruebas y Docker
├── docker/
│   └── create-test-db.sql        # Base de datos separada para pruebas
├── docs/
│   ├── api/
│   │   └── openapi.yaml          # Especificación OpenAPI versionada
│   ├── architecture/
│   │   ├── ARCHITECTURE.md       # Diseño y organización técnica
│   │   └── ADR-001...005*.md    # Decisiones de arquitectura
│   ├── evidencias/
│   │   └── INSTRUCCIONES.md      # Guía para capturas del PIA
│   ├── references/               # Documentos originales del proyecto
│   ├── BRD.md                    # Requisitos de negocio
│   ├── BPMN.md                   # Proceso de negocio
│   ├── USER_STORIES_GHERKIN.md   # Historias y criterios de aceptación
│   ├── GLOSARIO.md
│   ├── TRACEABILITY.md           # Trazabilidad requisito-código-prueba
│   ├── DEMO.md                   # Guion de demostración
│   ├── DESPLIEGUE.md             # Instrucciones de publicación
│   ├── INICIAR_EN_WINDOWS.md     # Guía de instalación detallada
│   └── RESULTADOS_PRUEBAS.txt
├── scripts/
│   ├── export_openapi.py         # Generación del contrato API
│   ├── generate_admin_pin.py     # Hash del PIN de demostración
│   └── build_deliverables.py     # Apoyo para entregables
├── src/
│   ├── api/
│   │   └── main.py               # Aplicación y rutas FastAPI
│   ├── application/
│   │   └── services.py           # Casos de uso y reglas coordinadas
│   ├── domain/
│   │   ├── hotel.py              # Modelo de dominio
│   │   ├── specifications.py     # Reglas de elegibilidad
│   │   └── state_machine.py      # Transiciones de estados
│   └── infrastructure/
│       └── repository.py         # Repositorio SQLite / PostgreSQL
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_domain.py
│   ├── test_service.py
│   └── test_postgres_integration.py
├── .dockerignore
├── .env.example                  # Plantilla; sin secretos reales
├── .gitignore
├── CHANGELOG.md
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── requirements-docs.txt
├── README.md
├── Presentacion_Defensa_PIA_Hotel_Costa_Azul.pptx
└── EQ9_Hotel_PIA_CLN.pdf
```

**Relación con la imagen de referencia:** allí se proponen carpetas `entities/`, `value_objects/`, `commands/`, `queries/`, `repositories/` y `routers/` como organización conceptual. En esta implementación, esas responsabilidades se agrupan principalmente en `hotel.py`, `specifications.py`, `services.py`, `repository.py` y `main.py`. **No es necesario crear carpetas vacías ni renombrar archivos para imitar el diagrama.**

## 6. Requisitos previos

1. **Python 3.12**, preferentemente 3.12.9. Se detectaron problemas al instalar dependencias con Python 3.14.
2. VS Code o editor equivalente.
3. Git para descargar y actualizar el repositorio.
4. Docker Desktop **solo** para el entorno con PostgreSQL y pruebas en contenedores.

## 7. Instalación local en Windows

En PowerShell, dentro de la carpeta raíz del proyecto:

```powershell
git clone https://github.com/rulocm07/PIA_EQ9_CLN.git
cd PIA_EQ9_CLN

# Crear el entorno con Python 3.12 instalado en Windows
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1

python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si la activación de PowerShell está bloqueada, usa directamente `.\.venv\Scripts\python.exe` en lugar de `python` para los comandos siguientes. **No subas `.venv/` a GitHub.**

### Iniciar la API con SQLite

```powershell
$env:PYTHONPATH='.'
$env:DATABASE_PATH='./hotel_v2.db'
$env:ENABLE_SCHEDULER='false'
python -m uvicorn src.api.main:app --reload
```

Abre:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json
- **Health:** http://127.0.0.1:8000/health

Detén el servidor con **Ctrl+C**. La base SQLite local no es la misma base que PostgreSQL en Render: las reservaciones de una no aparecerán automáticamente en la otra.

## 8. Variables de entorno y seguridad

Para Docker, crea tu archivo privado de configuración:

```powershell
Copy-Item .env.example .env
```

Completa **sin publicar valores reales**:

| Variable | Propósito |
|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL en Compose |
| `POSTGRES_PASSWORD` | Contraseña local de PostgreSQL |
| `POSTGRES_DB` | Nombre de base de datos |
| `DATABASE_URL` | Cadena de conexión; en Render se configura como secreto del servicio |
| `ADMIN_PIN_HASH` | Hash generado para operaciones administrativas |
| `ROLE_TOKEN_ADMIN` | Token de demostración para rol administrativo |
| `ROLE_TOKEN_MAINTENANCE` | Token de demostración para mantenimiento |
| `HOLY_WEEK_RANGES` | Rangos de fechas especiales definidos por el equipo |
| `ENABLE_SCHEDULER` | Activa/desactiva procesamiento periódico de no-shows |

Para generar el hash del PIN:

```powershell
python scripts/generate_admin_pin.py
```

El PIN se escribe **sin que aparezcan caracteres en pantalla**; es normal. En `.env` para Docker Compose, copia la línea `ADMIN_PIN_HASH=...` con las comillas simples indicadas por la guía para proteger los caracteres `$`. En Render, pega **solo el valor** en el campo correspondiente. No compartas PIN, hashes, contraseñas ni tokens en capturas, reportes o commits. Si alguno se expuso, reemplázalo.

## 9. Docker Compose: PostgreSQL + API + pruebas

Con Docker Desktop abierto y `.env` configurado:

```powershell
docker compose up --build -d db app
docker compose ps
```

La aplicación estará disponible en http://localhost:8000/docs. Verifica `db` saludable y `app` en ejecución.

Para lanzar las pruebas con base PostgreSQL separada:

```powershell
docker compose --profile test run --rm tests
```

Para ver registros y detener servicios:

```powershell
docker compose logs --tail=100 app
docker compose down
```

`docker compose down` detiene los contenedores sin eliminar el volumen por defecto. **No uses `docker compose down -v`** salvo que quieras borrar los datos persistidos en los volúmenes.

## 10. Pruebas automatizadas y cobertura

Ejecuta en la raíz del repositorio, con el entorno virtual activo:

```powershell
$env:PYTHONPATH='.'
$env:ENABLE_SCHEDULER='false'
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80
```

La configuración exige **cobertura mínima del 80 %**. Comprueba la fila `TOTAL`, el porcentaje y el resumen `passed / skipped / failed` al final de la ejecución. La prueba de integración PostgreSQL puede aparecer como `skipped` si no existe una base de pruebas configurada; para comprobarla usa Docker Compose.

> Evidencia: captura del comando, fila `TOTAL` y resumen final. No presentar una cobertura histórica como resultado de una ejecución actual.

## 11. API REST y Swagger

| Función | Método y ruta |
|---|---|
| Estado del sistema | `GET /health` |
| Habitaciones | `GET /rooms` |
| Disponibilidad | `GET /availability` |
| Cotización | `GET /pricing/quote` |
| Listar reservaciones | `GET /reservations` |
| Crear reservación | `POST /reservations` |
| Confirmar reservación | `POST /reservations/{reservation_id}/confirm` |
| Cancelar reservación | `POST /reservations/{reservation_id}/cancel` |
| Check-in | `POST /reservations/{reservation_id}/check-in` |
| Vista previa de salida | `GET /reservations/{reservation_id}/checkout-preview` |
| Check-out | `POST /reservations/{reservation_id}/check-out` |
| Folios | `GET /folios` |
| Reporte diario | `GET /reports/daily` |

Los parámetros y cuerpos JSON exactos se consultan en Swagger; no inventes campos. El conjunto completo de rutas se encuentra en `/openapi.json` y `docs/api/openapi.yaml`.

### Prueba básica guiada

1. Abre `/docs` y ejecuta `GET /health`. Verifica código HTTP `200` y estado `ok`.
2. Ejecuta `GET /rooms` para comprobar el inventario.
3. Ejecuta `GET /reservations`. Si responde `[]`, **no hay reservaciones en esa base**: primero crea una con `POST /reservations`.
4. Conserva el `id` devuelto por la creación. Úsalo en las operaciones de confirmación, check-in y check-out.
5. Respeta las fechas y transiciones válidas. **Un HTTP 400 no demuestra por sí solo un defecto:** revisa el campo `detail` para identificar qué regla rechazó la solicitud.
6. Para un flujo completo, sigue `docs/DEMO.md`. Un check-out exitoso puede modificar el estado y los datos de la reservación de prueba.

## 12. Integración continua con GitHub Actions

El flujo se define en `.github/workflows/ci.yml` y ejecuta comprobaciones automáticas del proyecto. Para revisar los resultados:

1. Abre el repositorio en GitHub.
2. Entra en **Actions**.
3. Selecciona la ejecución del último commit.
4. Verifica los trabajos **`tests`** y **`docker`** y abre sus registros si hay errores.
5. Conserva una captura del estado exitoso para el reporte.

Para subir cambios desde la raíz del proyecto:

```powershell
git status
git add .
git commit -m "Actualizar documentacion del PIA"
git push origin main
```

Revisa siempre `git status` antes del commit y verifica que `.env`, `.venv/` y archivos con credenciales no estén incluidos.

## 13. Despliegue en Render

El proyecto se ha desplegado como servicio web Docker y utiliza una base PostgreSQL de Render. Para replicarlo:

1. Conecta el repositorio GitHub al servicio web de Render.
2. Selecciona **Docker** y la rama `main`.
3. Configura `DATABASE_URL` con la URL **interna** de PostgreSQL si ambos servicios están en Render y pueden comunicarse por su red privada.
4. Configura los secretos `ADMIN_PIN_HASH`, `ROLE_TOKEN_ADMIN` y `ROLE_TOKEN_MAINTENANCE` en **Environment**.
5. Despliega y espera el estado **Live**.
6. Comprueba `/docs`, `/health` y `/rooms`.

**Nota:** el plan gratuito puede suspender instancias por inactividad y las bases gratuitas pueden expirar. Un despliegue `Live` y un `GET /health` exitoso verifican disponibilidad, **no garantizan persistencia**. Para verificarla, crea una reservación de prueba, comprueba que aparece en `GET /reservations`, reinicia el servicio y vuelve a consultarla.

## 14. Evidencias y entregables del PIA

Documenta resultados **reales**, no solo pantallas de configuración:

- [ ] Pytest aprobado con cobertura ≥80 %.
- [ ] GitHub Actions con `tests` y `docker` exitosos.
- [ ] Docker Compose: base de datos y API ejecutándose.
- [ ] Render con estado `Live`.
- [ ] Swagger UI disponible públicamente.
- [ ] `GET /health` y `GET /rooms` respondiendo `200`.
- [ ] Ejemplos de reglas de negocio y transiciones de estados, con respuestas de la API.
- [ ] Evidencia de PostgreSQL y, cuando se requiera, prueba de persistencia.
- [ ] Reporte PDF, presentación, repositorio y enlace del despliegue.

Estas son **evidencias recomendadas** para demostrar el funcionamiento; la lista exacta de entregables debe contrastarse con la rúbrica original en `docs/references/Rubrica_PIA_original.docx`.

## 15. Documentación complementaria

| Documento | Contenido |
|---|---|
| `docs/BRD.md` | Requisitos de negocio |
| `docs/BPMN.md` | Flujo del proceso |
| `docs/USER_STORIES_GHERKIN.md` | Historias y escenarios |
| `docs/GLOSARIO.md` | Términos de dominio |
| `docs/architecture/ARCHITECTURE.md` | Arquitectura y patrones |
| `docs/TRACEABILITY.md` | Relación entre requisitos, implementación y pruebas |
| `docs/DEMO.md` | Demostración funcional |
| `docs/DESPLIEGUE.md` | Despliegue en Render |
| `docs/INICIAR_EN_WINDOWS.md` | Instrucciones para Windows |
| `docs/evidencias/INSTRUCCIONES.md` | Organización de capturas |

## 16. Problemas frecuentes

**`py` no se reconoce:** invoca Python 3.12 por su ruta completa, como se muestra en la sección de instalación.

**Error instalando `pydantic-core` con Python 3.14:** crea de nuevo el entorno virtual usando Python 3.12 e instala las dependencias.

**`ModuleNotFoundError: No module named 'src'`:** ejecuta comandos desde la raíz del repositorio y define `$env:PYTHONPATH='.'`.

**`GET /reservations` devuelve `[]`:** la base conectada no contiene reservaciones; no significa necesariamente que falle el endpoint.

**`HTTP 400` al hacer check-out:** revisa `Response body` para determinar qué regla de negocio se incumplió; verifica fechas, estado, inspección y saldo según corresponda.

**Swagger funciona pero no hay datos después de un despliegue:** confirma que `DATABASE_URL` está configurada y que el servicio no está usando una base SQLite local efímera.

**Tests locales aprobados pero integración PostgreSQL omitida:** ejecuta las pruebas del perfil Docker con `POSTGRES_TEST_URL` configurada por Compose.

## 17. Alcance y limitaciones

Este proyecto es una demostración académica de lógica de negocios. No incluye una pasarela bancaria real ni debe emplearse para procesar información sensible de huéspedes. La autenticación y la gestión de secretos requerirían controles adicionales para un entorno productivo.

---

**Hotel Costa Azul · Equipo 9 · Componentes de Lógica de Negocios · 2026**
