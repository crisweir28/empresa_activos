# app/models/departamento.py
from ..extensions import db
from datetime import datetime


class Departamento(db.Model):
    __tablename__ = "departamentos"

    id          = db.Column(db.Integer,    primary_key=True)
    nombre      = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    creado_en   = db.Column(db.DateTime,   default=datetime.utcnow)

    # Relación: un departamento tiene muchos activos
    activos     = db.relationship("Activo", backref="departamento", lazy="dynamic")

    def __repr__(self):
        return f"<Departamento {self.nombre}>"
