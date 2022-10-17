from random import choices
from turtle import position
import pandas as pd
import ta
from ta.volatility import BollingerBands
import matplotlib.pyplot as plt
import numpy as np
from binance.client import Client
from simple_colors import *

###############



client = Client()
###############


class BackTest:
    def __init__(self, symbol):
        self.symbol = symbol
        self.df = pd.set_option('display.max_rows', None)
        self.df = pd.DataFrame(client.get_historical_klines(
            symbol, '1h', '30 days ago UTC'))
        self.df = self.df.iloc[:, 0:6]
        self.df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']

        self.df.set_index("Time", inplace=True)
        self.df.index = pd.to_datetime(self.df.index, unit='ms')
        self.df = self.df.astype(float)

        if self.df.empty:
            print('DATA Is Empty')
        else:
            self.calc_indicators()
            self.generate_signals()
            self.filter_signal_loop()
            self.profit = self.calc_profit() - 0.002
            self.binance_fees = (self.buy_arr.count() +
                                 self.sell_arr.count()) * .001
            self.total_transactions = self.buy_arr.count()

            self.cumulative_profit = (self.profit + 1).prod() - 1
            self.cumulative_profit = round(self.cumulative_profit * 100, 2)
            self.total_time = self.calc_time()
            self.cumulative_profit_number = self.cumulative_profit

            if self.cumulative_profit > 0:
                self.cumulative_profit = green(self.cumulative_profit)
            else:
                self.cumulative_profit = red(self.cumulative_profit)
            self.cumulative_profit_text = "Net Profit = " + \
                str(self.cumulative_profit) + "%" + " ||" + \
                yellow(" fees = ") + str(round(self.binance_fees * 100, 2)) + \
                "%" + " ||" + red(" Total trades = ") + \
                str(self.total_transactions) + " ||  " + \
                yellow(str(self.total_time))

    def calc_indicators(self):
        self.df['ma_2'] = self.df.Close.rolling(2).mean()
        self.df['ma_4'] = self.df.Close.rolling(4).mean()
        self.df['vol_std4'] = self.df.Volume.rolling(4).std()
        self.df['upper_bb20'] = BollingerBands(
            close=self.df["Close"], window=20, window_dev=2).bollinger_hband()
        self.df['lower_bb20'] = BollingerBands(
            close=self.df["Close"], window=20, window_dev=2).bollinger_lband()
        self.df['rsi_6'] = ta.momentum.rsi(self.df.Close, window=6)
        self.df['rsi_12'] = ta.momentum.rsi(self.df.Close, window=12)
        self.df['rsi_21'] = ta.momentum.rsi(self.df.Close, window=21)
        self.df.dropna(inplace=True)

    def generate_signals(self):
        ######################################################################################
        conditions = [

            # (self.df.rsi_12 <= 17),
            # (self.df.rsi_12 >= 65),
            (self.df.rsi_12 <= 16),
            (self.df.rsi_12 >= 70),


        ]
        #######################################################################################
        choices = ['BUY', 'SELL']
        self.df['signal'] = np.select(conditions, choices)
        self.df.signal = self.df.signal.shift()
        self.df.dropna(inplace=True)

    def filter_signal_loop(self):
        position = False
        buydates, selldates = [], []
        #buyprices,sellprices = [], []

        for index, row in self.df.iterrows():
            if not position and row['signal'] == 'BUY':
                position = True
                buydates.append(index)
                # buyprices.append(row.Open)

            if position and row['signal'] == 'SELL':
                position = False
                selldates.append(index)
                # sellprices.append(row.Open)

        self.buy_arr = self.df.loc[buydates].Open
        self.sell_arr = self.df.loc[selldates].Open

        self.buy_time = self.df.loc[buydates]
        self.sell_time = self.df.loc[selldates]

    def calc_profit(self):
        if self.buy_arr.index[-1] > self.sell_arr.index[-1]:
            self.buy_arr = self.buy_arr[:-1]

        return (self.sell_arr.values - self.buy_arr.values) / self.buy_arr.values

    def calc_time(self):
        if self.buy_arr.index[-1] > self.sell_arr.index[-1]:
            self.buy_arr = self.buy_arr[:-1]

        # return [str(i[0])[0:] for i in zip(self.sell_arr.index - self.buy_arr.index)]
        # return  [self.buy_arr.index, self.sell_arr.index],
        return 'Total_Time = ' + str((self.sell_arr.index - self.buy_arr.index).sum())[0:]

    def plot_chart(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.df.Close)
        plt.scatter(self.buy_arr.index, self.buy_arr.values, marker='^', c='b')
        plt.scatter(self.sell_arr.index,
                    self.sell_arr.values, marker='v', c='r')
        plt.show()




symbols = ['BTCUSDT', 'PUNDIXUSDT', 'BCHUSDT', 'ETHUSDT', 'SOLUSDT', 'UNIUSDT', 'AVAXUSDT', 'QNTUSDT', 'BNBUSDT',
           'GALAUSDT', 'XRPUSDT', 'SHIBUSDT', 'ENJUSDT', 'DOTUSDT', 'SANDUSDT', 'DOGEUSDT', 'VETUSDT',
           'NEARUSDT', 'ONEUSDT', 'XLMUSDT', 'MANAUSDT', 'TRXUSDT', 'XTZUSDT', 'BCHUSDT', 'FILUSDT', 'ATOMUSDT',
           'KLAYUSDT', 'AAVEUSDT', 'HNTUSDT', 'EGLDUSDT', 'ADAUSDT', 'LINKUSDT', 'MATICUSDT', 'EOSUSDT',
           'THETAUSDT', 'LTCUSDT', 'NEOUSDT', 'ETCUSDT', 'XMRUSDT', 'TFUELUSDT', 'FTMUSDT', 'ALGOUSDT', 'HBARUSDT',
           'FTTUSDT', 'MKRUSDT', 'AXSUSDT', 'GRTUSDT', 'CAKEUSDT', 'ICPUSDT', 'FLOWUSDT', 'XECUSDT', 'RSRUSDT',
           'GMTUSDT', 'KP3RUSDT', 'FLMUSDT', 'SKLUSDT', 'KSMUSDT']


count = 0
count2 = 0
for i in symbols:

    try:
        instance = BackTest(i)
        if "-" in instance.cumulative_profit_text:
            print("====>  " + red(i) + "  " +
                  instance.cumulative_profit_text + "  ")
            print("-" * 120)
            count += instance.cumulative_profit_number
            count2 += 1
        else:
            print("====>  " + green(i) + "  " +
                  instance.cumulative_profit_text + "  ")
            print("-" * 120)
            count += instance.cumulative_profit_number
    except:
        print(f'excluding {i}')
        print("-" * 120)
        count2 += 1
        continue
print("Total return in % : ",  end="")
print(round(count, 2), end="")
print(" Applied on ", end="")
print(round((1 - count2/len(symbols)) * 100, 2))


#------------------------------------------
# In case you wanna test only a single ticker 
#------------------------------------------



# instance = BackTest('PUNDIXUSDT')
# print(instance.cumulative_profit_text)
# print(instance.calc_time())
# instance.plot_chart()

