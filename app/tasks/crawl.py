from celery.utils.log import get_task_logger
from app import celery, db
from app.utils import datetool as du
import pandas as pd
import tushare as ts
import json


@celery.task
def async_stock_basics():
    """
    获取沪深上市公司基本情况
    :return: 
    """
    date = du.last_trading_day()
    if db.stock_basics.find({'date': date}).count() == 0:
        df = ts.get_stock_basics(date)
        if not df.empty:
            df['date'] = date
            df.reset_index(level=0, inplace=True)
            db.stock_basics.insert(json.loads(df.to_json(orient='records')))


@celery.task
def async_hist_market(code):
    """
    获取历史行情数据
    :param code: 股票代码
    :return: 
    """
    try:
        result = db.hist_market.find({'code': code}).sort('date', -1)[0]
        start = du.delay_days(result['date'])
    except:
        start = du.from_now_days(-90)
    df = ts.get_k_data(code, ktype='D', start=start, end=du.from_now_days(-1))
    if not df.empty:
        db.hist_market.insert(json.loads(df.to_json(orient='records')))


@celery.task
def async_hist_trade_details(code, date=du.today()):
    """
    获取历史交易分笔数据明细
    :param code: 
    :param date: 
    :return: 
    """
    df = ts.get_tick_data(code, date)
    if not df.empty and df.shape[0] > 5:
        df['date'] = date
        db['hist_trade_{0}'.format(code)].insert(json.loads(df.to_json(orient='records')))


def async_hist_trade(code):
    """
    获取历史交易数据
    :param code: 
    :return: 
    """
    try:
        result = db['hist_trade_{0}'.format(code)].find().sort('date', -1)[0]
        start = du.delay_days(result['date'])
    except:
        start = du.from_now_days(-90)
    dates = pd.date_range(start=start, end=du.from_now_days(-1)).format()
    for date in dates:
        async_hist_trade_details.delay(code, date)

