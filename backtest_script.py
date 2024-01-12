from backtest_framework import Backtest
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
from sma_crossover2 import SMACrossOver2
from buy_and_hold import BuyAndHoldStrategy
from Linear_regression import Linear_regression
from Bollinger_S import BBands
from RSI import RSI


if __name__ == '__main__':

    # Load the data feed from the CSV file
    frequency = 6*60 # in minutes
    path_to_file = "KDSH_Data/btc_6h.csv"
    feed = GenericBarFeed(frequency*60)
    feed.addBarsFromCSV("btc-usdt", path_to_file)

    #Create strategy
    broker_cash = 100000
    commission_percentage = 0.15
    strategy_buy_hold = BuyAndHoldStrategy(feed, "btc-usdt",broker_cash=broker_cash,broker_fee_percentage=commission_percentage/100)
    # strategy = Linear_regression(feed, file_name=path_to_file,instrument="btc-usdt",broker_cash=broker_cash,broker_fee_percentage=commission_percentage/100)
    # strategy = BBands(feed,"btc-usdt",bBandsPeriod=20,broker_fee_percentage=commission_percentage/100,broker_cash=broker_cash)
    # strategy = RSI(feed,"btc-usdt",entrySMA=341,exitSMA=19,rsiPeriod=10,overBoughtThreshold=90,overSoldThreshold=10,broker_cash=broker_cash,broker_fee_percentage=commission_percentage/100)
    strategy = SMACrossOver2(feed, "btc-usdt",broker_cash=broker_cash, stop_loss_percent=0.01,smaPeriod1=19,smaPeriod2=341,broker_fee_percentage=commission_percentage/100)

    # Create Backtest instance and plotter
    bt = Backtest(broker_cash,commission_percentage,"btc-usdt",strategy)
    bt.createPlotter()
    bt.addSimpleReturnsSubPlot()
    bt.addSubPlot("Instantaneous PnL Curve","Inst. PnL",strategy.positions)
    bt.addSubPlot("Cumulative PnL Curve","Cum. PnL",strategy.positions_cumulated)

    # Run backtest
    bt.runBacktest()

    # Print metrics
    bt.printMetrics()
    # Buy and Hold return
    buy_hold_return = (strategy_buy_hold.getResult()-broker_cash)
    strategy_return = strategy.getResult()-broker_cash
    print("16. Buy and Hold Return %.2f %%" % (buy_hold_return/(broker_cash)*100))
    # Net Profit exceeding benchmark return
    print("17. Net Profit exceeding Benchmark Returns (Buy & Hold Return) %.2f %%" % ((strategy_return-buy_hold_return)/buy_hold_return*100))

    # Plot the curve
    bt.plotCurve()

