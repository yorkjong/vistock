"""
Mansfield Stock Charts
======================

This module provides functionality for generating and plotting Mansfield Stock
Charts and Mansfield Relative Strength (RSM) charts based on the methods
outlined in Stan Weinstein's book "Secrets for Profiting in Bull and Bear
Markets." It includes two main classes for creating visualizations:

1. StockChart:
    - Generates a Mansfield Stock Chart for a given stock symbol compared to a
      reference index.
    - Allows customization of chart elements such as moving averages, chart
      templates, and hiding non-trading periods.

2. RelativeStrengthLines:
    - Plots the Mansfield Relative Strength (RSM) of multiple stocks compared
      to a reference index.
    - Allows comparison of multiple stocks’ RS values against a reference index
      with customization options for the time period, data interval, and moving
      average type.

Usage:
------
To generate a Mansfield Stock Chart:
    >>> StockChart.plot('TSLA', interval='1wk')

To generate a Relative Strength Lines chart for multiple stocks:
    >>> RelativeStrengthLines.plot(['NVDA', 'MSFT', 'META'], interval='1wk')

See Also:
---------
- `Mansfield relative strength | TrendSpider Store
  <https://trendspider.com/trading-tools-store/indicators/
  mansfield-relative-strength/>`_
"""
__software__ = "Mansfield Stock Charts"
__version__ = "1.7"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/24 (initial version) ~ 2024/08/26 (last revision)"

__all__ = [
    'StockChart',
    'RelativeStrengthLines',
]

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_util
from . import fig_utils as futil
from ..util import MarketColorStyle, decide_market_color_style
from .. import stock_indices as si
from ..ta import simple_moving_average, exponential_moving_average
from ..rsm import mansfield_relative_strength
from ..rsm import mansfield_relative_strength_with_ema


class StockChart:
    """A class for generating and plotting Mansfield Stock Charts based on Stan
    Weinstein's methods outlined in the book "Secrets for Profiting in Bull and
    Bear Markets."
    """
    @staticmethod
    def plot(symbol, period='2y', interval='1wk', ticker_ref=None, ma='SMA',
             market_color_style=MarketColorStyle.AUTO,
             template='plotly', hides_nontrading=True, out_dir='out'):
        """Plot a Mansfield Stock Chart for a given stock symbol and time
        period.

        Parameters
        ----------
        symbol: str
            the stock symbol.

        period: str, optional
            the period data to download. Valid values are 1y, 2y, 5y, 10y, ytd,
            max. Default is '2y'.

            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval: str, optional
            the interval of an OHLC item. Valid values are 1d, 1wk, 1mo, 3mo.
            Default is '1wk'.

            - d -- days
            - wk -- weeks
            - mo -- months

        ticker_ref : str, optional
            The ticker symbol of the reference index. If None, defaults to S&P
            500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock
            is a Taiwan stock.

        ma : str, optional
            Moving average type ('SMA', 'EMA'). Default to 'SMA'.

        market_color_style : MarketColorStyle, optional
            Color style for market data visualization. Default is
            MarketColorStyle.AUTO.

        template: str, optional:
            The Plotly template to use for styling the chart.
            Defaults to 'plotly'. Available templates include:

            - 'plotly': Default Plotly template with interactive plots.
            - 'plotly_white': Light theme with a white background.
            - 'plotly_dark': Dark theme for the chart background.
            - 'ggplot2': Style similar to ggplot2 from R.
            - 'seaborn': Style similar to Seaborn in Python.
            - 'simple_white': Minimal white style with no gridlines.
            - 'presentation': Designed for presentations with a clean look.
            - 'xgridoff': Plot with x-axis gridlines turned off.
            - 'ygridoff': Plot with y-axis gridlines turned off.

            For more details on templates, refer to Plotly's official
            documentation.

        hides_nontrading : bool, optional
            Whether to hide non-trading periods. Default is True.
        out_dir : str, optional
            Directory to save the output HTML file. Default is 'out'.

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
            rs_window = { '1d': 200, '1wk': 52, '1mo': 10 }[interval]
            ma_windows = {
                '1d': [50, 150, 200],
                '1wk': [10, 30],
                '1mo': [10,],
            }[interval]
        except KeyError:
            raise ValueError("Invalid interval. "
                             "Must be '1d', '1wk', or '1mo'.")
        vma_window, *_ = ma_windows

        # Select the RSM function based on the 'ma' parameter
        try:
            rsm_func = {
                'SMA': mansfield_relative_strength,
                'EMA': mansfield_relative_strength_with_ema
            }[ma]
        except KeyError:
            raise ValueError("Invalid ma type. Must be 'SMA' or 'EMA'.")

        # Select the MA function based on the 'ma' parameter
        try:
            ma_func = {
                'SMA': simple_moving_average,
                'EMA': exponential_moving_average,
            }[ma]
        except KeyError:
            raise ValueError("Invalid ma type. Must be 'SMA' or 'EMA'.")
        ma = ma.replace('SMA', 'MA')

        # Fetch data for stock and index
        df = yf.download([ticker_ref, ticker], period=period, interval=interval)
        df_ref = df.xs(ticker_ref, level='Ticker', axis=1)
        df = df.xs(ticker, level='Ticker', axis=1)

        # Calculate Mansfield Relative Strength (RSM)
        df['RSM'] = rsm_func(df['Close'], df_ref['Close'], rs_window)
        df[f'RS {ticker_ref}'] = 0

        # Calculate moving averages for stock
        for window in ma_windows:
            df[f'{ma}{window}'] = ma_func(df['Close'], window)

        # Calculate volume MA
        df[f'Vol {ma}{vma_window}'] = ma_func(df['Volume'], vma_window)

        # Create subplots
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.02, row_heights=[0.5, 0.3, 0.2])

        # colors of candlesticks
        mc_style = decide_market_color_style(ticker, market_color_style)
        mc_colors = futil.get_candlestick_colors(mc_style)

        # colors of volume bars
        cl = futil.get_volume_colors(mc_style)
        vol_colors = [cl['up'] if c >= o
                      else cl['down'] for o, c in zip(df['Open'], df['Close'])]

        # Plot the figure
        price_row, rsm_row, vol_row = 1, 2, 3
        traces = [
            # Stock Price and Moving Averages
            (go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name='Candle', **mc_colors),
             price_row),
            *[(go.Scatter(x=df.index, y=df[f'{ma}{window}'],
                          name=f'{ma}{window}'), price_row)
              for window in ma_windows],

            # RSM and zero line
            (go.Scatter(x=df.index, y=df['RSM'], name='RS',
                        line=dict(color='green', width=2)), rsm_row),
            (go.Scatter(x=df.index, y=df[f'RS {ticker_ref}'],
                        mode='lines', name=si.get_name(ticker_ref),
                        line=dict(dash='dash', color='gray')), rsm_row),

            # Volume and Volume MA
            (go.Bar(x=df.index, y=df['Volume'], name='Volume',
                    marker_color=vol_colors, opacity=0.5), vol_row),
            (go.Scatter(x=df.index, y=df[f'Vol {ma}{vma_window}'],
                        name=f'Vol {ma}{vma_window}',
                        line=dict(color='purple', width=2)), vol_row),
        ]
        for trace, row in traces:
            fig.add_trace(trace, row=row, col=1)

        # Convert datetime index to string format suitable for display
        df.index = df.index.strftime('%Y-%m-%d')

        # Update layout
        fig.update_layout(
            title=f'Mansfield Stock Charts: {ticker} - {interval} '
                  f'({df.index[0]} to {df.index[-1]})',
            title_x=0.5, title_y=0.92,

            xaxis=dict(anchor='free'),
            yaxis=dict(title='Price', side='right'),
            xaxis2=dict(anchor='free'),
            yaxis2=dict(title='Relative Strength', side='right'),
            yaxis3=dict(title='Volume', side='right'),
            legend=dict(yanchor='bottom', y=0.01, xanchor="left", x=0.01),
            height=1000,
            xaxis_rangeslider_visible=False,
            template=template,
        )
        if hides_nontrading:
            futil.hide_nontrading_periods(fig, df, interval)

        # For Crosshair cursor
        futil.add_crosshair_cursor(fig)
        futil.add_hovermode_menu(fig)

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info(symbol, interval, df.index[-1], 'RSM')
        fig.write_html(f'{out_dir}/{fn}.html')


class RelativeStrengthLines:
    """
    A class for plotting Mansfield Relative Strength (RSM) lines of multiple
    stocks compared to a reference index.

    This class generates an interactive Plotly chart that compares the Relative
    Strength (RS) of multiple stocks against a reference index (e.g., S&P 500
    or Taiwan Weighted Index). It provides a visualization of how each stock's
    RS changes over time relative to the reference index, with options to
    customize the time period, data interval, and moving average type.
    """
    @staticmethod
    def plot(symbols, period='2y', interval='1d', ticker_ref=None, ma='SMA',
             template='plotly', hides_nontrading=True, out_dir='out'):
        """
        Plot the Mansfield Relative Strength (RSM) of multiple stocks compared
        to a reference index.

        This function generates an interactive Plotly chart that compares the
        RS values of the specified stocks against a reference index (e.g.,
        S&P 500 or Taiwan Weighted Index).  The chart includes RS lines for
        each stock and can be customized based on the selected period and
        interval. The resulting plot is saved as an HTML file in the specified
        output directory.

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

        template: str, optional:
            The Plotly template to use for styling the chart.
            Defaults to 'plotly'. Available templates include:

            - 'plotly': Default Plotly template with interactive plots.
            - 'plotly_white': Light theme with a white background.
            - 'plotly_dark': Dark theme for the chart background.
            - 'ggplot2': Style similar to ggplot2 from R.
            - 'seaborn': Style similar to Seaborn in Python.
            - 'simple_white': Minimal white style with no gridlines.
            - 'presentation': Designed for presentations with a clean look.
            - 'xgridoff': Plot with x-axis gridlines turned off.
            - 'ygridoff': Plot with y-axis gridlines turned off.

            For more details on templates, refer to Plotly's official
            documentation.

        hides_nontrading : bool, optional
            Whether to hide non-trading periods on the plot. Defaults to True.
        out_dir : str, optional
            Directory to save the HTML file. Defaults to 'out'.

        Returns
        --------
        None
            The function generates a plot and saves it as an HTML file.

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
            rs_window = { '1d': 200, '1wk': 52, '1mo': 10 }[interval]
        except KeyError:
            raise ValueError("Invalid interval. Must be '1d', '1wk', or '1mo'.")

        # Select the RSM function based on the 'ma' parameter
        try:
            rsm_func = {
                'SMA': mansfield_relative_strength,
                'EMA': mansfield_relative_strength_with_ema
            }[ma]
        except KeyError:
            raise ValueError("Invalid ma. Must be 'SMA' or 'EMA'.")

        # Fetch data for stocks and index
        tickers = [tw.as_yfinance(s) for s in symbols]
        df = yf.download([ticker_ref]+tickers, period=period, interval=interval)
        df = df.xs('Close', level='Price', axis=1)

        # Plot the figure
        fig = go.Figure()
        for ticker, symbol in zip(tickers, symbols):
            rs = rsm_func(df[ticker], df[ticker_ref], rs_window)
            fig.add_trace(go.Scatter(x=rs.index, y=rs, mode='lines',
                                     name=si.get_name(symbol)))
        df[f'RS {ticker_ref}'] = 0
        fig.add_trace(go.Scatter(x=df.index, y=df[f'RS {ticker_ref}'],
                                 mode='lines', name=si.get_name(ticker_ref),
                                 line=dict(dash='dash', color='gray')))

        # Convert datetime index to string format suitable for display
        df.index = df.index.strftime('%Y-%m-%d')

        # Update layout
        fig.update_layout(
            title=f'Mansfield Relative Strength Comparison - {interval} '
                  f'({df.index[0]} to {df.index[-1]})',
            title_x=0.5, title_y=0.87,
            yaxis=dict(title='Relative Strength '
                             f'(Compared to {si.get_name(ticker_ref)})',
                       side='right'),
            #height=600,
            legend_title='Stocks',
            legend=dict(yanchor='top', y=.98, xanchor="left", x=0.01),
            xaxis_rangeslider_visible=False,
            template=template,
        )
        if hides_nontrading:
            futil.hide_nontrading_periods(fig, df, interval)

        # For Crosshair cursor
        futil.add_crosshair_cursor(fig)
        futil.add_hovermode_menu(fig, x=0, y=1.1)

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info('stocks', interval, df.index[-1], 'RsmLines')
        fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    #StockChart.plot('TSLA', interval='1d')
    StockChart.plot('TSLA', interval='1wk')

    symbols = ['羅昇', '昆盈', '穎漢', '光聖', '所羅門']
    RelativeStrengthLines.plot(symbols, interval='1d')


