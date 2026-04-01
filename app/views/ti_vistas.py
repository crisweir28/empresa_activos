from ..extensions import db


class VEquiposTI(db.Model):
    """Vista v_equipos_ti — equipos con usuario asignado."""
    __tablename__ = "v_equipos_ti"
    __table_args__ = {"extend_existing": True}

    IdElectronico       = db.Column(db.Integer, primary_key=True)
    Nombre              = db.Column(db.String(100))
    Marca               = db.Column(db.String(100))
    Modelo              = db.Column(db.String(100))
    NumeroSerie         = db.Column(db.String(100))
    TipoEquipo          = db.Column(db.String(30))
    Estado              = db.Column(db.String(20))
    Condicion           = db.Column(db.String(20))
    Costo               = db.Column(db.Float)
    FechaAdquisicion    = db.Column(db.Date)
    Descripcion         = db.Column(db.Text)
    UsuarioNombre       = db.Column(db.String(200))
    UsuarioCorreo       = db.Column(db.String(150))
    UsuarioRol          = db.Column(db.String(50))
    UbicacionNombre     = db.Column(db.String(100))
    MantenimientosActivos = db.Column(db.Integer)


class VEstadisticasTI(db.Model):
    """Vista v_estadisticas_ti — contadores para validación de estados."""
    __tablename__ = "v_estadisticas_ti"
    __table_args__ = {"extend_existing": True}

    TotalEquipos       = db.Column(db.Integer, primary_key=True)
    EnAlmacen          = db.Column(db.Integer)
    Asignados          = db.Column(db.Integer)
    EnMantenimiento    = db.Column(db.Integer)
    Bajas              = db.Column(db.Integer)
    EnBuenEstado       = db.Column(db.Integer)
    EnMalEstado        = db.Column(db.Integer)


class VMantenimientoElectronico(db.Model):
    """Vista v_mantenimiento_electronico — historial de mantenimientos."""
    __tablename__ = "v_mantenimiento_electronico"
    __table_args__ = {"extend_existing": True}

    IdMantenimiento  = db.Column(db.Integer, primary_key=True)
    Tipo             = db.Column(db.String(20))
    Diagnostico      = db.Column(db.Text)
    Descripcion      = db.Column(db.Text)
    FechaInicio      = db.Column(db.Date)
    FechaTermino     = db.Column(db.Date)
    Costo            = db.Column(db.Float)
    Tecnico          = db.Column(db.String(120))
    Estatus          = db.Column(db.String(20))
    CreadoEn         = db.Column(db.DateTime)
    IdElectronico    = db.Column(db.Integer)
    EquipoNombre     = db.Column(db.String(100))
    NumeroSerie      = db.Column(db.String(100))
    TipoEquipo       = db.Column(db.String(30))
    CreadoPorNombre  = db.Column(db.String(200))