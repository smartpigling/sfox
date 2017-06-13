# -*- coding:utf-8 -*-
import logging
import json
import pandas as pd
import tushare as ts
from app.utils import datetool as du

# Set up logger
log = logging.getLogger('process')


class DataProcess:

    def __init__(self, db=None):
        self.db = db
        # self.basic = ts.get_stock_basics()
        self.basic = None

    def download_dk_history(self, code):
        """
        下载历史至今天的数据
        date,open,high,close,low,volume,amount
        """
        try:
            result = self.db.dk.find({'code': code}).sort('date', -1)[0]
            start = du.delay_days(result['date'])
        except:
            date = str(self.basic.ix[code]['timeToMarket'])
            start = '{year}-{month}-{date}'.format(year=date[0:4], month=date[4:6], date=date[6:8])
        df = ts.get_k_data(code, start=start, end=du.from_now_days(-1))
        if not df.empty:
            self.db.dk.insert(json.loads(df.to_json(orient='records')))
        return True

    def download_all_dk_history(self):
        """
        下载所有股票的历史数据
        """
        for code in self.basic['code']:
            self.download_dk_history(code)

    def load_dk_data(self, code, count=90):
        df = pd.DataFrame(list(self.db.dk.find({'code': code}).sort('date', -1).limit(count)))
        return df


if __name__ == '__main__':
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['stock']

    dc = DataProcess(db=db)
    # dc.download_k_history('603600')
    df = dc.load_dk_data('603600')
    print(df)

