import os
import socket
from app import create_app
from app.extensions import socketio
from app.extensions import db
from app.models.usuario import Usuario
from app.models.departamento import Departamento
from app.models.activo import Activo

app = create_app(os.getenv("FLASK_ENV", "development"))


def get_local_ip():
    """Detecta la IP local de la máquina en la red."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def update_env_ip(ip: str):
    """Actualiza APP_HOST en el archivo .env con la IP actual."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r") as f:
        lines = f.readlines()

    nueva_linea = f"APP_HOST={ip}\n"
    encontrado  = False
    for i, line in enumerate(lines):
        if line.startswith("APP_HOST="):
            lines[i]   = nueva_linea
            encontrado = True
            break

    if not encontrado:
        lines.append(f"\n{nueva_linea}")

    with open(env_path, "w") as f:
        f.writelines(lines)

    # Actualizar también en memoria para esta sesión
    app.config["APP_HOST"] = ip


def seed():
    """
    Solo crea las tablas si no existen.
    Los datos de usuarios se insertan con setup_mysql.sql.
    """
    with app.app_context():
        db.create_all()

        if not Usuario.query.first():
            print("\n  ⚠️   No hay usuarios en la base de datos.")
            print("  Opciones:")
            print("  1. Ejecuta: mysql -u root -p < setup_mysql.sql")
            print("  2. O se creará un admin de emergencia ahora.\n")

            admin = Usuario(
                username = "admin",
                nombre   = "Administrador",
                email    = "admin@empresa.mx",
                rol      = "admin",
                activo   = True,
            )
            admin.set_password("Admin123!")
            db.session.add(admin)
            db.session.commit()
            print("  ✅  Admin temporal creado: admin / Admin123!")
            print("  ⚠️   Cambia la contraseña después del primer login.\n")
        else:
            total = Usuario.query.count()
            print(f"  ✅  DB conectada — {total} usuario(s) encontrado(s).")


if __name__ == "__main__":
    seed()

    # Detectar IP local y guardarla en .env automáticamente
    ip = get_local_ip()
    update_env_ip(ip)

    print(f"\n  🚀  Servidor en: http://localhost:5000")
    print(f"  🌐  Red local:   http://{ip}:5000")
    print(f"  🗄️   DB: {app.config['SQLALCHEMY_DATABASE_URI']}\n")

    # ✅ Sin watchdog — usar stat (default de Flask):
    socketio.run(app, debug=True, port=5000, host="0.0.0.0",
             use_reloader=True, reloader_type='stat')