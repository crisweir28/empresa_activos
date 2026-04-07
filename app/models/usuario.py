# app/models/usuario.py
from flask_login import UserMixin
from passlib.context import CryptContext
from ..extensions import db, login_manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Rol(db.Model):
    __tablename__ = "Rol"
    IdRol     = db.Column(db.Integer, primary_key=True)
    NombreRol = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Rol {self.NombreRol}>"


class Usuario(UserMixin, db.Model):
    __tablename__ = "Usuario"

    IdUsuario       = db.Column(db.Integer,     primary_key=True)
    NombreUsuario   = db.Column(db.String(50),  unique=True, nullable=False)
    Nombre          = db.Column(db.String(100), nullable=False)
    ApellidoPaterno = db.Column(db.String(100), nullable=False)
    ApellidoMaterno = db.Column(db.String(100), nullable=True)
    NumeroTelefono  = db.Column(db.String(15),  nullable=True)
    Correo          = db.Column(db.String(150), unique=True, nullable=False)
    Contrasena      = db.Column(db.String(255), nullable=False)
    Estatus         = db.Column(db.Boolean,     nullable=False, default=True)
    PrimerLogin     = db.Column(db.Boolean,     nullable=False, default=True)
    IdRol           = db.Column(db.Integer, db.ForeignKey("Rol.IdRol"), nullable=False)
    CreadoEn        = db.Column(db.DateTime, server_default=db.func.now())

    rol_obj = db.relationship("Rol", backref="usuarios", lazy="joined")

    # ── Flask-Login requiere 'id' como propiedad ──────────────
    @property
    def id(self):
        return self.IdUsuario

    # ── Compatibilidad con código existente ───────────────────
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

    # ── Rol helpers ───────────────────────────────────────────
    @property
    def rol(self):
        """Retorna el nombre del rol en formato slug para permisos."""
        if not self.rol_obj:
            return "viewer"
        nombre = self.rol_obj.NombreRol.lower()
        mapa = {
            "administrador":  "admin",   # Super admin — acceso total
            "usuario ti":     "ti",      # TI — solo equipos TI
            "administrativo": "administrativo",
            "almacenista":    "almacenista",
            "recursos humanos": "rh",
            "supervisor":     "supervisor",
        }
        return mapa.get(nombre, "viewer")

    @property
    def es_admin(self):
        return self.rol == "admin"  # Solo Administrador (IdRol=1)

    @property
    def puede_gestionar_usuarios(self):
        return self.rol in ("admin", "rh", "ti")

    @property
    def rol_label(self):
        return self.rol_obj.NombreRol if self.rol_obj else "Sin rol"

    @property
    def departamento_id(self):
        """
        Compatibilidad — en la nueva estructura el rol define el departamento.
        Retorna None ya que el acceso se controla por IdRol.
        """
        return None

    # ── Contraseña ────────────────────────────────────────────
    def set_password(self, password: str):
        self.Contrasena = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        if not self.Contrasena:
            return False
        return pwd_context.verify(password, self.Contrasena)

    def __repr__(self):
        return f"<Usuario {self.NombreUsuario}>"


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))