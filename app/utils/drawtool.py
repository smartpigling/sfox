import matplotlib.pyplot as plt
import matplotlib.finance as mpf
import pandas as pd
import numpy as np
import os
from matplotlib.dates import date2num
from app.models.dp4mongo import DataProcess


class KLinkChart(object):

    def __init__(self, stock={}, df=None):
        self.stock = stock
        self.data = np.array(df.ix[:, ['time', 'open', 'close', 'high', 'low']])

    def get_max(self, icol=3):
        irow = self.data[:, icol].argmax()
        return self.data[irow][0], self.data[irow][3]

    def draw(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        fig, ax = plt.subplots()
        ax.xaxis_date()
        plt.grid()
        plt.xticks(rotation=45)
        plt.title('{0}{1}'.format(self.stock['name'], self.stock['code']))
        plt.xlabel('时间')
        plt.ylabel('股价(元)')
        mpf.candlestick_ochl(ax, self.data, width=1.2, colorup='r', colordown='g')
        tx, ty = self.get_max()
        plt.text(tx, ty, ty, fontsize=15, color='red', verticalalignment='bottom', horizontalalignment='left')
        plt.show()
        # plt.savefig('{0}/images/{1}.png'.format(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'), self.stock['code']))


if __name__ == '__main__':
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['stock']

    dp = DataProcess(db=db)
    df = dp.load_dk_data('603600', count=60)

    df['time'] = df['date'].astype('datetime64[ns]')
    df['time'] = df['time'].map(date2num)

    k = KLinkChart(stock={'name': '永艺股份', 'code': '603600'}, df=df)
    k.draw()
