from ..extensions import db, login_manager
from flask_login import UserMixin
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    nombre        = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256))
    rol           = db.Column(db.String(20),  default="viewer")
    activo        = db.Column(db.Boolean,     default=True)
    primer_login  = db.Column(db.Boolean,     default=True)   # ← nuevo campo
    creado_en     = db.Column(db.DateTime,    default=datetime.utcnow)

    activos = db.relationship("Activo", backref="responsable", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f"<Usuario {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))