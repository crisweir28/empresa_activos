# ================================================================
# utils/permisos.py — Decoradores y helpers de permisos por rol
# ================================================================

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

# Roles con acceso total al sistema
ROLES_ADMIN = {"ti"}

# Roles con acceso al módulo administrativo
ROLES_ADMINISTRATIVO = {"ti", "administrativo"}

# Roles con acceso al módulo de almacén
ROLES_ALMACEN = {"ti", "almacenista"}

# Roles con acceso a RH
ROLES_RH = {"ti", "rh"}

# Todos los roles válidos
ROLES_VALIDOS = {"ti", "administrativo", "almacenista", "rh", "supervisor"}

# Etiquetas legibles
ROL_LABELS = {
    "ti":             "TI / Administrador",
    "administrativo": "Administrativo",
    "almacenista":    "Almacenista",
    "rh":             "Recursos Humanos",
    "supervisor":     "Supervisor",
}

# Colores por rol
ROL_COLORES = {
    "ti":             "rgba(124,92,252,.2)",
    "administrativo": "rgba(251,191,36,.2)",
    "almacenista":    "rgba(34,211,165,.2)",
    "rh":             "rgba(167,139,250,.2)",
    "supervisor":     "rgba(96,96,122,.2)",
}


def es_admin():
    return current_user.is_authenticated and current_user.rol in ROLES_ADMIN


def requiere_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not es_admin():
            flash("No tienes permiso para acceder a esta sección.", "error")
            return redirect(url_for("activos.dashboard"))
        return f(*args, **kwargs)
    return decorated


def requiere_rol(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol not in roles:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("activos.dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def puede_editar_activo(activo):
    if es_admin():
        return True
    # En la nueva estructura el acceso es por rol, no por departamento_id
    return current_user.rol in ("ti", "administrativo", "almacenista")