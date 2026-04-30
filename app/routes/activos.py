# app/routes/activos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import text
from ..extensions import db
from ..models.activo import Activo
from ..models.departamento import Departamento
from ..views import VActivo, VDashboardStats, VActivoPorDepartamento
from ..utils.permisos import es_admin, puede_editar_activo


activos_bp = Blueprint("activos", __name__)

# ── Temas visuales por rol ────────────────────────────────────
DEPTO_TEMAS = {
    "ti": {
        "nombre": "Tecnología e Información",
        "icon":   "💻",
        "color":  "#7c5cfc",
        "color2": "#e040fb",
        "rgb":    "124,92,252",
        "rgb2":   "224,64,251",
    },
    "administrativo": {
        "nombre": "Administrativo",
        "icon":   "🚗",
        "color":  "#fbbf24",
        "color2": "#f97316",
        "rgb":    "251,191,36",
        "rgb2":   "249,115,22",
    },
    "almacenista": {
        "nombre": "Almacén",
        "icon":   "📦",
        "color":  "#22d3a5",
        "color2": "#0ea5e9",
        "rgb":    "34,211,165",
        "rgb2":   "14,165,233",
    },
    "rh": {
        "nombre": "Recursos Humanos",
        "icon":   "👥",
        "color":  "#a78bfa",
        "color2": "#818cf8",
        "rgb":    "167,139,250",
        "rgb2":   "129,140,248",
    },
    "supervisor": {
        "nombre": "Supervisor",
        "icon":   "🔍",
        "color":  "#f87171",
        "color2": "#fb923c",
        "rgb":    "248,113,113",
        "rgb2":   "251,146,60",
    },
}


def _get_departamentos():
    if es_admin():
        return Departamento.query.order_by(Departamento.nombre).all()
    if current_user.departamento_id:
        return Departamento.query.filter_by(id=current_user.departamento_id).all()
    return []


def _portal_empleado():
    """Renderiza el portal de empleado con sus activos."""
    uid = current_user.id
    
    # Verificar si es conductor
    es_conductor = db.session.execute(text("""
        SELECT COUNT(*) as count FROM personal p
        INNER JOIN usuario u ON CONCAT(p.Nombre, p.Apellido) = u.NombreUsuario
        WHERE u.IdUsuario = :uid AND p.Activo = TRUE
    """), {'uid': uid}).fetchone().count > 0
    
    # Obtener equipos TI asignados
    equipos_raw = db.session.execute(text("""
        SELECT IdEquipo, Nombre, Marca, Modelo, MarcaModelo, TipoEquipo, 
               NumeroSerie, Estado, Condicion, Valor
        FROM v_equipos_usuario 
        WHERE IdUsuario = :uid
    """), {'uid': uid}).fetchall()
    
    # Convertir a diccionarios
    mis_equipos = []
    for row in equipos_raw:
        mis_equipos.append({
            'IdEquipo': row[0],
            'Nombre': row[1],
            'Marca': row[2],
            'Modelo': row[3],
            'MarcaModelo': row[4],
            'TipoEquipo': row[5],
            'NumeroSerie': row[6],
            'Estado': row[7],
            'Condicion': row[8],
            'Valor': row[9]
        })
    
    # ← NUEVO: Obtener herramientas asignadas
    herramientas_raw = db.session.execute(text("""
        SELECT 
            h.IdHerramienta,
            h.Nombre,
            h.Marca,
            h.Modelo,
            h.NumeroSerie,
            h.Estado,
            h.TipoHerramienta,
            h.Costo,
            a.FechaAsignacion
        FROM herramienta h
        JOIN asignacionherramienta a ON h.IdHerramienta = a.IdHerramienta
        WHERE a.IdUsuario = :uid 
          AND a.FechaDevolucion IS NULL
    """), {'uid': uid}).fetchall()
    
    # Convertir a diccionarios
    mis_herramientas = []
    for row in herramientas_raw:
        mis_herramientas.append({
            'IdHerramienta': row[0],
            'Nombre': row[1],
            'Marca': row[2],
            'Modelo': row[3],
            'NumeroSerie': row[4],
            'Estado': row[5],
            'TipoHerramienta': row[6],
            'Costo': row[7],
            'FechaAsignacion': row[8]
        })
    
    # Obtener vehículos asignados
    mis_vehiculos = []
    if es_conductor:
        try:
            vehiculos_raw = db.session.execute(text("""
                SELECT * FROM v_vehiculos_usuario WHERE IdUsuario = :uid
            """), {'uid': uid}).fetchall()
            mis_vehiculos = [dict(row._mapping) for row in vehiculos_raw]
        except:
            mis_vehiculos = []
    
    # Obtener documentos del usuario
    mis_documentos = []
    permisos_vehiculo = []
    if es_conductor:
        try:
            docs_raw = db.session.execute(text("""
                SELECT * FROM v_documentos_usuario 
                WHERE IdUsuario = :uid
                ORDER BY 
                    CASE EstadoDocumento
                        WHEN 'vencido' THEN 1
                        WHEN 'por_vencer' THEN 2
                        WHEN 'vigente' THEN 3
                        ELSE 4
                    END,
                    FechaVencimiento ASC
            """), {'uid': uid}).fetchall()
            mis_documentos = [dict(row._mapping) for row in docs_raw]
        except:
            mis_documentos = []
        
        # Obtener permisos del vehículo
        if mis_vehiculos:
            id_vehiculo = mis_vehiculos[0]['IdVehiculo']
            try:
                permisos_raw = db.session.execute(text("""
                    SELECT * FROM v_permisos_vehiculo 
                    WHERE IdVehiculo = :vid
                    ORDER BY FechaVencimiento ASC
                """), {'vid': id_vehiculo}).fetchall()
                permisos_vehiculo = [dict(row._mapping) for row in permisos_raw]
            except:
                permisos_vehiculo = []
    
    # Estadísticas (incluye herramientas ahora)
    docs_vencidos = sum(1 for d in mis_documentos if d.get('EstadoDocumento') == 'vencido')
    docs_por_vencer = sum(1 for d in mis_documentos if d.get('EstadoDocumento') == 'por_vencer')
    total_activos = len(mis_equipos) + len(mis_vehiculos) + len(mis_herramientas)  # ← ACTUALIZADO
    
    return render_template("portal_empleado/dashboard.html",
        area_nombre=current_user.rol_label or "Empleado",
        es_conductor=es_conductor,
        mis_equipos=mis_equipos,
        mis_herramientas=mis_herramientas,  # ← NUEVO
        mis_vehiculos=mis_vehiculos,
        mis_documentos=mis_documentos,
        permisos_vehiculo=permisos_vehiculo,
        total_activos=total_activos,
        docs_vencidos=docs_vencidos,
        docs_por_vencer=docs_por_vencer,
        hoy=date.today()
    )
    
@activos_bp.route("/dashboard")
@login_required
def dashboard():
    rol  = current_user.rol
    tema = DEPTO_TEMAS.get(rol, DEPTO_TEMAS["ti"])

    if rol == "admin":
        stats     = VDashboardStats.query.first()
        recientes = VActivo.query.order_by(VActivo.creado_en.desc()).limit(8).all()
        por_depto = VActivoPorDepartamento.query.order_by(
            VActivoPorDepartamento.total_activos.desc()
        ).all()
        return render_template("dashboard.html",
            total         = stats.total_activos   if stats else 0,
            activos       = stats.activos          if stats else 0,
            mantenimiento = stats.en_mantenimiento if stats else 0,
            baja          = stats.bajas            if stats else 0,
            recientes     = recientes,
            por_depto     = por_depto,
            tema          = tema,
        )

    elif rol == "ti":
        from ..utils.permisos import tiene_permiso
        if tiene_permiso('Equipos TI'):
            return redirect(url_for("ti.dashboard"))
        return _portal_empleado()

    elif rol == "administrativo":
        from ..utils.permisos import tiene_permiso
        if tiene_permiso('Dashboard'):
            return redirect(url_for("administrativo.dashboard"))
        if tiene_permiso('Vehículos'):
            return redirect(url_for("administrativo.vehiculos"))
        if tiene_permiso('Mantenimiento'):
            return redirect(url_for("administrativo.mantenimiento_lista"))
        return _portal_empleado()

    elif rol == "almacenista":
        from ..utils.permisos import tiene_permiso
        if tiene_permiso('Almacén'):
            return redirect(url_for("almacenista.dashboard"))
        return _portal_empleado()

    elif rol == "rh":
        from ..utils.permisos import tiene_permiso
        if tiene_permiso('Recursos Humanos'):
            return redirect(url_for("rh.activos_usuario"))
        return _portal_empleado()

    else:
        return _portal_empleado()


@activos_bp.route("/")
@login_required
def lista():
    estado = request.args.get("estado", "")
    query  = VActivo.query

    if not es_admin():
        query = query.filter_by(departamento_id=current_user.departamento_id)
    if estado:
        query = query.filter_by(estado=estado)

    page        = request.args.get("page", 1, type=int)
    per_page    = 15
    total       = query.count()
    total_pages = max(1, (total + per_page - 1) // per_page)
    activos     = query.order_by(VActivo.creado_en.desc()) \
                       .offset((page - 1) * per_page).limit(per_page).all()

    tema = DEPTO_TEMAS.get(current_user.rol, DEPTO_TEMAS["ti"])

    return render_template("activos/lista.html",
        activos       = activos,
        departamentos = _get_departamentos(),
        page          = page,
        total_pages   = total_pages,
        es_admin      = es_admin(),
        tema          = tema,
    )


@activos_bp.route("/nuevo", methods=["POST"])
@login_required
def nuevo():
    depto_id = request.form.get("departamento_id") or None
    if not es_admin():
        depto_id = current_user.departamento_id

    activo = Activo(
        nombre            = request.form.get("nombre", "").strip(),
        descripcion       = request.form.get("descripcion", "").strip() or None,
        numero_serie      = request.form.get("numero_serie", "").strip() or None,
        categoria         = request.form.get("categoria") or None,
        estado            = request.form.get("estado", "activo"),
        valor             = float(request.form.get("valor") or 0),
        fecha_adquisicion = request.form.get("fecha_adquisicion") or None,
        departamento_id   = int(depto_id) if depto_id else None,
        usuario_id        = current_user.id,
    )
    db.session.add(activo)
    db.session.commit()
    flash("Activo creado correctamente.", "success")
    return redirect(url_for("activos.lista"))


@activos_bp.route("/<int:id>/editar", methods=["POST"])
@login_required
def editar(id):
    activo = Activo.query.get_or_404(id)

    if not puede_editar_activo(activo):
        flash("No tienes permiso para editar este activo.", "error")
        return redirect(url_for("activos.lista"))

    activo.nombre            = request.form.get("nombre", "").strip()
    activo.descripcion       = request.form.get("descripcion", "").strip() or None
    activo.numero_serie      = request.form.get("numero_serie", "").strip() or None
    activo.categoria         = request.form.get("categoria") or None
    activo.estado            = request.form.get("estado", "activo")
    activo.valor             = float(request.form.get("valor") or 0)
    activo.fecha_adquisicion = request.form.get("fecha_adquisicion") or None

    if es_admin():
        depto_id = request.form.get("departamento_id") or None
        activo.departamento_id = int(depto_id) if depto_id else None

    db.session.commit()
    flash("Activo actualizado.", "success")
    return redirect(url_for("activos.lista"))


@activos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    activo = Activo.query.get_or_404(id)

    if not es_admin():
        flash("Solo TI puede eliminar activos.", "error")
        return redirect(url_for("activos.lista"))

    db.session.delete(activo)
    db.session.commit()
    flash("Activo eliminado.", "success")
    return redirect(url_for("activos.lista"))