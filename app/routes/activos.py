# app/routes/activos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
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
    uid  = current_user.id
    area = current_user.area_nombre or "Mi área"
    activos = db.session.execute(text("""
        SELECT a.nombre, a.categoria, a.estado, a.valor, a.creado_en
        FROM activos a
        WHERE a.usuario_id = :uid
        ORDER BY a.creado_en DESC
        LIMIT 20
    """), {'uid': uid}).fetchall()
    return render_template("portal_empleado.html",
        area_nombre = area,
        activos     = activos,
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

    return render_template("activos.html",
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