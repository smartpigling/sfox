from flask import Blueprint, current_app, redirect, url_for, jsonify
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
    from app.tasks.crawl import async_stock_basics
    async_stock_basics()
    return redirect(url_for('stock_basics.index_view'))