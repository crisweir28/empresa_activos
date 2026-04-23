# app/routes/permisos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from ..extensions import socketio
from flask_login import login_required, current_user
from sqlalchemy import text as sqla_text
from ..extensions import db
from ..models.usuario import Rol, Usuario
from ..models.permiso import Modulo, PermisoRol, PermisoUsuario
from ..utils.permisos import es_admin_rh

permisos_bp = Blueprint("permisos", __name__)


def _check_super_admin():
    """Solo el super administrador puede gestionar permisos de TODOS los roles."""
    if current_user.IdRol != 1:
        flash("Solo el Super Administrador puede gestionar permisos de roles.", "error")
        return False
    return True


def _check_puede_ver_permisos_rol():
    """Permite super admin OR admin de área (cada uno ve/edita su propio rol)."""
    if current_user.IdRol == 1:
        return True
    if current_user.es_administrador_area:
        from ..utils.permisos import tiene_permiso
        if tiene_permiso('Roles', 'ver'):
            return True
    flash("No tienes permiso para gestionar permisos de roles.", "error")
    return False


def _check_puede_editar_rol(rol_id: int):
    """Super admin edita cualquier rol. Admin de área solo su propio rol."""
    if current_user.IdRol == 1:
        return True
    if not current_user.es_administrador_area:
        flash("No tienes permiso para modificar permisos de roles.", "error")
        return False
    from ..utils.permisos import tiene_permiso
    if not tiene_permiso('Roles', 'editar'):
        flash("No tienes permiso para modificar permisos de roles.", "error")
        return False
    if rol_id != current_user.IdRol:
        flash("Solo puedes modificar permisos del rol de tu área.", "error")
        return False
    return True


def _check_puede_editar_usuario(usuario_id):
    """Validación de si el usuario actual puede editar permisos de otro usuario.
    - Super admin: puede editar cualquiera
    - Admin RH: puede editar usuarios de CUALQUIER área (excepto admins de área y super admins)
    - Otros admin de área: solo usuarios de su propia área
    """
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

    # Admin RH: puede editar usuarios de cualquier área, EXCEPTO admins de área
    if es_admin_rh():
        if usuario.TipoUsuario == "administrador":
            flash("No tienes permiso para modificar permisos de administradores de área.", "error")
            return False
        return True

    # Otros admin de área: solo usuarios de su misma área
    if usuario.IdDepartamento != current_user.IdDepartamento:
        flash("Solo puedes gestionar permisos de usuarios de tu área.", "error")
        return False

    return True


# ── Permisos por rol ──────────────────────────────────────────
# Super admin: ve y edita todos los roles
# Admin de área: ve y edita solo el rol de su área
@permisos_bp.route("/")
@login_required
def index():
    if not _check_puede_ver_permisos_rol():
        return redirect(url_for("activos.dashboard"))

    es_super = (current_user.IdRol == 1)

    if es_super:
        roles = Rol.query.order_by(Rol.IdRol).all()
    else:
        # Admin de área → solo su propio rol
        roles = Rol.query.filter_by(IdRol=current_user.IdRol).all()

    modulos = Modulo.query.order_by(Modulo.Orden).all()

    # Determinar rol seleccionado
    rol_id = request.args.get("rol", type=int)
    if not es_super:
        # Admin de área: forzar a su propio rol (ignora ?rol=...)
        rol_id = current_user.IdRol
    elif not rol_id and roles:
        rol_id = roles[0].IdRol

    rol_sel = Rol.query.get(rol_id) if rol_id else None

    # Filtrar módulos según área (solo para admin de área)
    if not es_super and current_user.area_nombre:
        modulos_ids_area = _modulos_de_area(current_user.area_nombre)
        if modulos_ids_area:
            modulos = [m for m in modulos if m.IdModulo in modulos_ids_area]

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
    try:
        rol_id = int(request.form.get("rol_id"))
    except (TypeError, ValueError):
        flash("Rol inválido.", "error")
        return redirect(url_for("permisos.index"))

    if not _check_puede_editar_rol(rol_id):
        return redirect(url_for("activos.dashboard"))

    modulos = Modulo.query.all()

    # Admin de área: solo puede tocar módulos de su área
    if current_user.IdRol != 1 and current_user.area_nombre:
        modulos_ids_area = _modulos_de_area(current_user.area_nombre)
        if modulos_ids_area:
            modulos = [m for m in modulos if m.IdModulo in modulos_ids_area]

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
    todos_modulos = Modulo.query.order_by(Modulo.Orden).all()  # ← CAMBIO: todos_modulos
    
    # Agrupar módulos por área
    modulos_agrupados = _agrupar_modulos_por_area(todos_modulos)  # ← NUEVO

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
        modulos_agrupados    = modulos_agrupados,  # ← CAMBIO: era "modulos"
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
        'TI':               [6, 13],     # Equipos TI + Personal Corporativo
        'Tecnología':       [6, 13],     # Equipos TI + Personal Corporativo
        'Recursos Humanos': [10, 13],    # Recursos Humanos + Personal Corporativo
        'Administrativo':   [3, 4, 13],  # Vehículos + Mantenimiento + Personal Corporativo
        'Almacén':          [5],
    }
    return base + mapa.get(area_nombre, [])

def _agrupar_modulos_por_area(modulos):
    """Agrupa módulos en categorías para mostrar en UI de permisos."""
    
    # Definir las áreas y sus módulos
    areas = {
        'Generales': [1, 7, 12, 11],  # Dashboard, Usuarios, Roles, Portal Empleado
        'Administrativo': [3, 4],      # Vehículos, Mantenimiento
        'TI / Tecnología': [6],        # Equipos TI
        'Recursos Humanos': [10],      # RH
        'Almacén': [5],                # Almacén
        'Personal Corporativo': [13],  # Personal Corporativo (cross-area)
    }
    
    agrupados = []
    modulos_dict = {m.IdModulo: m for m in modulos}
    
    for area_nombre, ids_modulos in areas.items():
        modulos_area = [modulos_dict[mid] for mid in ids_modulos if mid in modulos_dict]
        if modulos_area:
            agrupados.append({
                'area': area_nombre,
                'modulos': modulos_area
            })
    
    # Agregar módulos que no están en ninguna categoría
    ids_categorizados = [mid for ids in areas.values() for mid in ids]
    modulos_otros = [m for m in modulos if m.IdModulo not in ids_categorizados]
    if modulos_otros:
        agrupados.append({
            'area': 'Otros',
            'modulos': modulos_otros
        })
    
    return agrupados

# ── API ───────────────────────────────────────────────────────
@permisos_bp.route("/api/rol/<int:rol_id>")
@login_required
def api_permisos_rol(rol_id):
    # Super admin ve cualquier rol; admin de área solo su propio rol
    if current_user.IdRol != 1 and rol_id != current_user.IdRol:
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