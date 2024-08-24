"""
weinstein.py -- Stan Weinstein's Stock Charts

This module provides functionality for generating Mansfield Stock Charts based
on Stan Weinstein's methods outlined in the book "Secrets for Profiting in Bull
and Bear Markets."

It includes:
- Downloading stock and index data.
- Calculating Mansfield Relative Strength (RSM) using Simple Moving Average
  (SMA) or Exponential Moving Average (EMA).
- Plotting stock price, moving averages, Mansfield RS, and volume data using
  Plotly.
- Saving the resulting charts as interactive HTML files.

Classes:
- StockChart: A class for creating and plotting Mansfield Stock Charts.

Usage:
- Import the StockChart class and call the `plot` method with desired
  parameters to generate the chart.

See Also:
- `Mansfield relative strength | TrendSpider Store
  <https://trendspider.com/trading-tools-store/indicators/
  mansfield-relative-strength/>`_
"""
__software__ = "Stan Weinstein's stock charts"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/24 (initial version) ~ 2024/08/25 (last revision)"

__all__ = [
    'StockChart',
]

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import file_util
from . import fig_util as futil
from ..util import MarketColorStyle, decide_market_color_style
from ..rsm import mansfield_relative_strength
from ..rsm import mansfield_relative_strength_with_ema


class StockChart:
    """A class for generating and plotting Mansfield Stock Charts based on Stan
    Weinstein's methods outlined in the book "Secrets for Profiting in Bull and
    Bear Markets."
    """
    def plot(symbol, period='2y', interval='1wk', ticker_ref="^GSPC", ma='SMA',
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
            if is_taiwan_stock(ticker):
                ticker_ref = '^TWII'  # Taiwan Weighted Index

        ma_windows = np.array([10, 30, 40]) # weekly settings
        if interval == '1mo':
            ma_windows = [10,]
            rs_window = 10
        elif interval == '1wk':
            ma_windows = [10, 30]
            rs_window = 52
        elif interval == '1d':
            ma_windows = [50, 150, 200]
            rs_window = 200
        else:
            raise ValueError("Invalid interval. Must be '1wk' or '1d'.")
        vma_window = ma_windows[0]

        # Fetch data for stock and index
        df = yf.download([ticker_ref, ticker], period=period, interval=interval)
        df_ref = df.xs(ticker_ref, level='Ticker', axis=1)
        df = df.xs(ticker, level='Ticker', axis=1)

        # Calculate Mansfield Relative Strength (RSM)
        rsm = {
            'SMA': mansfield_relative_strength,
            'EMA': mansfield_relative_strength_with_ema
        }[ma]
        df['RSM'] = rsm(df['Close'], df_ref['Close'], rs_window)
        df['0'] = 0

        # Calculate moving averages for stock
        for window in ma_windows:
            df[f'MA{window}'] = df['Close'].rolling(window=window).mean()

        # Calculate volume MA
        df[f'VMA{vma_window}'] = df['Volume'].rolling(window=vma_window).mean()

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

        price_row, rsm_row, vol_row = 1, 2, 3
        traces = [
            # Stock Price and Moving Averages
            (go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name='Candle', **mc_colors),
             price_row),
            *[(go.Scatter(x=df.index, y=df[f'MA{window}'], name=f'MA{window}'),
               price_row) for window in ma_windows],

            # RSM and zero line
            (go.Scatter(x=df.index, y=df['RSM'], name='RS'), rsm_row),
            (go.Scatter(x=df.index, y=df['0'], mode='lines', name='Zero Line',
                        line=dict(dash='dash', color='gray')), rsm_row),

            # Volume and Volume MA
            (go.Bar(x=df.index, y=df['Volume'], name='Volume',
                    marker_color=vol_colors, opacity=0.5), vol_row),
            (go.Scatter(x=df.index,
                        y=df[f'VMA{vma_window}'], name=f'Vol MA{vma_window}'),
             vol_row),

        ]
        for trace, row in traces:
            fig.add_trace(trace, row=row, col=1)

        # Convert datetime index to string format suitable for display
        df.index = df.index.strftime('%Y-%m-%d')

        # Update layout
        fig.update_layout(
            title=f'Mansfield Stock Charts: {ticker} - {interval} '
                  f'({df.index[0]} to {df.index[-1]})',
            title_x=0.5, title_y=.9,

            xaxis=dict(anchor='free'),
            yaxis=dict(title='Price', side='right'),
            xaxis2=dict(anchor='free'),
            yaxis2=dict(title='Relative Strength', side='right'),
            yaxis3=dict(title='Volume', side='right'),
            legend=dict(yanchor='bottom', y=0.01, xanchor="left", x=0.01),
            height=700,
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


if __name__ == '__main__':
    #StockChart.plot('TSLA', interval='1d')
    StockChart.plot('TSLA', interval='1wk')
    #StockChart.plot('TSLA', interval='1mo')

