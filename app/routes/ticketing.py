# app/routes/ticketing.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.extensions import db, socketio
from ..utils.permisos import requiere_permiso, tiene_permiso
from werkzeug.utils import secure_filename

# Crear el Blueprint
ticketing_bp = Blueprint('ticketing', __name__)

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# MODELOS SQLAlchemy
# ============================================

class Ticket(db.Model):
    __tablename__ = 'Tickets'
    
    IdTicket = db.Column(db.Integer, primary_key=True)
    NumeroTicket = db.Column(db.String(20), unique=True, nullable=False)
    
    # Usuario creador
    IdUsuarioCreador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ← CAMBIAR
    
    # Información del ticket
    Titulo = db.Column(db.String(200), nullable=False)
    Descripcion = db.Column(db.Text, nullable=False)
    IdCategoria = db.Column(db.Integer, db.ForeignKey('CategoriasTicket.IdCategoria'), nullable=False)
    IdPrioridad = db.Column(db.Integer, db.ForeignKey('PrioridadesTicket.IdPrioridad'), nullable=False, default=2)
    IdEstado = db.Column(db.Integer, db.ForeignKey('EstadosTicket.IdEstado'), nullable=False, default=1)
    
    # Relación con activos (opcional)
    IdEquipo = db.Column(db.Integer, nullable=True)
    
    # Asignación
    IdAsignadoA = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True) 
    
    # Metadata organizacional
    IdSede = db.Column(db.Integer, nullable=True)
    IdDepartamento = db.Column(db.Integer, nullable=True)
    
    # Fechas
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    FechaUltimaActualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    FechaPrimeraRespuesta = db.Column(db.DateTime, nullable=True)
    FechaResolucion = db.Column(db.DateTime, nullable=True)
    FechaCierre = db.Column(db.DateTime, nullable=True)
    
    # Satisfacción
    CalificacionServicio = db.Column(db.Integer, nullable=True)
    ComentarioSatisfaccion = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Ticket {self.NumeroTicket}: {self.Titulo}>'


class CategoriaTicket(db.Model):
    __tablename__ = 'CategoriasTicket'
    
    IdCategoria = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Descripcion = db.Column(db.Text)
    Icono = db.Column(db.String(50))
    Color = db.Column(db.String(20))
    Activo = db.Column(db.Boolean, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CategoriaTicket {self.Nombre}>'


class EstadoTicket(db.Model):
    __tablename__ = 'EstadosTicket'
    
    IdEstado = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Descripcion = db.Column(db.Text)
    Color = db.Column(db.String(20))
    EsEstadoFinal = db.Column(db.Boolean, default=False)
    Orden = db.Column(db.Integer)
    Activo = db.Column(db.Boolean, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EstadoTicket {self.Nombre}>'


class PrioridadTicket(db.Model):
    __tablename__ = 'PrioridadesTicket'
    
    IdPrioridad = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)
    Descripcion = db.Column(db.Text)
    Color = db.Column(db.String(20))
    Nivel = db.Column(db.Integer)
    TiempoRespuestaHoras = db.Column(db.Integer)
    Activo = db.Column(db.Boolean, default=True)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrioridadTicket {self.Nombre}>'


class ComentarioTicket(db.Model):
    __tablename__ = 'ComentariosTicket'
    
    IdComentario = db.Column(db.Integer, primary_key=True)
    IdTicket = db.Column(db.Integer, db.ForeignKey('Tickets.IdTicket'), nullable=False)
    IdUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ← CAMBIAR
    Comentario = db.Column(db.Text, nullable=False)
    EsInterno = db.Column(db.Boolean, default=False)
    EsRespuestaOficial = db.Column(db.Boolean, default=False)
    FechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ComentarioTicket {self.IdComentario}>'


class AdjuntoTicket(db.Model):
    __tablename__ = 'AdjuntosTicket'
    
    IdAdjunto = db.Column(db.Integer, primary_key=True)
    IdTicket = db.Column(db.Integer, db.ForeignKey('Tickets.IdTicket'), nullable=False)
    IdUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ← CAMBIAR
    NombreArchivo = db.Column(db.String(255), nullable=False)
    NombreOriginal = db.Column(db.String(255), nullable=False)
    RutaArchivo = db.Column(db.String(500), nullable=False)
    TipoMIME = db.Column(db.String(100))
    TamanoKB = db.Column(db.Numeric(10, 2))
    FechaSubida = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdjuntoTicket {self.NombreOriginal}>'


class HistorialTicket(db.Model):
    __tablename__ = 'HistorialTicket'
    
    IdHistorial = db.Column(db.Integer, primary_key=True)
    IdTicket = db.Column(db.Integer, db.ForeignKey('Tickets.IdTicket'), nullable=False)
    IdUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    TipoCambio = db.Column(db.String(50), nullable=False)
    ValorAnterior = db.Column(db.String(255))
    ValorNuevo = db.Column(db.String(255))
    Descripcion = db.Column(db.Text)
    FechaCambio = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HistorialTicket {self.TipoCambio}>'


# ============================================
# RUTAS BÁSICAS
# ============================================

@ticketing_bp.route('/')
@login_required
def index():
    """
    Redirige según el rol del usuario:
    - Admin TI (con permiso eliminar): Dashboard completo
    - Técnico TI (con permiso editar): Mis asignados
    - Usuario normal: Mis tickets
    """
    if tiene_permiso('Ticketing', 'eliminar'):
        # Admin TI
        return redirect(url_for('ticketing.dashboard_ti'))
    elif tiene_permiso('Ticketing', 'editar'):
        # Técnico TI
        return redirect(url_for('ticketing.mis_tickets_asignados'))
    else:
        # Usuario normal
        return redirect(url_for('ticketing.mis_tickets'))

@ticketing_bp.route('/dashboard')
@login_required
@requiere_permiso('Ticketing', 'ver')
def dashboard_ti():
    """Dashboard para el área de TI con todos los tickets"""
    try:
        # ═══════════════════════════════════════════════════════
        # MÉTRICAS
        # ═══════════════════════════════════════════════════════
        metricas = db.session.execute(text('SELECT * FROM v_tickets_metricas')).fetchone()
        
        metricas_dict = {}
        if metricas:
            metricas_dict = dict(metricas._mapping)
        else:
            metricas_dict = {
                'TotalTickets': 0,
                'TotalAbiertos': 0,
                'TotalEnProceso': 0,
                'CerradosHoy': 0,
                'TotalCerrados': 0,
                'TotalUrgentes': 0
            }
        # ═══════════════════════════════════════════════════════
# TICKETS ACTIVOS (SIN apellidos)
# ═══════════════════════════════════════════════════════
        tickets_result = db.session.execute(text("""
        SELECT 
        t.IdTicket,
        t.NumeroTicket,
        t.Titulo,
        COALESCE(u.nombre, 'Usuario Desconocido') as UsuarioCreador,
        COALESCE(u.email, 'sin-email@empresa.com') as EmailCreador,
        c.Nombre as Categoria,
        c.Color as CategoriaColor,
        p.Nombre as Prioridad,
        p.Color as PrioridadColor,
        p.Nivel as PrioridadNivel,
        e.Nombre as Estado,
        e.Color as EstadoColor,
        COALESCE(asig.nombre, '') as AsignadoA,
        t.FechaCreacion,
        CASE 
            WHEN t.FechaPrimeraRespuesta IS NOT NULL 
                AND TIMESTAMPDIFF(HOUR, t.FechaCreacion, t.FechaPrimeraRespuesta) <= p.TiempoRespuestaHoras 
                THEN 1
            WHEN t.FechaPrimeraRespuesta IS NULL 
                AND TIMESTAMPDIFF(HOUR, t.FechaCreacion, NOW()) > p.TiempoRespuestaHoras 
                THEN 0
            ELSE NULL
        END as SLARespuestaCumplido,
        t.IdAsignadoA
    FROM Tickets t
    INNER JOIN CategoriasTicket c ON t.IdCategoria = c.IdCategoria
    INNER JOIN PrioridadesTicket p ON t.IdPrioridad = p.IdPrioridad
    INNER JOIN EstadosTicket e ON t.IdEstado = e.IdEstado
    LEFT JOIN usuarios u ON t.IdUsuarioCreador = u.id
    LEFT JOIN usuarios asig ON t.IdAsignadoA = asig.id
    WHERE e.Nombre IN ('Abierto', 'En Proceso', 'Escalado', 'Pendiente')
    ORDER BY p.Nivel DESC, t.FechaCreacion ASC 
    LIMIT 100
""")).fetchall()
        
        current_app.logger.info(f'🔍 Resultados de query: {len(tickets_result)} tickets')
        
        # Convertir a diccionarios
        tickets = []
        if tickets_result:
            for row in tickets_result:
                ticket_dict = dict(row._mapping)
                tickets.append(ticket_dict)
        
        current_app.logger.info(f'✅ Tickets convertidos: {len(tickets)}')
        
        if tickets:
            current_app.logger.info(f'🎫 Primer ticket: {tickets[0]}')
        
        return render_template(
            'ticketing/dashboard_ti.html',
            tickets=tickets,
            metricas=metricas_dict
        )
        
    except Exception as e:
        current_app.logger.error(f'❌ Error en dashboard_ti: {str(e)}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        flash('Error al cargar el dashboard de ticketing', 'danger')
        return redirect(url_for('activos.dashboard'))
    
    
@ticketing_bp.route('/mis-tickets')
@login_required
def mis_tickets():
    """Vista de tickets creados por el usuario actual"""
    try:
        # Obtener tickets del usuario usando la vista SQL
        tickets_query = text("""
            SELECT * FROM v_mis_tickets
            WHERE IdUsuarioCreador = :user_id
            ORDER BY FechaCreacion DESC
        """)
        
        tickets_result = db.session.execute(
            tickets_query, 
            {'user_id': current_user.id}
        ).fetchall()
        
        # Convertir a diccionarios
        tickets = []
        if tickets_result:
            columnas = tickets_result[0]._mapping.keys()
            for row in tickets_result:
                tickets.append(dict(zip(columnas, row)))
        
        return render_template(
            'ticketing/mis_tickets.html',
            tickets=tickets
        )
        
    except Exception as e:
        current_app.logger.error(f'Error en mis_tickets: {str(e)}')
        flash('Error al cargar tus tickets', 'danger')
        return redirect(url_for('main.index'))


@ticketing_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_ticket():
    """Crear un nuevo ticket"""
    if request.method == 'GET':
        # Obtener categorías activas
        categorias = CategoriaTicket.query.filter_by(Activo=True).order_by(CategoriaTicket.Nombre).all()
        
        return render_template(
            'ticketing/nuevo_ticket.html',
            categorias=categorias
        )
    
    # POST: Crear ticket usando SQL directo
    try:
        descripcion = request.form.get('descripcion', '').strip()
        categoria_id = request.form.get('categoria')
        
        # Auto-generar título desde los primeros 100 caracteres de la descripción
        titulo = descripcion[:100] if len(descripcion) <= 100 else descripcion[:97] + '...'
        
        # Insertar con SQL directo
        result = db.session.execute(text("""
            INSERT INTO Tickets (
                IdUsuarioCreador, Titulo, Descripcion, IdCategoria, 
                IdPrioridad, IdEstado, CanalCreacion
            ) VALUES (
                :user_id, :titulo, :descripcion, :categoria,
                2, 1, 'Portal de Usuario'
            )
        """), {
            'user_id': current_user.id,
            'titulo': titulo,
            'descripcion': descripcion,
            'categoria': categoria_id
        })
        
        # Obtener el ID del ticket recién creado
        id_ticket = result.lastrowid
        
        db.session.commit()
        
        # Emitir evento SocketIO para actualizar dashboards
        socketio.emit('ticketing_update', {
            'tipo': 'nuevo_ticket',
            'ticket_id': id_ticket
        })
        
        # Obtener el número de ticket generado por el trigger
        ticket_numero = db.session.execute(text("""
            SELECT NumeroTicket FROM Tickets WHERE IdTicket = :id
        """), {'id': id_ticket}).scalar()
        
        flash(f'Ticket {ticket_numero} creado exitosamente. El área de TI lo revisará pronto.', 'success')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al crear ticket: {str(e)}')
        flash('Error al crear el ticket. Intenta nuevamente.', 'danger')
        return redirect(url_for('ticketing.nuevo_ticket'))

@ticketing_bp.route('/ticket/<int:id_ticket>')
@login_required
def detalle_ticket(id_ticket):
    """Ver detalle completo de un ticket"""
    try:
        # Obtener ticket usando la vista SQL
        ticket_query = text("""
            SELECT * FROM v_tickets_completo
            WHERE IdTicket = :id_ticket
        """)
        
        ticket_result = db.session.execute(
            ticket_query,
            {'id_ticket': id_ticket}
        ).fetchone()
        
        if not ticket_result:
            flash('Ticket no encontrado', 'warning')
            return redirect(url_for('ticketing.index'))
        
        # Convertir a diccionario
        columnas = ticket_result._mapping.keys()
        ticket = dict(zip(columnas, ticket_result))
        
        # Verificar permisos
        es_creador = ticket['IdUsuarioCreador'] == current_user.id
        es_asignado = ticket['IdAsignadoA'] == current_user.id
        es_ti = tiene_permiso('Ticketing', 'editar')  # ✅ Cambio aquí

        if not (es_creador or es_asignado or es_ti):
            flash('No tienes permiso para ver este ticket', 'danger')
            return redirect(url_for('ticketing.index'))
        
        # Obtener comentarios con nombre de usuario
        comentarios_query = text("""
            SELECT 
                c.IdComentario,
                c.IdTicket,
                c.IdUsuario,
                c.Comentario,
                c.EsInterno,
                c.EsRespuestaOficial,
                c.FechaCreacion,
                u.Nombre as NombreUsuario
            FROM ComentariosTicket c
            LEFT JOIN usuario u ON c.IdUsuario = u.IdUsuario
            WHERE c.IdTicket = :id_ticket
            ORDER BY c.FechaCreacion ASC
        """)
        
        comentarios_result = db.session.execute(
            comentarios_query,
            {'id_ticket': id_ticket}
        ).fetchall()
        
        # Convertir comentarios a diccionarios
        comentarios = []
        if comentarios_result:
            cols = comentarios_result[0]._mapping.keys()
            for row in comentarios_result:
                comentario_dict = dict(zip(cols, row))
                # Filtrar comentarios internos si no eres de TI
                if not comentario_dict['EsInterno'] or es_ti:
                    comentarios.append(comentario_dict)
        
        # Obtener adjuntos
        adjuntos_query = text("""
            SELECT * FROM AdjuntosTicket 
            WHERE IdTicket = :id_ticket 
            ORDER BY FechaSubida DESC
        """)

        adjuntos_result = db.session.execute(
        adjuntos_query,
        {'id_ticket': id_ticket}
        ).fetchall()

        # Convertir a diccionarios
        adjuntos = []
        if adjuntos_result:
            cols = adjuntos_result[0]._mapping.keys()
        for row in adjuntos_result:
            adjuntos.append(dict(zip(cols, row)))
        
        # Obtener historial
        historial = HistorialTicket.query.filter_by(IdTicket=id_ticket).order_by(HistorialTicket.FechaCambio.desc()).all()
        
        return render_template(
            'ticketing/detalle_ticket.html',
            ticket=ticket,
            comentarios=comentarios,
            adjuntos=adjuntos,
            historial=historial,
            es_ti=es_ti
        )
        
    except Exception as e:
        current_app.logger.error(f'Error en detalle_ticket: {str(e)}')
        flash('Error al cargar el ticket', 'danger')
        return redirect(url_for('ticketing.index'))


# ============================================
# API ENDPOINTS (para AJAX)
# ============================================

@ticketing_bp.route('/api/categorias')
@login_required
def api_categorias():
    """Obtener categorías activas (para formularios dinámicos)"""
    categorias = CategoriaTicket.query.filter_by(Activo=True).order_by(CategoriaTicket.Nombre).all()
    
    return jsonify([{
        'id': c.IdCategoria,
        'nombre': c.Nombre,
        'descripcion': c.Descripcion,
        'icono': c.Icono,
        'color': c.Color
    } for c in categorias])


@ticketing_bp.route('/api/prioridades')
@login_required
def api_prioridades():
    """Obtener prioridades activas"""
    prioridades = PrioridadTicket.query.filter_by(Activo=True).order_by(PrioridadTicket.Nivel).all()
    
    return jsonify([{
        'id': p.IdPrioridad,
        'nombre': p.Nombre,
        'descripcion': p.Descripcion,
        'color': p.Color,
        'nivel': p.Nivel
    } for p in prioridades])


@ticketing_bp.route('/api/estados')
@login_required
def api_estados():
    """Obtener estados activos"""
    estados = EstadoTicket.query.filter_by(Activo=True).order_by(EstadoTicket.Orden).all()
    
    return jsonify([{
        'id': e.IdEstado,
        'nombre': e.Nombre,
        'descripcion': e.Descripcion,
        'color': e.Color,
        'es_final': e.EsEstadoFinal
    } for e in estados])
    
@ticketing_bp.route('/ticket/<int:id_ticket>/asignar', methods=['POST'])
@login_required
@requiere_permiso('Ticketing', 'editar')
def asignar_ticket(id_ticket):
    """Asignar ticket a un técnico"""
    try:
        id_tecnico = request.form.get('id_tecnico')
        nueva_prioridad = request.form.get('nueva_prioridad')
        
        if not id_tecnico:
            flash('Debes seleccionar un técnico', 'warning')
            return redirect(url_for('ticketing.dashboard_ti'))
        
        # Actualizar asignación
        query = "UPDATE Tickets SET IdAsignadoA = :tecnico, IdEstado = 2"  # 2 = En Proceso
        params = {'tecnico': id_tecnico, 'ticket': id_ticket}
        
        # Si cambió la prioridad también
        if nueva_prioridad:
            query += ", IdPrioridad = :prioridad"
            params['prioridad'] = nueva_prioridad
        
        query += " WHERE IdTicket = :ticket"
        
        db.session.execute(text(query), params)
        db.session.commit()
        
        # Emitir evento SocketIO para actualizar dashboards
        socketio.emit('ticketing_update', {
            'tipo': 'asignacion',
            'ticket_id': id_ticket,
            'tecnico_id': id_tecnico
        })
        
        # Obtener número de ticket para el mensaje
        ticket = db.session.execute(text("""
            SELECT NumeroTicket FROM Tickets WHERE IdTicket = :id
        """), {'id': id_ticket}).scalar()
        
        flash(f'Ticket {ticket} asignado correctamente', 'success')
        return redirect(url_for('ticketing.dashboard_ti'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al asignar ticket: {str(e)}')
        flash('Error al asignar el ticket', 'danger')
        return redirect(url_for('ticketing.dashboard_ti'))


@ticketing_bp.route('/api/tecnicos')
@login_required
def api_tecnicos():
    """Obtener lista de técnicos del área TI"""
    try:
        # Obtener solo usuarios del área TI (IdRol = 5)
        tecnicos_raw = db.session.execute(text("""
            SELECT IdUsuario, Nombre, Correo
            FROM usuario
            WHERE IdRol = 5 AND Estatus = 1
            ORDER BY Nombre
        """)).fetchall()
        
        tecnicos = []
        for row in tecnicos_raw:
            tecnicos.append({
                'id': row[0],
                'nombre': row[1],
                'email': row[2]
            })
        
        return jsonify(tecnicos)
        
    except Exception as e:
        current_app.logger.error(f'Error al obtener técnicos: {str(e)}')
        return jsonify([])
    
@ticketing_bp.route('/ticket/<int:id_ticket>/comentario', methods=['POST'])
@login_required
def agregar_comentario(id_ticket):
    """Agregar un comentario a un ticket"""
    try:
        comentario_texto = request.form.get('comentario', '').strip()
        es_interno = request.form.get('es_interno') == '1'
        
        if not comentario_texto:
            flash('El comentario no puede estar vacío', 'warning')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
        # Insertar comentario
        db.session.execute(text("""
            INSERT INTO ComentariosTicket (
                IdTicket, IdUsuario, Comentario, EsInterno, EsRespuestaOficial
            ) VALUES (
                :ticket, :usuario, :comentario, :interno, :oficial
            )
        """), {
            'ticket': id_ticket,
            'usuario': current_user.id,
            'comentario': comentario_texto,
            'interno': 1 if es_interno else 0,
            'oficial': 1 if current_user.rol == 'Usuario TI' else 0
        })
        
        db.session.commit()
        
        flash('Comentario agregado correctamente', 'success')
        
        # TODO: Enviar notificación por email aquí
        
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al agregar comentario: {str(e)}')
        flash('Error al agregar el comentario', 'danger')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
    
@ticketing_bp.route('/ticket/<int:id_ticket>/adjunto', methods=['POST'])
@login_required
def subir_adjunto(id_ticket):
    """Subir un archivo adjunto a un ticket"""
    try:
        # Verificar que el archivo existe
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'warning')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
        archivo = request.files['archivo']
        
        if archivo.filename == '':
            flash('No se seleccionó ningún archivo', 'warning')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
        # Validar extensión
        if not allowed_file(archivo.filename):
            flash('Tipo de archivo no permitido. Solo: PDF, imágenes, Word, Excel, TXT, ZIP', 'danger')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
        # Validar tamaño
        archivo.seek(0, os.SEEK_END)
        file_length = archivo.tell()
        if file_length > MAX_FILE_SIZE:
            flash('El archivo es demasiado grande. Máximo 10 MB', 'danger')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        archivo.seek(0)
        
        # Generar nombre único
        nombre_original = secure_filename(archivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = nombre_original.rsplit('.', 1)[1].lower()
        nombre_archivo = f"ticket_{id_ticket}_{timestamp}.{extension}"
        
        # Crear directorio si no existe
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'tickets')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Guardar archivo
        ruta_completa = os.path.join(upload_folder, nombre_archivo)
        archivo.save(ruta_completa)
        
        # Ruta relativa para guardar en BD
        ruta_relativa = f'/static/uploads/tickets/{nombre_archivo}'
        
        # Calcular tamaño en KB
        tamano_kb = round(file_length / 1024, 2)
        
        # Guardar en BD
        db.session.execute(text("""
            INSERT INTO AdjuntosTicket (
                IdTicket, IdUsuario, NombreArchivo, NombreOriginal, 
                RutaArchivo, TipoMIME, TamanoKB
            ) VALUES (
                :ticket, :usuario, :nombre, :original, :ruta, :mime, :tamano
            )
        """), {
            'ticket': id_ticket,
            'usuario': current_user.id,
            'nombre': nombre_archivo,
            'original': nombre_original,
            'ruta': ruta_relativa,
            'mime': archivo.content_type,
            'tamano': tamano_kb
        })
        
        db.session.commit()
        
        flash(f'Archivo "{nombre_original}" subido correctamente', 'success')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al subir adjunto: {str(e)}')
        flash('Error al subir el archivo', 'danger')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
    
@ticketing_bp.route('/ticket/<int:id_ticket>/cambiar-estado', methods=['POST'])
@login_required
@requiere_permiso('Ticketing', 'editar')
def cambiar_estado(id_ticket):
    """Cambiar el estado de un ticket"""
    try:
        nuevo_estado = request.form.get('nuevo_estado')
        
        if not nuevo_estado:
            flash('Debes seleccionar un estado', 'warning')
            return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
        # Actualizar estado
        db.session.execute(text("""
            UPDATE Tickets 
            SET IdEstado = :estado
            WHERE IdTicket = :ticket
        """), {
            'estado': nuevo_estado,
            'ticket': id_ticket
        })
        
        db.session.commit()
        
        flash('Estado actualizado correctamente', 'success')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al cambiar estado: {str(e)}')
        flash('Error al cambiar el estado', 'danger')
        return redirect(url_for('ticketing.detalle_ticket', id_ticket=id_ticket))
    
@ticketing_bp.route('/mis-asignados')
@login_required
@requiere_permiso('Ticketing', 'ver')  # ← SOLO NECESITA VER
def mis_tickets_asignados():
    """Ver tickets asignados al técnico actual (solo para técnicos, no admins)"""
    try:
        # Verificar si es admin TI (tiene permiso de eliminar) o técnico normal
        es_admin_ti = tiene_permiso('Ticketing', 'eliminar')
        
        if es_admin_ti:
            # Admin TI ve todos los tickets en el dashboard
            return redirect(url_for('ticketing.dashboard_ti'))
        
        # Técnico normal: ver solo tickets asignados a él
        tickets_query = text("""
            SELECT * FROM v_tickets_completo
            WHERE IdAsignadoA = :tecnico_id
            ORDER BY 
                CASE IdEstado
                    WHEN 1 THEN 1  -- Abierto
                    WHEN 2 THEN 2  -- En Proceso
                    WHEN 3 THEN 3  -- Escalado
                    WHEN 4 THEN 4  -- Pendiente
                    WHEN 5 THEN 5  -- Resuelto
                    WHEN 6 THEN 6  -- Sin Solución
                    WHEN 7 THEN 7  -- Cerrado
                END,
                FechaCreacion DESC
        """)
        
        result = db.session.execute(
            tickets_query,
            {'tecnico_id': current_user.id}
        ).fetchall()
        
        # Convertir a diccionarios
        tickets = []
        if result:
            cols = result[0]._mapping.keys()
            for row in result:
                tickets.append(dict(zip(cols, row)))
        
        # Contar por estado
        total_tickets = len(tickets)
        abiertos = len([t for t in tickets if t['IdEstado'] == 1])
        en_proceso = len([t for t in tickets if t['IdEstado'] == 2])
        escalados = len([t for t in tickets if t['IdEstado'] == 3])
        resueltos = len([t for t in tickets if t['IdEstado'] == 5])
        
        return render_template(
            'ticketing/mis_asignados.html',
            tickets=tickets,
            total_tickets=total_tickets,
            abiertos=abiertos,
            en_proceso=en_proceso,
            escalados=escalados,
            resueltos=resueltos
        )
        
    except Exception as e:
        current_app.logger.error(f'Error en mis_tickets_asignados: {str(e)}')
        flash('Error al cargar los tickets', 'danger')
        return redirect(url_for('ticketing.index'))
    

@ticketing_bp.route('/dashboard/estadisticas')
@login_required
@requiere_permiso('Ticketing', 'ver')
def dashboard_estadisticas():
    """
    Retorna estadísticas en formato JSON para las gráficas del dashboard TI
    """
    try:
        # ═══════════════════════════════════════════════════════
        # 1. TICKETS POR DEPARTAMENTO
        # ═══════════════════════════════════════════════════════
        tickets_por_depto_raw = db.session.execute(text("""
    SELECT 
        d.nombre as NombreDepartamento,
        COUNT(t.IdTicket) as total
    FROM Tickets t
    INNER JOIN usuario u ON t.IdUsuarioCreador = u.IdUsuario
    INNER JOIN departamentos d ON u.IdDepartamento = d.id
    GROUP BY d.nombre
    ORDER BY total DESC
    LIMIT 10
""")).fetchall()
        
        departamentos = [row[0] for row in tickets_por_depto_raw]
        cantidades_depto = [row[1] for row in tickets_por_depto_raw]
        
        # ═══════════════════════════════════════════════════════
        # 2. TICKETS POR MES (últimos 6 meses)
        # ═══════════════════════════════════════════════════════
        tickets_por_mes_raw = db.session.execute(text("""
            SELECT 
                DATE_FORMAT(FechaCreacion, '%Y-%m') as mes,
                COUNT(IdTicket) as total
            FROM Tickets
            WHERE FechaCreacion >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(FechaCreacion, '%Y-%m')
            ORDER BY mes ASC
        """)).fetchall()
        
        meses = [row[0] for row in tickets_por_mes_raw]
        cantidades_mes = [row[1] for row in tickets_por_mes_raw]
        
        # ═══════════════════════════════════════════════════════
        # 3. TIPOS DE PROBLEMA
        # ═══════════════════════════════════════════════════════
        tipos_problema_raw = db.session.execute(text("""
            SELECT 
                c.Nombre,
                COUNT(t.IdTicket) as total
            FROM Tickets t
            INNER JOIN CategoriasTicket c ON t.IdCategoria = c.IdCategoria
            GROUP BY c.Nombre
            ORDER BY total DESC
            LIMIT 8
        """)).fetchall()
        
        categorias = [row[0] for row in tipos_problema_raw]
        cantidades_cat = [row[1] for row in tipos_problema_raw]
        
        # ═══════════════════════════════════════════════════════
        # 4. TIEMPO PROMEDIO DE RESOLUCIÓN POR DEPARTAMENTO
        # ═══════════════════════════════════════════════════════
        tiempo_resolucion_raw = db.session.execute(text("""
    SELECT 
        d.nombre as NombreDepartamento,
        ROUND(AVG(TIMESTAMPDIFF(HOUR, t.FechaCreacion, t.FechaCierre)), 1) as horas_promedio
    FROM Tickets t
    INNER JOIN usuario u ON t.IdUsuarioCreador = u.IdUsuario
    INNER JOIN departamentos d ON u.IdDepartamento = d.id
    WHERE t.FechaCierre IS NOT NULL
    GROUP BY d.nombre
    ORDER BY horas_promedio ASC
    LIMIT 10
""")).fetchall()
        
        deptos_tiempo = [row[0] for row in tiempo_resolucion_raw]
        horas_promedio = [float(row[1]) if row[1] else 0 for row in tiempo_resolucion_raw]
        
        # ═══════════════════════════════════════════════════════
        # RETORNAR JSON
        # ═══════════════════════════════════════════════════════
        return jsonify({
            'tickets_por_departamento': {
                'labels': departamentos,
                'data': cantidades_depto
            },
            'tickets_por_mes': {
                'labels': meses,
                'data': cantidades_mes
            },
            'tipos_problema': {
                'labels': categorias,
                'data': cantidades_cat
            },
            'tiempo_resolucion': {
                'labels': deptos_tiempo,
                'data': horas_promedio
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error en dashboard_estadisticas: {str(e)}')
        return jsonify({
            'tickets_por_departamento': {'labels': [], 'data': []},
            'tickets_por_mes': {'labels': [], 'data': []},
            'tipos_problema': {'labels': [], 'data': []},
            'tiempo_resolucion': {'labels': [], 'data': []}
        }), 500
        
        
