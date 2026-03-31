from ..extensions import db


class VInventario(db.Model):
    """Vista v_inventario — herramientas con estado y asignación actual."""
    __tablename__ = "v_inventario"
    __table_args__ = {"extend_existing": True}

    IdHerramienta   = db.Column(db.Integer, primary_key=True)
    Nombre          = db.Column(db.String(100))
    Marca           = db.Column(db.String(100))
    Modelo          = db.Column(db.String(100))
    NumeroSerie     = db.Column(db.String(100))
    Estado          = db.Column(db.String(20))
    Costo           = db.Column(db.Float)
    FechaAlta       = db.Column(db.Date)
    Descripcion     = db.Column(db.Text)
    UsuarioAsignado = db.Column(db.String(200))
    FechaAsignacion = db.Column(db.Date)
    TotalReportes   = db.Column(db.Integer)
    TotalEvidencias = db.Column(db.Integer)


class VHistorialAsignaciones(db.Model):
    """Vista v_historial_asignaciones — historial completo."""
    __tablename__ = "v_historial_asignaciones"
    __table_args__ = {"extend_existing": True}

    IdAsignacion       = db.Column(db.Integer, primary_key=True)
    IdHerramienta      = db.Column(db.Integer)
    HerramientaNombre  = db.Column(db.String(100))
    NumeroSerie        = db.Column(db.String(100))
    UsuarioNombre      = db.Column(db.String(200))
    UsuarioCorreo      = db.Column(db.String(150))
    FechaAsignacion    = db.Column(db.Date)
    FechaDevolucion    = db.Column(db.Date)
    Observaciones      = db.Column(db.Text)
    AsignadoPorNombre  = db.Column(db.String(200))
    RecibidoPorNombre  = db.Column(db.String(200))
    EstadoAsignacion   = db.Column(db.String(20))
    EstadoHerramienta  = db.Column(db.String(20))