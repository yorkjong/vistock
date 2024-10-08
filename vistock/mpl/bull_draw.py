"""
Visualize a BullRun and Drawdown for a stock.
"""
__software__ = "BullRun & Drawdown"
__version__ = "1.8"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/21 (initial version) ~ 2024/09/05 (last revision)"

__all__ = [ 'plot' ]

import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mplfinance as mpf

from .. import tw
from .. import file_utils
from ..bull_draw_utils import calculate_bull_run, calculate_drawdown
from ..utils import MarketColorStyle, decide_market_color_style
from . import mpf_utils as mpfu


def plot(symbol='TSLA', period='1y', interval='1d', legend_loc='best',
         market_color_style=MarketColorStyle.AUTO,
         style='yahoo', hides_nontrading=True, out_dir='out'):
    """Plot a stock figure that consists of two subplots: a price subplot and
    a volume subplot.

    The price subplot includes price lines, bull-run bar cahrt, and drawdown
    bar chart, while the volume subplot includes a volume histogram and a
    volume moving average line.

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

    legend_loc: str, optional
        the location of the legend (default is 'best').
        Valid locations are

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
        The market color style to use. Default is MarketColorStyle.AUTO.

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
    out_dir: str, optional
        the output directory for saving figure.
    """
    # Download stock data
    ticker = tw.as_yfinance(symbol)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Calculate drawdown and bull run
    df['Drawdown'] = calculate_drawdown(df)
    df['BullRun'] = calculate_bull_run(df)

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                      market_color_style=mc_style)

    # Add Bull Run and Drawdown indicators
    cl_bullrun = get_bullrun_color(mc_style)
    cl_drawdown = get_drawdown_color(mc_style)
    bull_run_addplot = mpf.make_addplot(
        df['BullRun'], type='bar', color=cl_bullrun, alpha=0.5, label='BullRun',
        panel=0, secondary_y=True, ylabel='BullRun and Drawdown')
    drawdown_addplot = mpf.make_addplot(
        df['Drawdown'], type='bar', color=cl_drawdown, alpha=0.5,
        label='DrawDown', panel=0, secondary_y=True)

    # Add Volume Moving Average
    vma = mpf.make_addplot(
        df['Volume'], mav=50,
        type='line', linestyle='', color='purple',
        panel=1)

    # Plot price, bull-run, drawdown, volume, and volume MA
    fig, axes = mpf.plot(
        df, type='line',
        volume=True, addplot=[bull_run_addplot, drawdown_addplot, vma],
        figsize=(16, 8),
        style=mpf_style,
        show_nontrading=not hides_nontrading,
        returnfig=True
    )
    # Set location of legends
    for ax in axes:
        if ax.legend_:
            ax.legend(loc=legend_loc)

    # Move indicators y-axis to the left and price & volume y-axis to the right
    for ax in axes:
        if ax.get_ylabel() == 'BullRun and Drawdown':
            ax.yaxis.tick_left()
            ax.yaxis.set_label_position("left")
        else:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{symbol} - {interval} ({df.index[0]} to {df.index[-1]})",
                 y=0.93)

    # Show
    mpf.show()  # plt.show()

    # Write the figure to an PNG file
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(ticker, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png')


def get_bullrun_color(market_color_style=MarketColorStyle.WESTERN):
    if market_color_style == MarketColorStyle.WESTERN:
        return 'blue'
    else:
        return 'orange'


def get_drawdown_color(market_color_style=MarketColorStyle.WESTERN):
    if market_color_style == MarketColorStyle.WESTERN:
        return 'orange'
    else:
        return 'blue'


if __name__ == '__main__':
    mpfu.use_mac_chinese_font()
    plot('TSLA', style='binancedark')
    plot('台積電', style='binancedark')

