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

from flask import send_file
from io import BytesIO
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


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
# ── Dashboard TI ──────────────────────────────────────────────
@ti_bp.route("/")
@login_required
@requiere_permiso('Equipos TI')
def dashboard():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    todos_equipos = VEquiposTI.query.all()
    mantenimientos = VMantenimientoElectronico.query.filter_by(Estatus="en_proceso").limit(8).all()

    # ✅ CALCULAR STATS DESDE PYTHON (excluyendo bajas)
    equipos_activos = [e for e in todos_equipos if e.Estado != 'baja']
    
    class Stats:
        TotalEquipos    = len(equipos_activos)
        EnAlmacen       = sum(1 for e in equipos_activos if e.Estado == 'almacen')
        Asignados       = sum(1 for e in equipos_activos if e.Estado == 'asignado')
        EnMantenimiento = sum(1 for e in equipos_activos if e.Estado == 'mantenimiento')
        EnBuenEstado    = sum(1 for e in equipos_activos if e.Condicion == 'bueno')
        EnMalEstado     = sum(1 for e in equipos_activos if e.Condicion in ('malo', 'dañado', 'regular'))
    
    stats = Stats()
    
    # Calcular bajas
    bajas = sum(1 for e in todos_equipos if e.Estado == 'baja')

    por_tipo = {}
    for e in equipos_activos:  # ← solo equipos activos
        por_tipo[e.TipoEquipo] = por_tipo.get(e.TipoEquipo, 0) + 1

    por_area = {}
    for e in equipos_activos:
        if e.UsuarioRol:
            por_area[e.UsuarioRol] = por_area.get(e.UsuarioRol, 0) + 1

    # Para modales
    usuarios = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ubicaciones = Ubicacion.query.all()

    return render_template("ti/dashboard.html",
        stats=stats,
        equipos=todos_equipos,
        mantenimientos=mantenimientos,
        por_tipo=por_tipo,
        por_area=por_area,
        bajas=bajas,
        usuarios=usuarios,
        ubicaciones=ubicaciones,
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
        from ..models.asignacion import AsignacionEquipo
        from datetime import datetime
        
        # 1. Actualizar el equipo
        db.session.execute(db.text("""
            UPDATE electronico SET IdUsuario = :uid, Estado = 'asignado'
            WHERE IdElectronico = :id
        """), {'uid': usuario_id, 'id': id})
 
        # 2. ✅ REGISTRAR EN HISTORIAL
        nueva_asignacion = AsignacionEquipo(
            IdEquipo=id,
            IdUsuario=usuario_id,
            FechaAsignacion=datetime.utcnow(),
            AsignadoPor=current_user.id
        )
        db.session.add(nueva_asignacion)
 
        # 3. Proyecto (si aplica)
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
 

# ── Liberar equipo (CON HISTORIAL) ────────────────────────────
@ti_bp.route("/equipos/<int:id>/liberar", methods=["POST"])
@login_required
@requiere_permiso('Equipos TI', 'editar')
def equipo_liberar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
 
    try:
        from ..models.asignacion import AsignacionEquipo
        from datetime import datetime
        
        # 1. ✅ CERRAR LA ASIGNACIÓN ACTUAL EN EL HISTORIAL
        asignacion_actual = AsignacionEquipo.query.filter_by(
            IdEquipo=id,
            FechaLiberacion=None
        ).first()
        
        if asignacion_actual:
            asignacion_actual.FechaLiberacion = datetime.utcnow()
        
        # 2. Liberar el equipo
        db.session.execute(db.text("""
            UPDATE electronico 
            SET IdUsuario = NULL, Estado = 'almacen'
            WHERE IdElectronico = :id
        """), {'id': id})
        
        db.session.commit()
        _emit_actualizar()
        flash("Equipo regresado al almacén.", "success")
        
    except Exception as ex:
        db.session.rollback()
        flash(f'Error al liberar: {str(ex)}', 'error')
    
    return redirect(url_for('ti.equipo_detalle', id=id))

# ── Detalle equipo (CON HISTORIAL) ───────────────────────────
@ti_bp.route("/equipos/<int:id>")
@login_required
def equipo_detalle(id):
    """Vista de detalle de un equipo con toda su información"""
    from ..models.electronico import Electronico, MantenimientoElectronico
    from ..models.herramienta import EvidenciaEquipo
    from ..models.usuario import Usuario
    from ..models.asignacion import AsignacionEquipo  # ← HABILITAR ESTE IMPORT
    from datetime import datetime
    
    equipo = Electronico.query.get_or_404(id)
    
    mantenimientos = MantenimientoElectronico.query.filter_by(
        IdElectronico=id
    ).order_by(MantenimientoElectronico.FechaInicio.desc()).all()
    
    evidencias = EvidenciaEquipo.query.filter_by(
        IdElectronico=id
    ).order_by(EvidenciaEquipo.CreadoEn.desc()).all()
    
    # ✅ HABILITAR: Obtener historial de asignaciones
    historial_asignaciones = AsignacionEquipo.query.filter_by(
        IdEquipo=id
    ).order_by(AsignacionEquipo.FechaAsignacion.desc()).all()
    
    # Lista de usuarios para el modal de asignación
    usuarios = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    
    # Iconos para evidencias
    for ev in evidencias:
        if ev.TipoArchivo == 'imagen':
            ev.icono = '🖼️'
        else:
            ext = ev.NombreArchivo.rsplit('.', 1)[-1].lower() if ev.NombreArchivo else ''
            ev.icono = {
                'pdf': '📄', 'doc': '📝', 'docx': '📝',
                'xls': '📊', 'xlsx': '📊', 'csv': '📊',
                'txt': '📃', 'zip': '📦', 'rar': '📦'
            }.get(ext, '📎')
    
    return render_template(
        "ti/equipo_detalle.html",
        equipo=equipo,
        mantenimientos=mantenimientos,
        evidencias=evidencias,
        historial_asignaciones=historial_asignaciones,  # ✅ CON DATOS REALES
        usuarios=usuarios,
        now=datetime.utcnow()
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


# ── Reporte PDF ───────────────────────────────────────────────
@ti_bp.route("/reporte/pdf")
@login_required
@requiere_permiso('Equipos TI')
def reporte_pdf():
    """Genera reporte PDF de equipos según filtro"""
    
    filtro = request.args.get('filtro', 'todos')
    
    # Obtener equipos según filtro
    query = db.session.execute(db.text("""
        SELECT 
            e.Nombre,
            e.TipoEquipo,
            e.Marca,
            e.Modelo,
            e.NumeroSerie,
            e.Estado,
            e.Condicion,
            CONCAT(u.Nombre, ' ', u.ApellidoPaterno) as Usuario,
            e.FechaAdquisicion,
            e.Costo
        FROM electronico e
        LEFT JOIN usuario u ON e.IdUsuario = u.IdUsuario
        WHERE 1=1
    """))
    
    equipos = [dict(row._mapping) for row in query.fetchall()]
    
    # Filtrar según el filtro activo
    if filtro != 'todos':
        if filtro in ('almacen', 'asignado', 'mantenimiento', 'baja'):
            equipos = [e for e in equipos if e['Estado'] == filtro]
        elif filtro == 'bueno':
            equipos = [e for e in equipos if e['Condicion'] == 'bueno']
        elif filtro == 'malo':
            equipos = [e for e in equipos if e['Condicion'] in ('malo', 'dañado', 'regular')]
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo_filtro = {
        'todos': 'Todos los Equipos',
        'almacen': 'Equipos en Almacén',
        'asignado': 'Equipos Asignados',
        'bueno': 'Equipos en Buen Estado',
        'malo': 'Equipos en Mal Estado',
        'mantenimiento': 'Equipos en Mantenimiento',
        'baja': 'Equipos Dados de Baja'
    }.get(filtro, 'Equipos')
    
    title = Paragraph(f"<b>Reporte de Equipos TI</b><br/>{titulo_filtro}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de generación
    fecha_generacion = datetime.now().strftime('%d/%m/%Y %H:%M')
    info = Paragraph(f"<b>Generado:</b> {fecha_generacion}<br/><b>Total equipos:</b> {len(equipos)}", styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de datos
    data = [['Equipo', 'Tipo', 'Serie', 'Estado', 'Condición', 'Usuario']]
    
    for e in equipos:
        data.append([
            e['Nombre'],
            e['TipoEquipo'],
            e['NumeroSerie'] or '—',
            e['Estado'],
            e['Condicion'],
            e['Usuario'] or '—'
        ])
    
    # Crear tabla con estilo
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Enviar archivo
    fecha_archivo = datetime.now().strftime('%Y%m%d')
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'equipos_ti_{filtro}_{fecha_archivo}.pdf',
        mimetype='application/pdf'
    )
 
 
# ── Reporte Excel ─────────────────────────────────────────────
@ti_bp.route("/reporte/excel")
@login_required
@requiere_permiso('Equipos TI')
def reporte_excel():
    """Genera reporte Excel de equipos según filtro"""
    
    filtro = request.args.get('filtro', 'todos')
    
    # Obtener equipos según filtro
    query = db.session.execute(db.text("""
        SELECT 
            e.Nombre as Equipo,
            e.TipoEquipo as Tipo,
            e.Marca,
            e.Modelo,
            e.NumeroSerie as 'N° Serie',
            e.Estado,
            e.Condicion as 'Condición',
            CONCAT(u.Nombre, ' ', u.ApellidoPaterno) as 'Asignado a',
            DATE_FORMAT(e.FechaAdquisicion, '%d/%m/%Y') as 'Fecha Adquisición',
            CONCAT('$', FORMAT(e.Costo, 2)) as Costo,
            ub.Nombre as 'Ubicación'
        FROM electronico e
        LEFT JOIN usuario u ON e.IdUsuario = u.IdUsuario
        LEFT JOIN ubicacion ub ON e.IdUbicacion = ub.IdUbicacion
        WHERE 1=1
    """))
    
    equipos = [dict(row._mapping) for row in query.fetchall()]
    
    # Filtrar según el filtro activo
    if filtro != 'todos':
        if filtro in ('almacen', 'asignado', 'mantenimiento', 'baja'):
            equipos = [e for e in equipos if e['Estado'] == filtro]
        elif filtro == 'bueno':
            equipos = [e for e in equipos if e['Condición'] == 'bueno']
        elif filtro == 'malo':
            equipos = [e for e in equipos if e['Condición'] in ('malo', 'dañado', 'regular')]
    
    # Crear DataFrame
    df = pd.DataFrame(equipos)
    
    # Crear archivo Excel en memoria
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Equipos TI', index=False)
        
        # Obtener workbook y worksheet para aplicar estilos
        workbook = writer.book
        worksheet = writer.sheets['Equipos TI']
        
        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # Aplicar estilos al header
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_fill = PatternFill(start_color="2563eb", end_color="2563eb", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    buffer.seek(0)
    
    # Enviar archivo
    fecha_archivo = datetime.now().strftime('%Y%m%d')
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'equipos_ti_{filtro}_{fecha_archivo}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )