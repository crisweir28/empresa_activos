# extensions.py — instancias compartidas de extensiones Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_mail import Mail   

db            = SQLAlchemy()
login_manager = LoginManager()
migrate       = Migrate()
socketio      = SocketIO()
mail          = Mail()  

login_manager.login_view    = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder."