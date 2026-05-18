# app/routes/usuarios.py
"""
Gestión de usuarios DEL ÁREA PROPIA.
Cada admin de área ve solo los usuarios de su departamento.
Para gestión corporativa (todas las áreas), usar /rh/personal.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from passlib.context import CryptContext
from ..extensions import db, socketio
from ..models.usuario import Usuario, Rol, AREAS_CON_MODULO
from ..models.departamento import Departamento
from ..tasks.correo import enviar_bienvenida

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Mapa área → IdRol automático ──────────────────────────────
AREA_ROL_MAP = {
    'TI':               5,
    'Tecnología':       5,
    'Recursos Humanos': 4,
    'Administrativo':   2,
    'Almacén':          3,
}

def _rol_por_area(nombre_area: str, tipo: str) -> int:
    """Asigna IdRol automáticamente según área y tipo."""
    if nombre_area in AREA_ROL_MAP:
        return AREA_ROL_MAP[nombre_area]
    return 6  # Supervisor


# ══════════════════════════════════════════════════════════════
# LISTA DE USUARIOS DEL ÁREA PROPIA
# ══════════════════════════════════════════════════════════════
@usuarios_bp.route('/')
@login_required
def lista():
    """Lista de usuarios del área propia del admin.
    
    - Super admin: ve todos los usuarios
    - Admin de área (TI, RH, Administrativo, etc.): ve solo usuarios de su área
    """
    
    # Super admin ve todos
    if current_user.IdRol == 1:
        query = Usuario.query
    # Admin de área ve solo su área
    elif current_user.es_administrador_area and current_user.IdDepartamento:
        query = Usuario.query.filter_by(IdDepartamento=current_user.IdDepartamento)
    else:
        flash('No tienes permiso para gestionar usuarios.', 'warning')
        return redirect(url_for('activos.dashboard'))

    # Filtros
    area_filtro = request.args.get("area", "")
    tipo_filtro = request.args.get("tipo", "")

    if area_filtro:
        query = query.filter(Usuario.IdDepartamento == area_filtro)
    if tipo_filtro:
        query = query.filter(Usuario.TipoUsuario == tipo_filtro)

    usuarios = query.order_by(Usuario.Nombre).all()
    roles = Rol.query.all()
    departamentos = Departamento.query.order_by(Departamento.nombre).all()

    return render_template("usuarios/lista.html",
        usuarios      = usuarios,
        roles         = roles,
        departamentos = departamentos,
        area_filtro   = area_filtro,
        tipo_filtro   = tipo_filtro,
        areas_modulo  = AREAS_CON_MODULO,
    )


# ══════════════════════════════════════════════════════════════
# CREAR USUARIO (ÁREA PROPIA)
# ══════════════════════════════════════════════════════════════
@usuarios_bp.route('/nuevo', methods=['POST'])
@login_required
def nuevo():
    """Crear usuario en el área propia.
    
    - Super admin: puede crear en cualquier área
    - Admin de área: solo puede crear en su propia área
    """
    
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

    # Super admin puede elegir área
    if current_user.IdRol == 1:
        depto_id = request.form.get("departamento_id")
        tipo     = request.form.get("tipo_usuario", "empleado")
    # Admin de área crea en su propia área
    else:
        if not current_user.es_administrador_area or not current_user.IdDepartamento:
            flash("No tienes permiso para crear usuarios.", "error")
            return redirect(url_for("usuarios.lista"))
        depto_id = current_user.IdDepartamento
        tipo     = request.form.get("tipo_usuario", "empleado")

    depto  = Departamento.query.get(int(depto_id)) if depto_id else None
    id_rol = _rol_por_area(depto.nombre if depto else '', tipo)
    
    # ✅ VALIDACIÓN: Solo Super Admin puede crear Super Admins
    if id_rol == 1 and current_user.IdRol != 1:
        flash('No tienes permiso para crear Super Administradores.', 'error')
        return redirect(url_for('usuarios.lista'))

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
            password = password,
        )
        flash(f"Usuario '{username}' creado y correo enviado.", "success")
    except Exception:
        flash(f"Usuario '{username}' creado, pero no se pudo enviar el correo.", "warning")

    socketio.emit('usuarios_actualizados', {'accion': 'nuevo'})
    return redirect(url_for("usuarios.lista"))


# ══════════════════════════════════════════════════════════════
# EDITAR USUARIO (ÁREA PROPIA)
# ══════════════════════════════════════════════════════════════
@usuarios_bp.route('/<int:id>/editar', methods=['POST'])
@login_required
def editar(id):
    """Editar usuario del área propia.
    
    - Super admin: puede editar cualquier usuario
    - Admin de área: solo puede editar usuarios de su área
    """
    
    u = Usuario.query.get_or_404(id)

    # Verificar permisos
    if current_user.IdRol != 1:
        if not current_user.es_administrador_area:
            flash("No tienes permiso para editar usuarios.", "error")
            return redirect(url_for("usuarios.lista"))
        if u.IdDepartamento != current_user.IdDepartamento:
            flash("No puedes editar usuarios de otras áreas.", "error")
            return redirect(url_for("usuarios.lista"))
        if u.IdRol == 1:
            flash("No puedes editar al Super Administrador.", "error")
            return redirect(url_for("usuarios.lista"))

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

    # Solo super admin puede cambiar área, tipo y rol
    if current_user.IdRol == 1:
        depto_id = request.form.get("departamento_id")
        tipo     = request.form.get("tipo_usuario", "empleado")
        rol_id   = request.form.get("rol_id", type=int)  # Obtener rol del form
        depto    = Departamento.query.get(int(depto_id)) if depto_id else None
        
        # ✅ VALIDACIÓN: Solo Super Admin puede asignar rol de Super Admin
        if rol_id == 1 and current_user.IdRol != 1:
            flash('No tienes permiso para asignar el rol de Super Administrador.', 'error')
            return redirect(url_for('usuarios.lista'))
        
        u.IdDepartamento = int(depto_id) if depto_id else None
        u.TipoUsuario    = tipo
        
        # Si se especificó un rol manualmente, usarlo; sino calcular automáticamente
        if rol_id:
            u.IdRol = rol_id
        elif depto:
            u.IdRol = _rol_por_area(depto.nombre, tipo)
        # Si no hay rol ni área, mantener el rol actual (no hacer nada)

    # Cambio de contraseña opcional (FUERA del if, aplica a todos)
    nueva_pass = request.form.get("nueva_password", "").strip()
    if nueva_pass:
        if len(nueva_pass) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("usuarios.lista"))
        u.Contrasena  = pwd_context.hash(nueva_pass)
        u.PrimerLogin = True

    db.session.commit()
    flash(f"Usuario '{username}' actualizado.", "success")
    socketio.emit('usuarios_actualizados', {'accion': 'editar', 'usuario_id': id})
    socketio.emit('permisos_actualizados', {'usuario_id': id})
    return redirect(url_for("usuarios.lista"))


# ══════════════════════════════════════════════════════════════
# ELIMINAR USUARIO (ÁREA PROPIA)
# ══════════════════════════════════════════════════════════════
@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar usuario del área propia.
    
    - Super admin: puede eliminar cualquier usuario (excepto a sí mismo)
    - Admin de área: solo puede eliminar usuarios de su área (solo empleados)
    """
    
    if id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("usuarios.lista"))

    u = Usuario.query.get_or_404(id)

    # Verificar permisos
    if current_user.IdRol != 1:
        if not current_user.es_administrador_area:
            flash("No tienes permiso para eliminar usuarios.", "error")
            return redirect(url_for("usuarios.lista"))
        if u.IdDepartamento != current_user.IdDepartamento:
            flash("No puedes eliminar usuarios de otras áreas.", "error")
            return redirect(url_for("usuarios.lista"))
        if u.TipoUsuario == "administrador":
            flash("No puedes eliminar administradores de área.", "error")
            return redirect(url_for("usuarios.lista"))
        if u.IdRol == 1:
            flash("No puedes eliminar al Super Administrador.", "error")
            return redirect(url_for("usuarios.lista"))

    nombre = u.NombreUsuario

    # Limpiar relaciones
    db.session.execute(db.text("DELETE FROM permisousuario WHERE IdUsuario = :uid"),           {'uid': id})
    db.session.execute(db.text("DELETE FROM proyectopersonal WHERE IdUsuario = :uid"),         {'uid': id})
    db.session.execute(db.text("UPDATE electronico SET IdUsuario = NULL WHERE IdUsuario = :uid"), {'uid': id})
    db.session.execute(db.text("UPDATE asignacionherramienta SET IdUsuario = NULL WHERE IdUsuario = :uid"), {'uid': id})
    db.session.execute(db.text("UPDATE activos SET usuario_id = NULL WHERE usuario_id = :uid"), {'uid': id})

    db.session.delete(u)
    db.session.commit()
    flash(f"Usuario '{nombre}' eliminado.", "success")
    socketio.emit('usuarios_actualizados', {'accion': 'eliminar', 'usuario_id': id})
    return redirect(url_for("usuarios.lista"))


# ══════════════════════════════════════════════════════════════
# API PARA MODAL EDITAR
# ══════════════════════════════════════════════════════════════
@usuarios_bp.route('/api/<int:id>')
@login_required
def api_usuario(id):
    """API para obtener datos del usuario (modal editar)."""
    u = Usuario.query.get_or_404(id)
    
    # Verificar permisos de lectura
    if current_user.IdRol != 1:
        if not current_user.es_administrador_area:
            return jsonify({'error': 'Sin permiso'}), 403
        if u.IdDepartamento != current_user.IdDepartamento:
            return jsonify({'error': 'Sin permiso'}), 403

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
    })