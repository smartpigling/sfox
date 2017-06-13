from celery.utils.log import get_task_logger
from app import celery, db
from app.utils import datetool as du
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os



def trade_volume_decision(df):
    """
    交易手数判定
    :param df: 
    :return: 
    """
    if df['diff_volume'] > 0 and df['open'] > df['close']:
        return '空'
    elif df['diff_volume'] < 0 and df['open'] > df['close']:
        return '强空'
    elif df['diff_volume'] > 0 and df['open'] < df['close']:
        return '多'
    elif df['diff_volume'] < 0 and df['open'] < df['close']:
        return '强多'
    else:
        return '--'


@celery.task
def trade_strength_trend_chart(code):
    """
    交易强弱趋势图
    :param code: 
    :return: 
    """
    trade_df = pd.DataFrame(list(db['hist_trade_{0}'.format(code)].find()))
    #当日买盘手数
    buy_trade_df = trade_df[trade_df['type'] == '买盘'][['date', 'volume']].groupby('date').sum()
    # 当日卖盘手数
    sell_trade_df = trade_df[trade_df['type'] == '卖盘'][['date', 'volume']].groupby('date').sum()
    # 交易手数差值diff_volume
    trade_strength_df = (buy_trade_df - sell_trade_df).rename(columns={'volume': 'diff_volume'})
    trade_strength_df.reset_index(level=0, inplace=True)
    # trade_strength_df['date'] = trade_strength_df['date'].astype(np.datetime64)
    # 加载历史行情
    market_df = pd.DataFrame(list(db['hist_market'].find({'code': code})))
    # 合并当前code行情与交易力度
    df = pd.merge(market_df, trade_strength_df, on='date')
    df['volume_decision'] = df.apply(trade_volume_decision, axis=1)
    # 交易量化
    df['volume_quantizing'] = 0
    for i in range(1, df.shape[0]):
        ident = df.ix[i, 'volume_decision']
        value = 0
        if ident == '空':
            value = df.ix[i - 1, 'volume_quantizing'] - 1
        elif ident == '强空':
            value = df.ix[i - 1, 'volume_quantizing'] - 2
        elif ident == '多':
            value = df.ix[i - 1, 'volume_quantizing'] + 1
        elif ident == '强多':
            value = df.ix[i - 1, 'volume_quantizing'] + 2
        else:
            value = df.ix[i - 1, 'volume_quantizing']
        df.ix[i, 'volume_quantizing'] = value
    # 买卖强弱走势图
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.figure(figsize=(10, 6))
    df[['date', 'volume_quantizing']].plot(x='date', y='volume_quantizing', label=u'买卖趋势')
    plt.suptitle(u'买卖强弱趋势图', fontsize=16)
    plt.xlabel(u'时间', fontsize=14)
    plt.ylabel(u'力度', fontsize=14)
    plt.savefig('{0}/images/{1}.png'.format(file_path, code))