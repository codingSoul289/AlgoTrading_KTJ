from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns,sharpe,drawdown,trades
from buy_and_hold import BuyAndHoldStrategy

class Backtest:
    '''
    Setup Backtest
    '''
    def __init__(self,broker_cash,broker_fee_percentage,feed,instrument,strategy):
        self.returnsAnalyzer = returns.Returns()
        self.strategy = strategy
        self.instrument = instrument
        self.feed = feed
        
        self.broker_cash = broker_cash
        self.broker_fee_percentage = broker_fee_percentage
        
        # Attaching analyzers in strategy
        
        self.returnsAnalyzer = returns.Returns()
        self.strategy.attachAnalyzer(self.returnsAnalyzer)
        
        self.sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.strategy.attachAnalyzer(self.sharpeRatioAnalyzer)
        
        self.drawDownAnalyzer = drawdown.DrawDown()
        self.strategy.attachAnalyzer(self.drawDownAnalyzer)
        
        self.tradesAnalyzer = trades.Trades()
        self.strategy.attachAnalyzer(self.tradesAnalyzer)
        
    def printMetrics(self):
        
        print("Final portfolio value: USDT %.2f" % self.strategy.getResult())
        
        print()
        tot_closed_trades = self.tradesAnalyzer.getCount()
        profitable_trades = self.tradesAnalyzer.getProfitableCount()
        unprofitable_trades = self.tradesAnalyzer.getUnprofitableCount()
        
        all_trade_profits = self.tradesAnalyzer.getAll()
        gross_profit = all_trade_profits.sum()
        tot_commission = self.tradesAnalyzer.getCommissionsForAllTrades().sum()
        net_profit = gross_profit - tot_commission
        
        profitable_trade_profits = self.tradesAnalyzer.getProfits()
        largest_winning_trade = profitable_trade_profits.max()
        avg_winning_trade = profitable_trade_profits.mean()
        
        unprofitable_trade_losses = self.tradesAnalyzer.getLosses()
        gross_loss = unprofitable_trade_losses.sum()
        avg_losing_trade = unprofitable_trade_losses.mean()
        largest_losing_trade = unprofitable_trade_losses.max()
        
        tot_returns = self.tradesAnalyzer.getAllReturns()
        pos_returns = self.tradesAnalyzer.getPositiveReturns()
        neg_returns = self.tradesAnalyzer.getNegativeReturns()
        
        #Buy and Hold Return
        buy_hold_strat = BuyAndHoldStrategy(self.feed,self.instrument,self.broker_cash,self.broker_fee_percentage)
        buy_hold_trade_analyzer = trades.Trades()
        buy_hold_strat.attachAnalyzer(buy_hold_trade_analyzer)
        
        buy_hold_strat.run()
        buy_hold_return = buy_hold_trade_analyzer.getAllReturns().sum()
        
        print("1. Gross profit: USDT %.2f" % gross_profit)
        # print("2. Net profit: USDT %.2f" % net_profit)
        print("3. Total Closed Trades: %d" % tot_closed_trades)
        print("4. Win Rate: %d %%" % (profitable_trades/tot_closed_trades*100))
        print("5. Max. drawdown: %.2f %%" % (self.drawDownAnalyzer.getMaxDrawDown() * 100))
        print("6. Gross Loss: USDT %.2f" % gross_loss)
        print("7. Average Winning Trade: USDT %.2f" % avg_winning_trade)
        print("8. Average Losing Trade: USDT %.2f" % avg_losing_trade)
        print("9. Buy and Hold Return: USDT %.2f" % buy_hold_return)
        print("10. Largest Losing Trade: USDT %.2f" % largest_losing_trade)
        print("11. Largest Winning Trade: USDT %.2f" % largest_winning_trade)
        print("12. Sharpe ratio: %.2f" % self.sharpeRatioAnalyzer.getSharpeRatio(0.05))
        print("13. Sortino ratio: %.2f" % (self.sortino_ratio(self.tradesAnalyzer.getAllReturns())))
        
    def runBacktest(self):
        self.strategy.run()
    
    def sortino_ratio(self,returns):
        downside_returns = [r for r in returns if r < 0]
        mean_return = sum(returns) / len(returns)
        std_dev_downside = (sum((r - mean_return) ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5
        return mean_return / std_dev_downside if std_dev_downside != 0 else 0.0
    
    def addInstrumentSubPlot(self,parameter_name,parameter_list):
        self.plt.getInstrumentSubplot(self.instrument).addDataSeries(parameter_name, parameter_list)
        
    def addSimpleReturnsSubPlot(self):
        self.plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", self.returnsAnalyzer.getReturns())
    
    def createPlotter(self):
        self.plt = plotter.StrategyPlotter(self.strategy)
    
    def plotCurve(self):
        self.plt.plot()

