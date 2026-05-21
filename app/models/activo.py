# app/models/activo.py
from ..extensions import db
from datetime import datetime


class Activo(db.Model):
    __tablename__ = "activos"

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(120), nullable=False)
    descripcion     = db.Column(db.Text)
    numero_serie    = db.Column(db.String(100), unique=True)
    categoria       = db.Column(db.String(50))   # equipo, mueble, vehiculo, etc.
    estado          = db.Column(db.String(20), default="activo")  # activo | baja | mantenimiento
    valor           = db.Column(db.Float, default=0.0)
    fecha_adquisicion = db.Column(db.Date)
    creado_en       = db.Column(db.DateTime, default=datetime.now)
    actualizado_en  = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    estatus = db.Column(db.String(20), default="comprado")  # comprado | rentado

    # ✅ Foreign Keys corregidos
    departamento_id = db.Column(db.Integer, db.ForeignKey("departamentos.id"), nullable=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"), nullable=True)

    # ✅ Relationships explícitos (OPCIONAL, solo si no están en Departamento/Usuario)
    # departamento = db.relationship('Departamento', foreign_keys=[departamento_id])
    # responsable = db.relationship('Usuario', foreign_keys=[usuario_id])

    def to_dict(self):
        return {
            "id":             self.id,
            "nombre":         self.nombre,
            "descripcion":    self.descripcion,
            "numero_serie":   self.numero_serie,
            "categoria":      self.categoria,
            "estado":         self.estado,
            "valor":          self.valor,
            "departamento_id": self.departamento_id,
            "departamento":   self.departamento.nombre if self.departamento else None,
            "responsable":    self.responsable.nombre if self.responsable else None,
            "fecha_adquisicion": str(self.fecha_adquisicion) if self.fecha_adquisicion else None,
        }

    def __repr__(self):
        return f"<Activo {self.nombre} [{self.estado}]>"

