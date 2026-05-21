# app/models/proyecto.py
from ..extensions import db
from datetime import date


class Proyecto(db.Model):
    __tablename__ = "Proyecto"
    IdProyecto    = db.Column(db.Integer, primary_key=True)
    Nombre        = db.Column(db.String(120), nullable=False)
    Descripcion   = db.Column(db.Text)
    FechaInicio   = db.Column(db.Date, nullable=False)
    FechaTermino  = db.Column(db.Date, nullable=False)
    Estatus       = db.Column(db.Enum('Activo','En progreso','Pausado','Completado','Cancelado'),
                              nullable=False, default='Activo')
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"), nullable=False)
    CreadoEn      = db.Column(db.DateTime, server_default=db.func.now())
    ActualizadoEn = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    creador   = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="proyectos_creados")
    personal  = db.relationship("ProyectoPersonal", backref="proyecto", lazy="dynamic", cascade="all, delete")
    activos   = db.relationship("ProyectoActivo",   backref="proyecto", lazy="dynamic", cascade="all, delete")
    auditoria = db.relationship("ProyectoAuditoria",backref="proyecto", lazy="dynamic", cascade="all, delete")

    @property
    def dias_restantes(self):
        if self.FechaTermino:
            return (self.FechaTermino - date.today()).days
        return None

    @property
    def color_estatus(self):
        return {
            'Activo':       '#16a34a',
            'En progreso':  '#2563eb',
            'Pausado':      '#d97706',
            'Completado':   '#6366f1',
            'Cancelado':    '#dc2626',
        }.get(self.Estatus, '#94a3b8')

    @property
    def bg_estatus(self):
        return {
            'Activo':       '#dcfce7',
            'En progreso':  '#dbeafe',
            'Pausado':      '#fef3c7',
            'Completado':   '#eef2ff',
            'Cancelado':    '#fee2e2',
        }.get(self.Estatus, '#f1f5f9')


class ProyectoPersonal(db.Model):
    __tablename__ = "ProyectoPersonal"
    IdAsignacion    = db.Column(db.Integer, primary_key=True)
    IdProyecto      = db.Column(db.Integer, db.ForeignKey("Proyecto.IdProyecto"), nullable=False)
    IdUsuario       = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"),   nullable=False)
    Rol             = db.Column(db.String(80))
    FechaAsignacion = db.Column(db.Date, nullable=False)
    AsignadoPor     = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"),   nullable=False)
    CreadoEn        = db.Column(db.DateTime, server_default=db.func.now())

    usuario      = db.relationship("Usuario", foreign_keys=[IdUsuario])
    asignado_por = db.relationship("Usuario", foreign_keys=[AsignadoPor])


class ProyectoActivo(db.Model):
    __tablename__ = "ProyectoActivo"
    IdAsignacion    = db.Column(db.Integer, primary_key=True)
    IdProyecto      = db.Column(db.Integer, db.ForeignKey("Proyecto.IdProyecto"), nullable=False)
    TipoActivo      = db.Column(db.Enum('electronico','vehiculo','herramienta'),  nullable=False)
    IdActivo        = db.Column(db.Integer, nullable=False)
    EstadoInicial   = db.Column(db.String(50))
    EstadoFinal     = db.Column(db.String(50))
    AsignadoPor     = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"),   nullable=False)
    FechaAsignacion = db.Column(db.Date, nullable=False)
    FechaDevolucion = db.Column(db.Date)
    Observaciones   = db.Column(db.Text)
    CreadoEn        = db.Column(db.DateTime, server_default=db.func.now())

    asignado_por = db.relationship("Usuario", foreign_keys=[AsignadoPor])


class ProyectoAuditoria(db.Model):
    __tablename__ = "ProyectoAuditoria"
    IdAuditoria  = db.Column(db.Integer, primary_key=True)
    IdProyecto   = db.Column(db.Integer, db.ForeignKey("Proyecto.IdProyecto"), nullable=False)
    Accion       = db.Column(db.String(50), nullable=False)
    Detalle      = db.Column(db.Text)
    RazonCambio  = db.Column(db.String(255))
    RealizadoPor = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"),   nullable=False)
    RealizadoEn  = db.Column(db.DateTime, server_default=db.func.now())

    usuario = db.relationship("Usuario", foreign_keys=[RealizadoPor])

    @property
    def icono_accion(self):
        return {
            'crear':            '✨',
            'editar':           '✏️',
            'cambio_estatus':   '🔄',
            'asignar_personal': '👤',
            'asignar_activo':   '📦',
        }.get(self.Accion, '📝')
