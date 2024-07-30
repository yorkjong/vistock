"""
Plot a 3-split (price, volume, RSI) stock chart.

* Data from yfinance
* Plot with mplfinance
* RSI from TA-Lib
"""
__software__ = "Stock chart of price, volume, and RSI"
__version__ = "1.7"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/07/31 (last revision)"

__all__ = ['plot']

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

from .. import tw
from .. import file_util
from ..util import MarketColorStyle, decide_market_color_style
from .mpf_util import decide_mpf_style
from .. import ta


def installed(module_name):
    """Decides if a module is installed.
    """
    import importlib
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def plot(symbol='TSLA', period='12mo', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         legend_loc='best',
         market_color_style=MarketColorStyle.AUTO, out_dir='out'):
    """Plot a stock figure that consists 3 suplots: a price subplot, a
    volume subplot, and a RSI subplot.

    The price subplot shows price candlesticks, and price moving-average lines.
    The volume subplot shows a volume bar chart and a volume moving average
    line. The RSI subplot shows only the RSI curve.

    Parameters
    ----------
    symbol: str
        the stock symbol.
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

        * 'best'
        * 'upper right'
        * 'upper left'
        * 'lower left'
        * 'lower right'
        * 'right'
        * 'center left'
        * 'center right'
        * 'lower center'
        * 'upper center'
        * 'center'

    market_color_style (MarketColorStyle): The market color style to use.
        Default is MarketColorStyle.AUTO.
    out_dir: str
        the output directory for saving figure.
    """
    # Download stock data
    ticker = tw.as_yfinance(symbol)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Add Volume Moving Average
    vma = mpf.make_addplot(df['Volume'], mav=vma_nitems,
                           type='line', linestyle='', color='purple', panel=1)
    addplot = [vma]

    # Add RSI
    rsi = [
        mpf.make_addplot(ta.rsi(df['Close']), panel=2, ylabel='RSI'),
        mpf.make_addplot([70] * len(df), panel=2, color='red', linestyle='--'),
        mpf.make_addplot([30] * len(df), panel=2, color='green', linestyle='--')
    ]
    addplot.extend(rsi)

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = decide_mpf_style(base_mpf_style='yahoo', market_color_style=mc_style)

    # Plot candlesticks MA, volume, volume MA, RSI
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    fig, axes = mpf.plot(
        df, type='candle',                  # candlesticks
        mav=ma_nitems, mavcolors=colors,    # moving average lines
        volume=True, addplot=addplot,       # volume, volume MA, RSI
        style=mpf_style, figsize=(16, 8),
        returnfig=True
    )
    axes[0].legend([f'MA {d}' for d in ma_nitems], loc=legend_loc)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{ticker} {interval} "
                 f"({df.index.values[0]}~{df.index.values[-1]})",
                 y=0.93)

    # Show the figure
    mpf.show()

    # Write the figure to an PNG file
    out_dir = file_util.make_dir(out_dir)
    fn = file_util.gen_fn_info(ticker, interval, df.index.values[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png')


if __name__ == '__main__':
    plot('TSLA')

