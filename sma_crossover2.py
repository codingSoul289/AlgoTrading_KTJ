from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker.backtesting import TradePercentage


class SMACrossOver2(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,broker_cash,stop_loss_percent=0.02,smaPeriod1=10,smaPeriod2=50,broker_fee_percentage=0.0015):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.getBroker().setCash(broker_cash)
        self.getBroker().setCommission(TradePercentage(broker_fee_percentage))
        self.__sma1 = ma.SMA(self.__prices, smaPeriod1)
        self.__sma2 = ma.SMA(self.__prices, smaPeriod2)
        self.positions = []
        self.positions_cumulated = []
        self.__trade_start_time = None
        self.__max_duration = 0
        self.__stop_loss_percent = stop_loss_percent

    def getSMA1(self):
        return self.__sma1

    def getSMA2(self):
        return self.__sma2

    def onEnterOk(self, position):
        self.__position = position
        self.__trade_start_time = self.getCurrentDateTime()

        self.positions.append(self.__position.getPnL())

        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        exit_time = self.getCurrentDateTime()
        duration = (exit_time - self.__trade_start_time).days

        if duration > self.__max_duration:
            self.__max_duration = duration

        if(position is not None):
            self.positions.append(self.__position.getPnL())

        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

        self.__position = None
        self.__trade_start_time = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def getMaxTradeDuration(self):
        return self.__max_duration

    def onBars(self, bars):

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__sma1, self.__sma2) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__sma1, self.__sma2) > 0:
            self.__position.exitMarket()

        if (self.__position is not None and self.__position.getEntryOrder().getAvgFillPrice() is not None) and bars[self.__instrument].getClose() < self.__position.getEntryOrder().getAvgFillPrice() * (1 - self.__stop_loss_percent):
            self.info("Sell {} at {} due to stop-loss".format(self.__instrument, bars[self.__instrument].getClose()))
            self.__position.exitMarket()