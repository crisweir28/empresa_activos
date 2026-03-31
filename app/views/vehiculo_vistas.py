from ..extensions import db


class VVehiculo(db.Model):
    """Vista v_vehiculos — vehículos con conductor y alertas."""
    __tablename__ = "v_vehiculos"
    __table_args__ = {"extend_existing": True}

    id                    = db.Column(db.Integer, primary_key=True)
    nombre                = db.Column(db.String(120))
    marca                 = db.Column(db.String(100))
    modelo                = db.Column(db.String(100))
    matricula             = db.Column(db.String(20))
    kilometraje           = db.Column(db.Integer)
    tipo_adquisicion      = db.Column(db.String(20))
    estado                = db.Column(db.String(20))
    valor                 = db.Column(db.Float)
    fecha_adquisicion     = db.Column(db.Date)
    ubicacion_nombre      = db.Column(db.String(100))
    conductor_nombre      = db.Column(db.String(200))
    licencia_numero       = db.Column(db.String(50))
    licencia_vigencia     = db.Column(db.Date)
    permisos_por_vencer   = db.Column(db.Integer)
    mantenimientos_activos = db.Column(db.Integer)


class VPermisosVencer(db.Model):
    """Vista v_permisos_vencer — permisos próximos a vencer."""
    __tablename__ = "v_permisos_vencer"
    __table_args__ = {"extend_existing": True}

    id               = db.Column(db.Integer, primary_key=True)
    tipo             = db.Column(db.String(100))
    descripcion      = db.Column(db.String(255))
    numero           = db.Column(db.String(100))
    fecha_vencimiento = db.Column(db.Date)
    dias_restantes   = db.Column(db.Integer)
    vehiculo_id      = db.Column(db.Integer)
    vehiculo_nombre  = db.Column(db.String(120))
    matricula        = db.Column(db.String(20))


class VMantenimientoVehiculo(db.Model):
    """Vista v_mantenimiento_vehiculo — historial de mantenimiento."""
    __tablename__ = "v_mantenimiento_vehiculo"
    __table_args__ = {"extend_existing": True}

    id               = db.Column(db.Integer, primary_key=True)
    tipo_servicio    = db.Column(db.String(100))
    descripcion      = db.Column(db.Text)
    fecha_inicio     = db.Column(db.Date)
    fecha_entrega    = db.Column(db.Date)
    kilometraje      = db.Column(db.Integer)
    costo            = db.Column(db.Float)
    proveedor        = db.Column(db.String(120))
    estatus          = db.Column(db.String(20))
    creado_en        = db.Column(db.DateTime)
    vehiculo_id      = db.Column(db.Integer)
    vehiculo_nombre  = db.Column(db.String(120))
    matricula        = db.Column(db.String(20))
    personal_nombre  = db.Column(db.String(200))
    creado_por_nombre = db.Column(db.String(120))


class VAlertasMantenimiento(db.Model):
    """Vista v_alertas_mantenimiento — próximos mantenimientos."""
    __tablename__ = "v_alertas_mantenimiento"
    __table_args__ = {"extend_existing": True}

    IdMantenimiento      = db.Column(db.Integer, primary_key=True)
    ProximoKilometraje   = db.Column(db.Integer)
    ProximaFecha         = db.Column(db.Date)
    Estatus              = db.Column(db.String(20))
    TipoServicio         = db.Column(db.String(100))
    IdVehiculo           = db.Column(db.Integer)
    VehiculoNombre       = db.Column(db.String(120))
    Matricula            = db.Column(db.String(20))
    KilometrajeActual    = db.Column(db.Integer)
    AlertaKilometraje    = db.Column(db.Integer)
    KmRestantes          = db.Column(db.Integer)
    AlertaFecha          = db.Column(db.Integer)
    DiasRestantes        = db.Column(db.Integer)