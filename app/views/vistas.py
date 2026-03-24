"""
app/views/vistas.py
Modelos de solo lectura mapeados a las vistas de MySQL.
Las vistas no se pueden modificar directamente — son para consultas.
"""
from ..extensions import db
from datetime import datetime


class VActivo(db.Model):
    """
    Mapeado a la vista v_activos.
    Incluye nombre de departamento y responsable resueltos.
    """
    __tablename__ = "v_activos"

    id                  = db.Column(db.Integer,  primary_key=True)
    nombre              = db.Column(db.String(120))
    descripcion         = db.Column(db.Text)
    numero_serie        = db.Column(db.String(100))
    categoria           = db.Column(db.String(50))
    estado              = db.Column(db.String(20))
    valor               = db.Column(db.Float)
    fecha_adquisicion   = db.Column(db.Date)
    creado_en           = db.Column(db.DateTime)
    actualizado_en      = db.Column(db.DateTime)
    departamento_id     = db.Column(db.Integer)
    departamento_nombre = db.Column(db.String(100))
    usuario_id          = db.Column(db.Integer)
    responsable_nombre  = db.Column(db.String(120))
    responsable_email   = db.Column(db.String(120))

    # Vista es de solo lectura
    __table_args__ = {"info": {"is_view": True}}

    def to_dict(self):
        return {
            "id":                 self.id,
            "nombre":             self.nombre,
            "descripcion":        self.descripcion,
            "numero_serie":       self.numero_serie,
            "categoria":          self.categoria,
            "estado":             self.estado,
            "valor":              self.valor,
            "fecha_adquisicion":  str(self.fecha_adquisicion) if self.fecha_adquisicion else None,
            "departamento_id":    self.departamento_id,
            "departamento":       self.departamento_nombre,
            "responsable":        self.responsable_nombre,
            "responsable_email":  self.responsable_email,
        }


class VDepartamento(db.Model):
    """
    Mapeado a v_departamentos.
    Incluye conteo de activos y valor total.
    """
    __tablename__ = "v_departamentos"

    id            = db.Column(db.Integer,  primary_key=True)
    nombre        = db.Column(db.String(100))
    descripcion   = db.Column(db.String(255))
    creado_en     = db.Column(db.DateTime)
    total_activos = db.Column(db.Integer)
    valor_total   = db.Column(db.Float)

    __table_args__ = {"info": {"is_view": True}}


class VActivoPorDepartamento(db.Model):
    """
    Mapeado a v_activos_por_departamento.
    Resumen agrupado por departamento.
    """
    __tablename__ = "v_activos_por_departamento"

    departamento_id   = db.Column(db.Integer, primary_key=True)
    departamento      = db.Column(db.String(100))
    total_activos     = db.Column(db.Integer)
    activos           = db.Column(db.Integer)
    bajas             = db.Column(db.Integer)
    en_mantenimiento  = db.Column(db.Integer)
    valor_total       = db.Column(db.Float)

    __table_args__ = {"info": {"is_view": True}}


class VDashboardStats(db.Model):
    """
    Mapeado a v_dashboard_stats.
    Una sola fila con estadísticas globales.
    """
    __tablename__ = "v_dashboard_stats"

    # La vista no tiene PK natural — usamos un literal
    total_activos            = db.Column(db.Integer,  primary_key=True)
    activos                  = db.Column(db.Integer)
    bajas                    = db.Column(db.Integer)
    en_mantenimiento         = db.Column(db.Integer)
    valor_total              = db.Column(db.Float)
    valor_promedio           = db.Column(db.Float)
    departamentos_con_activos = db.Column(db.Integer)

    __table_args__ = {"info": {"is_view": True}}


class VUsuario(db.Model):
    """
    Mapeado a v_usuarios.
    Sin password_hash — seguro para exponer en consultas.
    """
    __tablename__ = "v_usuarios"

    id        = db.Column(db.Integer,  primary_key=True)
    username  = db.Column(db.String(64))
    email     = db.Column(db.String(120))
    nombre    = db.Column(db.String(120))
    rol       = db.Column(db.String(20))
    activo    = db.Column(db.Boolean)
    creado_en = db.Column(db.DateTime)

    __table_args__ = {"info": {"is_view": True}}