# Guía paso a paso en Windows / VS Code

**Importante: esta es una edición nueva del proyecto.** No sobrescribir la carpeta donde tienes la versión anterior hasta respaldarla. Extraer `PIA_Hotel_Costa_Azul_Equipo9_CORREGIDO.zip` en una carpeta nueva.

## 1. Abrir la carpeta correcta
En VS Code: File > Open Folder > `hotel_costa_azul_pia`. Confirmar que existen `src`, `tests`, `docs`, `requirements.txt`, `.github` y `docker-compose.yml`.

## 2. Preparar Python 3.12.9
Abre Terminal > New Terminal (PowerShell):

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" --version
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si `Activate.ps1` no se puede ejecutar por política de PowerShell, utiliza `.\.venv\Scripts\python.exe` para ejecutar Python sin activación, sin modificar la política del sistema.

## 3. Ejecutar las pruebas

```powershell
$env:PYTHONPATH='.'
$env:ENABLE_SCHEDULER='false'
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=80
```

Objetivo: pruebas aprobadas y cobertura ≥80%. Guarda una captura de la terminal, especialmente de `TOTAL` y `passed/skipped`. El test PostgreSQL se omite en ejecución local porque requiere Docker.

## 4. Ejecutar la API

```powershell
$env:DATABASE_PATH='./hotel_v2.db'
$env:ENABLE_SCHEDULER='true'
python -m uvicorn src.api.main:app --reload
```

Abre http://127.0.0.1:8000/docs. Prueba primero `GET /health` y `GET /rooms` (120 registros); luego `GET /availability` y `POST /reservations`. El número de habitación se asigna al crearla. Presiona Ctrl+C para detener el servidor.

## 5. Habilitar PIN y roles en demo
En otra terminal de la carpeta:

```powershell
python scripts/generate_admin_pin.py
```

Genera el hash desde un PIN de prueba elegido por el equipo. Para Docker, copiar la línea completa a `.env` y configurar tokens. Nunca subir `.env` al repositorio.

## 6. Validar DB real + App + Tests con Docker Desktop

```powershell
Copy-Item .env.example .env
# Edita .env: POSTGRES_PASSWORD, ADMIN_PIN_HASH, ROLE_TOKEN_ADMIN, ROLE_TOKEN_MAINTENANCE
docker compose up --build -d db app
docker compose ps
docker compose --profile test run --rm tests
```

Se espera `db` healthy, `app` running y tests sin saltarse la prueba PostgreSQL. Si no tienes Docker Desktop, detente aquí: **no afirmes que el requisito está verificado**.

## 7. GitHub
Si ya tienes repositorio conectado, usar `git status`, `git add .`, `git commit -m "Implementar PIA Hotel Costa Azul"` y `git push`. Si es repositorio nuevo, crear el remoto en GitHub y conectarlo antes de push. Es necesario comprobar que Actions queda en verde y que el historial corresponde a trabajo auténtico del equipo.

## 8. Desplegar y preparar reporte
Ver `docs/DESPLIEGUE.md` (Render). Tomar las evidencias señaladas en `docs/evidencias/INSTRUCCIONES.md`, editar el reporte con esas capturas y la URL pública real, y ensayar la presentación. **El reporte preparado ya contiene la arquitectura, tablas, pruebas locales y el BPMN original; faltan capturas de la computadora y servicios del equipo.**

## Datos del negocio por aclarar
Confirmar fechas de Semana Santa y tiempo máximo de reservas Pendientes. Se registran en `docs/PENDIENTES_PARA_ENTREGA.md` y nunca se inventan.
