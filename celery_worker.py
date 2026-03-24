# celery_worker.py — punto de entrada para el worker de Celery
# Uso: celery -A celery_worker.celery worker --loglevel=info
#
# Requiere Redis corriendo: docker run -d -p 6379:6379 redis

from app import create_app
from celery import Celery
import os

app = create_app(os.getenv("FLASK_ENV", "development"))

def make_celery(flask_app):
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config["CELERY_BROKER_URL"],
        backend=flask_app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)
