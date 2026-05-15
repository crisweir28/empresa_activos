# app/routes/proyectos.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text as sqla_text
from ..extensions import db, socketio
from ..models.proyecto import Proyecto, ProyectoPersonal, ProyectoActivo, ProyectoAuditoria
from ..models.usuario import Usuario
from ..models.electronico import Electronico
from ..models.vehiculo import Vehiculo
from ..models.herramienta import Herramienta

proyectos_bp = Blueprint("proyectos", __name__)

ROLES_PERMITIDOS = ("admin", "ti", "rh", "administrativo")


def _check_acceso():
    if current_user.rol not in ROLES_PERMITIDOS:
        flash("No tienes acceso al módulo de proyectos.", "error")
        return False
    return True


def _check_admin():
    if current_user.rol != "admin":
        flash("Solo el Administrador puede realizar esta acción.", "error")
        return False
    return True


# ── Lista de proyectos ────────────────────────────────────────
@proyectos_bp.route("/")
@login_required
def lista():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    estatus_filtro = request.args.get("estatus", "")
    q = Proyecto.query.order_by(Proyecto.CreadoEn.desc())
    if estatus_filtro:
        q = q.filter_by(Estatus=estatus_filtro)

    proyectos = q.all()
    stats = {
        "total":       Proyecto.query.count(),
        "activos":     Proyecto.query.filter_by(Estatus="Activo").count(),
        "en_progreso": Proyecto.query.filter_by(Estatus="En progreso").count(),
        "completados": Proyecto.query.filter_by(Estatus="Completado").count(),
        "pausados":    Proyecto.query.filter_by(Estatus="Pausado").count(),
        "cancelados":  Proyecto.query.filter_by(Estatus="Cancelado").count(),
    }

    return render_template("proyectos/lista.html",
        proyectos      = proyectos,
        stats          = stats,
        estatus_filtro = estatus_filtro,
        ESTATUS        = ['Activo','En progreso','Pausado','Completado','Cancelado'],
        es_admin       = current_user.rol == "admin",  # ← AGREGAR ESTA LÍNEA
    )


# ── Detalle de proyecto ───────────────────────────────────────
@proyectos_bp.route("/<int:id>")
@login_required
def detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    proyecto   = Proyecto.query.get_or_404(id)
    personal   = ProyectoPersonal.query.filter_by(IdProyecto=id).all()
    activos    = ProyectoActivo.query.filter_by(IdProyecto=id).all()
    auditoria  = ProyectoAuditoria.query.filter_by(IdProyecto=id).order_by(ProyectoAuditoria.RealizadoEn.desc()).all()

    # Usuarios disponibles para asignar
    usuarios_disponibles = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ids_asignados = {p.IdUsuario for p in personal}

    # Equipos disponibles por tipo
    electronicos = Electronico.query.filter_by(Estado="almacen").all() if current_user.rol in ("admin","ti") else []
    vehiculos    = Vehiculo.query.all() if current_user.rol in ("admin","administrativo") else []
    herramientas = Herramienta.query.filter_by(Estado="disponible").all() if current_user.rol in ("admin","almacenista") else []

    return render_template("proyectos/detalle.html",
        proyecto             = proyecto,
        personal             = personal,
        activos_asignados    = activos,
        auditoria            = auditoria,
        usuarios_disponibles = usuarios_disponibles,
        ids_asignados        = ids_asignados,
        electronicos         = electronicos,
        vehiculos            = vehiculos,
        herramientas         = herramientas,
        ESTATUS              = ['Activo','En progreso','Pausado','Completado','Cancelado'],
        es_admin             = current_user.rol == "admin",
    )


# ── Crear proyecto ────────────────────────────────────────────
@proyectos_bp.route("/nuevo", methods=["POST"])
@login_required
def nuevo():
    if not _check_admin():
        return redirect(url_for("proyectos.lista"))

    nombre       = request.form.get("nombre", "").strip()
    descripcion  = request.form.get("descripcion", "").strip()
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_termino= request.form.get("fecha_termino")

    if not all([nombre, fecha_inicio, fecha_termino]):
        flash("Nombre y fechas son obligatorios.", "error")
        return redirect(url_for("proyectos.lista"))

    try:
        db.session.execute(
            sqla_text("CALL sp_crear_proyecto(:nom,:desc,:fi,:ft,:uid,@id,@res)"),
            {"nom": nombre, "desc": descripcion, "fi": fecha_inicio,
             "ft": fecha_termino, "uid": current_user.id}
        )
        row = db.session.execute(sqla_text("SELECT @id AS id, @res AS res")).first()
        db.session.execute(sqla_text("COMMIT"))

        if row.res == "OK":
            flash(f"Proyecto '{nombre}' creado correctamente.", "success")
            socketio.emit("proyectos_actualizados", {"accion": "nuevo"})
            return redirect(url_for("proyectos.detalle", id=row.id))
        else:
            flash("Error al crear el proyecto.", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.lista"))


# ── Editar proyecto ───────────────────────────────────────────
@proyectos_bp.route("/<int:id>/editar", methods=["POST"])
@login_required
def editar(id):
    if not _check_admin():
        return redirect(url_for("proyectos.detalle", id=id))

    try:
        db.session.execute(
            sqla_text("CALL sp_actualizar_proyecto(:id,:nom,:desc,:fi,:ft,:est,:razon,:uid,@res)"),
            {
                "id":    id,
                "nom":   request.form.get("nombre","").strip(),
                "desc":  request.form.get("descripcion","").strip(),
                "fi":    request.form.get("fecha_inicio"),
                "ft":    request.form.get("fecha_termino"),
                "est":   request.form.get("estatus","Activo"),
                "razon": request.form.get("razon","").strip() or None,
                "uid":   current_user.id,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        flash("Proyecto actualizado correctamente.", "success")
        socketio.emit("proyectos_actualizados", {"accion": "editar", "id": id})
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.detalle", id=id))


# ── Eliminar proyecto ─────────────────────────────────────────
@proyectos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    if not _check_admin():
        return redirect(url_for("proyectos.lista"))

    p = Proyecto.query.get_or_404(id)
    try:
        db.session.delete(p)
        db.session.commit()
        flash("Proyecto eliminado.", "success")
        socketio.emit("proyectos_actualizados", {"accion": "eliminar"})
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.lista"))


# ── Asignar personal ──────────────────────────────────────────
@proyectos_bp.route("/<int:id>/asignar-personal", methods=["POST"])
@login_required
def asignar_personal(id):
    if not _check_acceso():
        return redirect(url_for("proyectos.detalle", id=id))

    try:
        db.session.execute(
            sqla_text("CALL sp_asignar_personal_proyecto(:pid,:uid,:rol,:apo,@res)"),
            {
                "pid": id,
                "uid": request.form.get("usuario_id"),
                "rol": request.form.get("rol_proyecto","").strip() or None,
                "apo": current_user.id,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        flash("Personal asignado correctamente.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.detalle", id=id))


# ── Quitar personal ───────────────────────────────────────────
@proyectos_bp.route("/<int:id>/quitar-personal/<int:asignacion_id>", methods=["POST"])
@login_required
def quitar_personal(id, asignacion_id):
    if not _check_acceso():
        return redirect(url_for("proyectos.detalle", id=id))

    a = ProyectoPersonal.query.get_or_404(asignacion_id)
    try:
        db.session.delete(a)
        db.session.commit()
        flash("Personal removido del proyecto.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.detalle", id=id))


# ── Asignar activo ────────────────────────────────────────────
@proyectos_bp.route("/<int:id>/asignar-activo", methods=["POST"])
@login_required
def asignar_activo(id):
    if not _check_acceso():
        return redirect(url_for("proyectos.detalle", id=id))

    try:
        db.session.execute(
            sqla_text("CALL sp_asignar_activo_proyecto(:pid,:tipo,:aid,:est,:apo,:obs,@res)"),
            {
                "pid":  id,
                "tipo": request.form.get("tipo_activo"),
                "aid":  request.form.get("activo_id"),
                "est":  request.form.get("estado_inicial","").strip() or None,
                "apo":  current_user.id,
                "obs":  request.form.get("observaciones","").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        flash("Activo asignado al proyecto.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("proyectos.detalle", id=id))


# ── API ───────────────────────────────────────────────────────
@proyectos_bp.route("/api/<int:id>")
@login_required
def api_proyecto(id):
    p = Proyecto.query.get_or_404(id)
    return jsonify({
        "id":           p.IdProyecto,
        "nombre":       p.Nombre,
        "descripcion":  p.Descripcion or "",
        "fecha_inicio": p.FechaInicio.isoformat() if p.FechaInicio else "",
        "fecha_termino":p.FechaTermino.isoformat() if p.FechaTermino else "",
        "estatus":      p.Estatus,
    })