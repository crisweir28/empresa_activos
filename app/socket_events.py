from flask_socketio import join_room
from flask_login import current_user
from . import socketio


@socketio.on('join')
def on_join(data):
    """El usuario se une a su sala personal para recibir notificaciones."""
    usuario_id = data.get('usuario_id')
    if current_user.is_authenticated and current_user.id == usuario_id:
        join_room(f"user_{usuario_id}")