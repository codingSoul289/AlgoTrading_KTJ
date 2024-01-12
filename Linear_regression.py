from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker.backtesting import TradePercentage
import pandas as pd
from pyalgotrade.dataseries import DataSeries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class Linear_regression(strategy.BacktestingStrategy):
    def __init__(self, feed,file_name, instrument,broker_cash,broker_fee_percentage):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.i=0
        self.__instrument = instrument
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.df=pd.read_csv(file_name,index_col='Date Time',parse_dates=["Date Time"])
        self.getBroker().setCash(broker_cash)
        self.getBroker().setCommission(TradePercentage(broker_fee_percentage))
        self.positions = []
        self.positions_cumulated = []
        self.LinearReg(self.df)
        self.__trade_start_time = None
        self.__max_duration = 0

    def LinearReg(self,df):
        self.df=df
        self.df['return']=np.log(df.Close/df.Close.shift())
        self.df['lag1']=self.df['return'].shift(1)
        self.df.dropna(inplace=True)
        self.df.iloc[:,-2:].plot(kind='scatter',x='lag1',y='return')
        plt.xlim(-0.5,0.5)
        plt.ylim(-0.5,0.5)
        plt.show()

        lm=LinearRegression(fit_intercept = True)
        lm.fit(self.df.lag1.to_frame(),self.df['return'])
        print(f'Slope = {lm.coef_}')
        self.df['pred']=np.sign(lm.predict(df.lag1.to_frame()))
        hits=np.sign(self.df['return']*self.df['pred']).value_counts()
        hit_ratio=hits[1.0]/sum(hits)
        print(f'Hit Ratio:{hit_ratio}')

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
        else:
            self.positions.append(0)

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
        self.i+=1
        if(self.i >= self.df.shape[0]):
            return

        if self.__position is None:
            if self.df.iloc[self.i]['pred']>0:
                shares = int(self.getBroker().getCash()/ bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive() and self.df.iloc[self.i]['pred']<0:
            self.__position.exitMarket()