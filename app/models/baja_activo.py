# app/models/baja_activo.py
from ..extensions import db
from datetime import datetime
import pytz
TIMEZONE = pytz.timezone('America/Mexico_City')

class BajaActivo(db.Model):
    __tablename__ = "BajaActivo"

    IdBaja        = db.Column(db.Integer, primary_key=True)
    TipoActivo    = db.Column(db.Enum('herramienta', 'electronico', 'vehiculo'), nullable=False)
    IdActivo      = db.Column(db.Integer, nullable=False)
    NombreActivo  = db.Column(db.String(150), nullable=False)
    DadoDeBajaPor = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"), nullable=True)
    FechaBaja = db.Column(db.DateTime, default=lambda: datetime.now(TIMEZONE).replace(tzinfo=None))

    dado_de_baja_por = db.relationship("Usuario", foreign_keys=[DadoDeBajaPor], backref="bajas_registradas")
