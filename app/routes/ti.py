# app/routes/ti.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import text as sqla_text
from ..extensions import db, socketio
from ..models.electronico import Electronico, MantenimientoElectronico
from ..models.usuario import Usuario
from ..models.vehiculo import Ubicacion
from ..models.herramienta import EvidenciaEquipo
from ..views.ti_vistas import VEquiposTI, VEstadisticasTI, VMantenimientoElectronico
from ..utils.permisos import requiere_rol, requiere_permiso
from ..utils.archivos import guardar_archivo
from ..models.baja_activo import BajaActivo

ti_bp = Blueprint("ti", __name__)

ROLES_TI = ("ti", "admin")


def _check_acceso():
    if current_user.rol not in ROLES_TI:
        flash("No tienes acceso al módulo TI.", "error")
        return False
    return True


def _emit_actualizar():
    socketio.emit('ti_equipos_update', {}, namespace='/')


# ── Dashboard TI ──────────────────────────────────────────────
@ti_bp.route("/")
@login_required
@requiere_permiso('Equipos TI')
def dashboard():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    stats          = VEstadisticasTI.query.first()
    equipos        = VEquiposTI.query.all()
    mantenimientos = VMantenimientoElectronico.query.filter_by(Estatus="en_proceso").limit(8).all()

    por_tipo = {}
    for e in equipos:
        por_tipo[e.TipoEquipo] = por_tipo.get(e.TipoEquipo, 0) + 1

    por_area = {}
    for e in equipos:
        if e.UsuarioRol:
            por_area[e.UsuarioRol] = por_area.get(e.UsuarioRol, 0) + 1

    return render_template("ti/dashboard.html",
        stats          = stats,
        equipos        = equipos[:10],
        mantenimientos = mantenimientos,
        por_tipo       = por_tipo,
        por_area       = por_area,
    )


# ── Gestión de equipos ────────────────────────────────────────
@ti_bp.route("/equipos")
@login_required
@requiere_permiso('Equipos TI')
def equipos():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    tipo   = request.args.get("tipo", "")
    estado = request.args.get("estado", "")
    query  = VEquiposTI.query

    if tipo:
        query = query.filter_by(TipoEquipo=tipo)
    if estado:
        query = query.filter_by(Estado=estado)
    else:
        query = query.filter(VEquiposTI.Estado != 'baja')

    usuarios    = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ubicaciones = Ubicacion.query.all()

    return render_template("ti/equipos.html",
        equipos       = query.order_by(VEquiposTI.Nombre).all(),
        usuarios      = usuarios,
        ubicaciones   = ubicaciones,
        tipo_filtro   = tipo,
        estado_filtro = estado,
    )


# ── Alta equipo ───────────────────────────────────────────────
@ti_bp.route("/equipos/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'crear')
def equipo_nuevo():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        e = Electronico(
            Nombre           = request.form.get("nombre", "").strip(),
            Marca            = request.form.get("marca", "").strip() or None,
            Modelo           = request.form.get("modelo", "").strip() or None,
            NumeroSerie      = request.form.get("numero_serie", "").strip() or None,
            TipoEquipo       = request.form.get("tipo_equipo", "otro"),
            Gama             = request.form.get("gama") or None,
            Estado           = request.form.get("estado", "almacen"),
            Condicion        = "bueno",
            FechaAdquisicion = request.form.get("fecha_adquisicion") or None,
            Costo            = float(request.form.get("costo") or 0),
            Descripcion      = request.form.get("descripcion", "").strip() or None,
            IdUbicacion      = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None,
            IMEI                   = request.form.get("imei", "").strip() or None,
            Procesador             = request.form.get("procesador", "").strip() or None,
            MemoriaRAM             = request.form.get("memoria_ram", "").strip() or None,
            Almacenamiento         = request.form.get("almacenamiento", "").strip() or None,
            SistemaOperativo       = request.form.get("sistema_operativo", "").strip() or None,
            Garantia               = request.form.get("garantia") or None,
            Accesorios             = request.form.get("accesorios", "").strip() or None,
            Comentarios            = request.form.get("comentarios", "").strip() or None,
            Arrendamiento          = bool(request.form.get("arrendamiento")),
            FechaRenovacion        = request.form.get("fecha_renovacion") or None,
            ProveedorArrendamiento = request.form.get("proveedor_arrendamiento", "").strip() or None,
        )
        db.session.add(e)
        db.session.flush()

        factura = request.files.get("factura")
        if factura and factura.filename:
            info = guardar_archivo(archivo=factura, prefijo=f"equipo_{e.IdElectronico}_factura", carpeta="documents")
            db.session.add(EvidenciaEquipo(
                IdElectronico=e.IdElectronico, ArchivoUrl=info["url"],
                NombreArchivo=info["filename"], Tipo="factura",
                TipoArchivo="documento", MimeType=info["mime_type"],
                Descripcion="Factura de compra", CreadoPor=current_user.id,
            ))

        evidencia = request.files.get("evidencia")
        if evidencia and evidencia.filename:
            info = guardar_archivo(archivo=evidencia, prefijo=f"equipo_{e.IdElectronico}_foto", carpeta="static/evidencias")
            db.session.add(EvidenciaEquipo(
                IdElectronico=e.IdElectronico, ArchivoUrl=info["url"],
                NombreArchivo=info["filename"], Tipo="entrega",
                TipoArchivo="imagen", MimeType=info["mime_type"],
                Descripcion="Foto inicial al dar de alta", CreadoPor=current_user.id,
            ))

        db.session.commit()
        _emit_actualizar()
        flash(f"Equipo '{e.Nombre}' registrado correctamente.", "success")

    except Exception as ex:
        db.session.rollback()
        flash(f"Error: {str(ex)}", "error")

    return redirect(url_for("ti.equipos"))


# ── Editar equipo ─────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/editar", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'editar')
def equipo_editar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    e = Electronico.query.get_or_404(id)
    e.Nombre           = request.form.get("nombre", "").strip()
    e.Marca            = request.form.get("marca", "").strip() or None
    e.Modelo           = request.form.get("modelo", "").strip() or None
    e.NumeroSerie      = request.form.get("numero_serie", "").strip() or None
    e.TipoEquipo       = request.form.get("tipo_equipo", "otro")
    e.Costo            = float(request.form.get("costo") or 0)
    e.FechaAdquisicion = request.form.get("fecha_adquisicion") or None
    e.Descripcion      = request.form.get("descripcion", "").strip() or None
    e.Condicion        = request.form.get("condicion", "bueno")
    e.IdUbicacion      = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None
    db.session.commit()
    _emit_actualizar()
    flash("Equipo actualizado.", "success")
    return redirect(url_for("ti.equipos"))


# ── Asignar equipo ────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/asignar", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'editar')
def equipo_asignar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    usuario_id  = request.form.get('usuario_id', type=int)
    proyecto_id = request.form.get('proyecto_id', type=int)

    if not usuario_id:
        flash('Selecciona un usuario.', 'warning')
        return redirect(url_for('ti.equipo_detalle', id=id))

    try:
        db.session.execute(db.text("""
            UPDATE electronico SET IdUsuario = :uid, Estado = 'asignado'
            WHERE IdElectronico = :id
        """), {'uid': usuario_id, 'id': id})

        if proyecto_id:
            existente = db.session.execute(db.text("""
                SELECT IdAsignacion FROM proyectoactivo
                WHERE IdProyecto = :pid AND TipoActivo = 'electronico'
                  AND IdActivo = :aid AND FechaDevolucion IS NULL LIMIT 1
            """), {'pid': proyecto_id, 'aid': id}).fetchone()

            if not existente:
                db.session.execute(db.text("""
                    INSERT INTO proyectoactivo
                        (IdProyecto, TipoActivo, IdActivo, EstadoInicial, AsignadoPor, FechaAsignacion)
                    VALUES (:pid, 'electronico', :aid, 'bueno', :usr, CURDATE())
                """), {'pid': proyecto_id, 'aid': id, 'usr': current_user.IdUsuario})

        db.session.commit()
        _emit_actualizar()
        flash('Equipo asignado correctamente.', 'success')

    except Exception as ex:
        db.session.rollback()
        flash(f'Error al asignar: {str(ex)}', 'error')

    return redirect(url_for('ti.equipo_detalle', id=id))


# ── Liberar equipo ────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/liberar", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'editar')
def equipo_liberar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    e = Electronico.query.get_or_404(id)
    e.IdUsuario = None
    e.Estado    = "almacen"
    db.session.commit()
    _emit_actualizar()
    flash("Equipo regresado al almacén.", "success")
    return redirect(url_for("ti.equipo_detalle", id=id))


# ── Detalle equipo ────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>")
@login_required
@requiere_permiso('Equipos TI')
def equipo_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    equipo         = Electronico.query.get_or_404(id)
    mantenimientos = VMantenimientoElectronico.query.filter_by(IdElectronico=id).all()
    usuarios       = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ubicaciones    = Ubicacion.query.all()
    evidencias     = EvidenciaEquipo.query.filter_by(
        IdElectronico=id
    ).order_by(EvidenciaEquipo.CreadoEn.desc()).all()

    proyectos_activos = db.session.execute(db.text("""
        SELECT IdProyecto, Nombre, Estatus FROM proyecto
        WHERE Estatus NOT IN ('Completado','Cancelado') ORDER BY Nombre
    """)).fetchall()

    return render_template("ti/equipo_detalle.html",
        equipo            = equipo,
        evidencias        = evidencias,
        mantenimientos    = mantenimientos,
        usuarios          = usuarios,
        ubicaciones       = ubicaciones,
        today             = date.today(),
        proyectos_activos = proyectos_activos,
    )


# ── Mantenimiento nuevo ───────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/mantenimiento/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'crear')
def mantenimiento_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_mantenimiento_electronico(:eid,:tipo,:diag,:desc,:fi,:ft,:costo,:tec,:usr,@res,@id)"),
            {
                "eid":   id,
                "tipo":  request.form.get("tipo", "previo"),
                "diag":  request.form.get("diagnostico", "").strip() or None,
                "desc":  request.form.get("descripcion", "").strip() or None,
                "fi":    request.form.get("fecha_inicio"),
                "ft":    request.form.get("fecha_termino") or None,
                "costo": float(request.form.get("costo") or 0),
                "tec":   request.form.get("tecnico", "").strip() or None,
                "usr":   current_user.id,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        _emit_actualizar()
        flash(
            "Mantenimiento registrado." if row and row.r == "OK" else f"Error: {row.r}.",
            "success" if row and row.r == "OK" else "error"
        )
    except Exception as ex:
        db.session.rollback()
        flash(f"Error: {str(ex)}", "error")

    return redirect(url_for("ti.equipo_detalle", id=id))


# ── Completar mantenimiento ───────────────────────────────────
@ti_bp.route("/mantenimiento/<int:id>/completar", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'editar')
def mantenimiento_completar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    m = MantenimientoElectronico.query.get_or_404(id)
    m.Estatus      = "completado"
    m.FechaTermino = request.form.get("fecha_termino") or date.today()
    m.Descripcion  = request.form.get("descripcion", m.Descripcion)

    otros = MantenimientoElectronico.query.filter_by(
        IdElectronico=m.IdElectronico, Estatus="en_proceso"
    ).filter(MantenimientoElectronico.IdMantenimiento != id).count()

    if otros == 0:
        e = Electronico.query.get(m.IdElectronico)
        if e and e.Estado == "mantenimiento":
            e.Estado = "almacen" if not e.IdUsuario else "asignado"

    db.session.commit()
    _emit_actualizar()
    flash("Mantenimiento completado.", "success")
    return redirect(url_for("ti.equipo_detalle", id=m.IdElectronico))


# ── Validación de estados ─────────────────────────────────────
@ti_bp.route("/validacion")
@login_required
@requiere_permiso('Equipos TI')
def validacion_estados():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    stats       = VEstadisticasTI.query.first()
    buen_estado = VEquiposTI.query.filter_by(Condicion="bueno").all()
    mal_estado  = VEquiposTI.query.filter(
        VEquiposTI.Condicion.in_(["malo", "dañado", "regular"])
    ).all()

    return render_template("ti/validacion.html",
        stats       = stats,
        buen_estado = buen_estado,
        mal_estado  = mal_estado,
    )


# ── Reporte consolidado ───────────────────────────────────────
@ti_bp.route("/reporte/consolidado")
@login_required
@requiere_permiso('Equipos TI')
def reporte_consolidado():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    tipo_filter     = request.args.get('tipo', '')
    estado_filter   = request.args.get('estado', '')
    proyecto_filter = request.args.get('proyecto_id', type=int)

    sql    = "SELECT * FROM v_equipos_consolidado WHERE 1=1"
    params = {}

    if tipo_filter:
        sql += " AND TipoEquipo = :tipo"
        params['tipo'] = tipo_filter
    if estado_filter:
        sql += " AND EstadoEquipo = :estado"
        params['estado'] = estado_filter
    if proyecto_filter:
        sql += " AND (IdProyecto = :pid OR IdProyectoEquipo = :pid)"
        params['pid'] = proyecto_filter

    sql += " ORDER BY NombreEquipo"

    equipos   = db.session.execute(db.text(sql), params).fetchall()
    proyectos = db.session.execute(db.text(
        "SELECT IdProyecto, Nombre, Estatus FROM proyecto ORDER BY Nombre"
    )).fetchall()

    return render_template('ti/reporte_consolidado.html',
        equipos         = equipos,
        proyectos       = proyectos,
        tipo_filter     = tipo_filter,
        estado_filter   = estado_filter,
        proyecto_filter = proyecto_filter,
    )


# ── Baja equipo ───────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/baja", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'eliminar')
def equipo_baja(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    e = Electronico.query.get_or_404(id)
    e.Estado = "baja"
    db.session.add(BajaActivo(
        TipoActivo    = "electronico",
        IdActivo      = e.IdElectronico,
        NombreActivo  = e.Nombre,
        DadoDeBajaPor = current_user.id,
    ))
    db.session.commit()
    _emit_actualizar()
    flash(f"'{e.Nombre}' dado de baja.", "success")
    return redirect(url_for("ti.equipos"))


# ── API ───────────────────────────────────────────────────────
@ti_bp.route("/api/equipo/<int:id>")
@login_required
def api_equipo(id):
    e = Electronico.query.get_or_404(id)
    return jsonify(e.to_dict())