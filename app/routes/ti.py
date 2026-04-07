# app/routes/ti.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import text as sqla_text
from ..extensions import db
from ..models.electronico import Electronico, MantenimientoElectronico
from ..models.usuario import Usuario
from ..models.vehiculo import Ubicacion
from ..views.ti_vistas import VEquiposTI, VEstadisticasTI, VMantenimientoElectronico
from ..utils.permisos import requiere_rol, requiere_permiso

ti_bp = Blueprint("ti", __name__)

ROLES_TI = ("ti", "admin")  # admin puede ver todo, ti solo su módulo


def _check_acceso():
    if current_user.rol not in ROLES_TI:
        flash("No tienes acceso al módulo TI.", "error")
        return False
    return True


# ── Dashboard TI ──────────────────────────────────────────────
@ti_bp.route("/")
@login_required
@requiere_permiso('Equipos TI')
def dashboard():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    stats      = VEstadisticasTI.query.first()
    equipos    = VEquiposTI.query.all()
    mantenimientos = VMantenimientoElectronico.query.filter_by(Estatus="en_proceso").limit(8).all()

    # Equipos por tipo
    por_tipo = {}
    for e in equipos:
        por_tipo[e.TipoEquipo] = por_tipo.get(e.TipoEquipo, 0) + 1

    # Equipos por área (usuario)
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

    tipo    = request.args.get("tipo", "")
    estado  = request.args.get("estado", "")
    query   = VEquiposTI.query

    if tipo:
        query = query.filter_by(TipoEquipo=tipo)
    if estado:
        query = query.filter_by(Estado=estado)

    usuarios    = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ubicaciones = Ubicacion.query.all()

    return render_template("ti/equipos.html",
        equipos     = query.order_by(VEquiposTI.Nombre).all(),
        usuarios    = usuarios,
        ubicaciones = ubicaciones,
        tipo_filtro  = tipo,
        estado_filtro = estado,
    )


# ── Alta equipo ───────────────────────────────────────────────
@ti_bp.route("/equipos/nuevo", methods=["POST"])
@login_required
def equipo_nuevo():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_registrar_equipo_ti(:nom,:marc,:mod,:serie,:tipo,:costo,:fecha,:desc,@res,@id)"),
            {
                "nom":   request.form.get("nombre", "").strip(),
                "marc":  request.form.get("marca", "").strip() or None,
                "mod":   request.form.get("modelo", "").strip() or None,
                "serie": request.form.get("numero_serie", "").strip() or None,
                "tipo":  request.form.get("tipo_equipo", "otro"),
                "costo": float(request.form.get("costo") or 0),
                "fecha": request.form.get("fecha_adquisicion") or None,
                "desc":  request.form.get("descripcion", "").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash("Equipo registrado correctamente." if row and row.r == "OK" else f"Error: {row.r}.", "success" if row and row.r == "OK" else "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("ti.equipos"))


# ── Editar equipo ─────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/editar", methods=["POST"])
@login_required
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
    flash("Equipo actualizado.", "success")
    return redirect(url_for("ti.equipos"))


# ── Asignar equipo a usuario ──────────────────────────────────
@ti_bp.route("/equipos/<int:id>/asignar", methods=["POST"])
@login_required
def equipo_asignar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_asignar_equipo_ti(:eid,:uid,@res)"),
            {
                "eid": id,
                "uid": int(request.form.get("usuario_id")),
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        if row and row.r == "OK":
            flash("Equipo asignado correctamente.", "success")
        else:
            flash(f"No se pudo asignar: {row.r if row else 'error'}.", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("ti.equipo_detalle", id=id))


# ── Liberar equipo ────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/liberar", methods=["POST"])
@login_required
def equipo_liberar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    e = Electronico.query.get_or_404(id)
    e.IdUsuario = None
    e.Estado    = "almacen"
    db.session.commit()
    flash("Equipo regresado al almacén.", "success")
    return redirect(url_for("ti.equipo_detalle", id=id))


# ── Detalle equipo ────────────────────────────────────────────
@ti_bp.route("/equipos/<int:id>")
@login_required
def equipo_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    equipo         = Electronico.query.get_or_404(id)
    mantenimientos = VMantenimientoElectronico.query.filter_by(IdElectronico=id).all()
    usuarios       = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()
    ubicaciones    = Ubicacion.query.all()

    return render_template("ti/equipo_detalle.html",
        equipo         = equipo,
        mantenimientos = mantenimientos,
        usuarios       = usuarios,
        ubicaciones    = ubicaciones,
        today          = date.today(),
    )


# ── Mantenimiento previo ──────────────────────────────────────
@ti_bp.route("/equipos/<int:id>/mantenimiento/nuevo", methods=["POST"])
@login_required
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
        flash("Mantenimiento registrado." if row and row.r == "OK" else f"Error: {row.r}.", "success" if row and row.r == "OK" else "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("ti.equipo_detalle", id=id))


# ── Completar mantenimiento ───────────────────────────────────
@ti_bp.route("/mantenimiento/<int:id>/completar", methods=["POST"])
@login_required
def mantenimiento_completar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    m = MantenimientoElectronico.query.get_or_404(id)
    m.Estatus      = "completado"
    m.FechaTermino = request.form.get("fecha_termino") or date.today()
    m.Descripcion  = request.form.get("descripcion", m.Descripcion)

    # Si no hay más mantenimientos activos, regresar a almacén
    otros = MantenimientoElectronico.query.filter_by(
        IdElectronico=m.IdElectronico, Estatus="en_proceso"
    ).filter(MantenimientoElectronico.IdMantenimiento != id).count()

    if otros == 0:
        e = Electronico.query.get(m.IdElectronico)
        if e and e.Estado == "mantenimiento":
            e.Estado = "almacen" if not e.IdUsuario else "asignado"

    db.session.commit()
    flash("Mantenimiento completado.", "success")
    return redirect(url_for("ti.equipo_detalle", id=m.IdElectronico))


# ── Validación de estados ─────────────────────────────────────
@ti_bp.route("/validacion")
@login_required
def validacion_estados():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    stats       = VEstadisticasTI.query.first()
    buen_estado = VEquiposTI.query.filter_by(Condicion="bueno").all()
    mal_estado  = VEquiposTI.query.filter(
        VEquiposTI.Condicion.in_(["malo", "dañado", "regular"])
    ).all()

    return render_template("ti/validacion.html",
        stats      = stats,
        buen_estado = buen_estado,
        mal_estado  = mal_estado,
    )


# ── API ───────────────────────────────────────────────────────
@ti_bp.route("/api/equipo/<int:id>")
@login_required
def api_equipo(id):
    e = Electronico.query.get_or_404(id)
    return jsonify(e.to_dict())