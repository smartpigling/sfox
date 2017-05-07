from flask import Blueprint, current_app, request, jsonify
from flask_admin import AdminIndexView, expose
from app.tasks.crawl import async_stock_basics
from app import db
import tushare as ts

portal = Blueprint('portal', __name__)


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        df = ts.get_latest_news()
        return self.render('admin/index.html', rows=df)


@portal.route('/get_stock_basics', methods=['GET'])
def get_stock_basics():
    app = current_app._get_current_object()
    print(db['stock_basics'].find({}).count())
    async_stock_basics.delay()
    return jsonify(code=0, message=u'成功')