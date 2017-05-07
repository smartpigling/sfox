from bson.objectid import ObjectId
from wtforms import form
from flask import current_app, url_for, redirect, request, flash, Markup
from flask_admin.actions import action
from flask_admin.contrib.pymongo import ModelView, filters
import re


class StockBasicsView(ModelView):
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
            # '<a href={0}?search={1}>{2}</a>'.format(url_for('sample.index_view'), m['code'], m['code'])
        )
    }

    @action('data_update_action', '数据同步')
    def data_update_action(self, ids):
        try:
            app = current_app._get_current_object()

            flash('所有数据更新完成!')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(str(ex), 'error')

    @action('data_analysis_action', '数据抽样')
    def data_analysis_action(self, ids):
        try:
            app = current_app._get_current_object()
            codes = []
            for pk in ids:
                stock = app.db.stock_basics.find_one({'_id': ObjectId(pk)})
                codes.append(stock['code'])
                # 数据采样乐观趋势分析
                # optimism_trend_analysis(stock['code'])
            return redirect('{0}?search={1}'.format(url_for('sample.index_view'), ','.join(codes)))
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


class SampleView(ModelView):
    column_labels = {
        'code': '代码',
        'name': '名称',
        'trend_image': '乐观趋势'
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

    def _search(self, query, search_term):
        if search_term.find(',') > 0:
            search_term = re.sub(r'\s+', '', search_term)
            query = {'$and': [query, {'code': {'$in': search_term.split(',')}}]}
            return query
        else:
            return super()._search(query, search_term)
