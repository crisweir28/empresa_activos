# app/models/asignacion.py
from ..extensions import db
from datetime import datetime


class AsignacionEquipo(db.Model):
    """Historial de asignaciones de equipos electrónicos a usuarios"""
    
    __tablename__ = 'asignacion_equipo'
    
    IdAsignacion      = db.Column(db.Integer, primary_key=True)
    IdEquipo          = db.Column(db.Integer, nullable=False)  # ← SIN ForeignKey por ahora
    IdUsuario         = db.Column(db.Integer, nullable=False)  # ← SIN ForeignKey por ahora
    FechaAsignacion   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    FechaLiberacion   = db.Column(db.DateTime, nullable=True)
    AsignadoPor       = db.Column(db.Integer, nullable=True)
    
    # ✅ Relaciones LAZY con primaryjoin explícito
    usuario = db.relationship(
        'Usuario',
        primaryjoin='AsignacionEquipo.IdUsuario == Usuario.IdUsuario',
        foreign_keys='AsignacionEquipo.IdUsuario',
        lazy='joined'
    )
    
    def __repr__(self):
        return f'<AsignacionEquipo {self.IdEquipo} -> Usuario {self.IdUsuario}>'