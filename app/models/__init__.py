# Importar modelos para que SQLAlchemy los registre
from .usuario      import Usuario
from .departamento import Departamento
from .activo       import Activo
from .vehiculo     import (
    Condicion, Categoria, TipoServicio, Ubicacion,
    Personal, Vehiculo, ConductorVehiculo,
    PermisosVehiculo, MantenimientoVehiculo
)