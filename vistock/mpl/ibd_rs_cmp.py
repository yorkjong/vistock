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
__software__ = "IBD RS Comparision chart"
__version__ = "1.0"
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


def plot(symbols, period='2y', interval='1d', ref_ticker=None,
         hides_nontrading=True, out_dir='out'):
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

    df_ref = yf.Ticker(ref_ticker).history(period=period, interval=interval)

    add_plots = []
    for symbol in symbols:
        ticker = tw.as_yfinance(symbol)
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        rs = relative_strength(df['Close'], df_ref['Close'], interval)
        add_plots.append(mpf.make_addplot(rs, label=f'{symbol}'))
    if not add_plots:
        return
    df['Close'] = rs    # for hiding 'Close' line from the mpf.plot call

    fig, axes = mpf.plot(
        df, type='line',
        volume=False, addplot=add_plots,
        figratio=(12, 6), figscale=1.2,
        style='charles', # classic, charles, nightclouds, yahoo, check
        show_nontrading=not hides_nontrading,
        returnfig=True,
    )

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"IBD Relative Strength Comparision {interval} "
                 f"({df.index.values[0]}~{df.index.values[-1]})", y=0.93)

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

