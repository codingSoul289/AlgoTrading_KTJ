# Configuration

1. **backtest_framework.py** - It contains modular code of backtesting
2. **backtest_script.py** - It contains script of backtesting
3. **strategy classes (sma_crossover, sma_crossover_2, etc.)** - Contains pyalgotrade-based strategy classes

# Setup

1. Run `pip install -r requirements.txt`.
2. Run `python3 backtest_script.py` to run for SMA crossover.
3. Check the metrics and plot.

# Strategy

1. Copy the framework in any of the strategy classes and change the OnBars() method according to the strategy.
2. Run `python3 backtest_script.py`.

**References**:

1. Pyalgotrade tutorial - [Tutorial Link](https://gbeced.github.io/pyalgotrade/docs/v0.20/html/index.html#).
