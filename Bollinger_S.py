from __future__ import print_function

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import quandl
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade import broker as basebroker
from pyalgotrade.broker.backtesting import TradePercentage


class BBands(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,bBandsPeriod=20,broker_fee_percentage=0.0015,broker_cash=1000000):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        self.__bbands = bollinger.BollingerBands(feed[instrument].getCloseDataSeries(), bBandsPeriod, 2)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.getBroker().setCash(broker_cash)
        self.getBroker().setCommission(TradePercentage(broker_fee_percentage))
        self.positions = []
        self.positions_cumulated = []
        self.__trade_start_time = None
        self.__max_duration = 0

    def getBollingerBands(self):
        return self.__bbands

    def onEnterOk(self, position):
        self.__position = position
        self.__trade_start_time = self.getCurrentDateTime()
        self.positions.append(position.getPnL())
        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

    def onExitOk(self, position):
        exit_time = self.getCurrentDateTime()
        duration = (exit_time - self.__trade_start_time).days

        if duration > self.__max_duration:
            self.__max_duration = duration

        if(position is not None):
            self.positions.append(position.getPnL())
        else:
            self.positions.append(0)

        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

        self.__position = None
        self.__trade_start_time = None

    def getMaxTradeDuration(self):
        return self.__max_duration

    def onBars(self, bars):
        lower = self.__bbands.getLowerBand()[-1]
        upper = self.__bbands.getUpperBand()[-1]
        if lower is None:
            return

        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]

        if(self.__position is None):
            if shares == 0 and bar.getClose() < lower:
                sharesToBuy = int(self.getBroker().getCash(False) / bar.getClose())
                self.__position=self.enterLong(self.__instrument, sharesToBuy, True)

        elif (not self.__position.exitActive() and (shares > 0 and bar.getClose() > upper) or (self.__position is not None and self.__position.getAge().days>10)):
                self.__position.exitMarket()
