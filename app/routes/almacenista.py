import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import date
from werkzeug.utils import secure_filename
from sqlalchemy import text as sqla_text
from ..extensions import db
from ..models.herramienta import Herramienta, AsignacionHerramienta, EvidenciaHerramienta, ReporteDanio
from ..models.usuario import Usuario
from ..views.almacen_vistas import VInventario, VHistorialAsignaciones
from ..utils.permisos import requiere_permiso

almacenista_bp = Blueprint("almacenista", __name__)

ROLES_ALMACEN = ("ti", "almacenista")
UPLOAD_FOLDER = "app/static/evidencias"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def _check_acceso():
    if current_user.rol not in ROLES_ALMACEN:
        flash("No tienes acceso al módulo de almacén.", "error")
        return False
    return True


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Dashboard ─────────────────────────────────────────────────
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

    recientes   = VHistorialAsignaciones.query.filter_by(
        EstadoAsignacion="activa"
    ).limit(8).all()
    reportes    = ReporteDanio.query.order_by(ReporteDanio.CreadoEn.desc()).limit(5).all()

    return render_template("almacenista/dashboard.html",
        total       = total,
        disponibles = disponibles,
        asignados   = asignados,
        daniados    = daniados,
        recientes   = recientes,
        reportes    = reportes,
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

    return render_template("almacenista/inventario.html",
        herramientas = query.order_by(VInventario.Nombre).all(),
        estado_filtro = estado,
    )


# ── Alta herramienta ──────────────────────────────────────────
@almacenista_bp.route("/herramientas/nueva", methods=["POST"])
@login_required
def herramienta_nueva():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    try:
        db.session.execute(
            sqla_text("CALL sp_alta_herramienta(:nom,:marc,:mod,:serie,:costo,:fecha,:desc,@res,@id)"),
            {
                "nom":   request.form.get("nombre", "").strip(),
                "marc":  request.form.get("marca", "").strip() or None,
                "mod":   request.form.get("modelo", "").strip() or None,
                "serie": request.form.get("numero_serie", "").strip() or None,
                "costo": float(request.form.get("costo") or 0),
                "fecha": request.form.get("fecha_alta") or None,
                "desc":  request.form.get("descripcion", "").strip() or None,
            }
        )
        db.session.execute(sqla_text("COMMIT"))
        row = db.session.execute(sqla_text("SELECT @res AS r")).fetchone()
        flash("Herramienta registrada correctamente." if row and row.r == "OK" else f"Error: {row.r}.", "success" if row and row.r == "OK" else "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.inventario"))


# ── Editar herramienta ────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/editar", methods=["POST"])
@login_required
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
        if row and row.r == "OK":
            flash("Herramienta asignada correctamente.", "success")
        else:
            flash(f"No se pudo asignar: {row.r if row else 'error'}.", "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.inventario"))


# ── Devolver herramienta ──────────────────────────────────────
@almacenista_bp.route("/asignaciones/<int:id>/devolver", methods=["POST"])
@login_required
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
        flash("Devolución registrada." if row and row.r == "OK" else "Error al registrar devolución.", "success" if row and row.r == "OK" else "error")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.historial"))


# ── Historial asignaciones ────────────────────────────────────
@almacenista_bp.route("/historial")
@login_required
def historial():
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    estado = request.args.get("estado", "")
    query  = VHistorialAsignaciones.query
    if estado:
        query = query.filter_by(EstadoAsignacion=estado)

    usuarios = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()

    return render_template("almacenista/historial.html",
        asignaciones  = query.order_by(VHistorialAsignaciones.FechaAsignacion.desc()).all(),
        usuarios      = usuarios,
        estado_filtro = estado,
    )


# ── Subir evidencia ───────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/evidencia", methods=["POST"])
@login_required
def subir_evidencia(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    archivo = request.files.get("archivo")
    if not archivo or archivo.filename == "":
        flash("Selecciona un archivo.", "error")
        return redirect(url_for("almacenista.inventario"))

    if not _allowed_file(archivo.filename):
        flash("Solo se permiten archivos PNG y JPG.", "error")
        return redirect(url_for("almacenista.inventario"))

    try:
        # Crear carpeta si no existe
        upload_path = os.path.join(current_app.root_path, "static", "evidencias")
        os.makedirs(upload_path, exist_ok=True)

        filename    = secure_filename(f"herr_{id}_{int(date.today().strftime('%Y%m%d'))}_{archivo.filename}")
        filepath    = os.path.join(upload_path, filename)
        archivo.save(filepath)

        url_relativa = f"/static/evidencias/{filename}"

        ev = EvidenciaHerramienta(
            IdHerramienta = id,
            ArchivoUrl    = url_relativa,
            NombreArchivo = filename,
            Tipo          = request.form.get("tipo", "daño"),
            CreadoPor     = current_user.id,
        )
        db.session.add(ev)
        db.session.commit()
        flash("Evidencia subida correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al subir archivo: {str(e)}", "error")

    return redirect(url_for("almacenista.herramienta_detalle", id=id))


# ── Reporte de daño ───────────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>/reporte", methods=["POST"])
@login_required
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
        db.session.add(r)

        # Actualizar estado de la herramienta
        nuevo_estado = "dañado" if r.Tipo == "daño" else "perdido"
        herr.Estado  = nuevo_estado
        db.session.commit()
        flash("Reporte de daño registrado.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "error")

    return redirect(url_for("almacenista.herramienta_detalle", id=id))


# ── Detalle herramienta ───────────────────────────────────────
@almacenista_bp.route("/herramientas/<int:id>")
@login_required
def herramienta_detalle(id):
    if not _check_acceso():
        return redirect(url_for("activos.dashboard"))

    herramienta  = Herramienta.query.get_or_404(id)
    asignacion   = AsignacionHerramienta.query.filter_by(
                    IdHerramienta=id, FechaDevolucion=None).first()
    evidencias   = EvidenciaHerramienta.query.filter_by(IdHerramienta=id).order_by(
                    EvidenciaHerramienta.CreadoEn.desc()).all()
    reportes     = ReporteDanio.query.filter_by(IdHerramienta=id).order_by(
                    ReporteDanio.CreadoEn.desc()).all()
    historial    = VHistorialAsignaciones.query.filter_by(IdHerramienta=id).all()
    usuarios     = Usuario.query.filter_by(Estatus=True).order_by(Usuario.Nombre).all()

    return render_template("almacenista/herramienta_detalle.html",
        herramienta = herramienta,
        asignacion  = asignacion,
        evidencias  = evidencias,
        reportes    = reportes,
        historial   = historial,
        usuarios    = usuarios,
        today       = date.today(),
    )


# ── API ───────────────────────────────────────────────────────
@almacenista_bp.route("/api/herramienta/<int:id>")
@login_required
def api_herramienta(id):
    h = Herramienta.query.get_or_404(id)
    return jsonify(h.to_dict())