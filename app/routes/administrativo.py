# app/routes/administrativo.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from sqlalchemy import text as sqla_text
import os
from ..extensions import db
from ..models.vehiculo import (
    EvidenciaVehiculo, Vehiculo, VehiculoArchivo, Personal, ConductorVehiculo,
    PermisosVehiculo, MantenimientoVehiculo, TipoServicio, Ubicacion, Condicion
)
from ..views.vehiculo_vistas import VVehiculo, VPermisosVencer, VMantenimientoVehiculo, VAlertasMantenimiento
from ..utils.permisos import requiere_rol, requiere_permiso
from ..utils.archivos import guardar_archivo
from ..models.baja_activo import BajaActivo

administrativo_bp = Blueprint("administrativo", __name__)

ROLES_ADMIN_VEHICULOS = ("admin", "administrativo")


def _check_acceso():
    if current_user.rol not in ROLES_ADMIN_VEHICULOS:
        flash("No tienes acceso al módulo administrativo.", "error")
        return False
    return True


# ── Helper: verificar duplicados de placa, VIN y póliza ────
def _verificar_duplicados(matricula, vin, poliza, id_excluir=None):
    if matricula:
        q = Vehiculo.query.filter(Vehiculo.Matricula == matricula.upper())
        if id_excluir:
            q = q.filter(Vehiculo.IdVehiculo != id_excluir)
        if q.first():
            return ("matricula", matricula)

    if vin:
        q = Vehiculo.query.filter(Vehiculo.VIN == vin)
        if id_excluir:
            q = q.filter(Vehiculo.IdVehiculo != id_excluir)
        if q.first():
            return ("vin", vin)

    if poliza:
        q = Vehiculo.query.filter(Vehiculo.PolizaSeguro == poliza)
        if id_excluir:
            q = q.filter(Vehiculo.IdVehiculo != id_excluir)
        if q.first():
            return ("poliza_seguro", poliza)

    return (None, None)


# ── Helper: borrar archivo físico del disco ────────────────
def _borrar_archivo_fisico(url):
    """Intenta borrar el archivo físico del disco. Falla silencioso."""
    if not url:
        return
    try:
        # Si la URL empieza con /static/, lo convertimos a ruta de disco
        ruta_relativa = url.lstrip('/')
        ruta_disco = os.path.join('app', ruta_relativa)
        if os.path.exists(ruta_disco):
            os.remove(ruta_disco)
    except Exception:
        pass


# ── Helper: guardar/reemplazar archivo de vehículo ─────────
def _guardar_archivo_vehiculo(id_vehiculo, archivo, tipo, carpeta="documents"):
    """
    Guarda un archivo en disco, registra en VehiculoArchivo
    y borra el anterior del mismo tipo (si existe).
    """
    if not archivo or not archivo.filename:
        return None

    # 1. Borrar el archivo anterior del mismo tipo
    anterior = VehiculoArchivo.query.filter_by(
        IdVehiculo=id_vehiculo, TipoArchivo=tipo
    ).first()
    if anterior:
        _borrar_archivo_fisico(anterior.ArchivoUrl)
        db.session.delete(anterior)

    # 2. Guardar el nuevo en disco
    info = guardar_archivo(
        archivo=archivo,
        prefijo=f"vehiculo_{id_vehiculo}_{tipo}",
        carpeta=carpeta
    )

    # 3. Registrar en BD
    nuevo = VehiculoArchivo(
        IdVehiculo=id_vehiculo,
        TipoArchivo=tipo,
        NombreArchivo=info.get("filename"),
        ArchivoUrl=info["url"],
        MimeType=info.get("mime_type"),
    )
    db.session.add(nuevo)
    return info["url"]


# ── Helper: guardar/reemplazar evidencia fotográfica ───────
def _guardar_evidencia_vehiculo(id_vehiculo, archivo, tipo):
    """
    Guarda una foto de evidencia, registra en EvidenciaVehiculo
    y borra la anterior del mismo tipo.
    """
    if not archivo or not archivo.filename:
        return None

    # 1. Borrar evidencia anterior del mismo tipo
    anterior = EvidenciaVehiculo.query.filter_by(
        IdVehiculo=id_vehiculo, Tipo=tipo
    ).first()
    if anterior:
        _borrar_archivo_fisico(anterior.ArchivoUrl)
        db.session.delete(anterior)

    # 2. Guardar en disco
    info = guardar_archivo(
        archivo=archivo,
        prefijo=f"vehiculo_{id_vehiculo}_{tipo}",
        carpeta="static/evidencias"
    )

    # 3. Registrar en BD
    nueva = EvidenciaVehiculo(
        IdVehiculo=id_vehiculo,
        Tipo=tipo,
        ArchivoUrl=info["url"],
        CreadoEn=datetime.now()
    )
    db.session.add(nueva)
    return info["url"]


@administrativo_bp.route("/")
@login_required
@requiere_permiso('Vehículos', 'ver')
def dashboard():
    todos_vehiculos = VVehiculo.query.all()
    vehiculos_activos = [v for v in todos_vehiculos if v.estado != 'baja']
    vehiculos_baja = [v for v in todos_vehiculos if v.estado == 'baja']

    permisos_vencer = VPermisosVencer.query.filter(
        VPermisosVencer.dias_restantes <= 30
    ).order_by(VPermisosVencer.dias_restantes).limit(10).all()

    mantenimientos = VMantenimientoVehiculo.query.filter_by(estatus="en_proceso").limit(8).all()

    alertas = VAlertasMantenimiento.query.filter(
        (VAlertasMantenimiento.AlertaKilometraje == 1) |
        (VAlertasMantenimiento.AlertaFecha == 1)
    ).all()

    return render_template("administrativo/dashboard.html",
        total_vehiculos=len(vehiculos_activos),
        activos=sum(1 for v in vehiculos_activos if v.estado == "activo"),
        en_mantenimiento=sum(1 for v in vehiculos_activos if v.estado == "mantenimiento"),
        vehiculos_baja=len(vehiculos_baja),
        permisos_vencer=permisos_vencer,
        mantenimientos=mantenimientos,
        vehiculos=todos_vehiculos,
        alertas_prox=alertas,
        ubicaciones=Ubicacion.query.all(),
    )


@administrativo_bp.route("/vehiculos/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'crear')
def vehiculo_nuevo():
    if not _check_acceso():
        return jsonify({'ok': False, 'mensaje': 'Sin acceso'}), 403

    matricula = request.form.get("matricula", "").strip().upper()
    vin       = request.form.get("vin", "").strip() or None
    poliza    = request.form.get("poliza_seguro", "").strip() or None

    # Validar duplicados ANTES de insertar
    campo, valor = _verificar_duplicados(matricula, vin, poliza)
    if campo:
        mensajes = {
            'matricula':     f'La placa <strong>{valor}</strong> ya está registrada en otro vehículo.',
            'vin':           f'El VIN <strong>{valor}</strong> ya está registrado en otro vehículo.',
            'poliza_seguro': f'La póliza <strong>{valor}</strong> ya está registrada en otro vehículo.',
        }
        return jsonify({'ok': False, 'campo': campo, 'mensaje': mensajes[campo]}), 200

    try:
        v = Vehiculo(
            Nombre=request.form.get("nombre", "").strip(),
            TipoVehiculo=request.form.get("tipo_vehiculo") or None,
            Marca=request.form.get("marca", "").strip() or None,
            Modelo=request.form.get("modelo", "").strip() or None,
            Anio=int(request.form.get("anio")) if request.form.get("anio") else None,
            Matricula=matricula,
            VIN=vin,
            Color=request.form.get("color", "").strip() or None,
            Kilometraje=int(request.form.get("kilometraje") or 0),
            TipoAdquisicion=request.form.get("tipo_adquisicion") or None,
            Estado=request.form.get("estado", "activo"),
            Valor=float(request.form.get("valor") or 0),
            FechaAdquisicion=request.form.get("fecha_adquisicion") or None,
            IdUbicacion=int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None,
            PolizaSeguro=poliza,
            Aseguradora=request.form.get("aseguradora", "").strip() or None,
            VigenciaSeguro=request.form.get("vigencia_seguro") or None,
            UltimaVerificacion=request.form.get("ultima_verificacion") or None,
            Accesorios=request.form.get("accesorios", "").strip() or None,
            Comentarios=request.form.get("comentarios", "").strip() or None,
            Arrendamiento=bool(request.form.get("arrendamiento")),
            FechaRenovacion=request.form.get("fecha_renovacion") or None,
            ProveedorArrendamiento=request.form.get("proveedor_arrendamiento", "").strip() or None,
        )
        db.session.add(v)
        db.session.flush()  # para tener v.IdVehiculo

        # ── Documentos (VehiculoArchivo) ────────────────────
        _guardar_archivo_vehiculo(
            v.IdVehiculo,
            request.files.get("tarjeta_circulacion"),
            "tarjeta_circulacion",
            carpeta="documents"
        )
        _guardar_archivo_vehiculo(
            v.IdVehiculo,
            request.files.get("certificado_verificacion"),
            "certificado_verificacion",
            carpeta="documents"
        )

        # ── Evidencias fotográficas (EvidenciaVehiculo) ─────
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_frente"),   "frente")
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_lateral"),  "lateral")
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_interior"), "interior")

        db.session.commit()
        flash(f"Vehículo '{v.Nombre}' registrado correctamente.", "success")
        return jsonify({'ok': True, 'mensaje': 'Vehículo registrado'}), 200

    except Exception as ex:
        db.session.rollback()
        return jsonify({'ok': False, 'mensaje': f'Error: {str(ex)}'}), 200


@administrativo_bp.route("/vehiculos/<int:id>/editar", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'editar')
def vehiculo_editar(id):
    if not _check_acceso():
        return jsonify({'ok': False, 'mensaje': 'Sin acceso'}), 403

    v = Vehiculo.query.get_or_404(id)

    matricula = request.form.get("matricula", "").strip().upper()
    vin       = request.form.get("vin", "").strip() or None
    poliza    = request.form.get("poliza_seguro", "").strip() or None
    print("====================================")
    print(request.form)
    print("MATRICULA:", request.form.get("matricula"))
    print("VIN:", request.form.get("vin"))
    print("POLIZA:", request.form.get("poliza_seguro"))
    print("====================================")
    
    print("ID ACTUAL:", id)

    campo, valor = _verificar_duplicados(
    matricula,
    vin,
    poliza,
    id_excluir=id
    )

    print("CAMPO:", campo)
    print("VALOR:", valor)

    
    # Validar duplicados ignorando el vehículo actual
    #campo, valor = _verificar_duplicados(matricula, vin, poliza, id_excluir=id)
    if campo:
        mensajes = {
            'matricula':     f'La placa <strong>{valor}</strong> ya está registrada en otro vehículo.',
            'vin':           f'El VIN <strong>{valor}</strong> ya está registrado en otro vehículo.',
            'poliza_seguro': f'La póliza <strong>{valor}</strong> ya está registrada en otro vehículo.',
        }
        return jsonify({'ok': False, 'campo': campo, 'mensaje': mensajes[campo]}), 200

    try:
        print("ENTRO AL TRY")
        v.Nombre           = request.form.get("nombre", "").strip()
        v.Marca            = request.form.get("marca", "").strip() or None
        v.Modelo           = request.form.get("modelo", "").strip() or None
        v.Matricula        = matricula
        v.VIN              = vin
        v.Kilometraje      = int(request.form.get("kilometraje") or 0)
        v.TipoAdquisicion  = request.form.get("tipo_adquisicion") or None
        nuevo_estado = request.form.get("estado", "activo")
        v.Valor            = float(request.form.get("valor") or 0)
        v.FechaAdquisicion = request.form.get("fecha_adquisicion") or None
        v.IdUbicacion      = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None
        v.PolizaSeguro     = poliza
        v.Aseguradora      = request.form.get("aseguradora", "").strip() or None
        v.VigenciaSeguro   = request.form.get("vigencia_seguro") or None
        v.UltimaVerificacion = request.form.get("ultima_verificacion") or None
        v.Accesorios       = request.form.get("accesorios", "").strip() or None
        v.Comentarios      = request.form.get("comentarios", "").strip() or None
        v.FechaRenovacion  = request.form.get("fecha_renovacion") or None
        v.ProveedorArrendamiento = request.form.get("proveedor_arrendamiento", "").strip() or None

        # ── Reemplazar archivos SOLO si se subieron nuevos ──
        _guardar_archivo_vehiculo(
            v.IdVehiculo,
            request.files.get("tarjeta_circulacion"),
            "tarjeta_circulacion",
            carpeta="documents"
        )
        _guardar_archivo_vehiculo(
            v.IdVehiculo,
            request.files.get("certificado_verificacion"),
            "certificado_verificacion",
            carpeta="documents"
        )
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_frente"),   "frente")
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_lateral"),  "lateral")
        _guardar_evidencia_vehiculo(v.IdVehiculo, request.files.get("evidencia_interior"), "interior")

        db.session.execute(
        sqla_text("""
        CALL sp_cambiar_estado_vehiculo(
            :vehiculo,
            :estado,
            :usuario
        )
        """),
        {
        "vehiculo": v.IdVehiculo,
        "estado": nuevo_estado,
        "usuario": current_user.id
        }
    )
        print("ANTES DE COMMIT")    
        db.session.commit()
        print("COMMIT OK")
        flash("Vehículo actualizado.", "success")
        return jsonify({'ok': True, 'mensaje': 'Vehículo actualizado'}), 200

    except Exception as ex:
        db.session.rollback()
        return jsonify({'ok': False, 'mensaje': f'Error: {str(ex)}'}), 200


@administrativo_bp.route("/vehiculos/<int:id>")
@login_required
def vehiculo_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    vehiculo = Vehiculo.query.get_or_404(id)
    permisos = PermisosVehiculo.query.filter_by(IdVehiculo=id).order_by(
        PermisosVehiculo.FechaVencimiento.asc()
    ).all()
    mantenimientos = VMantenimientoVehiculo.query.filter_by(vehiculo_id=id).all()
    conductor_act = ConductorVehiculo.query.filter_by(IdVehiculo=id, FechaFin=None).first()
    historial_conductores = ConductorVehiculo.query.filter_by(IdVehiculo=id).order_by(
        ConductorVehiculo.FechaInicio.desc()
    ).all()

    tipos_servicio = TipoServicio.query.all()
    personal_disponible = Personal.query.filter_by(Activo=True).order_by(Personal.Nombre).all()

    return render_template("administrativo/vehiculo_detalle.html",
        vehiculo=vehiculo,
        conductor_act=conductor_act,
        historial_conductores=historial_conductores,
        mantenimientos=mantenimientos,
        permisos=permisos,
        tipos_servicio=tipos_servicio,
        personal_disponible=personal_disponible,
        today_date=date.today(),
        now=date.today()
    )


@administrativo_bp.route("/vehiculos/<int:id>/permisos/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'crear')
def permiso_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        p = PermisosVehiculo(
            IdVehiculo=id,
            IdTipoServicio=int(request.form.get("tipo_servicio_id")),
            Descripcion=request.form.get("descripcion", "").strip() or None,
            Numero=request.form.get("numero", "").strip() or None,
            FechaInicio=request.form.get("fecha_inicio") or None,
            FechaVencimiento=request.form.get("fecha_vencimiento"),
        )
        archivo = request.files.get("archivo")
        if archivo and archivo.filename:
            info = guardar_archivo(
                archivo=archivo,
                prefijo=f"vehiculo_{id}_permiso",
                carpeta="documents" if not archivo.filename.rsplit(".", 1)[-1].lower()
                        in {"png", "jpg", "jpeg"} else "static/evidencias"
            )
            p.ArchivoUrl = info["url"]
        db.session.add(p)
        db.session.commit()
        flash("Permiso registrado.", "success")
    except Exception as ex:
        db.session.rollback()
        flash(f"Error: {str(ex)}", "error")

    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/permisos/<int:id>/eliminar", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'eliminar')
def permiso_eliminar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    p = PermisosVehiculo.query.get_or_404(id)
    vid = p.IdVehiculo
    db.session.delete(p)
    db.session.commit()
    flash("Permiso eliminado.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=vid))


@administrativo_bp.route("/mantenimiento")
@login_required
@requiere_permiso('Mantenimiento', 'ver')
def mantenimiento_lista():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    tipo = request.args.get("tipo", "")
    estatus = request.args.get("estatus", "")
    query = VMantenimientoVehiculo.query
    if tipo:
        query = query.filter(VMantenimientoVehiculo.tipo_servicio.ilike(f"%{tipo}%"))
    if estatus:
        query = query.filter_by(estatus=estatus)
    alertas = VAlertasMantenimiento.query.filter(
        (VAlertasMantenimiento.AlertaKilometraje == 1) |
        (VAlertasMantenimiento.AlertaFecha == 1)
    ).all()
    return render_template("administrativo/mantenimiento.html",
        mantenimientos=query.all(),
        alertas=alertas,
        tipos=TipoServicio.query.filter(TipoServicio.IdCategoria == 1).all(),
    )


@administrativo_bp.route("/vehiculos/<int:id>/mantenimiento/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Mantenimiento', 'crear')
def mantenimiento_nuevo(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    try:
        db.session.execute(
            sqla_text("""CALL sp_registrar_mantenimiento(
                :vid, :tipo, :diag, :desc, :fi, :fe,
                :km, :costo, :prov, :pkm, :pfecha, :usr,
                @res, @id_mant)"""),
            {
                "vid": id,
                "tipo": int(request.form.get("tipo_servicio_id")),
                "diag": request.form.get("diagnostico", "").strip() or None,
                "desc": request.form.get("descripcion", "").strip() or None,
                "fi": request.form.get("fecha_inicio"),
                "fe": request.form.get("fecha_entrega") or None,
                "km": int(request.form.get("kilometraje") or 0) or None,
                "costo": float(request.form.get("costo") or 0),
                "prov": request.form.get("proveedor", "").strip() or None,
                "pkm": int(request.form.get("proximo_kilometraje") or 0) or None,
                "pfecha": request.form.get("proxima_fecha") or None,
                "usr": current_user.id,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash(
            "Mantenimiento registrado correctamente." if row and row.r == "OK" else f"Error ({row.r if row else ''}).",
            "success" if row and row.r == "OK" else "error"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/mantenimiento/<int:id>/completar", methods=["POST"])
@login_required
@requiere_permiso('Mantenimiento', 'editar')
def mantenimiento_completar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    try:
        db.session.execute(
            sqla_text("CALL sp_completar_mantenimiento(:id, :fe, :costo, :desc, @res)"),
            {
                "id": id,
                "fe": request.form.get("fecha_entrega") or date.today(),
                "costo": float(request.form.get("costo_final") or 0) or None,
                "desc": request.form.get("descripcion_fin", "").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash(
            "Mantenimiento completado." if row and row.r == "OK" else "No se pudo completar.",
            "success" if row and row.r == "OK" else "error"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")
    m = MantenimientoVehiculo.query.get(id)
    return redirect(url_for("administrativo.vehiculo_detalle", id=m.IdVehiculo if m else 0))


@administrativo_bp.route("/personal")
@login_required
@requiere_permiso('Vehículos', 'crear')
def personal():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    return render_template("administrativo/personal.html",
        personal=Personal.query.order_by(Personal.Nombre).all(),
        condiciones=Condicion.query.all(),
    )


@administrativo_bp.route("/personal/nuevo", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'crear')
def personal_nuevo():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    p = Personal(
        Nombre=request.form.get("nombre", "").strip(),
        Apellido=request.form.get("apellido", "").strip(),
        Telefono=request.form.get("telefono", "").strip() or None,
        Area=request.form.get("area", "").strip() or None,
        Correo=request.form.get("correo", "").strip() or None,
        JefeInmediato=request.form.get("jefe_inmediato", "").strip() or None,
        LicenciaNumero=request.form.get("licencia_numero", "").strip() or None,
        LicenciaVigencia=request.form.get("licencia_vigencia") or None,
        SeguroMedico=request.form.get("seguro_medico", "").strip() or None,
        SeguroVigencia=request.form.get("seguro_vigencia") or None,
        IdCondicion=int(request.form.get("condicion_id")) if request.form.get("condicion_id") else None,
    )
    db.session.add(p)
    db.session.commit()
    flash("Personal registrado correctamente.", "success")
    return redirect(url_for("administrativo.personal"))


@administrativo_bp.route("/personal/<int:id>/editar", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'editar')
def personal_editar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    p = Personal.query.get_or_404(id)
    p.Nombre = request.form.get("nombre", "").strip()
    p.Apellido = request.form.get("apellido", "").strip()
    p.Telefono = request.form.get("telefono", "").strip() or None
    p.Area = request.form.get("area", "").strip() or None
    p.Correo = request.form.get("correo", "").strip() or None
    p.JefeInmediato = request.form.get("jefe_inmediato", "").strip() or None
    p.LicenciaNumero = request.form.get("licencia_numero", "").strip() or None
    p.LicenciaVigencia = request.form.get("licencia_vigencia") or None
    p.SeguroMedico = request.form.get("seguro_medico", "").strip() or None
    p.SeguroVigencia = request.form.get("seguro_vigencia") or None
    p.IdCondicion = int(request.form.get("condicion_id")) if request.form.get("condicion_id") else None
    db.session.commit()
    flash("Personal actualizado.", "success")
    return redirect(url_for("administrativo.personal"))


@administrativo_bp.route("/vehiculos/<int:id>/asignar-conductor", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'editar')
def asignar_conductor(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    anterior = ConductorVehiculo.query.filter_by(IdVehiculo=id, FechaFin=None).first()
    if anterior:
        anterior.FechaFin = date.today()
    nueva = ConductorVehiculo(
        IdPersonal=int(request.form.get("personal_id")),
        IdVehiculo=id,
        FechaInicio=request.form.get("fecha_inicio") or date.today(),
    )
    db.session.add(nueva)
    db.session.commit()
    flash("Conductor asignado correctamente.", "success")
    return redirect(url_for("administrativo.vehiculo_detalle", id=id))


@administrativo_bp.route("/vehiculos/<int:id>/baja", methods=["POST"])
@login_required
@requiere_permiso('Vehículos', 'eliminar')
def vehiculo_baja(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    v = Vehiculo.query.get_or_404(id)
    v.Estado = "baja"
    db.session.add(BajaActivo(
        TipoActivo="vehiculo",
        IdActivo=v.IdVehiculo,
        NombreActivo=v.Nombre,
        DadoDeBajaPor=current_user.id,
    ))
    db.session.commit()
    flash(f"'{v.Nombre}' dado de baja.", "success")
    return redirect(url_for("administrativo.dashboard"))


@administrativo_bp.route("/api/vehiculo/<int:id>")
@login_required
def api_vehiculo(id):
    v = Vehiculo.query.get_or_404(id)
    return jsonify(v.to_dict())


@administrativo_bp.route("/api/verificar-documentos-conductor/<int:id_personal>")
@login_required
def verificar_documentos_conductor(id_personal):
    try:
        docs = db.session.execute(sqla_text("""
            SELECT TipoDocumento, NumeroDocumento, FechaVencimiento,
                   EstadoDocumento, DiasParaVencer
            FROM v_documentos_usuario
            WHERE IdUsuario = (
                SELECT IdUsuario FROM usuario
                WHERE NombreUsuario = (
                    SELECT CONCAT(Nombre, Apellido)
                    FROM personal
                    WHERE IdPersonal = :id_personal
                )
                LIMIT 1
            )
        """), {'id_personal': id_personal}).fetchall()

        docs_criticos = ['licencia_conducir', 'examen_medico']
        docs_recomendados = ['ine', 'curp']

        docs_vencidos = []
        docs_por_vencer = []
        docs_faltantes_criticos = []
        docs_faltantes_recomendados = []

        tipos_presentes = [d.TipoDocumento for d in docs]

        for tipo in docs_criticos:
            doc = next((d for d in docs if d.TipoDocumento == tipo), None)
            if not doc:
                docs_faltantes_criticos.append(tipo)
            elif doc.EstadoDocumento == 'vencido':
                docs_vencidos.append({
                    'tipo': tipo, 'numero': doc.NumeroDocumento,
                    'vencimiento': str(doc.FechaVencimiento)
                })
            elif doc.EstadoDocumento == 'por_vencer':
                docs_por_vencer.append({
                    'tipo': tipo, 'dias': doc.DiasParaVencer,
                    'vencimiento': str(doc.FechaVencimiento)
                })

        for tipo in docs_recomendados:
            if tipo not in tipos_presentes:
                docs_faltantes_recomendados.append(tipo)

        tiene_criticos_vencidos = len(docs_vencidos) > 0 or len(docs_faltantes_criticos) > 0
        tiene_advertencias = len(docs_por_vencer) > 0 or len(docs_faltantes_recomendados) > 0

        if tiene_criticos_vencidos:
            estado, nivel_riesgo = 'bloqueado', 'alto'
        elif tiene_advertencias:
            estado, nivel_riesgo = 'advertencia', 'medio'
        else:
            estado, nivel_riesgo = 'ok', 'bajo'

        riesgos_conductor, riesgos_empresa = [], []
        if docs_faltantes_criticos or docs_vencidos:
            if 'licencia_conducir' in docs_faltantes_criticos or any(d['tipo'] == 'licencia_conducir' for d in docs_vencidos):
                riesgos_conductor.extend([
                    'Multas y sanciones por conducir sin licencia vigente',
                    'Sin cobertura del seguro en caso de accidente',
                    'Posible retención del vehículo por autoridades'
                ])
                riesgos_empresa.extend([
                    'Responsabilidad civil y penal en accidentes',
                    'Invalidación de póliza de seguro del vehículo',
                    'Sanciones laborales y multas administrativas',
                    'Daño reputacional y legal'
                ])
            if 'examen_medico' in docs_faltantes_criticos or any(d['tipo'] == 'examen_medico' for d in docs_vencidos):
                riesgos_conductor.append('Riesgo de salud no detectado que puede causar accidentes')
                riesgos_empresa.append('Responsabilidad por accidentes causados por condiciones médicas no evaluadas')

        return jsonify({
            'ok': True,
            'estado': estado, 'nivel_riesgo': nivel_riesgo,
            'puede_asignar': estado != 'bloqueado',
            'requiere_confirmacion': estado == 'advertencia',
            'resumen': {
                'docs_vencidos': len(docs_vencidos),
                'docs_por_vencer': len(docs_por_vencer),
                'docs_faltantes_criticos': len(docs_faltantes_criticos),
                'docs_faltantes_recomendados': len(docs_faltantes_recomendados)
            },
            'detalles': {
                'vencidos': docs_vencidos, 'por_vencer': docs_por_vencer,
                'faltantes_criticos': docs_faltantes_criticos,
                'faltantes_recomendados': docs_faltantes_recomendados
            },
            'riesgos': {'conductor': riesgos_conductor, 'empresa': riesgos_empresa}
        })

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'estado': 'error', 'puede_asignar': False}), 500
    
@administrativo_bp.route("/documents/<path:filename>")
@login_required
def servir_documento(filename):
    """Sirve archivos de la carpeta app/documents/"""
    import os
    from flask import send_from_directory, current_app
    docs_dir = os.path.join(current_app.root_path, "documents")
    return send_from_directory(docs_dir, filename, as_attachment=False)