# app/models/herramienta.py
from ..extensions import db
from datetime import datetime


class Herramienta(db.Model):
    __tablename__ = "Herramienta"

    IdHerramienta = db.Column(db.Integer, primary_key=True)
    Nombre        = db.Column(db.String(100), nullable=False)
    Marca         = db.Column(db.String(100))
    Modelo        = db.Column(db.String(100))
    NumeroSerie   = db.Column(db.String(100), unique=True)
    Estado        = db.Column(db.String(20), nullable=False, default="disponible")
    Costo         = db.Column(db.Float, default=0)
    FechaAlta     = db.Column(db.Date)
    Descripcion   = db.Column(db.Text)
    CreadoEn      = db.Column(db.DateTime, default=datetime.utcnow)
    ActualizadoEn = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asignaciones = db.relationship("AsignacionHerramienta", backref="herramienta", lazy="dynamic")
    evidencias   = db.relationship("EvidenciaHerramienta",  backref="herramienta", lazy="dynamic")
    reportes     = db.relationship("ReporteDanio",          backref="herramienta", lazy="dynamic")

    def to_dict(self):
        return {
            "id":           self.IdHerramienta,
            "nombre":       self.Nombre,
            "marca":        self.Marca,
            "modelo":       self.Modelo,
            "numero_serie": self.NumeroSerie,
            "estado":       self.Estado,
            "costo":        self.Costo,
            "fecha_alta":   str(self.FechaAlta) if self.FechaAlta else None,
            "descripcion":  self.Descripcion,
        }

    def __repr__(self):
        return f"<Herramienta {self.Nombre} [{self.Estado}]>"


class AsignacionHerramienta(db.Model):
    __tablename__ = "AsignacionHerramienta"

    IdAsignacion    = db.Column(db.Integer, primary_key=True)
    IdHerramienta   = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    IdUsuario       = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"),         nullable=False)
    FechaAsignacion = db.Column(db.Date, nullable=False)
    FechaDevolucion = db.Column(db.Date)
    AsignadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    RecibidoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    Observaciones   = db.Column(db.Text)
    CreadoEn        = db.Column(db.DateTime, default=datetime.utcnow)

    usuario      = db.relationship("Usuario", foreign_keys=[IdUsuario],   backref="herramientas_asignadas")
    asignado_por = db.relationship("Usuario", foreign_keys=[AsignadoPor], backref="asignaciones_hechas")
    recibido_por = db.relationship("Usuario", foreign_keys=[RecibidoPor], backref="devoluciones_recibidas")


class EvidenciaHerramienta(db.Model):
    __tablename__ = "EvidenciaHerramienta"

    IdEvidencia   = db.Column(db.Integer, primary_key=True)
    IdHerramienta = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    ArchivoUrl    = db.Column(db.String(255), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    Tipo          = db.Column(db.String(20), nullable=False, default="daño")
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn      = db.Column(db.DateTime, default=datetime.utcnow)

    creado_por = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="evidencias_subidas")


class ReporteDanio(db.Model):
    __tablename__ = "ReporteDanio"

    IdReporte            = db.Column(db.Integer, primary_key=True)
    IdHerramienta        = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    NombreMaterial       = db.Column(db.String(150), nullable=False)
    Caracteristica       = db.Column(db.Text, nullable=False)
    Razon                = db.Column(db.Text, nullable=False)
    Tipo                 = db.Column(db.String(20), nullable=False, default="daño")
    IdUsuarioResponsable = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoPor            = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn             = db.Column(db.DateTime, default=datetime.utcnow)

    responsable = db.relationship("Usuario", foreign_keys=[IdUsuarioResponsable], backref="reportes_responsable")
    creado_por  = db.relationship("Usuario", foreign_keys=[CreadoPor],            backref="reportes_creados")

    def to_dict(self):
        return {
            "id":             self.IdReporte,
            "herramienta_id": self.IdHerramienta,
            "nombre_material": self.NombreMaterial,
            "caracteristica": self.Caracteristica,
            "razon":          self.Razon,
            "tipo":           self.Tipo,
            "creado_en":      str(self.CreadoEn),
        }