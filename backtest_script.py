from backtest_framework import Backtest
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
import sma_crossover,sma_crossover2,buy_and_hold

if __name__ == '__main__':

    # Load the data feed from the CSV file
    frequency = 6*60 # in minutes
    feed = GenericBarFeed(frequency*60)
    feed.addBarsFromCSV("btc-usdt", "KDSH_Data/btc_4h.csv")

    #Create strategy
    broker_cash = 1000000
    commission_percentage = 0.15
    strategy = sma_crossover.SMACrossOver(feed, "btc-usdt",broker_cash=100000, smaPeriod=20,broker_fee_percentage=commission_percentage/100)
    # strategy = sma_crossover2.SMACrossOver2(feed, "btc-usdt",broker_cash=100000, smaPeriod1=75,smaPeriod2=100,broker_fee_percentage=commission_percentage/100)

    # Create Backtest instance and plotter
    bt = Backtest(broker_cash,commission_percentage,feed,"btc-usdt",strategy)
    bt.createPlotter()
    bt.addSimpleReturnsSubPlot()

    # Run backtest
    bt.runBacktest()

    # Print metrics
    bt.printMetrics()

    # Plot the curve
    bt.plotCurve()

