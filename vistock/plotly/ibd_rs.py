"""
ibd_rs.py - Provides IBD-compatible stock charts.

This module provides functionality for analyzing and plotting stock data
with a focus on Investor's Business Daily (IBD) Relative Strength metrics.
It includes capabilities for generating candlestick charts with moving averages,
volume analysis, and relative strength comparisons.

The main function 'plot' allows users to visualize stock performance
over various time periods and intervals, with customizable reference indexes
and styling options.

Usage:
::

    from vistock.plotly import ibd_rs
    ibd_rs.plot('TSLA', period='1y', interval='1d')
"""
__software__ = "IBD-compatible stock chart"
__version__ = "1.9"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/10/03 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_utils
from . import fig_utils as futil
from ..utils import MarketColorStyle, decide_market_color_style
from ..ibd import relative_strength, relative_strength_3m, ma_window_size
from .. import stock_indices as si


def plot(symbol, period='2y', interval='1d', ticker_ref=None, rs_period='12mo',
         market_color_style=MarketColorStyle.AUTO,
         template='plotly', hides_nontrading=True, out_dir='out'):
    """Generate and display a stock analysis plot with candlestick charts,
    moving averages, volume analysis, and Relative Strength (RS) metrics.

    Creates an interactive Plotly figure showing:
        - Candlestick chart of the stock with moving averages.
        - Relative Strength (RS) indicator in a separate subplot.
        - Volume and volume moving average in another subplot.

    The figure is saved as an HTML file in the specified output directory.

    Parameters
    ----------
    symbol: str
        The stock symbol to analyze.
    period: str
        the period data to download. . Defaults to '2y'. Valid values are
        6mo, 1y, 2y, 5y, 10y, ytd, max.

        - mo  -- monthes
        - y   -- years
        - ytd -- year to date
        - max -- all data

    interval: str
        The interval for data points ('1d' for daily, '1wk' for weekly; default
        is '1d').
    ticker_ref : str, optional
        The ticker symbol of the reference index. If None, defaults to S&P
        500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock
        is a Taiwan stock.
    rs_period : str, optional
        Specify the period for Relative Strength calculation ('12mo' or '3mo').
        Default to '12mo'.

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

    # Download data
    df = yf.download([ticker_ref, ticker], period=period, interval=interval)
    df_ref = df.xs(ticker_ref, level='Ticker', axis=1)
    df = df.xs(ticker, level='Ticker', axis=1)

    # Select the appropriate relative strength function based on the rs_period
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_period]

    # Calculate Relative Strength (RS)
    df['RS'] = rs_func(df['Close'], df_ref['Close'], interval)
    df[f'RS {ticker_ref}'] = 100

    # Calculate price moving average
    ma_nitems = [ma_window_size(interval, days) for days in (50, 200)]
    for n in ma_nitems:
        df[f'MA {n}'] = df['Close'].rolling(window=n, min_periods=1).mean()

    # Calculate volume moving averaage
    vma_nitems = ma_window_size(interval, 50)
    df[f'VMA {vma_nitems}'] = df['Volume'].rolling(window=vma_nitems,
                                                   min_periods=1).mean()

    # Create subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.01,
                        row_heights=[0.5, 0.3, 0.2],
                        figure=go.Figure(layout=go.Layout(height=1000)))

    # Add traces
    mc_style = decide_market_color_style(ticker, market_color_style)
    mc_colors = futil.get_candlestick_colors(mc_style)

    cl = futil.get_volume_colors(mc_style)
    vol_colors = [cl['up'] if c >= o
                  else cl['down'] for o, c in zip(df['Open'], df['Close'])]

    main_row, rs_row, vol_row = 1, 2, 3
    traces = [
        # Main subplot
        (go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'], name='Candle',
                        **mc_colors), main_row),
        *[(go.Scatter(x=df.index, y=df[f'MA {n}'],
                      mode='lines', name=f'MA {n}'), main_row)
          for n in ma_nitems],

        # RS subplot
        (go.Scatter(x=df.index, y=df['RS'], mode='lines', name='RS',
                    line=dict(color='green', width=2)), rs_row),
        (go.Scatter(x=df.index, y=df[f'RS {ticker_ref}'],
                    mode='lines', name=si.get_name(ticker_ref),
                    line=dict(dash='dash', color='gray')), rs_row),

        # Volume subplot
        (go.Bar(x=df.index, y=df['Volume'], name='Volume',
               marker_color=vol_colors, opacity=0.5), vol_row),
        (go.Scatter(x=df.index, y=df[f'VMA {vma_nitems}'],
                   mode='lines', name=f'VMA {vma_nitems}',
                   line=dict(color='purple', width=2)), vol_row),
    ]
    for trace, row in traces:
        fig.add_trace(trace, row=row, col=1)

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        title=f'{symbol} - {interval} '
              f'({df.index[0]} to {df.index[-1]})',
        title_x=0.5, title_y=0.92,
        legend=dict(yanchor='bottom', y=0.01, xanchor="left", x=0.01),

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x3', title='Price', side='right'),
        xaxis2=dict(anchor='free'),
        yaxis2=dict(title='IBD Relative Strength', side='right'),
        yaxis3=dict(title='Volume', side='right'),

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
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    plot('TSLA', interval='1d', template='simple_white')
    #plot('台積電', interval='1wk', template='presentation')

