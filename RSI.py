from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import cross
from pyalgotrade.broker.backtesting import TradePercentage

class RSI(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, entrySMA=200, exitSMA=5, rsiPeriod=2, overBoughtThreshold=90, overSoldThreshold=10, broker_cash=100000, broker_fee_percentage=0.0015):
        super(RSI, self).__init__(feed)
        self.__instrument = instrument
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__entrySMA = ma.SMA(self.__priceDS, entrySMA)
        self.__exitSMA = ma.SMA(self.__priceDS, exitSMA)
        self.__rsi = rsi.RSI(self.__priceDS, rsiPeriod)
        self.__overBoughtThreshold = overBoughtThreshold
        self.__overSoldThreshold = overSoldThreshold
        self.getBroker().setCash(broker_cash)
        self.getBroker().setCommission(TradePercentage(broker_fee_percentage))
        self.__longPos = None
        self.__shortPos = None
        self.positions = []
        self.positions_cumulated = []
        self.__trade_start_time = None
        self.__max_duration = 0

    def getEntrySMA(self):
        return self.__entrySMA

    def getExitSMA(self):
        return self.__exitSMA

    def getRSI(self):
        return self.__rsi

    def onEnterOk(self, position):
        self.__trade_start_time = self.getCurrentDateTime()
        self.positions.append(position.getPnL())

        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

        exit_time = self.getCurrentDateTime()
        duration = (exit_time - self.__trade_start_time).days

        self.positions.append(position.getPnL())

        if(len(self.positions)==1):
            self.positions_cumulated.append(self.positions[0])
        elif(len(self.positions)>1):
            self.positions_cumulated.append(self.positions_cumulated[-1]+self.positions[-1])

        if duration > self.__max_duration:
            self.__max_duration = duration

        self.__trade_start_time = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def getMaxTradeDuration(self):
        return self.__max_duration

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate SMA and RSI.
        if self.__exitSMA[-1] is None or self.__entrySMA[-1] is None or self.__rsi[-1] is None:
            return

        bar = bars[self.__instrument]
        if self.__longPos is not None:
            if self.exitLongSignal():
                self.__longPos.exitMarket()
        elif self.__shortPos is not None:
            if self.exitShortSignal():
                self.__shortPos.exitMarket()
        else:
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                if(shares != 0):
                    self.__longPos = self.enterLong(self.__instrument, shares, True)
            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                if(shares != 0):
                    self.__shortPos = self.enterShort(self.__instrument, shares, True)

    def enterLongSignal(self, bar):
        return bar.getPrice() > self.__entrySMA[-1] and self.__rsi[-1] <= self.__overSoldThreshold

    def exitLongSignal(self):
        return cross.cross_above(self.__priceDS, self.__exitSMA) and not self.__longPos.exitActive()

    def enterShortSignal(self, bar):
        return bar.getPrice() < self.__entrySMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold

    def exitShortSignal(self):
        return cross.cross_below(self.__priceDS, self.__exitSMA) and not self.__shortPos.exitActive()