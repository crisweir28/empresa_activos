# ================================================================
# utils/permisos.py — Decoradores y helpers de permisos por rol
# ================================================================

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user
from ..extensions import db

# Roles con acceso total al sistema
ROLES_ADMIN = {"admin"}

# Roles con acceso al módulo administrativo
ROLES_ADMINISTRATIVO = {"admin", "administrativo"}

# Roles con acceso al módulo de almacén
ROLES_ALMACEN = {"admin", "almacenista"}

# Roles con acceso a RH
ROLES_RH = {"admin", "rh"}

# Todos los roles válidos
ROLES_VALIDOS = {"admin", "ti", "administrativo", "almacenista", "rh", "supervisor"}


def es_admin():
    return current_user.is_authenticated and current_user.rol == "admin"


def es_admin_rh():
    """True si el usuario es admin de área de RH Y tiene permiso en módulo 'Recursos Humanos'."""
    if not current_user.is_authenticated:
        return False
    if current_user.IdRol == 1:
        return False
    if current_user.rol != "rh" or not current_user.es_administrador_area:
        return False
    
    return tiene_permiso('Recursos Humanos', 'ver')


def puede_gestionar_usuarios_globales():
    """True si el usuario puede gestionar usuarios de CUALQUIER área."""
    if not current_user.is_authenticated:
        return False
    if current_user.IdRol == 1:
        return True
    return es_admin_rh()


def puede_editar_activo(activo):
    if es_admin():
        return True
    return current_user.rol in ("administrativo", "almacenista")


# ── Validación de permisos individuales ──────────────────────
def tiene_permiso(modulo_nombre: str, accion: str = "ver") -> bool:
    """
    Verifica si el usuario actual tiene permiso en un módulo.
    Admin siempre tiene acceso total.
    Para otros roles, consulta PermisoUsuario primero, luego PermisoRol.
    """
    if not current_user.is_authenticated:
        return False
    if current_user.rol == "admin":
        return True

    try:
        from ..models.permiso import PermisoUsuario, PermisoRol, Modulo

        # FORZAR REFRESH DE LA SESIÓN (limpiar cache de SQLAlchemy)
        db.session.expire_all()

        modulo = Modulo.query.filter_by(Nombre=modulo_nombre).first()
        
        if not modulo:
            return False

        # Primero buscar permiso individual del usuario
        pu = PermisoUsuario.query.filter_by(
            IdUsuario=current_user.id,
            IdModulo=modulo.IdModulo
        ).first()

        if pu:
            mapa = {
                "ver":      pu.PuedeVer,
                "crear":    pu.PuedeCrear,
                "editar":   pu.PuedeEditar,
                "eliminar": pu.PuedeEliminar,
            }
            return bool(mapa.get(accion, False))

        # Si no tiene permiso individual, buscar el del rol
        pr = PermisoRol.query.filter_by(
            IdRol=current_user.IdRol,
            IdModulo=modulo.IdModulo
        ).first()

        if pr:
            mapa = {
                "ver":      pr.PuedeVer,
                "crear":    pr.PuedeCrear,
                "editar":   pr.PuedeEditar,
                "eliminar": pr.PuedeEliminar,
            }
            return bool(mapa.get(accion, False))

        return False

    except Exception as e:
        print(f">>> ERROR en tiene_permiso: {e}")
        return False


def requiere_permiso(modulo_nombre: str, accion: str = "ver"):
    """Decorador que bloquea rutas si el usuario no tiene permiso."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            
            if not tiene_permiso(modulo_nombre, accion):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated
    return decorator


def requiere_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not es_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def requiere_rol(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator