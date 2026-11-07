# Guía de despliegue y validación (no ejecutado por este paquete)

## Local con PostgreSQL y Docker Desktop
1. Instalar y abrir Docker Desktop.
2. Copiar `.env.example` a `.env`, sustituir contraseña y tokens por valores aleatorios de prueba.
3. Crear hash de PIN con `python scripts/generate_admin_pin.py` y pegar en `.env`.
4. Ejecutar `docker compose up --build -d db app`.
5. Comprobar `docker compose ps`; `db` debe estar **healthy** y `app` **running**.
6. Abrir `http://localhost:8000/health` y `http://localhost:8000/docs`.
7. Ejecutar `docker compose --profile test run --rm tests`: debe correr también el test PostgreSQL (no marcado como skipped).
8. Guardar capturas de contenedores, OpenAPI, pruebas y servicio en carpeta `docs/evidencias/`.

## GitHub Actions
1. Crear repositorio remoto propio y subir el proyecto con Git; hacer commits que correspondan a trabajo auténtico.
2. Verificar `.github/workflows/ci.yml`: job `tests` en Python 3.12 con ≥80% y contrato OpenAPI sincronizado; job `docker` levanta DB/App/Tests y hace smoke test.
3. Entrar en **Actions** y comprobar cada ejecución real. Una configuración de YAML local **no demuestra** pipeline activo.

## Render (opción de demostración)
Se incluye `render.yaml` como ejemplo de Blueprint. Elegir plan y base persistente que sean apropiados y revisar posibles costos antes de activar. Vincular repositorio, configurar `ADMIN_PIN_HASH` y tokens como secretos, publicar. Render suministra `DATABASE_URL`, cuya URL PostgreSQL se adapta al driver psycopg en `repository.py`. Configurar `HOLY_WEEK_RANGES` según fechas validadas.

Antes de compartir una URL, comprobar los endpoints desde una conexión externa. **No ingresar datos personales reales**, ya que la aplicación no tiene un sistema de cuentas ni protección completa de folios y consultas. La creación de cuenta/despliegue no puede verificarse desde este proyecto sin credenciales/acceso autorizados.

## Evidencias imprescindibles
- `pytest` aprobado, porcentaje de cobertura, OpenAPI y casos negativos.
- Docker: 3 servicios definidos, db healthy, app respondiente, tests exitosos.
- GitHub Actions: jobs verdes y commits propios.
- Host público: `/health`, `/docs`, `/openapi.json` funcionales y URL real.

## Problemas típicos
- **Python 3.14 / pydantic-core:** usar Python 3.12.9 en entorno virtual.
- **py no reconocido:** usar `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"`.
- **Docker compose error de contraseña:** completar `POSTGRES_PASSWORD` en `.env`.
- **Postgres no conecta:** comprobar db healthy, red interna y credenciales.
- **Base de datos antigua:** no reusar `hotel.db` con esquema v2.
