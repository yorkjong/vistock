"""
ibd_rs.py - IBD Relative Strength Analysis and Plotting Module

This module provides functionality for analyzing and plotting stock data
with a focus on Investor's Business Daily (IBD) Relative Strength metrics.
It includes capabilities for generating candlestick charts with moving averages,
volume analysis, and relative strength comparisons.

The main function 'plot' allows users to visualize stock performance
over various time periods and intervals, with customizable reference indexes
and styling options.

Usage:
    from vistock.mpl import ibd_rs
    ibd_rs.plot('TSLA', period='1y', interval='1d')
"""
__software__ = "IBD-compatible stock chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/08/16 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_util
from ..util import MarketColorStyle, decide_market_color_style, is_taiwan_stock
from .mpf_util import decide_mpf_style
from ..ibd import relative_strength, ma_window_size


def plot(symbol, period='2y', interval='1d', ref_ticker=None,
         legend_loc='best',
         market_color_style=MarketColorStyle.AUTO, out_dir='out'):
    """
    Generate and display a stock analysis plot with candlestick charts, moving
    averages, volume analysis, and Relative Strength (RS) metrics.

    Parameters
    ----------
    symbol : str
        The stock symbol to analyze.
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
        The reference ticker for calculating Relative Strength. Defaults to
        '^GSPC' (S&P 500) or '^TWII' (Taiwan Weighted Index) for Taiwan stocks.
    market_color_style : MarketColorStyle, optional
        Color style for market data visualization. Default is
        MarketColorStyle.AUTO.
    out_dir : str, optional
        Directory to save the output image file. Default is 'out'.

    Raises
    ------
    ValueError
        If an unsupported interval is provided.
    """
    ticker = tw.as_yfinance(symbol)
    if not ref_ticker:
        ref_ticker = '^GSPC'      # S&P 500 Index
        if is_taiwan_stock(ticker):
            ref_ticker = '^TWII'  # Taiwan Weighted Index

    # Download data
    df = yf.download(ticker, period=period, interval=interval)
    def_ref = yf.download(ref_ticker, period=period, interval=interval)

    # Calculate Relative Strength (RS)
    df['RS'] = relative_strength(df['Close'], def_ref['Close'], interval)

    # Calculate price moving average
    ma_nitems = [ma_window_size(interval, days) for days in (50, 200)]
    for n in ma_nitems:
        df[f'MA {n}'] = df['Close'].rolling(window=n).mean()

    # Calculate volume moving averaage
    vma_nitems = ma_window_size(interval, 50)
    df[f'VMA {vma_nitems}'] = df['Close'].rolling(window=vma_nitems).mean()

    addplot = [
        # Plot of Price Moving Average
        *[mpf.make_addplot(df[f'MA {n}'], panel=0, label=f'MA {n}')
            for n in ma_nitems],

        # Plot of Volume Moving Average
        mpf.make_addplot(df[f'VMA {vma_nitems}'], panel=1,
                         label=f'VMA {vma_nitems}', color='purple'),

        # Plot of Relative Strength
        mpf.make_addplot(df['RS'], panel=2, label=ticker,
                         color='green', ylabel='Relative Strength'),
        mpf.make_addplot([100]*len(df), panel=2, label=ref_ticker,
                         linestyle='--', color='gray'),
    ]

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = decide_mpf_style(base_mpf_style='yahoo',
                                 market_color_style=mc_style)

    # Plot candlesticks, MA, volume, volume MA, and RS
    fig, axes = mpf.plot(
        df, type='candle',              # candlesticks
        volume=True, addplot=addplot,   # MA, volume, volume MA, RS
        style=mpf_style,
        figsize=(16, 8), returnfig=True,
        #show_nontrading=True,
    )

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{ticker} {interval} "
                 f"({df.index.values[0]}~{df.index.values[-1]})", y=0.93)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_util.make_dir(out_dir)
    fn = file_util.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == '__main__':
    plot('TSLA', interval='1wk')

