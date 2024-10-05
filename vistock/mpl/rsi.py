"""
Plot a 3-split (price, volume, RSI) stock chart.

* Data from yfinance
* Plot with mplfinance
* RSI from TA-Lib
"""
__software__ = "Stock chart of price, volume, and RSI"
__version__ = "1.12"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/09/05 (last revision)"

__all__ = ['plot']

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

from .. import tw
from .. import file_utils
from ..utils import MarketColorStyle, decide_market_color_style
from . import mpf_utils as mpfu
from .. import ta


def plot(symbol='TSLA', period='1y', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         legend_loc='best',
         market_color_style=MarketColorStyle.AUTO,
         style='yahoo', hides_nontrading=True, out_dir='out'):
    """Plot a stock figure that consists 3 suplots: a price subplot, a
    volume subplot, and a RSI subplot.

    The price subplot shows price candlesticks, and price moving-average lines.
    The volume subplot shows a volume bar chart and a volume moving average
    line. The RSI subplot shows only the RSI curve.

    Parameters
    ----------
    symbol: str
        the stock symbol.

    period: str, optional
        the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
        1y, 2y, 5y, 10y, ytd, max. Default is '1y'

        - d   -- days
        - mo  -- monthes
        - y   -- years
        - ytd -- year to date
        - max -- all data

    interval: str, optional
        the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
        60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Default is '1d'

        - m  -- minutes
        - h  -- hours
        - wk -- weeks
        - mo -- monthes

        Intraday data cannot extend last 60 days:

        - 1m - max 7 days within last 30 days
        - up to 90m - max 60 days
        - 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)

    ma_nitems: sequence of int, optional
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int, optional
        the number of data items to calculate the volume moving average.

    legend_loc: str, optional
        the location of the legend. Default is 'best'. Valid locations are

        - 'best'
        - 'upper right'
        - 'upper left'
        - 'lower left'
        - 'lower right'
        - 'right'
        - 'center left'
        - 'center right'
        - 'lower center'
        - 'upper center'
        - 'center'

    market_color_style: MarketColorStyle, optional
        The market color style to use.  Default is MarketColorStyle.AUTO.

    style: str, optional
        The chart style to use. Common styles include:

        - 'yahoo': Yahoo Finance style
        - 'charles': Charles style
        - 'tradingview': TradingView style
        - 'binance': Binance style
        - 'binancedark': Binance dark mode style
        - 'mike': Mike style (dark mode)
        - 'nightclouds': Dark mode with sleek appearance
        - 'checkers': Checkered style
        - 'ibd': Investor's Business Daily style
        - 'sas': SAS style
        - 'starsandstripes': Stars and Stripes style
        - 'kenan': Kenan style
        - 'blueskies': Blue Skies style
        - 'brasil': Brasil style

        Default is 'yahoo'.

    hides_nontrading: bool, optional
        Whether to hide non-trading periods. Default is True.
    out_dir: str
        the output directory for saving figure.
    """
    # Download stock data
    ticker = tw.as_yfinance(symbol)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Calculate price moving average
    for n in ma_nitems:
        df[f'MA {n}'] = df['Close'].rolling(window=n).mean()
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')

    # Calculate volume moving averaage
    df[f'VMA {vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()

    # Create subplots
    addplot = [
        # Plot of Price Moving Average
        *[mpf.make_addplot(df[f'MA {n}'], panel=0, label=f'MA {n}', color=c)
            for n, c in zip(ma_nitems, colors)],

        # Plot of Volume Moving Average
        mpf.make_addplot(df[f'VMA {vma_nitems}'], panel=1,
                         label=f'VMA {vma_nitems}', color='purple'),

        # Plot of RSI
        mpf.make_addplot(ta.rsi(df['Close']), panel=2, ylabel='RSI'),
        mpf.make_addplot([70] * len(df), panel=2, color='red', linestyle='--'),
        mpf.make_addplot([30] * len(df), panel=2, color='green', linestyle='--')
    ]

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                      market_color_style=mc_style)

    # Plot candlesticks MA, volume, volume MA, RSI
    fig, axes = mpf.plot(
        df, type='candle',                  # candlesticks
        volume=True, addplot=addplot,       # MA, volume, volume MA, RSI
        figsize=(16, 8),
        style=mpf_style,
        show_nontrading=not hides_nontrading,
        returnfig=True
    )
    # Set location of legends
    for ax in axes:
        if ax.legend_:
            ax.legend(loc=legend_loc)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{symbol} - {interval} ({df.index[0]} to {df.index[-1]})",
                 y=0.93)

    # Show the figure
    mpf.show()

    # Write the figure to an PNG file
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(ticker, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png')


if __name__ == '__main__':
    mpfu.use_mac_chinese_font()
    plot('台積電')
    plot('TSLA')

