import math
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..extensions import db
from ..models.activo import Activo
from ..models.departamento import Departamento
from ..views.vistas import VActivo, VDashboardStats, VActivoPorDepartamento
from datetime import datetime

activos_bp = Blueprint("activos", __name__)

PER_PAGE = 8


@activos_bp.route("/dashboard")
@login_required
def dashboard():
    # Usar vista para stats — una sola consulta
    stats     = VDashboardStats.query.first()
    recientes = VActivo.query.order_by(VActivo.creado_en.desc()).limit(6).all()
    por_depto = VActivoPorDepartamento.query.order_by(
                    VActivoPorDepartamento.total_activos.desc()).all()

    return render_template("dashboard.html",
        total        = stats.total_activos    if stats else 0,
        activos      = stats.activos          if stats else 0,
        baja         = stats.bajas            if stats else 0,
        mantenimiento= stats.en_mantenimiento if stats else 0,
        valor_total  = stats.valor_total      if stats else 0,
        recientes    = recientes,
        por_depto    = por_depto,
    )


@activos_bp.route("/")
@login_required
def lista():
    estado = request.args.get("estado", "")
    page   = request.args.get("page", 1, type=int)

    # Consultar vista en lugar de tabla directa
    query = VActivo.query
    if estado:
        query = query.filter(VActivo.estado == estado)

    total_items = query.count()
    total_pages = max(1, math.ceil(total_items / PER_PAGE))
    page        = max(1, min(page, total_pages))

    items  = query.order_by(VActivo.creado_en.desc()) \
                  .offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    deptos = Departamento.query.all()

    return render_template("activos.html",
        activos      = items,
        departamentos= deptos,
        page         = page,
        total_pages  = total_pages,
    )


@activos_bp.route("/nuevo", methods=["POST"])
@login_required
def nuevo():
    # Escrituras siguen usando el modelo real (tabla activos)
    fecha = request.form.get("fecha_adquisicion")
    activo = Activo(
        nombre            = request.form["nombre"],
        descripcion       = request.form.get("descripcion"),
        numero_serie      = request.form.get("numero_serie") or None,
        categoria         = request.form.get("categoria") or None,
        estado            = request.form.get("estado", "activo"),
        valor             = float(request.form.get("valor") or 0),
        departamento_id   = request.form.get("departamento_id") or None,
        usuario_id        = current_user.id,
        fecha_adquisicion = datetime.strptime(fecha, "%Y-%m-%d").date() if fecha else None,
    )
    db.session.add(activo)
    db.session.commit()
    flash(f'Activo "{activo.nombre}" creado correctamente.', "success")
    return redirect(url_for("activos.lista"))


@activos_bp.route("/<int:id>/editar", methods=["POST"])
@login_required
def editar(id):
    activo = db.get_or_404(Activo, id)
    activo.nombre          = request.form["nombre"]
    activo.descripcion     = request.form.get("descripcion")
    activo.numero_serie    = request.form.get("numero_serie") or None
    activo.categoria       = request.form.get("categoria") or None
    activo.estado          = request.form.get("estado", "activo")
    activo.valor           = float(request.form.get("valor") or 0)
    activo.departamento_id = request.form.get("departamento_id") or None
    fecha = request.form.get("fecha_adquisicion")
    if fecha:
        activo.fecha_adquisicion = datetime.strptime(fecha, "%Y-%m-%d").date()
    db.session.commit()
    flash(f'Activo "{activo.nombre}" actualizado.', "success")
    return redirect(url_for("activos.lista"))


@activos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    activo = db.get_or_404(Activo, id)
    nombre = activo.nombre
    db.session.delete(activo)
    db.session.commit()
    flash(f'Activo "{nombre}" eliminado.', "success")
    return redirect(url_for("activos.lista"))


@activos_bp.route("/api")
@login_required
def api_lista():
    items = VActivo.query.all()
    return jsonify([a.to_dict() for a in items])