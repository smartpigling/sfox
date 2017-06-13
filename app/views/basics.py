from bson.objectid import ObjectId
from wtforms import form
from flask import current_app, url_for, redirect, request, flash, Markup
from flask_admin.actions import action
from flask_admin.contrib.pymongo import ModelView, filters
from app.utils import datetool as du
from app import db
import re
import pymongo


class BasicsView(ModelView):

    def scaffold_query(self):
        return {}

    def get_list(self, page, sort_column, sort_desc, search, filters,
                 execute=True, page_size=None):
        query = self.scaffold_query()

        # Filters
        if self._filters:
            data = []

            for flt, flt_name, value in filters:
                f = self._filters[flt]
                data = f.apply(data, value)

            if data:
                if len(data) == 1:
                    query = data[0]
                else:
                    query['$and'] = data

        # Search
        if self._search_supported and search:
            query = self._search(query, search)

        # Get count
        count = self.coll.find(query).count() if not self.simple_list_pager else None

        # Sorting
        sort_by = None

        if sort_column:
            sort_by = [(sort_column, pymongo.DESCENDING if sort_desc else pymongo.ASCENDING)]
        else:
            order = self._get_default_order()

            if order:
                sort_by = [(order[0], pymongo.DESCENDING if order[1] else pymongo.ASCENDING)]

        # Pagination
        if page_size is None:
            page_size = self.page_size

        skip = 0

        if page and page_size:
            skip = page * page_size

        results = self.coll.find(query, sort=sort_by, skip=skip, limit=page_size)

        if execute:
            results = list(results)

        return count, results


class StockBasicsView(BasicsView):
    list_template = 'basics_list.html'
    column_labels = {
        'code': '代码',
        'name': '名称',
        'industry': '所属行业',
        'area': '地区',
        'pe': '市盈率',
        'outstanding': '流通股本(亿)',
        'totals': '总股本(亿)',
        'totalAssets': '总资产(万)',
        'liquidAssets': '流动资产',
        'fixedAssets': '固定资产',
        'reserved': '公积金',
        'reservedPerShare': '每股公积金',
        'esp': '每股收益',
        'bvps': '每股净资',
        'pb': '市净率',
        'timeToMarket': '上市日期',
        'undp': '未分利润',
        'perundp': '每股未分配',
        'rev': '收入同比(%)',
        'profit': '利润同比(%)',
        'gpr': '毛利率(%)',
        'npr': '净利润率(%)',
        'holders': '股东人数'
    }
    column_list = ('code', 'name', 'industry', 'area', 'pe', 'outstanding', 'totals', 'holders')
    column_details_list = ('code', 'name', 'industry', 'area', 'pe', 'outstanding', 'totals',
                           'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved', 'reservedPerShare',
                           'esp', 'bvps', 'pb', 'timeToMarket', 'undp', 'perundp', 'rev', 'profit',
                           'gpr', 'npr', 'holders')
    column_sortable_list = ('pe', 'outstanding', 'totals', 'holders')
    column_searchable_list = ['code']
    column_formatters = {
        'code': lambda v, c, m, p: Markup(
            '<a href={0}?search={1}>{2}</a>'.format(url_for('trend_view.index_view'), m['code'], m['code'])
        )
    }

    def scaffold_query(self):
        query = {'date': {'$regex': du.last_trading_day()}}
        return query

    @action('data_update_action', '数据同步')
    def data_update_action(self, ids):
        try:
            from app.tasks.crawl import async_stock_basics
            async_stock_basics()
            flash('上市公司基本信息更新完成!')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(str(ex), 'error')

    @action('data_analysis_action', '趋势分析')
    def data_analysis_action(self, ids):
        try:
            from app.tasks.crawl import async_hist_market, async_hist_trade
            from app.tasks.graph import trade_strength_trend_chart
            codes = []
            for pk in ids:
                stock = db.stock_basics.find_one({'_id': ObjectId(pk)})
                code = stock['code']
                codes.append(code)
                # 数据采样乐观趋势分析
                async_hist_market.delay(code)
                async_hist_trade(code)
                trade_strength_trend_chart(code)
            return redirect('{0}?search={1}'.format(url_for('trend_view.index_view'), ','.join(codes)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(str(ex), 'error')

    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    form = form.Form
    page_size = 20


class TrendView(BasicsView):
    column_labels = {
        'code': '代码',
        'name': '名称',
        'trend_image': '买卖趋势'
    }
    column_list = ('code', 'name', 'trend_image')
    column_searchable_list = ['code']

    def _list_thumbnail(view, context, model, name):
        img_url = url_for('static', filename='images/{0}.png'.format(model['code']))
        return Markup(
            '<a href="{0}" target="_blank" class="thumbnail">'\
            '<img src="{1}" style="width:100%;height:100px;" ></a>'.format(img_url, img_url))

    column_formatters = {
        'trend_image': _list_thumbnail
    }
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = False

    form = form.Form
    page_size = 20

    def scaffold_query(self):
        query = {'date': {'$regex': du.last_trading_day()}}
        return query

    def _search(self, query, search_term):
        if search_term.find(',') > 0:
            search_term = re.sub(r'\s+', '', search_term)
            query = {'$and': [query, {'code': {'$in': search_term.split(',')}}]}
            return query
        else:
            return super()._search(query, search_term)
