"""
Plot a 3-split (price, volume, RSI) stock chart.
* Data from yfinance
* Plot with mplfinance
* RSI from TA-Lib
"""
__software__ = "Stock chart of price, volume, and RSI"
__version__ = "1.1"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/14 (last revision)"

__all__ = ['plot']

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf


def installed(module_name):
    import importlib
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


if installed('talib'):
    from talib import abstract
else:
    print('Please install "talib" package.')


def plot(ticker='TSLA', period='12mo', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, legend_loc='best'):
    """Plot a stock figure that consists 3 suplots: a price subplot, a
    volume subplot, and a RSI subplot.

    The price subplot shows price candlesticks, and price moving-average lines.
    The volume subplot shows a volume bar chart and a volume moving average
    line. The RSI subplot shows only the RSI curve.

    Parameters
    ----------
    ticker: str
        the ticker name.
    period: str
        the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
        1y, 2y, 5y, 10y, ytd, max.
        * d   -- days
        * mo  -- monthes
        * y   -- years
        * ytd -- year to date
        * max -- all data
    interval: str
        the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
        60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.
        * m  -- minutes
        * h  -- hours
        * wk -- weeks
        * mo -- monthes
        Intraday data cannot extend last 60 days:
        * 1m - max 7 days within last 30 days
        * up to 90m - max 60 days
        * 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)
    ma_nitems: sequence of int
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int
        the number of data items to calculate the volume moving average.
    legend_loc: str
        the location of the legend. Valid locations are
            'best'
            'upper right'
            'upper left'
            'lower left'
            'lower right'
            'right'
            'center left'
            'center right'
            'lower center'
            'upper center'
            'center'
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Add Volume Moving Average
    vma = mpf.make_addplot(df['Volume'], mav=vma_nitems,
                           type='line', linestyle='', color='purple', panel=1)
    addplot = [vma]

    if installed('talib'):
        # Add RSI
        RSI = lambda df, period: abstract.RSI(df, timeperiod=period)
        rsi = mpf.make_addplot(RSI(df['Close'], 14), panel=2, ylabel='RSI')
        addplot.append(rsi)

    # Plot candlesticks MA, volume, volume MA, RSI
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    fig, axes = mpf.plot(
        df, type='candle',                  # candlesticks
        mav=ma_nitems, mavcolors=colors,    # moving average lines
        volume=True, addplot=addplot,       # volume, volume MA, RSI
        style='yahoo', figsize=(16, 8),
        returnfig=True
    )
    axes[0].legend([f'MA {d}' for d in ma_nitems], loc=legend_loc)
    df.index = df.index.strftime('%Y-%m-%d %H:%M')
    fig.suptitle(f"{ticker} {interval} "
                 f"({df.index.values[0]}~{df.index.values[-1]})",
                 y=0.93)

    # Show the figure
    mpf.show()

    # Write the figure to an PNG file
    info = f'{ticker}_{interval}_{df.index.values[-1]}'
    info = info.translate({ord(i): None for i in ':-'})   # remove ':', '-'
    info = info.replace(' ', '_')
    fig.savefig(f'{info}_rsi.png')


if __name__ == '__main__':
    plot('TSLA')

