# app/routes/usuarios.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from ..extensions import socketio
from flask_login import login_required, current_user
from passlib.context import CryptContext
from ..extensions import db
from ..models.usuario import Usuario, Rol, AREAS_CON_MODULO
from ..models.departamento import Departamento
from datetime import datetime
from ..tasks.correo import enviar_bienvenida
from ..utils.permisos import requiere_permiso

usuarios_bp = Blueprint("usuarios", __name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Mapa área → IdRol automático ──────────────────────────────
AREA_ROL_MAP = {
    'TI':               5,  # Usuario TI
    'Tecnología':       5,  # Usuario TI
    'Recursos Humanos': 4,  # Recursos Humanos
    'Administrativo':   2,  # Administrativo
    'Almacén':          3,  # Almacenista
}

def _rol_por_area(nombre_area: str, tipo: str) -> int:
    """Asigna IdRol automáticamente según área y tipo."""
    if nombre_area in AREA_ROL_MAP:
        return AREA_ROL_MAP[nombre_area]
    return 6  # Supervisor para áreas corporativas sin módulo


def _check_admin():
    if current_user.IdRol == 1:
        return True
    if not current_user.es_administrador_area:
        flash("No tienes permiso para gestionar usuarios.", "error")
        return False
    # Admin de área verifica permiso específico
    from ..utils.permisos import tiene_permiso
    if not tiene_permiso('Usuarios', 'ver'):
        flash("No tienes permiso para gestionar usuarios.", "error")
        return False
    return True


def _solo_super_admin():
    if current_user.IdRol != 1:
        flash("Solo el Super Administrador puede realizar esta acción.", "error")
        return False
    return True


# ── Lista ─────────────────────────────────────────────────────
@usuarios_bp.route("/")
@login_required
def lista():
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    area_filtro = request.args.get("area", "")
    tipo_filtro = request.args.get("tipo", "")
    query       = Usuario.query

    if area_filtro:
        query = query.filter(Usuario.IdDepartamento == area_filtro)
    if tipo_filtro:
        query = query.filter(Usuario.TipoUsuario == tipo_filtro)

    # Admin de área solo ve usuarios de su área
    if current_user.IdRol != 1 and current_user.IdDepartamento:
        query = query.filter(
        Usuario.IdDepartamento == current_user.IdDepartamento,
        Usuario.IdRol != 1  # ← ocultar ninjas
    )

    usuarios      = query.order_by(Usuario.Nombre).all()
    roles         = Rol.query.all()
    departamentos = Departamento.query.order_by(Departamento.nombre).all()

    return render_template("usuarios/lista.html",
        usuarios      = usuarios,
        roles         = roles,
        departamentos = departamentos,
        area_filtro   = area_filtro,
        tipo_filtro   = tipo_filtro,
        areas_modulo  = AREAS_CON_MODULO,
    )


# ── Crear ─────────────────────────────────────────────────────
@usuarios_bp.route("/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Usuarios', 'crear')
def nuevo():
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo",   "").strip()

    if Usuario.query.filter_by(NombreUsuario=username).first():
        flash(f"El usuario '{username}' ya existe.", "error")
        return redirect(url_for("usuarios.lista"))
    if Usuario.query.filter_by(Correo=correo).first():
        flash(f"El correo '{correo}' ya está registrado.", "error")
        return redirect(url_for("usuarios.lista"))

    password = request.form.get("password", "").strip()
    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("usuarios.lista"))

    depto_id = request.form.get("departamento_id")
    tipo     = request.form.get("tipo_usuario", "empleado")

    # Admin de área solo puede crear empleados de su área
    if current_user.IdRol != 1:
        depto_id = current_user.IdDepartamento
        tipo     = "empleado"

    # Asignar IdRol automáticamente según área
    depto    = Departamento.query.get(int(depto_id)) if depto_id else None
    id_rol   = _rol_por_area(depto.nombre if depto else '', tipo)

    u = Usuario(
        NombreUsuario   = username,
        Nombre          = request.form.get("nombre", "").strip(),
        ApellidoPaterno = request.form.get("apellido_paterno", "").strip(),
        ApellidoMaterno = request.form.get("apellido_materno", "").strip() or None,
        NumeroTelefono  = request.form.get("telefono", "").strip() or None,
        Correo          = correo,
        Contrasena      = pwd_context.hash(password),
        Estatus         = True,
        PrimerLogin     = True,
        IdRol           = id_rol,
        IdDepartamento  = int(depto_id) if depto_id else None,
        TipoUsuario     = tipo,
    )
    db.session.add(u)
    db.session.commit()

    try:
        enviar_bienvenida(
            correo   = correo,
            nombre   = f"{u.Nombre} {u.ApellidoPaterno}",
            username = username,
            password = password,  # variable local, antes del hash
        )
        flash(f"Usuario '{username}' creado y correo enviado.", "success")
    except Exception:
        flash(f"Usuario '{username}' creado, pero no se pudo enviar el correo.", "warning")

    socketio.emit('usuarios_actualizados', {'accion': 'nuevo'})
    return redirect(url_for("usuarios.lista"))


# ── Editar ────────────────────────────────────────────────────
@usuarios_bp.route("/<int:id>/editar", methods=["POST"])
@login_required
@requiere_permiso('Usuarios', 'editar')
def editar(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    u        = Usuario.query.get_or_404(id)
    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo",   "").strip()

    dup_user = Usuario.query.filter(
        Usuario.NombreUsuario == username, Usuario.IdUsuario != id
    ).first()
    dup_mail = Usuario.query.filter(
        Usuario.Correo == correo, Usuario.IdUsuario != id
    ).first()

    if dup_user:
        flash(f"El usuario '{username}' ya existe.", "error")
        return redirect(url_for("usuarios.lista"))
    if dup_mail:
        flash(f"El correo '{correo}' ya está registrado.", "error")
        return redirect(url_for("usuarios.lista"))

    u.NombreUsuario   = username
    u.Nombre          = request.form.get("nombre", "").strip()
    u.ApellidoPaterno = request.form.get("apellido_paterno", "").strip()
    u.ApellidoMaterno = request.form.get("apellido_materno", "").strip() or None
    u.NumeroTelefono  = request.form.get("telefono", "").strip() or None
    u.Correo          = correo
    u.Estatus         = request.form.get("estatus") == "1"

     # Solo super admin puede cambiar área y tipo
    if current_user.IdRol == 1:
        depto_id = request.form.get("departamento_id")
        tipo     = request.form.get("tipo_usuario", "empleado")
        depto          = Departamento.query.get(int(depto_id)) if depto_id else None
        u.IdDepartamento = int(depto_id) if depto_id else None
        u.TipoUsuario    = tipo
        u.IdRol          = _rol_por_area(depto.nombre if depto else '', tipo)

    # Cambio de contraseña opcional
    nueva_pass = request.form.get("nueva_password", "").strip()
    if nueva_pass:
        if len(nueva_pass) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("usuarios.lista"))
        u.Contrasena  = pwd_context.hash(nueva_pass)
        u.PrimerLogin = True  # obliga a cambiarla en el próximo login

    db.session.commit()  # ← un solo commit al final
    flash(f"Usuario '{username}' actualizado.", "success")
    socketio.emit('usuarios_actualizados', {'accion': 'editar', 'usuario_id': id})
    socketio.emit('permisos_actualizados', {'usuario_id': id})
    return redirect(url_for("usuarios.lista"))


# ── Eliminar ──────────────────────────────────────────────────
@usuarios_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
@requiere_permiso('Usuarios', 'eliminar')
def eliminar(id):
    if not _solo_super_admin():
        return redirect(url_for("usuarios.lista"))
    if id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("usuarios.lista"))

    u = Usuario.query.get_or_404(id)
    nombre = u.NombreUsuario

    # Limpiar relaciones antes de eliminar
    db.session.execute(db.text("DELETE FROM permisousuario WHERE IdUsuario = :uid"),           {'uid': id})
    db.session.execute(db.text("DELETE FROM proyectopersonal WHERE IdUsuario = :uid"),         {'uid': id})
    db.session.execute(db.text("UPDATE electronico SET IdUsuario = NULL WHERE IdUsuario = :uid"), {'uid': id})
    db.session.execute(db.text("UPDATE asignacionherramienta SET IdUsuario = NULL WHERE IdUsuario = :uid"), {'uid': id})
    db.session.execute(db.text("UPDATE activos SET usuario_id = NULL WHERE usuario_id = :uid"), {'uid': id})

    db.session.delete(u)
    db.session.commit()
    flash(f"Usuario '{nombre}' eliminado.", "success")
    socketio.emit('usuarios_actualizados', {'accion': 'eliminar', 'usuario_id': id})  # ← agrega esto
    return redirect(url_for("usuarios.lista"))


# ── Reset contraseña ──────────────────────────────────────────
@usuarios_bp.route("/<int:id>/reset-password", methods=["POST"])
@login_required
def reset_password(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    u     = Usuario.query.get_or_404(id)
    nueva = request.form.get("nueva_password", "").strip()

    if len(nueva) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("usuarios.lista"))

    u.Contrasena  = pwd_context.hash(nueva)
    u.PrimerLogin = True
    db.session.commit()
    flash(f"Contraseña de '{u.NombreUsuario}' restablecida.", "success")
    return redirect(url_for("usuarios.lista"))


# ── API ───────────────────────────────────────────────────────
@usuarios_bp.route("/api/<int:id>")
@login_required
def api_usuario(id):
    u = Usuario.query.get_or_404(id)
    return jsonify({
        "id":               u.IdUsuario,
        "username":         u.NombreUsuario,
        "nombre":           u.Nombre,
        "apellido_paterno": u.ApellidoPaterno,
        "apellido_materno": u.ApellidoMaterno or "",
        "telefono":         u.NumeroTelefono or "",
        "correo":           u.Correo,
        "rol_id":           u.IdRol,
        "departamento_id":  u.IdDepartamento,
        "tipo_usuario":     u.TipoUsuario,
        "estatus":          u.Estatus,
        "primer_login":     u.PrimerLogin,
        "area_nombre":      u.area_nombre or "",
        "tiene_modulo":     u.tiene_modulo,
        "bloqueado":        bool(u.BloqueadoHasta and u.BloqueadoHasta > datetime.now()),
    })