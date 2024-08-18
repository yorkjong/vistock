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
__version__ = "1.4"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/08/18 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_util
from ..util import MarketColorStyle, decide_market_color_style, is_taiwan_stock
from .mpf_util import decide_mpf_style
from ..ibd import relative_strength, ma_window_size
from .. import stock_indices as si


def plot(symbol, period='2y', interval='1d', ref_ticker=None,
         legend_loc='best', market_color_style=MarketColorStyle.AUTO,
         style='yahoo', hides_nontrading=True, out_dir='out'):
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
        The ticker symbol of the reference index. If None, defaults to S&P
        500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock is
        a Taiwan stock.

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

    market_color_style : MarketColorStyle, optional
        Color style for market data visualization. Default is
        MarketColorStyle.AUTO.

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
    df = yf.download([ref_ticker, ticker], period=period, interval=interval)
    df_ref = df.xs(ref_ticker, level=1, axis=1)
    df = df.xs(ticker, level=1, axis=1)

    # Calculate Relative Strength (RS)
    df['RS'] = relative_strength(df['Close'], df_ref['Close'], interval)

    # Calculate price moving average
    ma_nitems = [ma_window_size(interval, days) for days in (50, 200)]
    for n in ma_nitems:
        df[f'MA {n}'] = df['Close'].rolling(window=n).mean()

    # Calculate volume moving averaage
    vma_nitems = ma_window_size(interval, 50)
    df[f'VMA {vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()

    addplot = [
        # Plot of Price Moving Average
        *[mpf.make_addplot(df[f'MA {n}'], panel=0, label=f'MA {n}')
            for n in ma_nitems],

        # Plot of Relative Strength
        mpf.make_addplot(df['RS'], panel=1, label=ticker,
                         color='green', ylabel='Relative Strength'),
        mpf.make_addplot([100]*len(df), panel=1, label=si.get_name(ref_ticker),
                         linestyle='--', color='gray'),

        # Plot of Volume Moving Average
        mpf.make_addplot(df[f'VMA {vma_nitems}'], panel=2,
                         label=f'VMA {vma_nitems}', color='purple'),
    ]

    # Make a customized color style
    mc_style = decide_market_color_style(ticker, market_color_style)
    mpf_style = decide_mpf_style(base_mpf_style=style,
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
    fig.suptitle(f"{ticker} - {interval} "
                 f"({df.index[0]} to {df.index[-1]})", y=0.93)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_util.make_dir(out_dir)
    fn = file_util.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == '__main__':
    plot('TSLA', interval='1d', hides_nontrading=True)
    plot('台積電', interval='1wk')

