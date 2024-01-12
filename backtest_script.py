from backtest_framework import Backtest
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
import sma_crossover,sma_crossover2,buy_and_hold
from Linear_regression import Linear_regression
import copy


if __name__ == '__main__':

    # Load the data feed from the CSV file
    frequency = 6*60 # in minutes
    feed = GenericBarFeed(frequency*60)
    feed.addBarsFromCSV("btc-usdt", "KDSH_Data/btc_4h.csv")

    #Create strategy
    broker_cash = 1000000
    commission_percentage = 0.15
    strategy = sma_crossover.SMACrossOver(feed, "btc-usdt",broker_cash=broker_cash, smaPeriod=20,broker_fee_percentage=commission_percentage/100)
    # strategy = sma_crossover2.SMACrossOver2(feed, "btc-usdt",broker_cash=broker_cash, smaPeriod1=75,smaPeriod2=100,broker_fee_percentage=commission_percentage/100)

    # Create Backtest instance and plotter
    bt = Backtest(broker_cash,commission_percentage,feed_buy_hold,"btc-usdt",strategy)
    bt.createPlotter()
    bt.addSimpleReturnsSubPlot()
    bt.addSubPlot("Instantaneous PnL Curve","Inst. PnL",strategy.positions)
    bt.addSubPlot("Cumulative PnL Curve","Cum. PnL",strategy.positions_cumulated)

    # Run backtest
    bt.runBacktest()
 

    # Print metrics
    bt.printMetrics()
    # Buy and Hold return
    print("13. Buy and Hold Return %.2f %%" % ((strategy_buy_hold.getResult()-broker_cash)/(broker_cash)*100))

    # Plot the curve
    bt.plotCurve()

