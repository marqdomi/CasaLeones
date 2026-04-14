# KaiResto — Sistema POS para Restaurante

Sistema punto de venta completo para restaurantes: órdenes, cocina KDS, inventario, facturación CFDI, reportes y más.

**Stack:** Flask 3.1 · PostgreSQL 16 · Redis · Socket.IO · Gunicorn · Docker

---

## Requisitos previos

| Herramienta | Versión mínima | Verificar |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24+ | `docker --version` |
| [Git](https://git-scm.com/) | cualquiera | `git --version` |

No se necesita Python ni Node instalados localmente — todo corre dentro de Docker.

---

## Correr el proyecto localmente

### 1. Clonar el repositorio

```bash
git clone https://github.com/marqdomi/kairest.git
cd kairest
```

### 2. Crear el archivo `.env`

Copia el ejemplo y genera una `SECRET_KEY`:

```bash
cp .env.example .env
```

Edita `.env` y completa `SECRET_KEY`:

```bash
# Genera la clave con:
python3 -c "import secrets; print(secrets.token_hex(32))"
```

El `.env` mínimo para desarrollo local:

```env
SECRET_KEY=<pega_aquí_la_clave_generada>
POSTGRES_PASSWORD=casaleones_secret
APP_PORT=5005
CORS_ORIGINS=http://localhost:5005
```

### 3. Levantar los servicios

```bash
docker compose up --build -d
```

Esto levanta 4 contenedores:
- **web** — Flask + Gunicorn (puerto 5005)
- **db** — PostgreSQL 16 (puerto 5433 en host)
- **redis** — Caché y sesiones
- **backup** — pg_dump automático cada hora

Espera ~30 segundos a que el healthcheck pase. Verifica con:

```bash
docker compose ps
```

Todos deben estar en estado `healthy` o `Up`.

### 4. Aplicar migraciones

```bash
docker compose exec web flask db upgrade
```

### 5. Abrir la app

[http://localhost:5005](http://localhost:5005)

Si es la primera vez verás el **wizard de onboarding** (5 pasos) para configurar el negocio, admin y menú inicial.

---

## Credenciales de desarrollo

Si la base de datos ya tiene datos (ej. clonaste un volumen o restauraste un backup), las cuentas por defecto son:

| Email | Contraseña | Rol |
|---|---|---|
| `superadmin@kainet.mx` | `Admin1234!` | Superadmin |
| `admin@kainet.mx` | `Admin1234!` | Admin |
| `mesero1@kainet.mx` | `Mesero123!` | Mesero |
| `cocinero1@kainet.mx` | `Cocina123!` | Cocina |

> En una DB nueva (onboarding fresh), las credenciales son las que configures en el paso 2 del wizard.

---

## Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f web

# Reiniciar solo el servidor web (sin rebuild)
docker compose restart web

# Acceder a la DB directamente
docker compose exec db psql -U casaleones -d casaleones

# Ejecutar comandos Flask
docker compose exec web flask <comando>

# Parar todo
docker compose down

# Parar y eliminar volúmenes (⚠️ borra la base de datos)
docker compose down -v
```

---

## Estructura del proyecto

```
backend/
├── app.py              # Factory de la app Flask
├── extensions.py       # SQLAlchemy, SocketIO, Login, Limiter
├── models/
│   └── models.py       # Todos los modelos SQLAlchemy
├── routes/             # Blueprints por módulo
│   ├── auth.py
│   ├── meseros.py
│   ├── cocina.py
│   ├── admin_routes.py
│   ├── reportes.py
│   └── ...
├── services/           # Lógica de negocio
│   ├── cfdi.py         # Facturación SAT (Facturapi)
│   ├── pdf_generator.py
│   ├── printer.py      # ESC/POS impresoras térmicas
│   └── ...
├── templates/          # Jinja2 (sin React)
│   ├── base.html
│   ├── login.html
│   ├── layouts/
│   └── ...
└── static/
    ├── css/            # Design System v7 (tokens, dark mode)
    └── img/

migrations/             # Alembic (c001–c009)
tests/                  # pytest suite
docker-compose.yml      # Desarrollo local
docker-compose.prod.yml # Producción
```

---

## Variables de entorno

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Clave Flask (genera con `secrets.token_hex(32)`) |
| `POSTGRES_PASSWORD` | ✅ | `casaleones_secret` | Password de PostgreSQL |
| `APP_PORT` | — | `5005` | Puerto de la app |
| `CORS_ORIGINS` | — | `http://localhost:5005` | Orígenes CORS permitidos |
| `FACTURAPI_KEY` | — | — | API key de Facturapi (CFDI) |
| `SENTRY_DSN` | — | — | DSN de Sentry para monitoreo |
| `PRINTER_TYPE` | — | `none` | `none` / `usb` / `network` |
| `AUTO_PRINT_COMANDA` | — | `false` | Imprimir comanda automáticamente |

---

## Migraciones

Las migraciones usan Flask-Migrate (Alembic). Versiones: `c001` → `c009`.

```bash
# Ver estado actual
docker compose exec web flask db current

# Aplicar pendientes
docker compose exec web flask db upgrade

# Crear nueva migración (tras cambiar models.py)
docker compose exec web flask db migrate -m "descripcion"
```

---

## Tests

```bash
# Correr toda la suite
docker compose exec web pytest tests/ -v

# Con cobertura
docker compose exec web pytest tests/ --cov=backend --cov-report=term-missing
```

---

## Producción

Usa `docker-compose.prod.yml` con las variables de entorno apropiadas:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Ver también los scripts de instalación: `install.sh` (macOS/Linux) y `install.ps1` (Windows).
