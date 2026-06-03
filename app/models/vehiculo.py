#app/models/vehiculo.py
from ..extensions import db
from datetime import datetime


class Condicion(db.Model):
    __tablename__ = "Condicion"
    IdCondicion     = db.Column(db.Integer, primary_key=True)
    NombreCondicion = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Condicion {self.NombreCondicion}>"


class Categoria(db.Model):
    __tablename__ = "Categoria"
    IdCategoria = db.Column(db.Integer, primary_key=True)
    Nombre      = db.Column(db.String(100), nullable=False)

    tipos = db.relationship("TipoServicio", backref="categoria", lazy="dynamic")


class TipoServicio(db.Model):
    __tablename__ = "TipoServicio"
    IdTipoServicio = db.Column(db.Integer, primary_key=True)
    Nombre         = db.Column(db.String(100), nullable=False)
    IdCategoria    = db.Column(db.Integer, db.ForeignKey("Categoria.IdCategoria"), nullable=False)


class Ubicacion(db.Model):
    __tablename__ = "Ubicacion"
    IdUbicacion = db.Column(db.Integer, primary_key=True)
    Nombre      = db.Column(db.String(100), nullable=False)


class Personal(db.Model):
    __tablename__ = "Personal"
    IdPersonal       = db.Column(db.Integer, primary_key=True)
    Nombre           = db.Column(db.String(100), nullable=False)
    Apellido         = db.Column(db.String(100), nullable=False)
    Telefono         = db.Column(db.String(15))
    Area             = db.Column(db.String(100))
    Correo           = db.Column(db.String(150))
    JefeInmediato    = db.Column(db.String(200))
    LicenciaNumero   = db.Column(db.String(50))
    LicenciaVigencia = db.Column(db.Date)
    SeguroMedico     = db.Column(db.String(100))
    SeguroVigencia   = db.Column(db.Date)
    IdCondicion      = db.Column(db.Integer, db.ForeignKey("Condicion.IdCondicion"))
    Activo           = db.Column(db.Boolean, nullable=False, default=True)
    CreadoEn         = db.Column(db.DateTime, default=datetime.now)

    condicion = db.relationship("Condicion", backref="personal")

    @property
    def nombre_completo(self):
        return f"{self.Nombre} {self.Apellido}"

    def to_dict(self):
        return {
            "id":               self.IdPersonal,
            "nombre":           self.Nombre,
            "apellido":         self.Apellido,
            "nombre_completo":  self.nombre_completo,
            "telefono":         self.Telefono,
            "area":             self.Area,
            "correo":           self.Correo,
            "jefe_inmediato":   self.JefeInmediato,
            "licencia_numero":  self.LicenciaNumero,
            "licencia_vigencia": str(self.LicenciaVigencia) if self.LicenciaVigencia else None,
            "seguro_medico":    self.SeguroMedico,
            "seguro_vigencia":  str(self.SeguroVigencia) if self.SeguroVigencia else None,
            "activo":           self.Activo,
        }


class Vehiculo(db.Model):
    __tablename__ = "Vehiculo"

    IdVehiculo      = db.Column(db.Integer, primary_key=True)
    Nombre          = db.Column(db.String(120), nullable=False)
    TipoVehiculo    = db.Column(db.String(20),  nullable=True)
    Marca           = db.Column(db.String(100))
    Modelo          = db.Column(db.String(100))
    Anio            = db.Column(db.SmallInteger, nullable=True)
    Matricula       = db.Column(db.String(20), nullable=False, unique=True)
    VIN             = db.Column(db.String(50),  nullable=True)
    Color           = db.Column(db.String(50),  nullable=True)
    Kilometraje     = db.Column(db.Integer, default=0)
    TipoAdquisicion = db.Column(db.String(20))
    Estado          = db.Column(db.String(20), nullable=False, default="activo")
    Valor           = db.Column(db.Float, nullable=False, default=0)
    FechaAdquisicion = db.Column(db.Date)
    IdUbicacion     = db.Column(db.Integer, db.ForeignKey("Ubicacion.IdUbicacion"))
    PolizaSeguro    = db.Column(db.String(100), nullable=True)
    Aseguradora     = db.Column(db.String(100), nullable=True)
    VigenciaSeguro  = db.Column(db.Date,        nullable=True)
    UltimaVerificacion = db.Column(db.Date,     nullable=True)
    Accesorios      = db.Column(db.String(255), nullable=True)
    Comentarios     = db.Column(db.Text,        nullable=True)
    Arrendamiento   = db.Column(db.Boolean,     nullable=False, default=False)
    FechaRenovacion = db.Column(db.Date,        nullable=True)
    ProveedorArrendamiento = db.Column(db.String(150), nullable=True)
    CreadoEn        = db.Column(db.DateTime, default=datetime.now)
    ActualizadoEn   = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    ubicacion      = db.relationship("Ubicacion",            backref="vehiculos")
    conductores    = db.relationship("ConductorVehiculo",    backref="vehiculo",  lazy="dynamic")
    permisos       = db.relationship("PermisosVehiculo",     backref="vehiculo",  lazy="dynamic")
    mantenimientos = db.relationship("MantenimientoVehiculo", backref="vehiculo", lazy="dynamic")
    archivos       = db.relationship("VehiculoArchivo",      backref="vehiculo",  lazy="dynamic", cascade="all, delete-orphan")
    evidencias     = db.relationship("EvidenciaVehiculo",    backref="vehiculo",  lazy="dynamic", cascade="all, delete-orphan")

    def _ultimo_archivo(self, tipo):
        """Devuelve la URL del último archivo subido de un tipo dado, o None."""
        a = (VehiculoArchivo.query
             .filter_by(IdVehiculo=self.IdVehiculo, TipoArchivo=tipo)
             .order_by(VehiculoArchivo.FechaSubida.desc())
             .first())
        return a.ArchivoUrl if a else None

    def _ultima_evidencia(self, tipo):
        """Devuelve la URL de la última evidencia subida de un tipo dado, o None."""
        e = (EvidenciaVehiculo.query
             .filter_by(IdVehiculo=self.IdVehiculo, Tipo=tipo)
             .order_by(EvidenciaVehiculo.CreadoEn.desc())
             .first())
        return e.ArchivoUrl if e else None

    def to_dict(self):
        return {
            "id":               self.IdVehiculo,
            "nombre":           self.Nombre,
            "tipo_vehiculo":    self.TipoVehiculo,
            "marca":            self.Marca,
            "modelo":           self.Modelo,
            "anio":             self.Anio,
            "matricula":        self.Matricula,
            "vin":              self.VIN,
            "color":            self.Color,
            "kilometraje":      self.Kilometraje,
            "tipo_adquisicion": self.TipoAdquisicion,
            "estado":           self.Estado,
            "valor":            self.Valor,
            "fecha_adquisicion": str(self.FechaAdquisicion) if self.FechaAdquisicion else None,
            "ubicacion_id":     self.IdUbicacion,
            "poliza_seguro":    self.PolizaSeguro,
            "aseguradora":      self.Aseguradora,
            "vigencia_seguro":  str(self.VigenciaSeguro) if self.VigenciaSeguro else None,
            "ultima_verificacion": str(self.UltimaVerificacion) if self.UltimaVerificacion else None,
            "accesorios":       self.Accesorios,
            "comentarios":      self.Comentarios,
            "arrendamiento":    self.Arrendamiento,
            "fecha_renovacion": str(self.FechaRenovacion) if self.FechaRenovacion else None,
            "proveedor_arrendamiento": self.ProveedorArrendamiento,
            # ── Archivos (documentos) ────────────────────────────
            "tarjeta_circulacion_url":     self._ultimo_archivo("tarjeta_circulacion"),
            "certificado_verificacion_url": self._ultimo_archivo("certificado_verificacion"),
            # ── Evidencias (fotos) ───────────────────────────────
            "evidencia_frente_url":   self._ultima_evidencia("frente"),
            "evidencia_lateral_url":  self._ultima_evidencia("lateral"),
            "evidencia_interior_url": self._ultima_evidencia("interior"),
        }


class VehiculoArchivo(db.Model):
    __tablename__ = "VehiculoArchivo"

    IdArchivo     = db.Column(db.Integer, primary_key=True)
    IdVehiculo    = db.Column(db.Integer, db.ForeignKey("Vehiculo.IdVehiculo"), nullable=False)
    TipoArchivo   = db.Column(db.String(50), nullable=False)
    NombreArchivo = db.Column(db.String(255))
    ArchivoUrl    = db.Column(db.String(255), nullable=False)
    MimeType      = db.Column(db.String(100))
    FechaSubida   = db.Column(db.DateTime, default=datetime.now)


class EvidenciaVehiculo(db.Model):
    __tablename__ = "EvidenciaVehiculo"

    IdEvidencia = db.Column(db.Integer, primary_key=True)
    IdVehiculo  = db.Column(db.Integer, db.ForeignKey("Vehiculo.IdVehiculo"), nullable=False)
    Tipo        = db.Column(db.String(50))
    ArchivoUrl  = db.Column(db.String(255))
    CreadoEn    = db.Column(db.DateTime, default=datetime.now)


class ConductorVehiculo(db.Model):
    __tablename__ = "ConductorVehiculo"
    IdConductorVehiculo = db.Column(db.Integer, primary_key=True)
    IdPersonal          = db.Column(db.Integer, db.ForeignKey("Personal.IdPersonal"), nullable=False)
    IdVehiculo          = db.Column(db.Integer, db.ForeignKey("Vehiculo.IdVehiculo"), nullable=False)
    FechaInicio         = db.Column(db.Date, nullable=False)
    FechaFin            = db.Column(db.Date)

    personal = db.relationship("Personal", backref="asignaciones")


class PermisosVehiculo(db.Model):
    __tablename__ = "PermisosVehiculo"
    IdPermiso        = db.Column(db.Integer, primary_key=True)
    IdVehiculo       = db.Column(db.Integer, db.ForeignKey("Vehiculo.IdVehiculo"),        nullable=False)
    IdTipoServicio   = db.Column(db.Integer, db.ForeignKey("TipoServicio.IdTipoServicio"), nullable=False)
    Descripcion      = db.Column(db.String(255))
    Numero           = db.Column(db.String(100))
    FechaInicio      = db.Column(db.Date)
    FechaVencimiento = db.Column(db.Date, nullable=False)
    ArchivoUrl       = db.Column(db.String(255))
    CreadoEn         = db.Column(db.DateTime, default=datetime.now)

    tipo_servicio = db.relationship("TipoServicio", backref="permisos")

    def to_dict(self):
        return {
            "id":               self.IdPermiso,
            "vehiculo_id":      self.IdVehiculo,
            "tipo_servicio_id": self.IdTipoServicio,
            "tipo_nombre":      self.tipo_servicio.Nombre if self.tipo_servicio else None,
            "descripcion":      self.Descripcion,
            "numero":           self.Numero,
            "fecha_inicio":     str(self.FechaInicio) if self.FechaInicio else None,
            "fecha_vencimiento": str(self.FechaVencimiento) if self.FechaVencimiento else None,
        }


class MantenimientoVehiculo(db.Model):
    __tablename__ = "MantenimientoVehiculo"
    IdMantenimiento = db.Column(db.Integer, primary_key=True)
    IdVehiculo      = db.Column(db.Integer, db.ForeignKey("Vehiculo.IdVehiculo"),           nullable=False)
    IdPersonal      = db.Column(db.Integer, db.ForeignKey("Personal.IdPersonal"),            nullable=True)
    IdTipoServicio  = db.Column(db.Integer, db.ForeignKey("TipoServicio.IdTipoServicio"),    nullable=False)
    Descripcion     = db.Column(db.Text)
    FechaInicio     = db.Column(db.Date, nullable=False)
    FechaEntrega    = db.Column(db.Date)
    Kilometraje     = db.Column(db.Integer)
    Costo           = db.Column(db.Float, default=0)
    Proveedor       = db.Column(db.String(120))
    Estatus         = db.Column(db.String(20), nullable=False, default="en_proceso")
    CreadoPor       = db.Column(db.Integer, db.ForeignKey("usuario.IdUsuario"), nullable=True)
    CreadoEn        = db.Column(db.DateTime, default=datetime.now)

    personal      = db.relationship("Personal",     backref="mantenimientos")
    tipo_servicio = db.relationship("TipoServicio", backref="mantenimientos")
    creado_por    = db.relationship("Usuario",
                                    foreign_keys="MantenimientoVehiculo.CreadoPor",
                                    backref="mantenimientos_creados",
                                    primaryjoin="MantenimientoVehiculo.CreadoPor == Usuario.IdUsuario")

    def to_dict(self):
        return {
            "id":            self.IdMantenimiento,
            "vehiculo_id":   self.IdVehiculo,
            "tipo_servicio": self.tipo_servicio.Nombre if self.tipo_servicio else None,
            "descripcion":   self.Descripcion,
            "fecha_inicio":  str(self.FechaInicio)  if self.FechaInicio  else None,
            "fecha_entrega": str(self.FechaEntrega) if self.FechaEntrega else None,
            "kilometraje":   self.Kilometraje,
            "costo":         self.Costo,
            "proveedor":     self.Proveedor,
            "estatus":       self.Estatus,
        }