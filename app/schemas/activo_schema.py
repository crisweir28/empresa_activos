# Marshmallow schema — útil para validar JSON en APIs REST
from marshmallow import Schema, fields, validate, ValidationError


class ActivoSchema(Schema):
    id              = fields.Int(dump_only=True)
    nombre          = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    descripcion     = fields.Str(load_default=None)
    numero_serie    = fields.Str(load_default=None)
    categoria       = fields.Str(validate=validate.OneOf(
                        ["equipo", "mueble", "vehiculo", "software", "otro"]))
    estado          = fields.Str(validate=validate.OneOf(["activo", "baja", "mantenimiento"]),
                        load_default="activo")
    valor           = fields.Float(load_default=0.0)
    departamento_id = fields.Int(load_default=None)
    fecha_adquisicion = fields.Date(load_default=None)

activo_schema  = ActivoSchema()
activos_schema = ActivoSchema(many=True)
