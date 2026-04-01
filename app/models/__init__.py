# Importar modelos para que SQLAlchemy los registre
from .usuario      import Usuario
from .departamento import Departamento
from .activo       import Activo
from .vehiculo     import (
    Condicion, Categoria, TipoServicio, Ubicacion,
    Personal, Vehiculo, ConductorVehiculo,
    PermisosVehiculo, MantenimientoVehiculo
)

from .herramienta import Herramienta, AsignacionHerramienta, EvidenciaHerramienta, ReporteDanio
from .electronico import Electronico, MantenimientoElectronico
from .permiso import Modulo, PermisoRol, PermisoUsuario