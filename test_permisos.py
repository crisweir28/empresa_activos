# test_permisos.py
from app import create_app, db
from app.models import Usuario
from sqlalchemy import text

app = create_app()
with app.app_context():
    admin = Usuario.query.filter_by(Nombre='adminTI').first()
    
    print(f"Usuario: {admin.Nombre}")
    print(f"IdUsuario: {admin.IdUsuario}")
    print(f"IdRol: {admin.IdRol}")
    
    # ✅ Cambio aquí: Permisos con mayúscula
    permisos = db.session.execute(text("""
        SELECT m.NombreModulo, p.Ver, p.Crear, p.Editar, p.Eliminar
        FROM Permisos p
        JOIN Modulos m ON p.IdModulo = m.IdModulo
        WHERE p.IdRol = :id_rol AND m.NombreModulo = 'Ticketing'
    """), {'id_rol': admin.IdRol}).fetchone()
    
    if permisos:
        print(f"\n✅ Permisos de Ticketing:")
        print(f"  Ver: {permisos[1]}")
        print(f"  Crear: {permisos[2]}")
        print(f"  Editar: {permisos[3]}")
        print(f"  Eliminar: {permisos[4]}")
    else:
        print("\n❌ NO TIENE PERMISOS DE TICKETING")