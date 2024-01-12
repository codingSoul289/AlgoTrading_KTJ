from pyalgotrade import strategy
from pyalgotrade.broker.backtesting import TradePercentage
class BuyAndHoldStrategy(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument,broker_cash,broker_fee_percentage):
        super(BuyAndHoldStrategy, self).__init__(feed)
        self.instrument = instrument
        self.__position = None
        self.feed = feed
        self.getBroker().setCash(broker_cash)
        self.getBroker().setCommission(TradePercentage(broker_fee_percentage))

    def onBars(self, bars):
        bar = bars[self.instrument]

        if self.__position is None:
            close = bar.getClose()
            broker = self.getBroker()
            cash = broker.getCash()
            quantity = cash / close

            self.__position = self.enterLong(self.instrument, quantity)