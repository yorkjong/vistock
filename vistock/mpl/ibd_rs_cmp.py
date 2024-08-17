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
__version__ = "1.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/08/17 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_util
from ..util import is_taiwan_stock
from ..ibd import relative_strength
from .. import stock_indices as si


def plot(symbols, period='2y', interval='1d', ref_ticker=None,
         style='checkers', hides_nontrading=True, out_dir='out'):
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
    symbols : list of str
        List of stock symbols to compare. Can include both US and Taiwan stocks.

    period : str, optional
        The period of historical data to fetch. Valid values are '6mo', '1y',
        '2y', '5y', '10y', 'ytd', 'max'.  Default is '2y'.

        * mo  -- monthes
        * y   -- years
        * ytd -- year to date
        * max -- all data

    interval : str, optional
        The interval for data points. Valid values are '1d' for daily or '1wk'
        for weekly. Default is '1d'.

    ref_ticker : str, optional
        The ticker symbol of the reference index. If None, defaults to S&P
        500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock is
        a Taiwan stock.

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

    hides_nontrading : bool, optional
        Whether to hide non-trading periods. Default is True.
    out_dir : str, optional
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

    if not ref_ticker:
        ref_ticker = '^GSPC'      # S&P 500 Index
        if is_taiwan_stock(tw.as_yfinance(symbols[0])):
            ref_ticker = '^TWII'  # Taiwan Weighted Index

    df_ref = yf.download(ref_ticker, period=period, interval=interval)

    add_plots = []
    for symbol in symbols:
        ticker = tw.as_yfinance(symbol)
        df = yf.download(ticker, period=period, interval=interval)
        rs = relative_strength(df['Close'], df_ref['Close'], interval)
        add_plots.append(mpf.make_addplot(rs, label=f'{ticker}'))
    if not add_plots:
        return
    df['Close'] = rs    # for hiding 'Close' line from the mpf.plot call

    fig, axes = mpf.plot(
        df, type='line',
        volume=False, addplot=add_plots,
        ylabel=f'Relative Strength (Compared to {si.get_name(ref_ticker)})',
        figratio=(2, 1), figscale=1.2,
        style=style,
        show_nontrading=not hides_nontrading,
        returnfig=True,
    )

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"IBD Relative Strength Comparison - {interval} "
                 f"({df.index.values[0]} to {df.index.values[-1]})", y=0.93)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_util.make_dir(out_dir)
    fn = file_util.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------

def main():
    symbols = ['NVDA', 'MSFT', 'META', 'AAPL', 'TSM']
    plot(symbols)
    symbols = ['羅昇', '昆盈', '穎漢', '光聖', '所羅門']
    plot(symbols, interval='1wk')


if __name__ == '__main__':
    main()

