from celery.schedules import crontab


class BaseConfig(object):
    # Flask Config
    SECRET_KEY = b'D\xfc2\xdf\x18\xb2\xd2d\xf9\xae\xeb\xa7\xc4\xba\xd5\xec9\x89\xae\xf9\xcf\x18M'
    # DB Config
    DB_HOST = 'localhost'
    DB_PORT = 27017
    DB_DBNAME = 'stock'
    # Celery Config
    CELERY_IMPORTS = ('app.tasks.crawl', 'app.tasks.graph')
    CELERY_BROKER_URL = 'mongodb://localhost:27017/stock'
    CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/'
    CELERY_MONGODB_BACKEND_SETTINGS = {
        'database': 'stock',
        'taskmeta_collection': 'taskmeta_collection',
    }
    CELERY_TIMEZONE = 'Asia/Shanghai'
    # 定时任务
    CELERYBEAT_SCHEDULE = {
        'fetch_all_dk_data': {
            'task': 'app.tasks.fetchdata.fetch_all_dk_data',
            'schedule': crontab(minute=30, hour=2),
            'args': ()
        }
    }


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}