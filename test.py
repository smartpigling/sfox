# -*- coding:utf-8 -*-
import pandas as pd

df = pd.read_csv('E:\SgccData\c_cons.csv', encoding='GB18030')

# from app.tasks import crawl, graph
# from celery import chain
# import pandas as pd
# import tushare as ts
#
# # crawl.async_stock_basics()
#
# if __name__ == '__main__':
#     # target = ['002108','000958','002011','000786','300107']
#     # for code in target:
#     #     crawl.async_hist_market.delay(code)
#     #     crawl.async_hist_trade(code)
#     #     graph.trade_strength_trend_chart.delay(code)
#
#     df = ts.get_k_data('603600')
#     print(df.dtypes)
#     json = df.to_json(orient='records', date_format='epoch')
#     print(json)
#
