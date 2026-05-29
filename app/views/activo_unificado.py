# app/views/activo_unificado.py
# ════════════════════════════════════════════════════════════════
# Modelo que mapea la vista SQL v_activos_unificado
# Une activos generales, equipos TI, vehículos y herramientas
# ════════════════════════════════════════════════════════════════

from ..extensions import db


class VActivoUnificado(db.Model):
    """
    Vista de solo lectura que une las 4 tablas de activos:
      - activos       (muebles, software, otros)
      - electronico   (equipos TI)
      - vehiculo      (vehículos)
      - herramienta   (herramientas)
    """
    __tablename__ = 'v_activos_unificado'
    __table_args__ = {'info': {'is_view': True}}

    # ⚠️ Las vistas SQL no tienen primary key real.
    # SQLAlchemy requiere una clave primaria para mapear → usamos id_unico
    id_unico            = db.Column(db.String(20), primary_key=True)
    id_origen           = db.Column(db.Integer)
    origen              = db.Column(db.String(20))  # 'activos' | 'electronico' | 'vehiculo' | 'herramienta'

    nombre              = db.Column(db.String(150))
    numero_serie        = db.Column(db.String(100))
    descripcion         = db.Column(db.Text)
    categoria           = db.Column(db.String(50))  # 'equipo' | 'vehiculo' | 'herramienta' | etc.
    estado              = db.Column(db.String(20))  # 'activo' | 'baja' | 'mantenimiento'
    valor               = db.Column(db.Float)
    fecha_adquisicion   = db.Column(db.Date)

    departamento_id     = db.Column(db.Integer)
    departamento_nombre = db.Column(db.String(100))
    usuario_id          = db.Column(db.Integer)

    creado_en           = db.Column(db.DateTime)

    # ── Propiedades útiles para el template ────────────────────
    @property
    def id(self):
        """Alias para compatibilidad con templates viejos que usan a.id"""
        return self.id_origen

    @property
    def es_editable(self):
        """Solo los activos generales se editan desde este módulo"""
        return self.origen == 'activos'

    @property
    def url_modulo(self):
        """URL del módulo correspondiente para ver el detalle"""
        if self.origen == 'electronico':
            return f"/ti/equipos/{self.id_origen}"
        elif self.origen == 'vehiculo':
            return f"/administrativo/vehiculos/{self.id_origen}"
        elif self.origen == 'herramienta':
            return f"/almacenista/herramientas/{self.id_origen}"
        return None

    def __repr__(self):
        return f"<VActivoUnificado {self.id_unico} {self.nombre}>"