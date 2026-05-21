# app/models/departamento.py
from ..extensions import db
from datetime import datetime

class Departamento(db.Model):
    __tablename__ = "departamentos"

    # ✅ Nombre REAL de la columna en la BD
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    creado_en   = db.Column(db.DateTime, default=datetime.now)

    # ✅ Relación con foreign_keys explícito
    activos = db.relationship("Activo", 
                             foreign_keys="Activo.departamento_id",
                             backref="departamento", 
                             lazy="dynamic")

    def __repr__(self):
        return f"<Departamento {self.nombre}>"
