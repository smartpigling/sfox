from app.tasks import crawl, graph
from celery import chain
import pandas as pd
from app.utils.dateutil import last_trading_day

# crawl.async_stock_basics()

if __name__ == '__main__':
    target = ['002108','000958','002011','000786','300107']
    for code in target:
        crawl.async_hist_market.delay(code)
        crawl.async_hist_trade(code)
        graph.trade_strength_trend_chart.delay(code)

