from celery.utils.log import get_task_logger
from app import celery, db
from app.models.dp4mongo import DataProcess


@celery.task
def fetch_all_dk_data():
    dp = DataProcess(db)
    dp.download_all_dk_history()