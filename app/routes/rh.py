# app/routes/rh.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from passlib.context import CryptContext
from ..extensions import db, socketio
from ..models.usuario import Usuario, Rol, AREAS_CON_MODULO
from ..models.departamento import Departamento
from datetime import datetime
from ..tasks.correo import enviar_bienvenida
from ..utils.permisos import tiene_permiso, es_admin_rh, requiere_permiso
from flask import send_file
from io import BytesIO, StringIO
from datetime import datetime
import pandas as pd
import csv
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import json

rh_bp = Blueprint('rh', __name__, url_prefix='/rh')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Mapa área → IdRol automático ──────────────────────────────
AREA_ROL_MAP = {
    'TI':               5,
    'Tecnología':       5,
    'Recursos Humanos': 4,
    'Administrativo':   2,
    'Almacén':          3,
}

MAPEO_COLUMNAS = {
    'Tipo': 'TipoEquipo',
    'Nombre': 'Nombre',
    'N° Serie': 'NumeroSerie',
    'Estado': 'Estado',
    'Condición': 'Condicion',
    'Valor': 'Valor',
    'Asignado a': 'AsignadoA',
    'Ubicación': 'Ubicacion',
}

def _rol_por_area(nombre_area: str, tipo: str) -> int:
    """Asigna IdRol automáticamente según área y tipo."""
    if nombre_area in AREA_ROL_MAP:
        return AREA_ROL_MAP[nombre_area]
    return 6  # Supervisor

# ─────────────────────────────────────────────────────────────
# Helper de permisos
# ─────────────────────────────────────────────────────────────
def _puede(accion='ver'):
    col_map = {'ver': 'PuedeVer', 'crear': 'PuedeCrear',
               'editar': 'PuedeEditar', 'eliminar': 'PuedeEliminar'}
    col = col_map.get(accion, 'PuedeVer')
    row = db.session.execute(
        db.text(f"""
            SELECT {col} AS ok
            FROM v_permisos_usuario
            WHERE IdUsuario = :uid AND IdModulo = 10
            LIMIT 1
        """),
        {'uid': current_user.IdUsuario}
    ).fetchone()
    return bool(row and row.ok)

# ══════════════════════════════════════════════════════════════
# GESTIÓN DE PERSONAL CORPORATIVO (todos los usuarios)
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/personal')
@login_required
def personal():
    
    print(f">>> current_user.IdRol = {current_user.IdRol}")
    print(f">>> tiene_permiso('Personal Corporativo', 'ver') = {tiene_permiso('Personal Corporativo', 'ver')}")
    
    if current_user.IdRol != 1 and not tiene_permiso('Personal Corporativo', 'ver'):
        flash('No tienes permiso para gestionar personal corporativo.', 'warning')
        return redirect(url_for('activos.dashboard'))

    area_filtro = request.args.get("area", "")
    tipo_filtro = request.args.get("tipo", "")
    query       = Usuario.query

    if area_filtro:
        query = query.filter(Usuario.IdDepartamento == area_filtro)
    if tipo_filtro:
        query = query.filter(Usuario.TipoUsuario == tipo_filtro)

    # Admin RH ve todos excepto super admins
    # Super admin ve absolutamente todo
    if current_user.IdRol != 1:
        query = query.filter(Usuario.IdRol != 1)

    usuarios      = query.order_by(Usuario.Nombre).all()
    roles         = Rol.query.all()
    departamentos = Departamento.query.order_by(Departamento.nombre).all()

    return render_template("rh/personal.html",
        usuarios      = usuarios,
        roles         = roles,
        departamentos = departamentos,
        area_filtro   = area_filtro,
        tipo_filtro   = tipo_filtro,
        areas_modulo  = AREAS_CON_MODULO,
    )


@rh_bp.route('/personal/nuevo', methods=['POST'])
@login_required
def personal_nuevo():
    """Crear usuario desde el módulo de RH corporativo."""
    if current_user.IdRol != 1 and not tiene_permiso('Personal Corporativo', 'crear'):
        flash('No tienes permiso.', 'error')
        return redirect(url_for('rh.personal'))

    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo",   "").strip()

    if Usuario.query.filter_by(NombreUsuario=username).first():
        flash(f"El usuario '{username}' ya existe.", "error")
        return redirect(url_for("rh.personal"))
    if Usuario.query.filter_by(Correo=correo).first():
        flash(f"El correo '{correo}' ya está registrado.", "error")
        return redirect(url_for("rh.personal"))

    password = request.form.get("password", "").strip()
    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "error")
        return redirect(url_for("rh.personal"))

    depto_id = request.form.get("departamento_id")
    tipo     = request.form.get("tipo_usuario", "empleado")

    # Admin RH solo puede crear empleados (no administradores de área)
    if current_user.IdRol != 1:
        tipo = "empleado"
        if not depto_id:
            flash("Debes seleccionar un área para el usuario.", "error")
            return redirect(url_for("rh.personal"))

    depto  = Departamento.query.get(int(depto_id)) if depto_id else None
    id_rol = _rol_por_area(depto.nombre if depto else '', tipo)

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
    return redirect(url_for("rh.personal"))


@rh_bp.route('/personal/<int:id>/editar', methods=['POST'])
@login_required
def personal_editar(id):
    """Editar usuario desde el módulo de RH corporativo."""
    if current_user.IdRol != 1 and not tiene_permiso('Personal Corporativo', 'editar'):
        flash('No tienes permiso.', 'error')
        return redirect(url_for('rh.personal'))

    u        = Usuario.query.get_or_404(id)
    username = request.form.get("username", "").strip()
    correo   = request.form.get("correo",   "").strip()

    # Admin RH no puede editar admins de área ni super admins
    if current_user.IdRol != 1 and tiene_permiso('Personal Corporativo', 'ver'):
        if u.TipoUsuario == "administrador":
            flash("No tienes permiso para editar administradores de área.", "error")
            return redirect(url_for("rh.personal"))
        if u.IdRol == 1:
            flash("No tienes permiso para editar al Super Administrador.", "error")
            return redirect(url_for("rh.personal"))

    dup_user = Usuario.query.filter(
        Usuario.NombreUsuario == username, Usuario.IdUsuario != id
    ).first()
    dup_mail = Usuario.query.filter(
        Usuario.Correo == correo, Usuario.IdUsuario != id
    ).first()

    if dup_user:
        flash(f"El usuario '{username}' ya existe.", "error")
        return redirect(url_for("rh.personal"))
    if dup_mail:
        flash(f"El correo '{correo}' ya está registrado.", "error")
        return redirect(url_for("rh.personal"))

    u.NombreUsuario   = username
    u.Nombre          = request.form.get("nombre", "").strip()
    u.ApellidoPaterno = request.form.get("apellido_paterno", "").strip()
    u.ApellidoMaterno = request.form.get("apellido_materno", "").strip() or None
    u.NumeroTelefono  = request.form.get("telefono", "").strip() or None
    u.Correo          = correo
    u.Estatus         = request.form.get("estatus") == "1"

    # Cambio de área (super admin puede todo, admin RH solo área)
    if current_user.IdRol == 1:
        depto_id = request.form.get("departamento_id")
        tipo     = request.form.get("tipo_usuario", "empleado")
        depto    = Departamento.query.get(int(depto_id)) if depto_id else None
        u.IdDepartamento = int(depto_id) if depto_id else None
        u.TipoUsuario    = tipo
        u.IdRol          = _rol_por_area(depto.nombre if depto else '', tipo)
    elif tiene_permiso('Personal Corporativo', 'editar'):
        depto_id = request.form.get("departamento_id")
        if depto_id:
            depto = Departamento.query.get(int(depto_id))
            u.IdDepartamento = int(depto_id)
            u.IdRol = _rol_por_area(depto.nombre if depto else '', u.TipoUsuario)

    # Cambio de contraseña opcional
    nueva_pass = request.form.get("nueva_password", "").strip()
    if nueva_pass:
        if len(nueva_pass) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return redirect(url_for("rh.personal"))
        u.Contrasena  = pwd_context.hash(nueva_pass)
        u.PrimerLogin = True

    db.session.commit()
    flash(f"Usuario '{username}' actualizado.", "success")
    socketio.emit('usuarios_actualizados', {'accion': 'editar', 'usuario_id': id})
    socketio.emit('permisos_actualizados', {'usuario_id': id})
    return redirect(url_for("rh.personal"))


@rh_bp.route('/personal/<int:id>/eliminar', methods=['POST'])
@login_required
def personal_eliminar(id):
    """Eliminar usuario desde el módulo de RH corporativo."""
    if current_user.IdRol != 1 and not tiene_permiso('Personal Corporativo', 'eliminar'):
        flash("No tienes permiso para eliminar usuarios.", "error")
        return redirect(url_for("rh.personal"))

    if id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("rh.personal"))

    u = Usuario.query.get_or_404(id)

    # Admin RH NO puede eliminar admins de área ni super admins
    if current_user.IdRol != 1 and tiene_permiso('Personal Corporativo', 'eliminar'):
        if u.IdRol == 1:
            flash("No puedes eliminar al Super Administrador.", "error")
            return redirect(url_for("rh.personal"))
        if u.TipoUsuario == "administrador":
            flash("No tienes permiso para eliminar administradores de área.", "error")
            return redirect(url_for("rh.personal"))

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
    return redirect(url_for("rh.personal"))


# ══════════════════════════════════════════════════════════════
# INDEX
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/')
@login_required
def index():
    return redirect(url_for('rh.activos_usuario'))


# ══════════════════════════════════════════════════════════════
# SECCIÓN 1 — ACTIVOS POR USUARIO
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/activos/usuario')
@login_required
def activos_usuario():
    if not _puede('ver'):
        flash('No tienes permiso para acceder a Recursos Humanos.', 'warning')
        return redirect(url_for('activos.dashboard'))

    usuarios = db.session.execute(db.text("""
        SELECT u.IdUsuario,
               CONCAT(u.Nombre,' ',u.ApellidoPaterno) AS NombreCompleto,
               u.Correo, r.NombreRol AS Rol
        FROM usuario u
        JOIN rol r ON r.IdRol = u.IdRol
        WHERE u.Estatus = 1
        ORDER BY NombreCompleto
    """)).fetchall()

    uid = request.args.get('usuario_id', type=int)
    activos = []
    usuario_sel = None
    resumen = {'electronico': 0, 'herramienta': 0, 'general': 0, 'total': 0}

    if uid:
        activos = db.session.execute(db.text("""
            SELECT * FROM v_activos_por_usuario
            WHERE IdUsuario = :uid
            ORDER BY TipoActivo, NombreActivo
        """), {'uid': uid}).fetchall()

        usuario_sel = db.session.execute(db.text("""
            SELECT u.IdUsuario,
                   CONCAT(u.Nombre,' ',u.ApellidoPaterno) AS NombreCompleto,
                   u.Correo, r.NombreRol AS Rol, u.NumeroTelefono
            FROM usuario u
            JOIN rol r ON r.IdRol = u.IdRol
            WHERE u.IdUsuario = :uid LIMIT 1
        """), {'uid': uid}).fetchone()

        for a in activos:
            tipo = a.TipoActivo
            resumen[tipo] = resumen.get(tipo, 0) + 1
        resumen['total'] = len(activos)

    return render_template('rh/activos_usuario.html',
                           usuarios=usuarios,
                           activos=activos,
                           usuario_sel=usuario_sel,
                           uid=uid,
                           resumen=resumen)


# ══════════════════════════════════════════════════════════════
# SECCIÓN 1b — ACTIVOS POR ÁREA
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/activos/area')
@login_required
def activos_area():
    if not _puede('ver'):
        flash('No tienes permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    departamentos = db.session.execute(db.text("""
        SELECT id, nombre FROM departamentos ORDER BY nombre
    """)).fetchall()

    did = request.args.get('depto_id', type=int)
    activos = []
    depto_sel = None

    if did:
        activos = db.session.execute(db.text("""
            SELECT * FROM v_activos_por_area
            WHERE IdDepartamento = :did
            ORDER BY TipoActivo, NombreActivo
        """), {'did': did}).fetchall()
        depto_sel = next((d for d in departamentos if d.id == did), None)

    return render_template('rh/activos_area.html',
                           departamentos=departamentos,
                           activos=activos,
                           depto_sel=depto_sel,
                           did=did)


# ══════════════════════════════════════════════════════════════
# SECCIÓN 2 — PROCESOS DE BAJA
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/bajas/')
@login_required
def bajas_lista():
    if not _puede('ver'):
        flash('No tienes permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    estatus_filter = request.args.get('estatus', '')
    sql = "SELECT * FROM v_procesos_baja"
    params = {}
    if estatus_filter:
        sql += " WHERE Estatus = :est"
        params['est'] = estatus_filter
    sql += " ORDER BY CreadoEn DESC"

    bajas = db.session.execute(db.text(sql), params).fetchall()

    conteos = db.session.execute(db.text("""
        SELECT
            COUNT(*) AS total,
            SUM(Estatus='aviso')       AS aviso,
            SUM(Estatus='proceso')     AS proceso,
            SUM(Estatus='autorizado')  AS autorizado,
            SUM(Estatus='completado')  AS completado,
            SUM(Estatus='cancelado')   AS cancelado
        FROM procesoBaja
    """)).fetchone()

    return render_template('rh/bajas_lista.html',
                           bajas=bajas,
                           conteos=conteos,
                           estatus_filter=estatus_filter,
                           puede_crear=_puede('crear'))


@rh_bp.route('/bajas/nuevo', methods=['GET', 'POST'])
@login_required
def baja_nueva():
    if not _puede('crear'):
        flash('No tienes permiso para iniciar procesos de baja.', 'warning')
        return redirect(url_for('rh.bajas_lista'))

    if request.method == 'POST':
        uid         = request.form.get('usuario_id', type=int)
        motivo      = request.form.get('motivo', '').strip()
        fecha_aviso = request.form.get('fecha_aviso') or datetime.today().strftime('%Y-%m-%d')

        if not uid:
            flash('Selecciona un empleado.', 'warning')
        else:
            existente = db.session.execute(db.text("""
                SELECT IdBaja FROM procesoBaja
                WHERE IdUsuario = :uid
                  AND Estatus NOT IN ('completado','cancelado')
                LIMIT 1
            """), {'uid': uid}).fetchone()

            if existente:
                flash('Ya existe un proceso de baja activo para ese empleado.', 'warning')
            else:
                db.session.execute(db.text("""
                    INSERT INTO procesoBaja
                        (IdUsuario, FechaAviso, Motivo, Estatus, SolicitadoPor)
                    VALUES (:uid, :fa, :motivo, 'aviso', :sol)
                """), {'uid': uid, 'fa': fecha_aviso,
                       'motivo': motivo, 'sol': current_user.IdUsuario})
                db.session.commit()
                flash('Aviso de baja registrado correctamente.', 'success')
                return redirect(url_for('rh.bajas_lista'))

    usuarios = db.session.execute(db.text("""
        SELECT u.IdUsuario,
               CONCAT(u.Nombre,' ',u.ApellidoPaterno) AS NombreCompleto,
               u.Correo, r.NombreRol AS Rol
        FROM usuario u
        JOIN rol r ON r.IdRol = u.IdRol
        WHERE u.Estatus = 1
          AND u.IdUsuario NOT IN (
              SELECT IdUsuario FROM procesoBaja
              WHERE Estatus NOT IN ('completado','cancelado')
          )
        ORDER BY NombreCompleto
    """)).fetchall()

    return render_template('rh/baja_nueva.html', usuarios=usuarios)


@rh_bp.route('/bajas/<int:id_baja>/avanzar', methods=['POST'])
@login_required
def baja_avanzar(id_baja):
    if not _puede('editar'):
        return jsonify({'error': 'Sin permiso'}), 403

    baja = db.session.execute(db.text(
        "SELECT Estatus FROM procesoBaja WHERE IdBaja = :id"
    ), {'id': id_baja}).fetchone()

    if not baja:
        flash('Proceso no encontrado.', 'danger')
        return redirect(url_for('rh.bajas_lista'))

    siguiente = {'aviso': 'proceso', 'proceso': 'autorizado'}
    nuevo_est = siguiente.get(baja.Estatus)

    if not nuevo_est:
        flash('Este proceso no puede avanzar desde su estado actual.', 'warning')
        return redirect(url_for('rh.bajas_lista'))

    extra = {}
    if nuevo_est == 'autorizado':
        extra_sql = ", AutorizadoPor = :auth, FechaAutorizacion = NOW()"
        extra['auth'] = current_user.IdUsuario
    else:
        extra_sql = ""

    db.session.execute(db.text(f"""
        UPDATE procesoBaja
        SET Estatus = :est {extra_sql}, ActualizadoEn = NOW()
        WHERE IdBaja = :id
    """), {'est': nuevo_est, 'id': id_baja, **extra})
    db.session.commit()

    labels = {'proceso': 'Proceso iniciado', 'autorizado': 'Baja autorizada'}
    flash(f'{labels[nuevo_est]} correctamente.', 'success')
    return redirect(url_for('rh.bajas_lista'))


@rh_bp.route('/bajas/<int:id_baja>/retirar', methods=['GET', 'POST'])
@login_required
def baja_retirar(id_baja):
    if not _puede('editar'):
        flash('Sin permiso.', 'warning')
        return redirect(url_for('rh.bajas_lista'))

    baja = db.session.execute(db.text(
        "SELECT * FROM v_procesos_baja WHERE IdBaja = :id"
    ), {'id': id_baja}).fetchone()

    if not baja or baja.Estatus != 'autorizado':
        flash('El proceso debe estar autorizado antes de retirar activos.', 'warning')
        return redirect(url_for('rh.bajas_lista'))

    activos_usuario = db.session.execute(db.text("""
        SELECT * FROM v_activos_por_usuario WHERE IdUsuario = :uid
    """), {'uid': baja.IdUsuario}).fetchall()

    if request.method == 'POST':
        seleccionados = request.form.getlist('activos[]')

        for item in seleccionados:
            parts = item.split(':', 2)
            if len(parts) != 3:
                continue
            tipo, id_activo, nombre_activo = parts
            id_activo = int(id_activo)
            condicion = request.form.get(f'condicion_{tipo}_{id_activo}', 'bueno')

            db.session.execute(db.text("""
                INSERT INTO bajaActivoRetiro
                    (IdBaja, TipoActivo, IdActivo, NombreActivo, Condicion, RetiroPor)
                VALUES (:baja, :tipo, :id, :nombre, :cond, :retiro)
            """), {'baja': id_baja, 'tipo': tipo, 'id': id_activo,
                   'nombre': nombre_activo, 'cond': condicion,
                   'retiro': current_user.IdUsuario})

            if tipo == 'electronico':
                db.session.execute(db.text("""
                    UPDATE electronico SET Estado='almacen', IdUsuario=NULL
                    WHERE IdElectronico = :id
                """), {'id': id_activo})
            elif tipo == 'herramienta':
                db.session.execute(db.text("""
                    UPDATE asignacionherramienta
                    SET FechaDevolucion = CURDATE()
                    WHERE IdHerramienta = :id AND IdUsuario = :uid
                      AND FechaDevolucion IS NULL
                """), {'id': id_activo, 'uid': baja.IdUsuario})
                db.session.execute(db.text("""
                    UPDATE herramienta SET Estado='disponible'
                    WHERE IdHerramienta = :id
                """), {'id': id_activo})
            elif tipo == 'general':
                db.session.execute(db.text("""
                    UPDATE activos SET usuario_id=NULL WHERE id=:id
                """), {'id': id_activo})

        db.session.execute(db.text("""
            UPDATE procesoBaja
            SET Estatus='completado', ActualizadoEn=NOW()
            WHERE IdBaja = :id
        """), {'id': id_baja})

        db.session.execute(db.text("""
            UPDATE usuario SET Estatus=0 WHERE IdUsuario=:uid
        """), {'uid': baja.IdUsuario})

        db.session.commit()
        flash('Activos retirados. Baja completada y usuario desactivado.', 'success')
        return redirect(url_for('rh.bajas_lista'))

    return render_template('rh/baja_retirar.html',
                           baja=baja,
                           activos=activos_usuario)


@rh_bp.route('/bajas/<int:id_baja>/cancelar', methods=['POST'])
@login_required
def baja_cancelar(id_baja):
    if not _puede('editar'):
        flash('Sin permiso.', 'warning')
        return redirect(url_for('rh.bajas_lista'))

    db.session.execute(db.text("""
        UPDATE procesoBaja SET Estatus='cancelado', ActualizadoEn=NOW()
        WHERE IdBaja=:id AND Estatus NOT IN ('completado')
    """), {'id': id_baja})
    db.session.commit()
    flash('Proceso de baja cancelado.', 'warning')
    return redirect(url_for('rh.bajas_lista'))


# ══════════════════════════════════════════════════════════════
# SECCIÓN 3 — AUDITORÍA
# ══════════════════════════════════════════════════════════════
@rh_bp.route('/auditoria/')
@login_required
def auditoria():
    if not _puede('ver'):
        flash('No tienes permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    tipo_filter = request.args.get('tipo', '')
    cond_filter = request.args.get('condicion', '')

    sql = "SELECT * FROM v_auditoria_resguardo WHERE 1=1"
    params = {}
    if tipo_filter:
        sql += " AND TipoActivo=:tipo"
        params['tipo'] = tipo_filter
    if cond_filter:
        sql += " AND Condicion=:cond"
        params['cond'] = cond_filter
    sql += " ORDER BY TipoActivo, NombreActivo"

    activos = db.session.execute(db.text(sql), params).fetchall()

    stats = db.session.execute(db.text("""
        SELECT
            COUNT(*)                               AS total,
            SUM(Condicion='bueno')                 AS bueno,
            SUM(Condicion='regular')               AS regular,
            SUM(Condicion='dañado')                AS danado,
            SUM(AsignadoA IS NOT NULL)             AS asignados,
            SUM(AsignadoA IS NULL)                 AS en_almacen
        FROM v_auditoria_resguardo
    """)).fetchone()

    return render_template('ti/auditoria.html',
                           activos=activos, stats=stats,
                           tipo_filter=tipo_filter,
                           cond_filter=cond_filter)


@rh_bp.route('/auditoria/usuarios')
@login_required
def auditoria_usuarios():
    if not _puede('ver'):
        flash('No tienes permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    rol_filter    = request.args.get('rol', '')
    estatus_filter = request.args.get('estatus', '1')

    sql = """
        SELECT u.IdUsuario,
               CONCAT(u.Nombre,' ',u.ApellidoPaterno) AS NombreCompleto,
               u.NombreUsuario, u.Correo, u.NumeroTelefono,
               r.NombreRol AS Rol, u.Estatus, u.CreadoEn
        FROM usuario u JOIN rol r ON r.IdRol=u.IdRol
        WHERE 1=1
    """
    params = {}
    if rol_filter:
        sql += " AND r.NombreRol=:rol"
        params['rol'] = rol_filter
    if estatus_filter != '':
        sql += " AND u.Estatus=:est"
        params['est'] = int(estatus_filter)
    sql += " ORDER BY NombreCompleto"

    usuarios = db.session.execute(db.text(sql), params).fetchall()
    roles    = db.session.execute(db.text(
        "SELECT IdRol, NombreRol FROM rol ORDER BY NombreRol"
    )).fetchall()

    return render_template('rh/auditoria_usuarios.html',
                           usuarios=usuarios, roles=roles,
                           rol_filter=rol_filter,
                           estatus_filter=estatus_filter)


# ──────────────────────────────────────────────────────────────
# API JSON
# ──────────────────────────────────────────────────────────────
@rh_bp.route('/api/usuario/<int:uid>/activos')
@login_required
def api_activos_usuario(uid):
    if not _puede('ver'):
        return jsonify({'error': 'Sin permiso'}), 403
    rows = db.session.execute(db.text("""
        SELECT * FROM v_activos_por_usuario WHERE IdUsuario=:uid
        ORDER BY TipoActivo, NombreActivo
    """), {'uid': uid}).fetchall()
    return jsonify([dict(r._mapping) for r in rows])


@rh_bp.route('/api/usuario/<int:id>')
@login_required
def api_usuario(id):
    """API para modal editar: obtener datos del usuario."""
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


# ── Dashboard de empleado (todos sus activos + proyectos) ────

@rh_bp.route('/empleado/<int:uid>')
@login_required
def empleado_dashboard(uid):
    if not _puede('ver'):
        flash('Sin permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    empleado = db.session.execute(db.text("""
        SELECT u.IdUsuario,
               CONCAT(u.Nombre,' ',u.ApellidoPaterno) AS NombreCompleto,
               u.NombreUsuario, u.Correo, u.NumeroTelefono,
               r.NombreRol AS Rol, u.Estatus, u.CreadoEn
        FROM usuario u
        JOIN rol r ON r.IdRol = u.IdRol
        WHERE u.IdUsuario = :uid
    """), {'uid': uid}).fetchone()

    if not empleado:
        flash('Empleado no encontrado.', 'danger')
        return redirect(url_for('rh.activos_usuario'))

    activos = db.session.execute(db.text("""
        SELECT * FROM v_empleado_activos_completo
        WHERE IdUsuario = :uid
        ORDER BY TipoActivo, NombreActivo
    """), {'uid': uid}).fetchall()

    proyectos = db.session.execute(db.text("""
        SELECT p.IdProyecto, p.Nombre, p.Estatus,
               p.FechaInicio, p.FechaTermino,
               pp.Rol AS RolEnProyecto,
               (SELECT COUNT(*) FROM proyectoactivo pa
                WHERE pa.IdProyecto = p.IdProyecto
                  AND pa.FechaDevolucion IS NULL) AS TotalActivos
        FROM proyecto p
        JOIN proyectopersonal pp ON pp.IdProyecto = p.IdProyecto
        WHERE pp.IdUsuario = :uid
        ORDER BY p.FechaInicio DESC
    """), {'uid': uid}).fetchall()

    resumen = {'electronico': 0, 'herramienta': 0, 'general': 0, 'total': 0}
    valor_total = 0
    for a in activos:
        resumen[a.TipoActivo] = resumen.get(a.TipoActivo, 0) + 1
        resumen['total'] += 1
        valor_total += float(a.Valor or 0)

    baja_activa = db.session.execute(db.text("""
        SELECT * FROM v_procesos_baja
        WHERE IdUsuario = :uid
          AND Estatus NOT IN ('completado','cancelado')
        LIMIT 1
    """), {'uid': uid}).fetchone()

    return render_template('rh/empleado_dashboard.html',
                           empleado=empleado,
                           activos=activos,
                           proyectos=proyectos,
                           resumen=resumen,
                           valor_total=valor_total,
                           baja_activa=baja_activa)


# ── Reporte consolidado Equipo → Usuario → Área → Proyecto ───

@rh_bp.route('/reporte/consolidado')
@login_required
def reporte_consolidado():
    if not _puede('ver'):
        flash('Sin permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    proyecto_filter = request.args.get('proyecto_id', type=int)
    depto_filter    = request.args.get('depto_id', type=int)
    tipo_filter     = request.args.get('tipo', '')
    sin_proyecto    = request.args.get('sin_proyecto', '')

    sql = "SELECT * FROM v_equipos_consolidado WHERE 1=1"
    params = {}

    if tipo_filter:
        sql += " AND TipoEquipo = :tipo"
        params['tipo'] = tipo_filter

    if proyecto_filter:
        sql += " AND (IdProyecto = :pid OR IdProyectoEquipo = :pid)"
        params['pid'] = proyecto_filter

    if depto_filter:
        sql += " AND IdDepartamento = :did"
        params['did'] = depto_filter

    if sin_proyecto:
        sql += " AND IdProyecto IS NULL AND IdProyectoEquipo IS NULL"

    sql += " ORDER BY NombreEquipo"

    equipos = db.session.execute(db.text(sql), params).fetchall()

    proyectos = db.session.execute(db.text("""
        SELECT IdProyecto, Nombre, Estatus FROM proyecto ORDER BY Nombre
    """)).fetchall()

    departamentos = db.session.execute(db.text("""
        SELECT id, nombre FROM departamentos ORDER BY nombre
    """)).fetchall()

    stats = {
        'total':        len(equipos),
        'con_usuario':  sum(1 for e in equipos if e.IdUsuario),
        'con_proyecto': sum(1 for e in equipos if e.IdProyecto or e.IdProyectoEquipo),
        'sin_asignar':  sum(1 for e in equipos if not e.IdUsuario),
    }

    return render_template('rh/reporte_consolidado.html',
                           equipos=equipos,
                           proyectos=proyectos,
                           departamentos=departamentos,
                           stats=stats,
                           proyecto_filter=proyecto_filter,
                           depto_filter=depto_filter,
                           tipo_filter=tipo_filter,
                           sin_proyecto=sin_proyecto)
    
# ══════════════════════════════════════════════════════════════
# REPORTES DE AUDITORÍA (solo equipos TI/Electrónicos)
# ══════════════════════════════════════════════════════════════
 
def _obtener_activos_filtrados(tipo_filter, cond_filter):
    """Obtiene activos TI con los filtros aplicados."""
    sql = """
        SELECT 
            'electronico' as TipoActivo,
            e.Nombre,
            e.TipoEquipo,
            e.Marca,
            e.Modelo,
            e.NumeroSerie,
            e.Estado,
            e.Condicion,
            e.Costo as Valor,
            CONCAT(COALESCE(u.Nombre,''), ' ', COALESCE(u.ApellidoPaterno,'')) as AsignadoA,
            ub.Nombre as Ubicacion,
            DATE_FORMAT(e.FechaAdquisicion, '%%d/%%m/%%Y') as FechaAdquisicion
        FROM electronico e
        LEFT JOIN usuario u ON e.IdUsuario = u.IdUsuario
        LEFT JOIN Ubicacion ub ON e.IdUbicacion = ub.IdUbicacion
        WHERE e.Estado != 'baja'
    """
    
    params = {}
    
    if cond_filter:
        sql += " AND e.Condicion = :condicion"
        params['condicion'] = cond_filter
    
    sql += " ORDER BY e.Nombre"
    
    result = db.session.execute(db.text(sql), params).fetchall()
    return [dict(row._mapping) for row in result]

def _obtener_columnas_solicitadas():
    """Lee el parámetro 'columnas' del request y devuelve la lista de columnas."""
    columnas_param = request.args.get('columnas', '')
    
    if not columnas_param:
        # Si no se envían columnas, devolver todas por defecto
        return list(MAPEO_COLUMNAS.keys())
    
    try:
        columnas = json.loads(columnas_param)
        # Filtrar solo las que existen en el mapeo
        return [c for c in columnas if c in MAPEO_COLUMNAS]
    except (json.JSONDecodeError, TypeError):
        return list(MAPEO_COLUMNAS.keys())

def _obtener_valor_celda(activo, nombre_columna):
    """Obtiene el valor formateado de una celda según el nombre de la columna."""
    key = MAPEO_COLUMNAS.get(nombre_columna)
    if not key:
        return '—'
    
    valor = activo.get(key)
    
    # Formateos especiales
    if nombre_columna == 'Tipo':
        return '💻 TI' if activo.get('TipoActivo') == 'electronico' else '📦 General'
    
    if nombre_columna == 'Valor':
        return f"${valor:,.2f}" if valor else '$0.00'
    
    if nombre_columna == 'Asignado a':
        return (valor or '').strip() or 'Sin asignar'
    
    return valor or '—'
 
 
# ── Reporte PDF ───────────────────────────────────────────────
@rh_bp.route("/auditoria/reporte/pdf")
@login_required
@requiere_permiso('Auditoria', 'ver')
def auditoria_reporte_pdf():
    """Genera reporte PDF con SOLO las columnas seleccionadas."""
    
    tipo_filter = request.args.get('tipo', '')
    cond_filter = request.args.get('condicion', '')
    columnas = _obtener_columnas_solicitadas()
    
    activos = _obtener_activos_filtrados(tipo_filter, cond_filter)
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()
    
    titulo_cond = {
        'bueno': 'En Buen Estado',
        'regular': 'En Estado Regular',
        'dañado': 'Dañados'
    }.get(cond_filter, 'Todos los Equipos')
    
    title = Paragraph(
        f"<b>Reporte de Auditoría - Activos TI</b><br/>{titulo_cond}",
        styles['Title']
    )
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    fecha_gen = datetime.now().strftime('%d/%m/%Y %H:%M')
    info = Paragraph(
        f"<b>Generado:</b> {fecha_gen}<br/><b>Total equipos:</b> {len(activos)}",
        styles['Normal']
    )
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    # ✅ Construir tabla DINÁMICAMENTE con columnas seleccionadas
    data = [columnas]  # Encabezados = columnas seleccionadas
    
    for a in activos:
        fila = []
        for col in columnas:
            valor = _obtener_valor_celda(a, col)
            # Recortar nombres muy largos
            if col == 'Nombre' and isinstance(valor, str):
                valor = valor[:30]
            fila.append(str(valor))
        data.append(fila)
    
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9B2335')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    fecha_archivo = datetime.now().strftime('%Y%m%d')
    nombre = f'auditoria_ti_{fecha_archivo}.pdf'
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre,
        mimetype='application/pdf'
    )
 
# ── Reporte Excel ─────────────────────────────────────────────
@rh_bp.route("/auditoria/reporte/excel")
@login_required
@requiere_permiso('Auditoria', 'ver')
def auditoria_reporte_excel():
    """Genera reporte Excel con SOLO las columnas seleccionadas."""
    
    tipo_filter = request.args.get('tipo', '')
    cond_filter = request.args.get('condicion', '')
    columnas = _obtener_columnas_solicitadas()
    
    activos = _obtener_activos_filtrados(tipo_filter, cond_filter)
    
    # ✅ Construir filas DINÁMICAMENTE con columnas seleccionadas
    activos_excel = []
    for a in activos:
        fila = {}
        for col in columnas:
            fila[col] = _obtener_valor_celda(a, col)
        activos_excel.append(fila)
    
    df = pd.DataFrame(activos_excel)
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Auditoría TI', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Auditoría TI']
        
        # Ajustar anchos
        for column in worksheet.columns:
            max_length = 0
            column_cells = [cell for cell in column]
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_cells[0].column_letter].width = adjusted_width
        
        # Estilo header
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_fill = PatternFill(start_color="9B2335", end_color="9B2335", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    buffer.seek(0)
    
    fecha_archivo = datetime.now().strftime('%Y%m%d')
    nombre = f'auditoria_ti_{fecha_archivo}.xlsx'
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
 
 
# ── Reporte CSV ───────────────────────────────────────────────
@rh_bp.route("/auditoria/reporte/csv")
@login_required
@requiere_permiso('Auditoria', 'ver')
def auditoria_reporte_csv():
    """Genera reporte CSV con SOLO las columnas seleccionadas."""
    
    tipo_filter = request.args.get('tipo', '')
    cond_filter = request.args.get('condicion', '')
    columnas = _obtener_columnas_solicitadas()
    
    activos = _obtener_activos_filtrados(tipo_filter, cond_filter)
    
    # Crear CSV en memoria
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    
    # ✅ Encabezados = columnas seleccionadas
    writer.writerow(columnas)
    
    # ✅ Datos solo con columnas seleccionadas
    for a in activos:
        fila = [_obtener_valor_celda(a, col) for col in columnas]
        writer.writerow(fila)
    
    output.seek(0)
    
    # BOM para que Excel abra acentos correctamente
    csv_bytes = '\ufeff' + output.getvalue()
    buffer = BytesIO(csv_bytes.encode('utf-8'))
    
    fecha_archivo = datetime.now().strftime('%Y%m%d')
    nombre = f'auditoria_ti_{fecha_archivo}.csv'
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre,
        mimetype='text/csv'
    )
 