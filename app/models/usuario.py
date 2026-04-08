# app/models/usuario.py
from flask_login import UserMixin
from passlib.context import CryptContext
from .departamento import Departamento
from ..extensions import db, login_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Departamentos que tienen módulo propio en el sistema
AREAS_CON_MODULO = {'TI', 'Tecnología', 'Recursos Humanos', 'Administrativo', 'Almacén'}


class Rol(db.Model):
    __tablename__ = "Rol"
    IdRol     = db.Column(db.Integer, primary_key=True)
    NombreRol = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Rol {self.NombreRol}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = "Usuario"

    IdUsuario        = db.Column(db.Integer,     primary_key=True)
    NombreUsuario    = db.Column(db.String(50),  unique=True, nullable=False)
    Nombre           = db.Column(db.String(100), nullable=False)
    ApellidoPaterno  = db.Column(db.String(100), nullable=False)
    ApellidoMaterno  = db.Column(db.String(100), nullable=True)
    NumeroTelefono   = db.Column(db.String(15),  nullable=True)
    Correo           = db.Column(db.String(150), unique=True, nullable=False)
    Contrasena       = db.Column(db.String(255), nullable=False)
    Estatus          = db.Column(db.Boolean,     nullable=False, default=True)
    PrimerLogin      = db.Column(db.Boolean,     nullable=False, default=True)
    IdRol            = db.Column(db.Integer, db.ForeignKey("Rol.IdRol"), nullable=False)
    CreadoEn         = db.Column(db.DateTime, server_default=db.func.now())
    IntentosFallidos = db.Column(db.Integer,  nullable=False, default=0)
    BloqueadoHasta   = db.Column(db.DateTime, nullable=True,  default=None)

    # ── Nuevas columnas ───────────────────────────────────────
    IdDepartamento = db.Column(
        db.Integer,
        db.ForeignKey("departamentos.id"),
        nullable=True,
        default=None
    )
    TipoUsuario = db.Column(
        db.Enum('administrador', 'empleado'),
        nullable=False,
        default='empleado'
    )

    # ── Relaciones ────────────────────────────────────────────
    rol_obj         = db.relationship("Rol",          backref="usuarios",     lazy="joined")
    departamento_obj = db.relationship("Departamento", backref="usuarios",     lazy="joined")

    # ── Flask-Login ───────────────────────────────────────────
    @property
    def id(self):
        return self.IdUsuario

    # ── Compatibilidad ────────────────────────────────────────
    @property
    def username(self):
        return self.NombreUsuario

    @property
    def email(self):
        return self.Correo

    @property
    def nombre(self):
        return f"{self.Nombre} {self.ApellidoPaterno}"

    @property
    def activo(self):
        return self.Estatus

    @property
    def primer_login(self):
        return self.PrimerLogin

    @primer_login.setter
    def primer_login(self, value):
        self.PrimerLogin = value

    @property
    def password_hash(self):
        return self.Contrasena

    # ── Área ─────────────────────────────────────────────────
    @property
    def area_nombre(self):
        """Nombre del área/departamento asignado."""
        return self.departamento_obj.nombre if self.departamento_obj else None

    @property
    def tiene_modulo(self):
        """True si el área del usuario tiene módulo propio en el sistema."""
        return self.area_nombre in AREAS_CON_MODULO if self.area_nombre else False

    @property
    def es_administrador_area(self):
        return self.TipoUsuario == 'administrador'

    @property
    def es_empleado(self):
        return self.TipoUsuario == 'empleado'

    # ── Rol helpers (compatibilidad con código existente) ─────
    @property
    def rol(self):
        """
        Slug del rol para compatibilidad con permisos existentes.
        El super admin (IdRol=1) sigue siendo 'admin'.
        Para el resto, el slug se deriva del área.
        """
        if not self.rol_obj:
            return "viewer"

        # Super admin — acceso total
        if self.IdRol == 1:
            return "admin"

        # Derivar slug del área
        area = self.area_nombre or ""
        mapa_area = {
            "TI":               "ti",
            "Tecnología":       "ti",
            "Recursos Humanos": "rh",
            "Administrativo":   "administrativo",
            "Almacén":          "almacenista",
        }
        return mapa_area.get(area, "empleado")

    @property
    def es_admin(self):
        return self.IdRol == 1

    @property
    def puede_gestionar_usuarios(self):
        return self.IdRol == 1 or self.es_administrador_area

    @property
    def rol_label(self):
        """Etiqueta legible para mostrar en UI."""
        if self.IdRol == 1:
            return "Super Administrador"
        area  = self.area_nombre or "Sin área"
        tipo  = "Administrador" if self.es_administrador_area else "Empleado"
        return f"{tipo} — {area}"

    @property
    def departamento_id(self):
        return self.IdDepartamento

    # ── Contraseña ────────────────────────────────────────────
    def set_password(self, password: str):
        self.Contrasena = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        if not self.Contrasena:
            return False
        return pwd_context.verify(password, self.Contrasena)

    def __repr__(self):
        return f"<Usuario {self.NombreUsuario} [{self.area_nombre}/{self.TipoUsuario}]>"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))