# app/routes/permisos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from ..extensions import socketio
from flask_login import login_required, current_user
from sqlalchemy import text as sqla_text
from ..extensions import db
from ..models.usuario import Rol, Usuario
from ..models.permiso import Modulo, PermisoRol, PermisoUsuario

permisos_bp = Blueprint("permisos", __name__)


def _check_super_admin():
    """Solo el super administrador puede gestionar permisos de roles globales."""
    if current_user.IdRol != 1:
        flash("Solo el Super Administrador puede gestionar permisos de roles.", "error")
        return False
    return True


def _check_puede_editar_usuario(usuario_id):
    if current_user.IdRol == 1:
        return True

    if not current_user.es_administrador_area:
        flash("No tienes permiso para gestionar permisos.", "error")
        return False

    from ..utils.permisos import tiene_permiso
    if not tiene_permiso('Roles', 'editar'):
        flash("No tienes permiso para modificar permisos de usuarios.", "error")
        return False

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        flash("Usuario no encontrado.", "error")
        return False

    if usuario.IdRol == 1:
        flash("No puedes modificar permisos de un Super Administrador.", "error")
        return False

    if usuario.IdDepartamento != current_user.IdDepartamento:
        flash("Solo puedes gestionar permisos de usuarios de tu área.", "error")
        return False

    return True


# ── Permisos por rol (solo super admin) ───────────────────────
@permisos_bp.route("/")
@login_required
def index():
    if not _check_super_admin():
        # Admin de área → redirigir a lista de usuarios de su área
        return redirect(url_for("usuarios.lista"))

    roles   = Rol.query.order_by(Rol.IdRol).all()
    modulos = Modulo.query.order_by(Modulo.Orden).all()

    rol_id  = request.args.get("rol", roles[0].IdRol if roles else None, type=int)
    rol_sel = Rol.query.get(rol_id) if rol_id else None

    permisos_raw = PermisoRol.query.filter_by(IdRol=rol_id).all() if rol_id else []
    permisos_map = {
        p.IdModulo: {
            'PuedeVer':      p.PuedeVer,
            'PuedeCrear':    p.PuedeCrear,
            'PuedeEditar':   p.PuedeEditar,
            'PuedeEliminar': p.PuedeEliminar,
        } for p in permisos_raw
    }

    usuarios_rol     = Usuario.query.filter_by(IdRol=rol_id).order_by(Usuario.Nombre).all() if rol_id else []
    usuarios_por_rol = {r.IdRol: Usuario.query.filter_by(IdRol=r.IdRol, Estatus=True).count() for r in roles}

    return render_template("usuarios/permisos.html",
        roles            = roles,
        modulos          = modulos,
        rol_sel          = rol_sel,
        permisos_map     = permisos_map,
        usuarios_rol     = usuarios_rol,
        usuarios_por_rol = usuarios_por_rol,
    )


@permisos_bp.route("/guardar", methods=["POST"])
@login_required
def guardar():
    if not _check_super_admin():
        return redirect(url_for("activos.dashboard"))

    rol_id  = int(request.form.get("rol_id"))
    modulos = Modulo.query.all()

    for m in modulos:
        prefix = f"mod_{m.IdModulo}_"
        try:
            db.session.execute(
                sqla_text("CALL sp_guardar_permisos_rol(:rol,:mod,:ver,:crear,:editar,:eliminar,@res)"),
                {
                    "rol":      rol_id,
                    "mod":      m.IdModulo,
                    "ver":      1 if request.form.get(f"{prefix}ver")      else 0,
                    "crear":    1 if request.form.get(f"{prefix}crear")    else 0,
                    "editar":   1 if request.form.get(f"{prefix}editar")   else 0,
                    "eliminar": 1 if request.form.get(f"{prefix}eliminar") else 0,
                }
            )
            db.session.execute(sqla_text("COMMIT"))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("permisos.index", rol=rol_id))

    flash("Permisos del rol actualizados correctamente.", "success")
    return redirect(url_for("permisos.index", rol=rol_id))


# ── Permisos individuales por usuario ─────────────────────────
@permisos_bp.route("/usuario/<int:usuario_id>")
@login_required
def usuario_permisos(usuario_id):
    if not _check_puede_editar_usuario(usuario_id):
        return redirect(url_for("usuarios.lista"))

    usuario = Usuario.query.get_or_404(usuario_id)
    modulos = Modulo.query.order_by(Modulo.Orden).all()

    # Filtrar módulos según el área del usuario que se está editando
    area_usuario = usuario.area_nombre  # área del usuario editado, no del editor
    if area_usuario:
        modulos_ids_area = _modulos_de_area(area_usuario)
        if modulos_ids_area:
            modulos = [m for m in modulos if m.IdModulo in modulos_ids_area]
    # Si el usuario editado es super admin (sin área), mostrar todos

    permisos_raw = PermisoUsuario.query.filter_by(IdUsuario=usuario_id).all()
    permisos_map = {
        p.IdModulo: {
            'PuedeVer':        p.PuedeVer,
            'PuedeCrear':      p.PuedeCrear,
            'PuedeEditar':     p.PuedeEditar,
            'PuedeEliminar':   p.PuedeEliminar,
            'EsPersonalizado': True,
        } for p in permisos_raw
    }

    permisos_rol = {
        p.IdModulo: {
            'PuedeVer':      p.PuedeVer,
            'PuedeCrear':    p.PuedeCrear,
            'PuedeEditar':   p.PuedeEditar,
            'PuedeEliminar': p.PuedeEliminar,
        } for p in PermisoRol.query.filter_by(IdRol=usuario.IdRol).all()
    }

    tiene_personalizados = len(permisos_raw) > 0

    return render_template("usuarios/permisos_usuario.html",
        usuario              = usuario,
        modulos              = modulos,
        permisos_map         = permisos_map,
        permisos_rol         = permisos_rol,
        tiene_personalizados = tiene_personalizados,
    )


@permisos_bp.route("/usuario/<int:usuario_id>/guardar", methods=["POST"])
@login_required
def usuario_permisos_guardar(usuario_id):
    if not _check_puede_editar_usuario(usuario_id):
        return redirect(url_for("usuarios.lista"))

    modulos = Modulo.query.all()

    for m in modulos:
        prefix = f"mod_{m.IdModulo}_"
        try:
            db.session.execute(
                sqla_text("CALL sp_guardar_permisos_usuario(:uid,:mod,:ver,:crear,:editar,:eliminar,@res)"),
                {
                    "uid":      usuario_id,
                    "mod":      m.IdModulo,
                    "ver":      1 if request.form.get(f"{prefix}ver")      else 0,
                    "crear":    1 if request.form.get(f"{prefix}crear")    else 0,
                    "editar":   1 if request.form.get(f"{prefix}editar")   else 0,
                    "eliminar": 1 if request.form.get(f"{prefix}eliminar") else 0,
                }
            )
            db.session.execute(sqla_text("COMMIT"))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("permisos.usuario_permisos", usuario_id=usuario_id))

    flash("Permisos individuales guardados correctamente.", "success")
    socketio.emit("permisos_actualizados", {"usuario_id": usuario_id}, room=f"user_{usuario_id}")
    return redirect(url_for("permisos.usuario_permisos", usuario_id=usuario_id))


@permisos_bp.route("/usuario/<int:usuario_id>/reset", methods=["POST"])
@login_required
def usuario_permisos_reset(usuario_id):
    if not _check_puede_editar_usuario(usuario_id):
        return redirect(url_for("usuarios.lista"))

    try:
        db.session.execute(
            sqla_text("CALL sp_inicializar_permisos_usuario(:uid, @res)"),
            {"uid": usuario_id}
        )
        db.session.execute(sqla_text("COMMIT"))
        flash("Permisos restablecidos desde el rol.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("permisos.usuario_permisos", usuario_id=usuario_id))


# ── Helper: módulos relevantes por área ───────────────────────
def _modulos_de_area(area_nombre: str) -> list:
    base = [1, 7, 12, 11]  # Dashboard + Usuarios + Roles + Portal Empleado
    mapa = {
        'TI':               [6],
        'Tecnología':       [6],
        'Recursos Humanos': [10],
        'Administrativo':   [3, 4],
        'Almacén':          [5],
    }
    return base + mapa.get(area_nombre, [])


# ── API ───────────────────────────────────────────────────────
@permisos_bp.route("/api/rol/<int:rol_id>")
@login_required
def api_permisos_rol(rol_id):
    if current_user.IdRol != 1:
        return jsonify({"error": "Sin acceso"}), 403
    permisos = PermisoRol.query.filter_by(IdRol=rol_id).all()
    return jsonify([p.to_dict() for p in permisos])


@permisos_bp.route("/api/usuario/<int:usuario_id>")
@login_required
def api_permisos_usuario(usuario_id):
    if not _check_puede_editar_usuario(usuario_id):
        return jsonify({"error": "Sin acceso"}), 403
    permisos = PermisoUsuario.query.filter_by(IdUsuario=usuario_id).all()
    return jsonify([p.to_dict() for p in permisos])