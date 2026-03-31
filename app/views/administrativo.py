from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date
from ..extensions import db
from ..models.vehiculo import (
    Vehiculo, Personal, ConductorVehiculo,
    PermisosVehiculo, MantenimientoVehiculo,
    TipoServicio, Ubicacion, Condicion
)
from ..views.vehiculo_vistas import VVehiculo, VPermisosVencer, VMantenimientoVehiculo, VAlertasMantenimiento
from ..utils.permisos import requiere_rol

administrativo_bp = Blueprint("administrativo", __name__)

ROLES_ADMIN_VEHICULOS = ("ti", "administrativo")


def _check_acceso():
    """Verifica que el usuario tenga acceso al módulo administrativo."""
    if current_user.rol not in ROLES_ADMIN_VEHICULOS:
        flash("No tienes acceso al módulo administrativo.", "error")
        return False
    return True


# ── Dashboard administrativo ──────────────────────────────────
@administrativo_bp.route("/")
@login_required
def dashboard():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    vehiculos       = VVehiculo.query.all()
    permisos_vencer = VPermisosVencer.query.filter(
        VPermisosVencer.dias_restantes <= 30
    ).order_by(VPermisosVencer.dias_restantes).limit(10).all()
    mantenimientos  = VMantenimientoVehiculo.query.filter_by(
        estatus="en_proceso"
    ).limit(8).all()

    total_vehiculos  = len(vehiculos)
    activos          = sum(1 for v in vehiculos if v.estado == "activo")
    en_mant          = sum(1 for v in vehiculos if v.estado == "mantenimiento")
    alertas_permisos = sum(1 for v in vehiculos if v.permisos_por_vencer > 0)

    alertas = VAlertasMantenimiento.query.filter(
        (VAlertasMantenimiento.AlertaKilometraje == 1) |
        (VAlertasMantenimiento.AlertaFecha == 1)
    ).all()
    return render_template("administrativo/dashboard.html",
        total_vehiculos  = total_vehiculos,
        activos          = activos,
        en_mantenimiento = en_mant,
        alertas_permisos = alertas_permisos,
        permisos_vencer  = permisos_vencer,
        mantenimientos   = mantenimientos,
        vehiculos        = vehiculos[:8],
        alertas_prox     = alertas,
    )


# ── CRUD Vehículos ────────────────────────────────────────────
@administrativo_bp.route("/vehiculos")
@login_required
def vehiculos():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    estado  = request.args.get("estado", "")
    query   = VVehiculo.query
    if estado:
        query = query.filter_by(estado=estado)

    lista       = query.all()
    ubicaciones = Ubicacion.query.all()

    return render_template("administrativo/vehiculos.html",
        vehiculos   = lista,
        ubicaciones = ubicaciones,
    )


@administrativo_bp.route("/vehiculos/nuevo", methods=["POST"])
@login_required
def vehiculo_nuevo():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    v = Vehiculo(
        Nombre           = request.form.get("nombre", "").strip(),
        Marca            = request.form.get("marca", "").strip() or None,
        Modelo           = request.form.get("modelo", "").strip() or None,
        Matricula        = request.form.get("matricula", "").strip().upper(),
        Kilometraje      = int(request.form.get("kilometraje") or 0),
        TipoAdquisicion  = request.form.get("tipo_adquisicion") or None,
        Estado           = request.form.get("estado", "activo"),
        Valor            = float(request.form.get("valor") or 0),
        FechaAdquisicion = request.form.get("fecha_adquisicion") or None,
        IdUbicacion      = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None,
    )
    db.session.add(v)
    db.session.commit()
    flash("Vehículo registrado correctamente.", "success")
    return redirect(url_for("administrativo.vehiculos"))


@administrativo_bp.route("/vehiculos/<int:id>/editar", methods=["POST"])
@login_required
def vehiculo_editar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    v = Vehiculo.query.get_or_404(id)
    v.Nombre           = request.form.get("nombre", "").strip()
    v.Marca            = request.form.get("marca", "").strip() or None
    v.Modelo           = request.form.get("modelo", "").strip() or None
    v.Matricula        = request.form.get("matricula", "").strip().upper()
    v.Kilometraje      = int(request.form.get("kilometraje") or 0)
    v.TipoAdquisicion  = request.form.get("tipo_adquisicion") or None
    v.Estado           = request.form.get("estado", "activo")
    v.Valor            = float(request.form.get("valor") or 0)
    v.FechaAdquisicion = request.form.get("fecha_adquisicion") or None
    v.IdUbicacion      = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None
    db.session.commit()
    flash("Vehículo actualizado.", "success")
    return redirect(url_for("administrativo.vehiculos"))


@administrativo_bp.route("/vehiculos/<int:id>/eliminar", methods=["POST"])
@login_required
def vehiculo_eliminar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    v = Vehiculo.query.get_or_404(id)
    db.session.delete(v)
    db.session.commit()
    flash("Vehículo eliminado.", "success")
    return redirect(url_for("administrativo.vehiculos"))


# ── Detalle de vehículo (permisos + mantenimiento) ────────────
@administrativo_bp.route("/vehiculos/<int:id>")
@login_required
def vehiculo_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    vehiculo       = Vehiculo.query.get_or_404(id)
    permisos       = PermisosVehiculo.query.filter_by(IdVehiculo=id).order_by(
                        PermisosVehiculo.FechaVencimiento.asc()).all()
    mantenimientos = VMantenimientoVehiculo.query.filter_by(
                        vehiculo_id=id).all()
    conductor_act  = ConductorVehiculo.query.filter_by(
                        IdVehiculo=id, FechaFin=None).first()
    tipos          = TipoServicio.query.all()
    personal       = Personal.query.filter_by(Activo=True).order_by(Personal.Nombre).all()

    from datetime import date as date_type
    return render_template("administrativo/vehiculo_detalle.html",
        vehiculo       = vehiculo,
        permisos       = permisos,
        mantenimientos = mantenimientos,
        conductor_act  = conductor_act,
        tipos          = tipos,
        personal       = personal,
        today_date     = date_type.today(),
    )


# ── Permisos ──────────────────────────────────────────────────
@administrativo_bp.route("/vehiculos/<int:id>/permisos/nuevo", methods=["POST"])
@login_required
def permiso_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    p = PermisosVehiculo(
        IdVehiculo       = id,
        IdTipoServicio   = int(request.form.get("tipo_servicio_id")),
        Descripcion      = request.form.get("descripcion", "").strip() or None,
        Numero           = request.form.get("numero", "").strip() or None,
        FechaInicio      = request.form.get("fecha_inicio") or None,
        FechaVencimiento = request.form.get("fecha_vencimiento"),
    )
    db.session.add(p)
    db.session.commit()
    flash("Permiso registrado.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/permisos/<int:id>/eliminar", methods=["POST"])
@login_required
def permiso_eliminar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    p = PermisosVehiculo.query.get_or_404(id)
    vid = p.IdVehiculo
    db.session.delete(p)
    db.session.commit()
    flash("Permiso eliminado.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=vid))


# ── Mantenimiento ─────────────────────────────────────────────
@administrativo_bp.route("/vehiculos/<int:id>/mantenimiento/nuevo", methods=["POST"])
@login_required
def mantenimiento_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    m = MantenimientoVehiculo(
        IdVehiculo     = id,
        IdPersonal     = int(request.form.get("personal_id")) if request.form.get("personal_id") else None,
        IdTipoServicio = int(request.form.get("tipo_servicio_id")),
        Descripcion    = request.form.get("descripcion", "").strip() or None,
        FechaInicio    = request.form.get("fecha_inicio"),
        FechaEntrega   = request.form.get("fecha_entrega") or None,
        Kilometraje    = int(request.form.get("kilometraje") or 0) or None,
        Costo          = float(request.form.get("costo") or 0),
        Proveedor      = request.form.get("proveedor", "").strip() or None,
        Estatus        = "en_proceso",
        CreadoPor      = current_user.id,
    )
    db.session.add(m)
    db.session.commit()
    flash("Mantenimiento registrado.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/mantenimiento/<int:id>/completar", methods=["POST"])
@login_required
def mantenimiento_completar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    m = MantenimientoVehiculo.query.get_or_404(id)
    m.Estatus      = "completado"
    m.FechaEntrega = request.form.get("fecha_entrega") or date.today()
    db.session.commit()
    flash("Mantenimiento marcado como completado.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=m.IdVehiculo))


# ── CRUD Personal (conductores) ───────────────────────────────
@administrativo_bp.route("/personal")
@login_required
def personal():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    lista      = Personal.query.order_by(Personal.Nombre).all()
    condiciones = Condicion.query.all()
    return render_template("administrativo/personal.html",
        personal    = lista,
        condiciones = condiciones,
    )


@administrativo_bp.route("/personal/nuevo", methods=["POST"])
@login_required
def personal_nuevo():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    p = Personal(
        Nombre           = request.form.get("nombre", "").strip(),
        Apellido         = request.form.get("apellido", "").strip(),
        Telefono         = request.form.get("telefono", "").strip() or None,
        Area             = request.form.get("area", "").strip() or None,
        Correo           = request.form.get("correo", "").strip() or None,
        JefeInmediato    = request.form.get("jefe_inmediato", "").strip() or None,
        LicenciaNumero   = request.form.get("licencia_numero", "").strip() or None,
        LicenciaVigencia = request.form.get("licencia_vigencia") or None,
        SeguroMedico     = request.form.get("seguro_medico", "").strip() or None,
        SeguroVigencia   = request.form.get("seguro_vigencia") or None,
        IdCondicion      = int(request.form.get("condicion_id")) if request.form.get("condicion_id") else None,
    )
    db.session.add(p)
    db.session.commit()
    flash("Personal registrado correctamente.", "success")
    return redirect(url_for("administrativo.personal"))


@administrativo_bp.route("/personal/<int:id>/editar", methods=["POST"])
@login_required
def personal_editar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    p = Personal.query.get_or_404(id)
    p.Nombre           = request.form.get("nombre", "").strip()
    p.Apellido         = request.form.get("apellido", "").strip()
    p.Telefono         = request.form.get("telefono", "").strip() or None
    p.Area             = request.form.get("area", "").strip() or None
    p.Correo           = request.form.get("correo", "").strip() or None
    p.JefeInmediato    = request.form.get("jefe_inmediato", "").strip() or None
    p.LicenciaNumero   = request.form.get("licencia_numero", "").strip() or None
    p.LicenciaVigencia = request.form.get("licencia_vigencia") or None
    p.SeguroMedico     = request.form.get("seguro_medico", "").strip() or None
    p.SeguroVigencia   = request.form.get("seguro_vigencia") or None
    p.IdCondicion      = int(request.form.get("condicion_id")) if request.form.get("condicion_id") else None
    db.session.commit()
    flash("Personal actualizado.", "success")
    return redirect(url_for("administrativo.personal"))


# ── Asignar conductor a vehículo ──────────────────────────────
@administrativo_bp.route("/vehiculos/<int:id>/asignar-conductor", methods=["POST"])
@login_required
def asignar_conductor(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    # Cerrar asignación anterior si existe
    anterior = ConductorVehiculo.query.filter_by(IdVehiculo=id, FechaFin=None).first()
    if anterior:
        anterior.FechaFin = date.today()

    nueva = ConductorVehiculo(
        IdPersonal  = int(request.form.get("personal_id")),
        IdVehiculo  = id,
        FechaInicio = request.form.get("fecha_inicio") or date.today(),
    )
    db.session.add(nueva)
    db.session.commit()
    flash("Conductor asignado correctamente.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=id))



# ── Mantenimiento ─────────────────────────────────────────────
@administrativo_bp.route("/mantenimiento")
@login_required
def mantenimiento_lista():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    tipo    = request.args.get("tipo", "")
    estatus = request.args.get("estatus", "")
    query   = VMantenimientoVehiculo.query
    if tipo:
        query = query.filter(VMantenimientoVehiculo.tipo_servicio.ilike(f"%{tipo}%"))
    if estatus:
        query = query.filter_by(estatus=estatus)

    lista   = query.all()
    alertas = VAlertasMantenimiento.query.filter(
        (VAlertasMantenimiento.AlertaKilometraje == 1) |
        (VAlertasMantenimiento.AlertaFecha == 1)
    ).all()
    tipos   = TipoServicio.query.filter(TipoServicio.IdCategoria == 1).all()

    return render_template("administrativo/mantenimiento.html",
        mantenimientos = lista,
        alertas        = alertas,
        tipos          = tipos,
    )


@administrativo_bp.route("/vehiculos/<int:id>/mantenimiento/nuevo", methods=["POST"])
@login_required
def mantenimiento_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    from sqlalchemy import text as sqla_text
    try:
        db.session.execute(
            sqla_text("""CALL sp_registrar_mantenimiento(
                :vid, :tipo, :diag, :desc, :fi, :fe,
                :km, :costo, :prov, :pkm, :pfecha, :usr,
                @res, @id_mant
            )"""),
            {
                "vid":    id,
                "tipo":   int(request.form.get("tipo_servicio_id")),
                "diag":   request.form.get("diagnostico", "").strip() or None,
                "desc":   request.form.get("descripcion", "").strip() or None,
                "fi":     request.form.get("fecha_inicio"),
                "fe":     request.form.get("fecha_entrega") or None,
                "km":     int(request.form.get("kilometraje") or 0) or None,
                "costo":  float(request.form.get("costo") or 0),
                "prov":   request.form.get("proveedor", "").strip() or None,
                "pkm":    int(request.form.get("proximo_kilometraje") or 0) or None,
                "pfecha": request.form.get("proxima_fecha") or None,
                "usr":    current_user.id,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        if row and row.r == "OK":
            flash("Mantenimiento registrado correctamente.", "success")
        else:
            flash(f"Error al registrar ({row.r if row else 'sin respuesta'}).", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/mantenimiento/<int:id>/completar", methods=["POST"])
@login_required
def mantenimiento_completar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    from sqlalchemy import text as sqla_text
    try:
        db.session.execute(
            sqla_text("CALL sp_completar_mantenimiento(:id, :fe, :costo, :desc, @res)"),
            {
                "id":    id,
                "fe":    request.form.get("fecha_entrega") or date.today(),
                "costo": float(request.form.get("costo_final") or 0) or None,
                "desc":  request.form.get("descripcion_fin", "").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        if row and row.r == "OK":
            flash("Mantenimiento completado.", "success")
        else:
            flash("No se pudo completar.", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    m = MantenimientoVehiculo.query.get(id)
    return redirect(url_for("administrativo.vehiculo_detalle", id=m.IdVehiculo if m else 0))

# ── API: datos de vehículo para modal ─────────────────────────
@administrativo_bp.route("/api/vehiculo/<int:id>")
@login_required
def api_vehiculo(id):
    v = Vehiculo.query.get_or_404(id)
    return jsonify(v.to_dict())