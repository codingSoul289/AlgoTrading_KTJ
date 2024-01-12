# Configuration

1. **backtest_framework.py** - It contains modular code of backtesting
2. **backtest_script.py** - It contains script of backtesting
3. **strategy classes (sma_crossover_2, Bolinger_S, etc.)** - Contains pyalgotrade-based strategy classes

# Strategy

1. Instantiate the class of any strategy needed to be implemented in backtest_script.py file.
2. Run `python3 backtest_script.py`.

# Setup

1. Run `pip install -r requirements.txt`.
2. Run `python3 backtest_script.py` to run strategy.
3. Check the metrics and plot.

**References**:

1. Pyalgotrade tutorial - [Tutorial Link](https://gbeced.github.io/pyalgotrade/docs/v0.20/html/index.html#).
2. Pyalgotrade Strategy Class Documentation - [Documentation Link](https://gbeced.github.io/pyalgotrade/docs/v0.20/html/strategy.html)
3. Pyalgotrade Playlist - [Playlist Link](https://www.youtube.com/watch?v=JcHOOEhaDtU)
