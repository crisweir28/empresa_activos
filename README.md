# ActivosApp — Sistema de Gestión de Activos

Aplicación web Flask para gestionar activos de empresa: equipos, muebles, vehículos, software, etc.

## Estructura

```
empresa_activos/
├── venv/                  # Entorno virtual (no versionar)
├── app/
│   ├── __init__.py        # Application Factory
│   ├── config.py          # Configuración por ambiente
│   ├── extensions.py      # db, login_manager, mail (sin imports circulares)
│   ├── models/            # Modelos SQLAlchemy
│   ├── routes/            # Blueprints Flask
│   ├── schemas/           # Validación Marshmallow
│   ├── tasks/             # Tareas asíncronas (Celery)
│   ├── templates/         # HTML Jinja2
│   └── static/            # CSS, JS, imágenes
├── migrations/            # Flask-Migrate
├── tests/                 # Pruebas unitarias
├── celery_worker.py       # Entry point Celery
├── run.py                 # Entry point Flask
└── requirements.txt
```

## Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Correr (crea DB + datos de ejemplo automáticamente)
python run.py
```

Abre http://localhost:5000

**Credenciales por defecto:** `admin` / `admin123`

## Variables de entorno (opcional)

Crea un archivo `.env` en la raíz:

```env
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///empresa.db
# Para MySQL: mysql+pymysql://usuario:password@localhost/empresa_db

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu@correo.com
MAIL_PASSWORD=tu-app-password

REDIS_URL=redis://localhost:6379/0
```

## Blueprints / Rutas

| Blueprint       | Prefijo          | Descripción              |
|----------------|------------------|--------------------------|
| auth           | /                | Login, logout            |
| activos        | /activos         | CRUD de activos          |
| departamentos  | /departamentos   | CRUD de departamentos    |
