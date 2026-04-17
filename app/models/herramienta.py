# app/models/herramienta.py
from ..extensions import db
from datetime import datetime

# ── Mixins ────────────────────────────────────────────────────
class TimestampMixin:
    """Agrega CreadoEn a cualquier modelo."""
    CreadoEn = db.Column(db.DateTime, default=datetime.utcnow)

class ArchivoAdjuntoMixin:
    """Campos y helpers para modelos con archivo adjunto."""
    ArchivoUrl    = db.Column(db.String(500))
    NombreArchivo = db.Column(db.String(255))
    TipoArchivo   = db.Column(db.Enum("imagen", "documento"))
    MimeType      = db.Column(db.String(100))

    @property
    def tiene_archivo(self):
        return bool(self.ArchivoUrl)

    @property
    def icono(self):
        mime = self.MimeType or ""
        if mime == "application/pdf":             return "📄"
        if "word" in mime:                        return "📝"
        if "excel" in mime or "spreadsheet" in mime: return "📊"
        if "image" in mime or self.TipoArchivo == "imagen": return "🖼️"
        return "📎"

# ── Modelos ───────────────────────────────────────────────────
class Herramienta(TimestampMixin, db.Model):
    __tablename__ = "Herramienta"

    IdHerramienta   = db.Column(db.Integer, primary_key=True)
    Nombre          = db.Column(db.String(100), nullable=False)
    Marca           = db.Column(db.String(100))
    Modelo          = db.Column(db.String(100))
    NumeroSerie     = db.Column(db.String(100), unique=True)
    Estado          = db.Column(db.String(20), nullable=False, default="disponible")
    Costo           = db.Column(db.Float, default=0)
    FechaAlta       = db.Column(db.Date)
    Descripcion     = db.Column(db.Text)
    ActualizadoEn   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Campos consumidos por las vistas SQL (VInventario / VHistorialAsignaciones)
    TipoHerramienta = db.Column(db.String(100))
    IdCategoria     = db.Column(db.Integer)
    IdUbicacion     = db.Column(db.Integer)
    IdDepartamento  = db.Column(db.Integer)
    Subarea         = db.Column(db.String(100))

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

class AsignacionHerramienta(TimestampMixin, db.Model):
    __tablename__ = "AsignacionHerramienta"

    IdAsignacion    = db.Column(db.Integer, primary_key=True)
    IdHerramienta   = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    IdUsuario       = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"),          nullable=False)
    FechaAsignacion = db.Column(db.Date, nullable=False)
    FechaDevolucion = db.Column(db.Date)
    AsignadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    RecibidoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    Observaciones   = db.Column(db.Text)

    usuario = db.relationship("Usuario", foreign_keys=[IdUsuario], backref="herramientas_asignadas")


class EvidenciaHerramienta(TimestampMixin, db.Model):
    __tablename__ = "EvidenciaHerramienta"

    IdEvidencia   = db.Column(db.Integer, primary_key=True)
    IdHerramienta = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    ArchivoUrl    = db.Column(db.String(500), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    Tipo          = db.Column(db.String(20), nullable=False, default="daño")
    TipoArchivo   = db.Column(db.Enum("imagen", "documento"), nullable=False, default="imagen")
    MimeType      = db.Column(db.String(100))
    Descripcion   = db.Column(db.String(255))
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))

class ReporteDanio(ArchivoAdjuntoMixin, TimestampMixin, db.Model):
    __tablename__ = "ReporteDanio"

    IdReporte            = db.Column(db.Integer, primary_key=True)
    IdHerramienta        = db.Column(db.Integer, db.ForeignKey("Herramienta.IdHerramienta"), nullable=False)
    NombreMaterial       = db.Column(db.String(150), nullable=False)
    Caracteristica       = db.Column(db.Text, nullable=False)
    Razon                = db.Column(db.Text, nullable=False)
    Tipo                 = db.Column(db.String(20), nullable=False, default="daño")
    IdUsuarioResponsable = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))
    CreadoPor            = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))


class EvidenciaEquipo(TimestampMixin, db.Model):
    """Evidencias para equipos TI."""
    __tablename__ = "EvidenciaEquipo"

    IdEvidencia   = db.Column(db.Integer, primary_key=True)
    IdElectronico = db.Column(db.Integer, nullable=False)
    IdAsignacion  = db.Column(db.Integer)
    ArchivoUrl    = db.Column(db.String(500), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    Tipo          = db.Column(db.String(20), nullable=False, default="entrega")
    TipoArchivo   = db.Column(db.Enum("imagen", "documento"), nullable=False, default="imagen")
    MimeType      = db.Column(db.String(100))
    Descripcion   = db.Column(db.String(255))
    CreadoPor     = db.Column(db.Integer, db.ForeignKey("Usuario.IdUsuario"))

    @property
    def es_imagen(self):
        return self.TipoArchivo == "imagen"

    @property
    def icono(self):
        mime = self.MimeType or ""
        if mime == "application/pdf":             return "📄"
        if "word" in mime:                        return "📝"
        if "excel" in mime or "spreadsheet" in mime: return "📊"
        if self.es_imagen:                        return "🖼️"
        return "📎"