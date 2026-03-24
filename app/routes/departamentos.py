from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from ..extensions import db
from ..models.departamento import Departamento
from ..views.vistas import VDepartamento

departamentos_bp = Blueprint("departamentos", __name__)


@departamentos_bp.route("/")
@login_required
def lista():
    # Usar vista — ya incluye total_activos y valor_total
    deptos = VDepartamento.query.order_by(VDepartamento.nombre).all()
    return render_template("departamentos.html", departamentos=deptos)


@departamentos_bp.route("/nuevo", methods=["POST"])
@login_required
def nuevo():
    depto = Departamento(
        nombre      = request.form["nombre"],
        descripcion = request.form.get("descripcion"),
    )
    db.session.add(depto)
    db.session.commit()
    flash(f'Departamento "{depto.nombre}" creado.', "success")
    return redirect(url_for("departamentos.lista"))


@departamentos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    depto = db.get_or_404(Departamento, id)
    nombre = depto.nombre
    db.session.delete(depto)
    db.session.commit()
    flash(f'Departamento "{nombre}" eliminado.', "success")
    return redirect(url_for("departamentos.lista"))


@departamentos_bp.route("/api")
@login_required
def api_lista():
    deptos = VDepartamento.query.all()
    return jsonify([{
        "id":           d.id,
        "nombre":       d.nombre,
        "descripcion":  d.descripcion,
        "total_activos":d.total_activos,
        "valor_total":  d.valor_total,
    } for d in deptos])