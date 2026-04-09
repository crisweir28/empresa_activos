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
    TipoHerramienta = db.Column(db.String(100), nullable=True)
    IdCategoria    = db.Column(db.Integer, nullable=True)
    IdUbicacion    = db.Column(db.Integer, nullable=True)
    IdDepartamento = db.Column(db.Integer, nullable=True)
    Subarea         = db.Column(db.String(100), nullable=True)
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


class AsignacionHerramienta(db.Model):
    __tablename__ = "AsignacionHerramienta"

    IdAsignacion    = db.Column(db.Integer, primary_key=True)
    IdHerramienta   = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    IdUsuario       = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"),          nullable=False)
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
    ArchivoUrl    = db.Column(db.String(500), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    Tipo          = db.Column(db.String(20),  nullable=False, default="daño")
    TipoArchivo   = db.Column(db.Enum("imagen", "documento"), nullable=False, default="imagen")
    MimeType      = db.Column(db.String(100))
    Descripcion   = db.Column(db.String(255))
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn      = db.Column(db.DateTime, default=datetime.utcnow)

    creado_por = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="evidencias_subidas")

    @property
    def es_imagen(self):
        return self.TipoArchivo == "imagen"

    @property
    def icono(self):
        if self.MimeType == "application/pdf":
            return "📄"
        if "word" in (self.MimeType or ""):
            return "📝"
        if "excel" in (self.MimeType or "") or "spreadsheet" in (self.MimeType or ""):
            return "📊"
        if self.es_imagen:
            return "🖼️"
        return "📎"


class ReporteDanio(db.Model):
    __tablename__ = "ReporteDanio"

    IdReporte            = db.Column(db.Integer, primary_key=True)
    IdHerramienta        = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    NombreMaterial       = db.Column(db.String(150), nullable=False)
    Caracteristica       = db.Column(db.Text, nullable=False)
    Razon                = db.Column(db.Text, nullable=False)
    Tipo                 = db.Column(db.String(20), nullable=False, default="daño")
    # ── Archivo adjunto opcional ──────────────────────────────
    ArchivoUrl           = db.Column(db.String(500), nullable=True)
    NombreArchivo        = db.Column(db.String(255), nullable=True)
    TipoArchivo          = db.Column(db.Enum("imagen", "documento"), nullable=True)
    MimeType             = db.Column(db.String(100), nullable=True)
    # ─────────────────────────────────────────────────────────
    IdUsuarioResponsable = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoPor            = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn             = db.Column(db.DateTime, default=datetime.utcnow)

    responsable = db.relationship("Usuario", foreign_keys=[IdUsuarioResponsable], backref="reportes_responsable")
    creado_por  = db.relationship("Usuario", foreign_keys=[CreadoPor],            backref="reportes_creados")

    @property
    def tiene_archivo(self):
        return bool(self.ArchivoUrl)

    @property
    def icono(self):
        if not self.MimeType:
            return "📎"
        if self.MimeType == "application/pdf":
            return "📄"
        if "word" in self.MimeType:
            return "📝"
        if "excel" in self.MimeType or "spreadsheet" in self.MimeType:
            return "📊"
        if "image" in self.MimeType:
            return "🖼️"
        return "📎"

    def to_dict(self):
        return {
            "id":              self.IdReporte,
            "herramienta_id":  self.IdHerramienta,
            "nombre_material": self.NombreMaterial,
            "caracteristica":  self.Caracteristica,
            "razon":           self.Razon,
            "tipo":            self.Tipo,
            "archivo_url":     self.ArchivoUrl,
            "nombre_archivo":  self.NombreArchivo,
            "creado_en":       str(self.CreadoEn),
        }


class EvidenciaEquipo(db.Model):
    """Evidencias para equipos TI."""
    __tablename__ = "EvidenciaEquipo"

    IdEvidencia   = db.Column(db.Integer, primary_key=True)
    IdElectronico = db.Column(db.Integer, nullable=False)
    IdAsignacion  = db.Column(db.Integer, nullable=True)
    ArchivoUrl    = db.Column(db.String(500), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    Tipo          = db.Column(db.String(20),  nullable=False, default="entrega")
    TipoArchivo   = db.Column(db.Enum("imagen", "documento"), nullable=False, default="imagen")
    MimeType      = db.Column(db.String(100))
    Descripcion   = db.Column(db.String(255))
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoEn      = db.Column(db.DateTime, default=datetime.utcnow)

    creado_por_rel = db.relationship("Usuario", foreign_keys=[CreadoPor], backref="evidencias_equipo_subidas")

    @property
    def es_imagen(self):
        return self.TipoArchivo == "imagen"

    @property
    def icono(self):
        if self.MimeType == "application/pdf":
            return "📄"
        if "word" in (self.MimeType or ""):
            return "📝"
        if "excel" in (self.MimeType or "") or "spreadsheet" in (self.MimeType or ""):
            return "📊"
        if self.es_imagen:
            return "🖼️"
        return "📎"