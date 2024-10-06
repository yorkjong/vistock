"""
ibd_rs_cmp - A module for plotting IBD Relative Strength (RS) comparisons of
multiple stocks using mplfinance.

This module provides functionality to plot the Relative Strength (RS) of
multiple stocks compared to a reference index (e.g., S&P 500 or Taiwan
Weighted Index) using mplfinance.  It fetches historical stock data from Yahoo
Finance, calculates RS values, and generates a multi-panel chart. The resulting
chart is saved as an image file.

Functions:
- plot: Generates a Relative Strength comparison plot for multiple stocks.

Usage:
To use this module, call the `plot` function with a list of stock symbols and
desired parameters.
"""
__software__ = "IBD RS Comparison chart"
__version__ = "2.5"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/10/05 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

from .. import tw
from .. import file_utils
from . import mpf_utils as mpfu
from ..ibd import relative_strength, relative_strength_3m
from .. import stock_indices as si


def plot(symbols, period='2y', interval='1d', ticker_ref=None,
         rs_window='12mo', legend_loc='best',
         style='checkers', color_cycle=plt.cm.Paired.colors,
         out_dir='out'):
    """
    Plot the Relative Strength (RS) of multiple stocks compared to a reference
    index using mplfinance.

    This function generates a multi-panel chart that compares the RS values i
    of the specified stocks against a reference index (e.g., S&P 500 or Taiwan
    Weighted Index). The chart includes RS lines for each stock, and can be
    customized based on the selected period and interval. The resulting plot is
    saved as an image file in the specified output directory.

    Parameters
    ------------
    symbols: list of str
        List of stock symbols to compare. Can include both US and Taiwan stocks.

    period: str, optional
        The period of historical data to fetch. Valid values are '6mo', '1y',
        '2y', '5y', '10y', 'ytd', 'max'.  Default is '2y'.

        - mo  -- monthes
        - y   -- years
        - ytd -- year to date
        - max -- all data

    interval: str, optional
        The interval for data points. Valid values are '1d' for daily or '1wk'
        for weekly. Default is '1d'.

    ticker_ref: str, optional
        The ticker symbol of the reference index. If None, defaults to S&P
        500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock is
        a Taiwan stock.

    rs_window: str, optional
        Specify the time window ('3mo' or '12mo') for Relative Strength
        calculation. Default to '12mo'.

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

        Default is 'checkers'.

    color_cycle: list or None
        Specifies a list of colors to be used for cycling through plot
        lines. If None, the default matplotlib color cycle will be used.
        You can pass a list of colors to override the default color cycle.
        Each plot line will use the next color in the sequence.

        Default color sequence:

        - plt.cm.Paired.colors (20 colors, cooler and more muted)

        Other useful predefined color cycles:

        - plt.cm.tab20.colors (20 colors, brighter)
        - plt.cm.tab20b.colors (20 colors, darker)
        - plt.cm.Paired.colors (12 colors, alternating between deep and
          pastel colors; useful for categorical data)
        - plt.cm.Set3.colors (12 colors, pastel-like; good for categorical
          data)
        - plt.cm.Set1.colors (9 colors, bold and highly distinct; ideal for
          categorical data)

    out_dir: str, optional
        Directory to save the image file. Defaults to 'out'.

    Returns
    --------
    None
        The function generates a plot and saves it as an image file.

    Example
    --------
    >>> symbols = ['NVDA', 'MSFT', 'META', 'AAPL', 'TSM']
    >>> plot(symbols)
    """
    if not ticker_ref:
        ticker_ref = '^GSPC'      # S&P 500 Index
        if tw.is_taiwan_stock(tw.as_yfinance(symbols[0])):
            ticker_ref = '^TWII'  # Taiwan Weighted Index

    # Fetch data for stocks and index
    tickers = [tw.as_yfinance(s) for s in symbols]
    df = yf.download([ticker_ref]+tickers, period=period, interval=interval)
    df_price = df.xs('Close', level='Price', axis=1)

    # Select the appropriate relative strength function based on the rs_window
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_window]

    # Set the figure
    fig = mpf.figure(style=style, figsize=(12, 6))
    ax = fig.add_subplot()  # Add first subplot
    if color_cycle:
        ax.set_prop_cycle(color=color_cycle)

    # Plot Relative Strength Lines
    for ticker, symbol in zip(tickers, symbols):
        rs = rs_func(df_price[ticker], df_price[ticker_ref], interval)
        ax.plot(rs.index, rs, label=f'{si.get_name(symbol)}')

    # Plot the Reference Line
    ax.plot(rs.index, [100]*len(df), label=f'{si.get_name(ticker_ref)}',
            color='gray', linestyle='--')

    # Set Y axis
    ax.set_ylabel('Relative Strength '
                  f'(Compared to {si.get_name(ticker_ref)})')
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.tick_params(axis='y', labelright=True, labelleft=False)

    # Set location of legends
    ax.legend(loc=legend_loc)

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"IBD Relative Strength Comparison - {interval} "
                 f"({df.index[0]} to {df.index[-1]})"
                 f"; RS: {rs_window}", y=0.93)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info('stocks', interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------

def main():
    mpfu.use_mac_chinese_font()
    symbols = ['NVDA', 'MSFT', 'META', '^NDX', '^TWII']
    #symbols = ['NVDA', 'MSFT', 'META', '^NDX']
    #plot(symbols)
    #symbols = ['羅昇', '昆盈', '穎漢', '光聖', '所羅門']
    plot(symbols, rs_window='3mo', interval='1d', period='1y')


if __name__ == '__main__':
    main()

