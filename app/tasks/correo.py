# tasks/correo.py — tareas asíncronas con Celery
# Para usar: asegúrate de tener Redis corriendo y ejecutar:
#   celery -A celery_worker.celery worker --loglevel=info

from flask_mail import Message
from ..extensions import mail
from flask import current_app


def enviar_notificacion(destinatario: str, asunto: str, cuerpo: str):
    """
    Envía un correo. 
    En producción conviene convertir esto en tarea Celery con @celery.task.
    Por ahora es síncrona para simplificar el setup inicial.
    """
    try:
        msg = Message(subject=asunto, recipients=[destinatario], body=cuerpo)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo a {destinatario}: {e}")
