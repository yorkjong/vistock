"""
Mansfield Stock Charts
======================
This module provides tools for generating and plotting Mansfield Stock Charts
based on Stan Weinstein's methods, as described in the book "Secrets for
Profiting in Bull and Bear Markets." It includes functionalities for
calculating and plotting Mansfield Relative Strength (RSM) using `mplfinance`
for visualization.

Classes:
--------
- StockChart : A class for generating and plotting Mansfield Stock Charts for
  individual stocks.
- RelativeStrengthLines : A class for plotting Mansfield Relative Strength
  (RSM) lines of multiple stocks compared to a reference index.

Dependencies:
-------------
- numpy
- pandas
- yfinance
- mplfinance
- Custom modules: tw, file_utils, utils, stock_indices, ta, rsm, mpf_utils

Usage:
------
To generate a Mansfield Stock Chart for a single stock:
    >>> StockChart.plot('TSLA', interval='1wk')

To compare the Mansfield Relative Strength of multiple stocks:
    >>> symbols = ['NVDA', 'MSFT', 'META', 'AAPL', 'TSM']
    >>> RelativeStrengthLines.plot(symbols, interval='1d')

See Also:
---------
- `Mansfield relative strength | TrendSpider Store
  <https://trendspider.com/trading-tools-store/indicators/
  mansfield-relative-strength/>`_
"""
__software__ = "Mansfield Stock Charts"
__version__ = "1.7"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/25 (initial version) ~ 2024/09/04 (last revision)"

__all__ = [
    'StockChart',
    'RelativeStrengthLines',
]

import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_utils
from ..utils import MarketColorStyle, decide_market_color_style
from . import mpf_utils as mpfu
from .. import stock_indices as si
from ..ta import simple_moving_average, exponential_moving_average
from ..rsm import mansfield_relative_strength


class StockChart:
    """
    A class for generating and plotting Mansfield Stock Charts.

    Mansfield Stock Charts are a method for visualizing stock trends and
    relative strength compared to a reference index, as popularized by Stan
    Weinstein. This class provides methods to fetch stock data, compute
    relative strength, and plot the resulting charts using mplfinance.
    """
    @staticmethod
    def plot(symbol, period='2y', interval='1d', ticker_ref=None, ma='SMA',
             legend_loc='best', market_color_style=MarketColorStyle.AUTO,
             style='yahoo', hides_nontrading=True, out_dir='out'):
        """Plot a Mansfield Stock Chart for a given stock symbol and time
        period.

        Parameters
        ----------
        symbol : str
            The stock symbol to analyze.
        period : str, optional
            The period of historical data to fetch. Valid values are '6mo', '1y',
            '2y', '5y', '10y', 'ytd', 'max'.  Default is '2y'.

            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval : str, optional
            The interval for data points. Valid values are '1d' for daily or '1wk'
            for weekly. Default is '1d'.

        ticker_ref : str, optional
            The ticker symbol of the reference index. If None, defaults to S&P
            500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock is
            a Taiwan stock.

        ma : str, optional
            Moving average type ('SMA', 'EMA'). Default to 'SMA'.

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

        hides_nontrading : bool, optional
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

        # Set moving average windows based on the interval
        try:
            rs_window = { '1d': 252, '1wk': 52, '1mo': 12 }[interval]
            ma_windows = {
                '1d': [50, 150, 200],
                '1wk': [10, 30, 40],
                '1mo': [3, 8, 10],
            }[interval]
        except KeyError:
            raise ValueError("Invalid interval. "
                             "Must be '1d', '1wk', or '1mo'.")
        vma_window, *_ = ma_windows

        # Select the MA function based on the 'ma' parameter
        try:
            ma_func = {
                'SMA': simple_moving_average,
                'EMA': exponential_moving_average,
            }[ma]
        except KeyError:
            raise ValueError("Invalid ma type. Must be 'SMA' or 'EMA'.")

        # Fetch data for stock and index
        df = yf.download([ticker_ref, ticker], period=period, interval=interval)
        df_ref = df.xs(ticker_ref, level='Ticker', axis=1)
        df = df.xs(ticker, level='Ticker', axis=1)

        # Calculate Mansfield Relative Strength (RSM)
        df['RSM'] = mansfield_relative_strength(df['Close'], df_ref['Close'],
                                                rs_window, ma=ma)

        # Calculate moving averages for stock
        ma = ma.replace('SMA', 'MA')
        for window in ma_windows:
            df[f'{ma}{window}'] = ma_func(df['Close'], window)

        # Calculate volume MA
        df[f'Vol {ma}{vma_window}'] = ma_func(df['Volume'], vma_window)

        # Plot the figure
        addplot = [
            # Plot of Price Moving Average
            *[mpf.make_addplot(df[f'{ma}{n}'], panel=0, label=f'{ma}{n}')
              for n in ma_windows],

            # Plot of Relative Strength
            mpf.make_addplot(df['RSM'], panel=1, label=ticker, color='green',
                             ylabel='Relative Strength'),
            mpf.make_addplot([0]*len(df), panel=1,
                             label=si.get_name(ticker_ref),
                             linestyle='--', color='gray', secondary_y=False),

            # Plot of Volume Moving Average
            mpf.make_addplot(df[f'Vol {ma}{vma_window}'], panel=2,
                             label=f'Vol {ma}{vma_window}', color='purple'),
        ]

        # Make a customized color style
        mc_style = decide_market_color_style(ticker, market_color_style)
        mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                          market_color_style=mc_style)

        # Plot candlesticks, MA, volume, volume MA, and RS
        fig, axes = mpf.plot(
            df, type='candle',              # candlesticks
            volume=True, volume_panel=2,    # volume
            addplot=addplot,                # MA, RS, and Volume MA
            panel_ratios=(5, 3, 2),
            figratio=(2, 1), figscale=1.4,
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
        fig.suptitle(f"Mansfield Stock Chart: {symbol} - {interval} "
                     f"({df.index[0]} to {df.index[-1]})", y=0.93)

        # Show the figure
        mpf.show()

        # Save the figure
        out_dir = file_utils.make_dir(out_dir)
        fn = file_utils.gen_fn_info(symbol, interval, df.index[-1], 'RSM')
        fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


class RelativeStrengthLines:
    """
    A class for plotting Mansfield Relative Strength (RSM) lines of multiple
    stocks.

    This class allows for the comparison of the relative strength of multiple
    stocks against a reference index over a specified period. It supports
    various intervals and moving average calculations (SMA and EMA) for the
    relative strength computation.
    """
    @staticmethod
    def plot(symbols, period='2y', interval='1d', ticker_ref=None, ma='SMA',
             legend_loc='best',
             style='checkers', hides_nontrading=True, out_dir='out'):
        """
        Plot the Mansfield Relative Strength (RSM) of multiple stocks compared
        to a reference index.

        Parameters
        ------------
        symbols : list of str
            List of stock symbols to compare. Can include both US and Taiwan
            stocks.
        period : str, optional
            the period data to download. . Defaults to '2y'. Valid values are
            6mo, 1y, 2y, 5y, 10y, ytd, max.

            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval : str, optional
            The interval for data points ('1d' for daily, '1wk' for weekly;
            default is '1d').
        ticker_ref : str, optional
            The ticker symbol of the reference index. If None, defaults to S&P
            500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock
            is a Taiwan stock.

        ma : str, optional
            Moving average type ('SMA', 'EMA'). Default to 'SMA'.

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
        if not ticker_ref:
            ticker_ref = '^GSPC'      # S&P 500 Index
            if tw.is_taiwan_stock(tw.as_yfinance(symbols[0])):
                ticker_ref = '^TWII'  # Taiwan Weighted Index

        # Set moving average windows based on the interval
        try:
            rs_window = { '1d': 252, '1wk': 52, '1mo': 12 }[interval]
        except KeyError:
            raise ValueError("Invalid interval. Must be '1d', '1wk', or '1mo'.")

        # Fetch data for stocks and index
        tickers = [tw.as_yfinance(s) for s in symbols]
        df = yf.download([ticker_ref]+tickers, period=period, interval=interval)
        df_price = df.xs('Close', level='Price', axis=1)

        # Plot the figure
        add_plots = []
        for ticker, symbol in zip(tickers, symbols):
            rs = mansfield_relative_strength(df_price[ticker],
                                             df_price[ticker_ref],
                                             rs_window, ma=ma)
            add_plots.append(mpf.make_addplot(rs,
                                              label=f'{si.get_name(symbol)}'))
        add_plots.append(
            mpf.make_addplot([0]*len(df), color='gray', linestyle='--',
                             label=f'{si.get_name(ticker_ref)}',
                             secondary_y=False)
        )

        # for hiding 'Close' line from the mpf.plot call
        df_dummy = df.xs(tickers[0], level='Ticker', axis=1).copy()
        for col in ['Open', 'High', 'Low', 'Close']:
            df_dummy[col] = rs

        fig, axes = mpf.plot(
            df_dummy, type='line',
            volume=False, addplot=add_plots,
            ylabel=f'Relative Strength (Compared to {si.get_name(ticker_ref)})',
            figratio=(2, 1), figscale=1.2,
            style=style,
            show_nontrading=not hides_nontrading,
            returnfig=True,
        )
        # Set location of legends
        for ax in axes:
            if ax.legend_:
                ax.legend(loc=legend_loc)

        # Convert datetime index to string format suitable for display
        df.index = df.index.strftime('%Y-%m-%d')
        fig.suptitle(f"Mansfield Relative Strength Comparison - {interval} "
                     f"({df.index[0]} to {df.index[-1]})", y=0.93)

        # Show the figure
        mpf.show()

        # Save the figure
        out_dir = file_utils.make_dir(out_dir)
        fn = file_utils.gen_fn_info('stocks', interval, df.index[-1], 'RsmLines')
        fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == '__main__':
    """
    Example usage of StockChart and RelativeStrengthLines classes to generate
    plots.
    """
    mpfu.use_mac_chinese_font()
    StockChart.plot('TSLA', interval='1wk')
    StockChart.plot('羅昇', interval='1wk')

    symbols = ['羅昇', '昆盈', '穎漢', '光聖', '所羅門']
    RelativeStrengthLines.plot(symbols, interval='1d')

    symbols = ['^NDX', '^DJA', '^RUI', '^SOX']
    RelativeStrengthLines.plot(symbols, interval='1d')

