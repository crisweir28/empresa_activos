# app/routes/portal_empleado.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import text as sqla_text  # ← CORREGIDO: estaba como 'text'
from datetime import date
from ..extensions import db
from ..utils.archivos import guardar_archivo

portal_bp = Blueprint("portal", __name__, url_prefix="/portal")

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@portal_bp.route("/")
@login_required
def dashboard():
    """Dashboard del empleado - ve sus activos y documentos."""
    uid = current_user.id
    
    # Verificar si es conductor (tiene registro en Personal)
    es_conductor = db.session.execute(sqla_text("""
        SELECT COUNT(*) as count FROM personal p
        INNER JOIN usuario u ON CONCAT(p.Nombre, p.Apellido) = u.NombreUsuario
        WHERE u.IdUsuario = :uid AND p.Activo = TRUE
    """), {'uid': uid}).fetchone().count > 0
    
    # Obtener equipos TI asignados
    equipos_raw = db.session.execute(sqla_text("""
        SELECT IdEquipo, Nombre, Marca, Modelo, MarcaModelo, TipoEquipo, 
               NumeroSerie, Estado, Condicion, Valor
        FROM v_equipos_usuario 
        WHERE IdUsuario = :uid
    """), {'uid': uid}).fetchall()

    # Convertir manualmente a diccionarios
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

    # 🔍 DEBUG
    print(f"🔍 DEBUG - IdUsuario: {uid}")
    print(f"🔍 DEBUG - Total equipos: {len(mis_equipos)}")
    if mis_equipos:
        print(f"🔍 DEBUG - Primer equipo: {mis_equipos[0]}")
    
    # Obtener vehículos asignados (solo si es conductor)
    mis_vehiculos = []
    if es_conductor:
        vehiculos_raw = db.session.execute(sqla_text("""
            SELECT * FROM v_vehiculos_usuario WHERE IdUsuario = :uid
        """), {'uid': uid}).fetchall()
        mis_vehiculos = [dict(row._mapping) for row in vehiculos_raw]
    
    # Obtener documentos del usuario (solo si es conductor)
    mis_documentos = []
    permisos_vehiculo = []
    if es_conductor:
        docs_raw = db.session.execute(sqla_text("""
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
        
        # Obtener permisos del vehículo
        if mis_vehiculos:
            id_vehiculo = mis_vehiculos[0]['IdVehiculo']
            permisos_raw = db.session.execute(sqla_text("""
                SELECT * FROM v_permisos_vehiculo 
                WHERE IdVehiculo = :vid
                ORDER BY FechaVencimiento ASC
            """), {'vid': id_vehiculo}).fetchall()
            permisos_vehiculo = [dict(row._mapping) for row in permisos_raw]
    
    # Estadísticas
    docs_vencidos = sum(1 for d in mis_documentos if d.get('EstadoDocumento') == 'vencido')
    docs_por_vencer = sum(1 for d in mis_documentos if d.get('EstadoDocumento') == 'por_vencer')
    total_activos = len(mis_equipos) + len(mis_vehiculos)
    
    return render_template("portal_empleado/dashboard.html",
        area_nombre=current_user.rol_label or "Empleado",
        es_conductor=es_conductor,
        mis_equipos=mis_equipos,
        mis_vehiculos=mis_vehiculos,
        mis_documentos=mis_documentos,
        permisos_vehiculo=permisos_vehiculo,
        total_activos=total_activos,
        docs_vencidos=docs_vencidos,
        docs_por_vencer=docs_por_vencer,
        hoy=date.today()
    )

@portal_bp.route("/documento/subir", methods=["POST"])
@login_required
def subir_documento():
    """Subir un nuevo documento personal."""
    try:
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento', '').strip()
        fecha_emision = request.form.get('fecha_emision') or None
        fecha_vencimiento = request.form.get('fecha_vencimiento') or None
        descripcion = request.form.get('descripcion', '').strip() or None
        
        archivo = request.files.get('archivo')
        
        if not archivo or archivo.filename == '':
            flash('Selecciona un archivo', 'error')
            return redirect(url_for('portal.dashboard'))
        
        if not allowed_file(archivo.filename):
            flash('Tipo de archivo no permitido. Solo PDF, JPG, PNG', 'error')
            return redirect(url_for('portal.dashboard'))
        
        # Guardar archivo
        info = guardar_archivo(
            archivo=archivo,
            prefijo=f"doc_{current_user.id}_{tipo_documento}",
            carpeta="documentos"
        )
        
        # Guardar en BD
        db.session.execute(sqla_text("""
            INSERT INTO documentousuario 
                (IdUsuario, TipoDocumento, NombreArchivo, ArchivoUrl, TipoArchivo, MimeType,
                 FechaEmision, FechaVencimiento, NumeroDocumento, Descripcion, CreadoPor)
            VALUES 
                (:uid, :tipo, :nombre, :url, :tipo_arch, :mime,
                 :f_emision, :f_venc, :numero, :desc, :creado_por)
        """), {
            'uid': current_user.id,
            'tipo': tipo_documento,
            'nombre': info['filename'],
            'url': info['url'],
            'tipo_arch': 'pdf' if info['mime_type'] == 'application/pdf' else 'imagen',
            'mime': info['mime_type'],
            'f_emision': fecha_emision,
            'f_venc': fecha_vencimiento,
            'numero': numero_documento or None,
            'desc': descripcion,
            'creado_por': current_user.id
        })
        
        db.session.commit()
        flash(f'Documento subido correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al subir documento: {str(e)}', 'error')
    
    return redirect(url_for('portal.dashboard'))


@portal_bp.route("/documento/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_documento(id):
    """Eliminar un documento personal."""
    try:
        # Verificar propiedad
        doc = db.session.execute(sqla_text("""
            SELECT IdDocumento FROM documentousuario 
            WHERE IdDocumento = :id AND IdUsuario = :uid
        """), {'id': id, 'uid': current_user.id}).fetchone()
        
        if not doc:
            flash('Documento no encontrado', 'error')
            return redirect(url_for('portal.dashboard'))
        
        db.session.execute(sqla_text("DELETE FROM documentousuario WHERE IdDocumento = :id"), {'id': id})
        db.session.commit()
        flash('Documento eliminado', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('portal.dashboard'))