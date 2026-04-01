from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from passlib.context import CryptContext
from ..extensions import db
from ..models.usuario import Usuario, Rol

usuarios_bp = Blueprint("usuarios", __name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ROLES_GESTION_USUARIOS = ("admin", "rh", "ti")

def _check_admin():
    if current_user.rol not in ROLES_GESTION_USUARIOS:
        flash("No tienes permiso para gestionar usuarios.", "error")
        return False
    return True

def _solo_admin():
    """Solo el super admin puede eliminar usuarios y gestionar permisos."""
    if current_user.rol != "admin":
        flash("Solo el Administrador puede realizar esta acción.", "error")
        return False
    return True


# ── Lista ─────────────────────────────────────────────────────
@usuarios_bp.route("/")
@login_required
def lista():
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    rol_filtro = request.args.get("rol", "")
    query      = Usuario.query
    if rol_filtro:
        query = query.join(Rol).filter(Rol.IdRol == rol_filtro)

    usuarios = query.order_by(Usuario.Nombre).all()
    roles    = Rol.query.all()

    return render_template("usuarios/lista.html",
        usuarios   = usuarios,
        roles      = roles,
        rol_filtro = rol_filtro,
    )


# ── Crear ─────────────────────────────────────────────────────
@usuarios_bp.route("/nuevo", methods=["POST"])
@login_required
def nuevo():
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo", "").strip()

    # Verificar duplicados
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
        IdRol           = int(request.form.get("rol_id")),
    )
    db.session.add(u)
    db.session.commit()
    flash(f"Usuario '{username}' creado correctamente.", "success")
    return redirect(url_for("usuarios.lista"))


# ── Editar ────────────────────────────────────────────────────
@usuarios_bp.route("/<int:id>/editar", methods=["POST"])
@login_required
def editar(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    u = Usuario.query.get_or_404(id)

    # Verificar duplicado de username (excluyendo el mismo)
    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo", "").strip()
    dup_user = Usuario.query.filter(
        Usuario.NombreUsuario == username,
        Usuario.IdUsuario != id
    ).first()
    dup_mail = Usuario.query.filter(
        Usuario.Correo == correo,
        Usuario.IdUsuario != id
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
    u.IdRol           = int(request.form.get("rol_id"))
    u.Estatus         = request.form.get("estatus") == "1"

    db.session.commit()
    flash(f"Usuario '{username}' actualizado.", "success")
    return redirect(url_for("usuarios.lista"))


# ── Desactivar / Activar ──────────────────────────────────────
@usuarios_bp.route("/<int:id>/toggle", methods=["POST"])
@login_required
def toggle_estatus(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    if not _solo_admin():
        return redirect(url_for("usuarios.lista"))

    if id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "error")
        return redirect(url_for("usuarios.lista"))

    u = Usuario.query.get_or_404(id)
    u.Estatus = not u.Estatus
    db.session.commit()
    accion = "activado" if u.Estatus else "desactivado"
    flash(f"Usuario '{u.NombreUsuario}' {accion}.", "success")
    return redirect(url_for("usuarios.lista"))


# ── Eliminar ──────────────────────────────────────────────────
@usuarios_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    if not _solo_admin():
        return redirect(url_for("usuarios.lista"))

    if id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("usuarios.lista"))

    u = Usuario.query.get_or_404(id)
    nombre = u.NombreUsuario
    db.session.delete(u)
    db.session.commit()
    flash(f"Usuario '{nombre}' eliminado.", "success")
    return redirect(url_for("usuarios.lista"))


# ── Reset contraseña ──────────────────────────────────────────
@usuarios_bp.route("/<int:id>/reset-password", methods=["POST"])
@login_required
def reset_password(id):
    if not _check_admin():
        return redirect(url_for("activos.dashboard"))

    u        = Usuario.query.get_or_404(id)
    nueva    = request.form.get("nueva_password", "").strip()

    if len(nueva) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("usuarios.lista"))

    u.Contrasena  = pwd_context.hash(nueva)
    u.PrimerLogin = True
    db.session.commit()
    flash(f"Contraseña de '{u.NombreUsuario}' restablecida. El usuario deberá cambiarla al iniciar sesión.", "success")
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
        "estatus":          u.Estatus,
        "primer_login":     u.PrimerLogin,
    })