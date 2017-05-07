import os
from app import create_app, celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()


# celery worker -A celery_worker.celery -c 5  --loglevel=info
# celery beat -A celery_worker.celery  -c 5 --loglevel=info
