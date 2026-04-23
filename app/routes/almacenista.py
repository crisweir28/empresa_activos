# app/routes/almacenista.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import date
from sqlalchemy import text as sqla_text
from ..extensions import db
from ..models.herramienta import Herramienta, AsignacionHerramienta, EvidenciaHerramienta, ReporteDanio
from ..models.usuario import Usuario
from ..models.vehiculo import Categoria, Ubicacion
from ..models.departamento import Departamento
from ..views.almacen_vistas import VInventario, VHistorialAsignaciones
from ..utils.permisos import requiere_permiso
from ..utils.archivos import guardar_archivo
from ..models.baja_activo import BajaActivo

almacenista_bp = Blueprint("almacenista", __name__)

ROLES_ALMACEN = ("admin", "almacenista")


def _check_acceso():
    if current_user.rol not in ROLES_ALMACEN:
        flash("No tienes acceso al módulo de almacén.", "error")
        return False
    return True


# ── Dashboard ─────────────────────────────────────────────────
# app/routes/almacenista.py - Actualizar la función dashboard()

@almacenista_bp.route("/")
@login_required
@requiere_permiso('Almacén')
def dashboard():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    inventario  = VInventario.query.all()
    total       = len(inventario)
    disponibles = sum(1 for h in inventario if h.Estado == "disponible")
    asignados   = sum(1 for h in inventario if h.Estado == "asignado")
    daniados    = sum(1 for h in inventario if h.Estado in ("dañado", "perdido"))
    bajas       = sum(1 for h in inventario if h.Estado == "baja")  # ← NUEVO

    recientes = VHistorialAsignaciones.query.filter_by(EstadoAsignacion="activa").limit(8).all()
    reportes  = ReporteDanio.query.order_by(ReporteDanio.CreadoEn.desc()).limit(5).all()
    
    # Traer TODAS las herramientas para filtrado JS (igual que Vehículos)
    herramientas = inventario  # ← NUEVO
    usuarios = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()  # ← NUEVO para modal
    categorias = Categoria.query.order_by(Categoria.Nombre).all()  # ← NUEVO
    ubicaciones = Ubicacion.query.order_by(Ubicacion.Nombre).all()  # ← NUEVO
    departamentos = Departamento.query.order_by(Departamento.nombre).all()  # ← NUEVO

    return render_template("almacenista/dashboard.html",
        total         = total,
        disponibles   = disponibles,
        asignados     = asignados,
        daniados      = daniados,
        bajas         = bajas,  # ← NUEVO
        recientes     = recientes,
        reportes      = reportes,
        herramientas  = herramientas,  # ← NUEVO
        usuarios      = usuarios,  # ← NUEVO
        categorias    = categorias,  # ← NUEVO
        ubicaciones   = ubicaciones,  # ← NUEVO
        departamentos = departamentos,  # ← NUEVO
    )


# ── Inventario ────────────────────────────────────────────────
@almacenista_bp.route("/inventario")
@login_required
@requiere_permiso('Almacén')
def inventario():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    estado = request.args.get("estado", "")
    query  = VInventario.query
    if estado:
        query = query.filter_by(Estado=estado)
    else:
        query = query.filter(VInventario.Estado != 'baja')

    return render_template("almacenista/inventario.html",
        herramientas  = query.order_by(VInventario.Nombre).all(),
        estado_filtro = estado,
        usuarios      = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all(),
        categorias    = Categoria.query.order_by(Categoria.Nombre).all(),
        ubicaciones   = Ubicacion.query.order_by(Ubicacion.Nombre).all(),
        departamentos = Departamento.query.order_by(Departamento.nombre).all(),
    )


# ── Alta herramienta ──────────────────────────────────────────
@almacenista_bp.route("/herramientas/nueva", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'crear')
def herramienta_nueva():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        h = Herramienta(
            Nombre          = request.form.get("nombre", "").strip(),
            Marca           = request.form.get("marca", "").strip() or None,
            Modelo          = request.form.get("modelo", "").strip() or None,
            NumeroSerie     = request.form.get("numero_serie", "").strip() or None,
            Estado          = request.form.get("estado", "disponible"),
            Costo           = float(request.form.get("costo") or 0),
            FechaAlta       = request.form.get("fecha_alta") or None,
            Descripcion     = request.form.get("descripcion", "").strip() or None,
            TipoHerramienta = request.form.get("tipo_herramienta", "").strip() or None,
            IdCategoria     = int(request.form.get("categoria_id")) if request.form.get("categoria_id") else None,
            IdUbicacion     = int(request.form.get("ubicacion_id")) if request.form.get("ubicacion_id") else None,
            IdDepartamento  = int(request.form.get("departamento_id")) if request.form.get("departamento_id") else None,
            Subarea         = request.form.get("subarea", "").strip() or None,
        )
        db.session.add(h)
        db.session.flush()

        evidencia = request.files.get("evidencia")
        if evidencia and evidencia.filename:
            info = guardar_archivo(archivo=evidencia, prefijo=f"herr_{h.IdHerramienta}", carpeta="static/evidencias")
            db.session.add(EvidenciaHerramienta(
                IdHerramienta=h.IdHerramienta, ArchivoUrl=info["url"],
                NombreArchivo=info["filename"], Tipo="entrega",
                TipoArchivo="imagen", MimeType=info["mime_type"],
                Descripcion="Foto inicial al dar de alta", CreadoPor=current_user.id,
            ))

        db.session.commit()
        flash(f"Herramienta '{h.Nombre}' registrada correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.inventario"))


# ── Editar herramienta ────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/editar", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'editar')
def herramienta_editar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    h = Herramienta.query.get_or_404(id)
    h.Nombre      = request.form.get("nombre", "").strip()
    h.Marca       = request.form.get("marca", "").strip() or None
    h.Modelo      = request.form.get("modelo", "").strip() or None
    h.NumeroSerie = request.form.get("numero_serie", "").strip() or None
    h.Costo       = float(request.form.get("costo") or 0)
    h.FechaAlta   = request.form.get("fecha_alta") or None
    h.Descripcion = request.form.get("descripcion", "").strip() or None
    db.session.commit()
    flash("Herramienta actualizada.", "success")
    return redirect(url_for("almacenista.inventario"))


# ── Asignar herramienta ───────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/asignar", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'editar')
def herramienta_asignar(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_asignar_herramienta(:hid,:uid,:fecha,:por,:obs,@res)"),
            {
                "hid":   id,
                "uid":   int(request.form.get("usuario_id")),
                "fecha": request.form.get("fecha_asignacion") or None,
                "por":   current_user.id,
                "obs":   request.form.get("observaciones", "").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash(
            "Herramienta asignada correctamente." if row and row.r == "OK" else f"No se pudo asignar: {row.r if row else 'error'}.",
            "success" if row and row.r == "OK" else "error"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.inventario"))


# ── Devolver herramienta ──────────────────────────────────────
@almacenista_bp.route("/asignaciones/<int:id>/devolver", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'editar')
def herramienta_devolver(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_devolver_herramienta(:aid,:fecha,:por,:obs,:estado,@res)"),
            {
                "aid":    id,
                "fecha":  request.form.get("fecha_devolucion") or None,
                "por":    current_user.id,
                "obs":    request.form.get("observaciones", "").strip() or None,
                "estado": request.form.get("estado_final", "disponible"),
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash(
            "Devolución registrada." if row and row.r == "OK" else "Error al registrar devolución.",
            "success" if row and row.r == "OK" else "error"
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.historial"))


# ── Historial asignaciones ────────────────────────────────────
@almacenista_bp.route("/historial")
@login_required
@requiere_permiso('Almacén')
def historial():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    estado = request.args.get("estado", "")
    query  = VHistorialAsignaciones.query
    if estado:
        query = query.filter_by(EstadoAsignacion=estado)

    return render_template("almacenista/historial.html",
        asignaciones  = query.order_by(VHistorialAsignaciones.FechaAsignacion.desc()).all(),
        usuarios      = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all(),
        estado_filtro = estado,
    )


# ── Subir evidencia ───────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/evidencia", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'editar')
def subir_evidencia(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    archivo = request.files.get("archivo")
    if not archivo or archivo.filename == "":
        flash("Selecciona un archivo.", "error")
        return redirect(url_for("almacenista.herramienta_detalle", id=id))

    try:
        info = guardar_archivo(
            archivo = archivo,
            prefijo = f"herr_{id}",
            carpeta = "documents" if not archivo.filename.rsplit(".", 1)[-1].lower()
                      in {"png","jpg","jpeg","gif","webp"} else "static/evidencias"
        )
        db.session.add(EvidenciaHerramienta(
            IdHerramienta=id, ArchivoUrl=info["url"],
            NombreArchivo=info["filename"],
            Tipo=request.form.get("tipo", "daño"),
            TipoArchivo=info["tipo_archivo"], MimeType=info["mime_type"],
            Descripcion=request.form.get("descripcion", "").strip() or None,
            CreadoPor=current_user.id,
        ))
        db.session.commit()
        flash("Archivo subido correctamente.", "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al subir archivo: {str(e)}", "error")

    return redirect(url_for("almacenista.herramienta_detalle", id=id))


# ── Reporte de daño ───────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/reporte", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'crear')
def reporte_danio(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    herr = Herramienta.query.get_or_404(id)
    try:
        r = ReporteDanio(
            IdHerramienta        = id,
            NombreMaterial       = request.form.get("nombre_material", herr.Nombre),
            Caracteristica       = request.form.get("caracteristica", "").strip(),
            Razon                = request.form.get("razon", "").strip(),
            Tipo                 = request.form.get("tipo", "daño"),
            IdUsuarioResponsable = int(request.form.get("responsable_id")) if request.form.get("responsable_id") else None,
            CreadoPor            = current_user.id,
        )

        archivo = request.files.get("archivo")
        if archivo and archivo.filename:
            info = guardar_archivo(
                archivo = archivo,
                prefijo = f"reporte_{id}",
                carpeta = "documents" if not archivo.filename.rsplit(".", 1)[-1].lower()
                          in {"png","jpg","jpeg","gif","webp"} else "static/evidencias"
            )
            r.ArchivoUrl    = info["url"]
            r.NombreArchivo = info["filename"]
            r.TipoArchivo   = info["tipo_archivo"]
            r.MimeType      = info["mime_type"]

        db.session.add(r)
        herr.Estado = "dañado" if r.Tipo == "daño" else "perdido"
        db.session.commit()
        flash("Reporte de daño registrado.", "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.herramienta_detalle", id=id))


# ── Detalle herramienta ───────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>")
@login_required
@requiere_permiso('Almacén')
def herramienta_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    herramienta = Herramienta.query.get_or_404(id)
    asignacion  = AsignacionHerramienta.query.filter_by(IdHerramienta=id, FechaDevolucion=None).first()
    evidencias  = EvidenciaHerramienta.query.filter_by(IdHerramienta=id).order_by(EvidenciaHerramienta.CreadoEn.desc()).all()
    reportes    = ReporteDanio.query.filter_by(IdHerramienta=id).order_by(ReporteDanio.CreadoEn.desc()).all()
    historial   = VHistorialAsignaciones.query.filter_by(IdHerramienta=id).all()
    usuarios    = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()

    return render_template("almacenista/herramienta_detalle.html",
        herramienta = herramienta,
        asignacion  = asignacion,
        evidencias  = evidencias,
        reportes    = reportes,
        historial   = historial,
        usuarios    = usuarios,
        today       = date.today(),
    )


# ── Baja herramienta ──────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/baja", methods=["POST"])
@login_required
@requiere_permiso('Almacén', 'eliminar')
def herramienta_baja(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))
    h = Herramienta.query.get_or_404(id)
    h.Estado = "baja"
    db.session.add(BajaActivo(
        TipoActivo    = "herramienta",
        IdActivo      = h.IdHerramienta,
        NombreActivo  = h.Nombre,
        DadoDeBajaPor = current_user.id,
    ))
    db.session.commit()
    flash(f"'{h.Nombre}' dado de baja.", "success")
    return redirect(url_for("almacenista.inventario"))


# ── API ───────────────────────────────────────────────────────
@almacenista_bp.route("/api/herramienta/<int:id>")
@login_required
def api_herramienta(id):
    h = Herramienta.query.get_or_404(id)
    return jsonify(h.to_dict())