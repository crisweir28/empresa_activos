from flask import Flask, send_from_directory
from .config import config
from .extensions import db, login_manager, migrate, socketio, mail


def create_app(env="default"):
    app = Flask(__name__)
    app.config.from_object(config[env])

    # ── Extensiones ───────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins='*')
    mail.init_app(app)   # ← agrega esta línea

    # ── Blueprints ────────────────────────────────────────────────────────────
    from .routes.auth           import auth_bp
    from .routes.activos        import activos_bp
    from .routes.departamentos  import departamentos_bp
    from .routes.administrativo import administrativo_bp
    from .routes.almacenista    import almacenista_bp
    from .routes.ti             import ti_bp
    from .routes.usuarios       import usuarios_bp
    from .routes.permisos       import permisos_bp
    from .routes.proyectos      import proyectos_bp
    from .routes.rh             import rh_bp
    from .routes.portal_empleado import portal_bp
    from .routes.ticketing      import ticketing_bp 
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(activos_bp,        url_prefix="/activos")
    app.register_blueprint(departamentos_bp,  url_prefix="/departamentos")
    app.register_blueprint(administrativo_bp, url_prefix="/administrativo")
    app.register_blueprint(almacenista_bp,    url_prefix="/almacen")
    app.register_blueprint(ti_bp,             url_prefix="/ti")
    app.register_blueprint(usuarios_bp,       url_prefix="/usuarios")
    app.register_blueprint(permisos_bp,       url_prefix="/permisos")
    app.register_blueprint(proyectos_bp,      url_prefix="/proyectos")
    app.register_blueprint(rh_bp,             url_prefix="/rh")
    app.register_blueprint(portal_bp)
    app.register_blueprint(ticketing_bp,      url_prefix="/ticketing")

    # ── Socket events ─────────────────────────────────────────────────────────
    from . import socket_events  # noqa

    # ── Funciones globales Jinja2 ──────────────────────────────────────────────
    from .utils.permisos import tiene_permiso
    app.jinja_env.globals['tiene_permiso'] = tiene_permiso

    # ── Filtros Jinja2 ────────────────────────────────────────────────────────
    @app.template_filter("moneda")
    def filtro_moneda(valor):
        try:
            return f"${float(valor):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"

    @app.template_filter("fecha_corta")
    def filtro_fecha_corta(fecha):
        if fecha is None:
            return "—"
        try:
            return fecha.strftime("%d/%m/%Y")
        except AttributeError:
            return str(fecha)

    @app.template_filter("fecha_relativa")
    def filtro_fecha_relativa(fecha):
        from datetime import datetime
        if fecha is None:
            return "—"
        try:
            diff = datetime.utcnow() - fecha
            dias = diff.days
            if dias == 0:
                horas = diff.seconds // 3600
                if horas == 0:
                    mins = diff.seconds // 60
                    return f"Hace {mins} min" if mins > 0 else "Justo ahora"
                return f"Hace {horas} h"
            elif dias == 1:
                return "Ayer"
            elif dias < 7:
                return f"Hace {dias} días"
            elif dias < 30:
                return f"Hace {dias // 7} semanas"
            else:
                return fecha.strftime("%d/%m/%Y")
        except Exception:
            return str(fecha)

    # ── Seguridad: sin caché ──────────────────────────────────────────────────
    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"]        = "no-cache"
        response.headers["Expires"]       = "0"
        return response

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    # ── Shell context ─────────────────────────────────────────────────────────
    from .models.usuario      import Usuario
    from .models.activo       import Activo
    from .models.departamento import Departamento

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "Usuario": Usuario, "Activo": Activo,
                "Departamento": Departamento}
        
    @app.route('/documents/<path:filename>')
    def serve_document(filename):
        return send_from_directory('documents', filename)

    return app