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
::

    from vistock.mpl import ibd_rs
    ibd_rs.plot('TSLA', period='1y', interval='1d')
"""
__software__ = "IBD-compatible stock chart"
__version__ = "1.9"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/10/10 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_utils
from ..utils import MarketColorStyle, decide_market_color_style
from . import mpf_utils as mpfu
from ..ibd import relative_strength, relative_strength_3m
from .. import stock_indices as si


def plot(symbol, period='2y', interval='1d', ticker_ref=None, rs_window='12mo',
         legend_loc='best', market_color_style=MarketColorStyle.AUTO,
         style='yahoo', hides_nontrading=True, out_dir='out'):
    """
    Generate and display a stock analysis plot with candlestick charts, moving
    averages, volume analysis, and Relative Strength (RS) metrics.

    Parameters
    ----------
    symbol: str
        The stock symbol to analyze.
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

    Raises
    ------
    ValueError
        If an unsupported interval is provided.
    """
    ticker = tw.as_yfinance(symbol)
    if not ticker_ref:
        ticker_ref = '^GSPC'      # S&P 500 Index
        if tw.is_taiwan_stock(ticker):
            ticker_ref = '^TWII'  # Taiwan Weighted Index

    # Download data
    df = yf.download([ticker_ref, ticker], period=period, interval=interval)
    df_ref = df.xs(ticker_ref, level='Ticker', axis=1)
    df = df.xs(ticker, level='Ticker', axis=1)

    # Select the appropriate relative strength function based on the rs_window
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_window]

    # Calculate Relative Strength (RS)
    df['RS'] = rs_func(df['Close'], df_ref['Close'], interval)

    # Set moving average windows based on the interval
    try:
        ma_wins = { '1d': [50, 200], '1wk': [10, 40]}[interval]
        vma_win = { '1d': 50, '1wk': 10}[interval]
    except KeyError:
        raise ValueError("Invalid interval. " "Must be '1d', or '1wk'.")

    # Calculate price moving average
    for n in ma_wins:
        df[f'MA {n}'] = df['Close'].rolling(window=n, min_periods=1).mean()

    # Calculate volume moving averaage
    df[f'VMA {vma_win}'] = df['Volume'].rolling(window=vma_win,
                                                   min_periods=1).mean()

    addplot = [
        # Plot of Price Moving Average
        *[mpf.make_addplot(df[f'MA {n}'], panel=0, label=f'MA {n}')
            for n in ma_wins],

        # Plot of Relative Strength
        mpf.make_addplot(df['RS'], panel=1, label=ticker,
                         color='green', ylabel='Relative Strength'),
        mpf.make_addplot([100]*len(df), panel=1, label=si.get_name(ticker_ref),
                         linestyle='--', color='gray'),

        # Plot of Volume Moving Average
        mpf.make_addplot(df[f'VMA {vma_win}'], panel=2,
                         label=f'VMA {vma_win}', color='purple'),
    ]

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                      market_color_style=mc_style)

    # Plot candlesticks, MA, volume, volume MA, and RS
    fig, axes = mpf.plot(
        df, type='candle',              # candlesticks
        #main_panel=0,
        volume=True, volume_panel=2,    # volume
        addplot=addplot,                # MA, RS, and Volume MA
        panel_ratios=(5, 3, 2),
        figratio=(2, 1), figscale=1.2,
        style=mpf_style,
        show_nontrading=not hides_nontrading,
        returnfig=True,
    )
    # Set location of legends
    for ax in axes:
        if ax.legend_:
            ax.legend(loc=legend_loc)

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{symbol} - {interval} "
                 f"({df.index[0]} to {df.index[-1]})"
                 f"; RS: {rs_window}", y=0.93)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == '__main__':
    mpfu.use_mac_chinese_font()
    plot('TSLA', interval='1d', rs_window='3mo', hides_nontrading=True)
    #plot('台積電', interval='1wk')

