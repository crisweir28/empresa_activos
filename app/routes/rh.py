# app/routes/rh.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from datetime import datetime

rh_bp = Blueprint('rh', __name__, url_prefix='/rh')

# ─────────────────────────────────────────────────────────────
# Helper de permisos (igual que los otros blueprints)
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

    return render_template('rh/auditoria.html',
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


# ============================================================
#  AGREGAR ESTAS RUTAS AL FINAL DE app/routes/rh.py
# ============================================================

# ── Dashboard de empleado (todos sus activos + proyectos) ────

@rh_bp.route('/empleado/<int:uid>')
@login_required
def empleado_dashboard(uid):
    if not _puede('ver'):
        flash('Sin permiso.', 'warning')
        return redirect(url_for('activos.dashboard'))

    # Info del empleado
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

    # Todos sus activos con proyecto relacionado
    activos = db.session.execute(db.text("""
        SELECT * FROM v_empleado_activos_completo
        WHERE IdUsuario = :uid
        ORDER BY TipoActivo, NombreActivo
    """), {'uid': uid}).fetchall()

    # Proyectos en los que participa el empleado
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

    # Resumen por tipo
    resumen = {'electronico': 0, 'herramienta': 0, 'general': 0, 'total': 0}
    valor_total = 0
    for a in activos:
        resumen[a.TipoActivo] = resumen.get(a.TipoActivo, 0) + 1
        resumen['total'] += 1
        valor_total += float(a.Valor or 0)

    # Proceso de baja activo si existe
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

    # Stats rápidos
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