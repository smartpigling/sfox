from celery import Celery
from flask import Flask, request, session
from flask_admin import Admin
from flask_babelex import Babel
from config import config, BaseConfig
from pymongo import MongoClient


celery = Celery(__name__, broker=BaseConfig.CELERY_BROKER_URL, backend=BaseConfig.CELERY_RESULT_BACKEND)
client = MongoClient(BaseConfig.DB_HOST, BaseConfig.DB_PORT)
db = client[BaseConfig.DB_DBNAME]


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # Celery
    celery.conf.update(app.config)
    # Babel
    babel = Babel(app)
    babel.localeselector(get_locale)
    # Blueprint
    from app.views.portal import portal as portal_blueprint
    app.register_blueprint(portal_blueprint, url_prefix='/portal')

    from app.views.portal import HomeView
    from app.views.basics import StockBasicsView
    # Create admin
    admin = Admin(app, name='SFox', index_view=HomeView(name='首页', url='/admin'),
                  template_mode='bootstrap3')
    admin.add_view(StockBasicsView(db.stock_basics, name='股票基本信息', endpoint='stock_basics'))

    return app


def get_locale():
    override = request.args.get('lang')

    if override:
        session['lang'] = override
    return session.get('lang', 'zh_CN')
