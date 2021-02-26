#! /home/mira/anaconda3/bin/python3

from datetime import datetime
import backtrader as bt
import math

# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=100,  # period for the fast moving average
        pslow=200,   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal
        self.previous_buy = None
        self.units = 0

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.previous_buy = self.datas[0].close[0]
                self.units = (self.broker.getvalue() // self.previous_buy) / 2
                # self.units = 1000
                print("Buying {} units at {:.2f}".format(self.units, self.previous_buy))
                self.buy(size=self.units)  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            price = self.datas[0].close[0]
            profit = price-self.previous_buy
            print("Selling {} units at {:.2f}\tprofit {:.2f}\t{:.2f} %".format(self.units, price, self.units*profit, profit/self.previous_buy*100))
            self.close()  # close long position
            self.previous_buy = None
            self.units = 0


if __name__ == '__main__':
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    cerebro.broker.setcash(100000.0)

    # Create a data feed
    data = bt.feeds.YahooFinanceData(dataname='AAPL',
                                    fromdate=datetime(2011, 1, 1),
                                    todate=datetime(2019, 12, 31),)
    cerebro.adddata(data)  # Add the data feed
    cerebro.addstrategy(SmaCross)  # Add the trading strategy

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()
    # cerebro.plot()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
