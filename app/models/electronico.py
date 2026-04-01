from ..extensions import db
from datetime import datetime


class Electronico(db.Model):
    __tablename__ = "Electronico"

    IdElectronico    = db.Column(db.Integer, primary_key=True)
    Nombre           = db.Column(db.String(100), nullable=False)
    Marca            = db.Column(db.String(100))
    Modelo           = db.Column(db.String(100))
    NumeroSerie      = db.Column(db.String(100), unique=True)
    TipoEquipo       = db.Column(db.String(30), nullable=False, default="otro")
    Estado           = db.Column(db.String(20), nullable=False, default="almacen")
    Condicion        = db.Column(db.String(20), nullable=False, default="bueno")
    IdUsuario        = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"),     nullable=True)
    IdUbicacion      = db.Column(db.Integer, db.ForeignKey("Ubicacion.IdUbicacion"), nullable=True)
    FechaAdquisicion = db.Column(db.Date)
    Costo            = db.Column(db.Float, default=0)
    Descripcion      = db.Column(db.Text)
    CreadoEn         = db.Column(db.DateTime, default=datetime.utcnow)
    ActualizadoEn    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario      = db.relationship("Usuario",    foreign_keys=[IdUsuario],   backref="equipos_asignados")
    ubicacion    = db.relationship("Ubicacion",  foreign_keys=[IdUbicacion], backref="equipos")
    mantenimientos = db.relationship("MantenimientoElectronico", backref="equipo", lazy="dynamic")

    TIPOS = {
        "laptop":  "💻 Laptop",
        "desktop": "🖥️ Desktop",
        "monitor": "🖵 Monitor",
        "red":     "🌐 Red",
        "otro":    "📦 Otro",
    }

    ESTADOS = {
        "almacen":      "En almacén",
        "asignado":     "Asignado",
        "mantenimiento":"Mantenimiento",
        "baja":         "Baja",
        "mal_estado":   "Mal estado",
    }

    @property
    def tipo_label(self):
        return self.TIPOS.get(self.TipoEquipo, self.TipoEquipo)

    @property
    def estado_label(self):
        return self.ESTADOS.get(self.Estado, self.Estado)

    def to_dict(self):
        return {
            "id":           self.IdElectronico,
            "nombre":       self.Nombre,
            "marca":        self.Marca,
            "modelo":       self.Modelo,
            "numero_serie": self.NumeroSerie,
            "tipo_equipo":  self.TipoEquipo,
            "estado":       self.Estado,
            "condicion":    self.Condicion,
            "costo":        self.Costo,
            "fecha_adquisicion": str(self.FechaAdquisicion) if self.FechaAdquisicion else None,
            "descripcion":  self.Descripcion,
            "usuario_id":   self.IdUsuario,
        }

    def __repr__(self):
        return f"<Electronico {self.Nombre} [{self.Estado}]>"


class MantenimientoElectronico(db.Model):
    __tablename__ = "MantenimientoElectronico"

    IdMantenimiento = db.Column(db.Integer, primary_key=True)
    IdElectronico   = db.Column(db.Integer, db.ForeignKey("Electronico.IdElectronico"), nullable=False)
    Tipo            = db.Column(db.String(20), nullable=False)   # previo | correctivo
    Diagnostico     = db.Column(db.Text)
    Descripcion     = db.Column(db.Text)
    FechaInicio     = db.Column(db.Date, nullable=False)
    FechaTermino    = db.Column(db.Date)
    Costo           = db.Column(db.Float, default=0)
    Tecnico         = db.Column(db.String(120))
    Estatus         = db.Column(db.String(20), nullable=False, default="en_proceso")
    CreadoPor       = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn        = db.Column(db.DateTime, default=datetime.utcnow)

    creado_por = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="mantenimientos_elec")

    def to_dict(self):
        return {
            "id":           self.IdMantenimiento,
            "equipo_id":    self.IdElectronico,
            "tipo":         self.Tipo,
            "diagnostico":  self.Diagnostico,
            "descripcion":  self.Descripcion,
            "fecha_inicio": str(self.FechaInicio) if self.FechaInicio else None,
            "fecha_termino": str(self.FechaTermino) if self.FechaTermino else None,
            "costo":        self.Costo,
            "tecnico":      self.Tecnico,
            "estatus":      self.Estatus,
        }