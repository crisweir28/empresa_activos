# app/models/electronico.py
from ..extensions import db
from datetime import datetime


class Electronico(db.Model):
    __tablename__ = "Electronico"

    IdElectronico    = db.Column(db.Integer, primary_key=True)
    Nombre           = db.Column(db.String(100), nullable=False)
    Marca            = db.Column(db.String(100))
    Modelo           = db.Column(db.String(100))
    NumeroSerie      = db.Column(db.String(100), unique=True)
    TipoEquipo       = db.Column(db.String(30),  nullable=False, default="otro")
    Gama             = db.Column(db.String(20),  nullable=True)   # Baja | Media | Alta | Gamer
    Estado           = db.Column(db.String(20),  nullable=False, default="almacen")
    Condicion        = db.Column(db.String(20),  nullable=False, default="bueno")
    IdUsuario        = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"),     nullable=True)
    IdUbicacion      = db.Column(db.Integer, db.ForeignKey("Ubicacion.IdUbicacion"), nullable=True)
    FechaAdquisicion = db.Column(db.Date)
    Costo            = db.Column(db.Float, default=0)
    Descripcion      = db.Column(db.Text)
    # ── Campos técnicos ───────────────────────────────────────
    IMEI                  = db.Column(db.String(50),  nullable=True)
    Procesador            = db.Column(db.String(100), nullable=True)
    MemoriaRAM            = db.Column(db.String(50),  nullable=True)
    Almacenamiento        = db.Column(db.String(50),  nullable=True)
    SistemaOperativo      = db.Column(db.String(100), nullable=True)
    Garantia              = db.Column(db.Date,        nullable=True)
    Accesorios            = db.Column(db.String(255), nullable=True)
    Comentarios           = db.Column(db.Text,        nullable=True)
    Arrendamiento         = db.Column(db.Boolean,     nullable=False, default=False)
    FechaRenovacion       = db.Column(db.Date,        nullable=True)
    ProveedorArrendamiento = db.Column(db.String(150), nullable=True)
    # ─────────────────────────────────────────────────────────
    CreadoEn      = db.Column(db.DateTime, default=datetime.now)
    ActualizadoEn = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    usuario        = db.relationship("Usuario",   foreign_keys=[IdUsuario],   backref="equipos_asignados")
    ubicacion      = db.relationship("Ubicacion", foreign_keys=[IdUbicacion], backref="equipos")
    mantenimientos = db.relationship("MantenimientoElectronico", backref="equipo", lazy="dynamic")

    TIPOS = {
        "laptop":   "💻 Laptop",
        "desktop":  "🖥️ Desktop",
        "monitor":  "🖵 Monitor",
        "celular":  "📱 Celular",
        "red":      "🌐 Red",
        "otro":     "📦 Otro",
    }

    ESTADOS = {
        "almacen":       "En almacén",
        "asignado":      "Asignado",
        "mantenimiento": "Mantenimiento",
        "baja":          "Baja",
        "mal_estado":    "Mal estado",
    }

    GAMAS = ["Baja", "Media", "Alta", "Gamer"]

    @property
    def tipo_label(self):
        return self.TIPOS.get(self.TipoEquipo, self.TipoEquipo)

    @property
    def estado_label(self):
        return self.ESTADOS.get(self.Estado, self.Estado)

    @property
    def es_celular(self):
        return self.TipoEquipo == "celular"

    @property
    def es_monitor(self):
        return self.TipoEquipo == "monitor"

    def to_dict(self):
        return {
            "id":                    self.IdElectronico,
            "nombre":                self.Nombre,
            "marca":                 self.Marca,
            "modelo":                self.Modelo,
            "numero_serie":          self.NumeroSerie,
            "tipo_equipo":           self.TipoEquipo,
            "gama":                  self.Gama,
            "estado":                self.Estado,
            "condicion":             self.Condicion,
            "costo":                 self.Costo,
            "fecha_adquisicion":     str(self.FechaAdquisicion) if self.FechaAdquisicion else None,
            "descripcion":           self.Descripcion,
            "imei":                  self.IMEI,
            "procesador":            self.Procesador,
            "memoria_ram":           self.MemoriaRAM,
            "almacenamiento":        self.Almacenamiento,
            "sistema_operativo":     self.SistemaOperativo,
            "garantia":              str(self.Garantia) if self.Garantia else None,
            "accesorios":            self.Accesorios,
            "comentarios":           self.Comentarios,
            "arrendamiento":         self.Arrendamiento,
            "fecha_renovacion":      str(self.FechaRenovacion) if self.FechaRenovacion else None,
            "proveedor_arrendamiento": self.ProveedorArrendamiento,
            "usuario_id":            self.IdUsuario,
        }

    def __repr__(self):
        return f"<Electronico {self.Nombre} [{self.Estado}]>"


class MantenimientoElectronico(db.Model):
    __tablename__ = "MantenimientoElectronico"

    IdMantenimiento = db.Column(db.Integer, primary_key=True)
    IdElectronico   = db.Column(db.Integer, db.ForeignKey("Electronico.IdElectronico"), nullable=False)
    Tipo            = db.Column(db.String(20), nullable=False)
    Diagnostico     = db.Column(db.Text)
    Descripcion     = db.Column(db.Text)
    FechaInicio     = db.Column(db.Date, nullable=False)
    FechaTermino    = db.Column(db.Date)
    Costo           = db.Column(db.Float, default=0)
    Tecnico         = db.Column(db.String(120))
    Estatus         = db.Column(db.String(20), nullable=False, default="en_proceso")
    CreadoPor       = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"))
    CreadoEn        = db.Column(db.DateTime, default=datetime.now)

    creado_por = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="mantenimientos_elec")

    def to_dict(self):
        return {
            "id":            self.IdMantenimiento,
            "equipo_id":     self.IdElectronico,
            "tipo":          self.Tipo,
            "diagnostico":   self.Diagnostico,
            "descripcion":   self.Descripcion,
            "fecha_inicio":  str(self.FechaInicio) if self.FechaInicio else None,
            "fecha_termino": str(self.FechaTermino) if self.FechaTermino else None,
            "costo":         self.Costo,
            "tecnico":       self.Tecnico,
            "estatus":       self.Estatus,
        }
