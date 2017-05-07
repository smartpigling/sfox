from app.tasks import crawl, graph
import pandas as pd


crawl.async_stock_basics()

# graph.trade_strength_trend_chart('600279')