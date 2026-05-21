# app/models/permiso.py
from ..extensions import db


class Modulo(db.Model):
    __tablename__ = "Modulo"
    IdModulo    = db.Column(db.Integer, primary_key=True)
    Nombre      = db.Column(db.String(50), nullable=False)
    Descripcion = db.Column(db.String(150))
    Icono       = db.Column(db.String(10))
    Orden       = db.Column(db.Integer, default=0)

    permisos = db.relationship("PermisoRol", backref="modulo", lazy="dynamic")


class PermisoRol(db.Model):
    __tablename__ = "PermisoRol"
    IdPermiso     = db.Column(db.Integer, primary_key=True)
    IdRol         = db.Column(db.Integer, db.ForeignKey("Rol.IdRol"),       nullable=False)
    IdModulo      = db.Column(db.Integer, db.ForeignKey("Modulo.IdModulo"), nullable=False)
    PuedeVer      = db.Column(db.Boolean, nullable=False, default=False)
    PuedeCrear    = db.Column(db.Boolean, nullable=False, default=False)
    PuedeEditar   = db.Column(db.Boolean, nullable=False, default=False)
    PuedeEliminar = db.Column(db.Boolean, nullable=False, default=False)
    ActualizadoEn = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    rol = db.relationship("Rol", backref="permisos")

    def to_dict(self):
        return {
            "modulo_id":      self.IdModulo,
            "puede_ver":      self.PuedeVer,
            "puede_crear":    self.PuedeCrear,
            "puede_editar":   self.PuedeEditar,
            "puede_eliminar": self.PuedeEliminar,
        }


class PermisoUsuario(db.Model):
    __tablename__ = "PermisoUsuario"
    IdPermiso     = db.Column(db.Integer, primary_key=True)
    IdUsuario     = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"), nullable=False)
    IdModulo      = db.Column(db.Integer, db.ForeignKey("Modulo.IdModulo"),   nullable=False)
    PuedeVer      = db.Column(db.Boolean, nullable=False, default=False)
    PuedeCrear    = db.Column(db.Boolean, nullable=False, default=False)
    PuedeEditar   = db.Column(db.Boolean, nullable=False, default=False)
    PuedeEliminar = db.Column(db.Boolean, nullable=False, default=False)
    ActualizadoEn = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    usuario = db.relationship("Usuario", backref="permisos_individuales")

    def to_dict(self):
        return {
            "modulo_id":      self.IdModulo,
            "puede_ver":      self.PuedeVer,
            "puede_crear":    self.PuedeCrear,
            "puede_editar":   self.PuedeEditar,
            "puede_eliminar": self.PuedeEliminar,
        }
