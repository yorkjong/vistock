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
    from vistock.plotly import ibd_rs
    ibd_rs.plot('TSLA', period='1y', interval='1d')
"""
__software__ = "IBD-compatible stock chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/08/16 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_util
from . import fig_util as futil
from ..util import MarketColorStyle, decide_market_color_style, is_taiwan_stock
from ..ibd import relative_strength


#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------

def ma_window_size(interval, days):
    """Calculate window size based on interval.

    Args:
        interval (str): The data interval ('1d' or '1wk').
        days (int): Number of days for the window.

    Returns:
        int: Calculated window size.

    Raises:
        ValueError: If an unsupported interval is provided.
    """
    if interval == '1d':
        return days
    elif interval == '1wk':
        return days // 5  # 1 week = 5 trading days
    else:
        raise ValueError("Unsupported interval")


def calc_moving_averages(df, interval, window_days):
    """Calculate moving averages based on window days"""
    for days in window_days:
        window_size = ma_window_size(interval, days)
        df[f'{days}d_MA'] = df['Close'].rolling(window=window_size).mean()
    return df


def calc_volume_moving_average(df, interval, days):
    """Calculate volume moving average based on interval"""
    window_size = ma_window_size(interval, days)
    df[f'Volume_MA{days}'] = df['Volume'].rolling(window=window_size).mean()
    return df

#------------------------------------------------------------------------------

def create_candlestick_trace(df, mc_style):
    """Create candlestick trace"""
    mc_colors = futil.get_candlestick_colors(mc_style)
    return go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC',
        **mc_colors
    )


def create_moving_average_traces(df, interval):
    """Create moving average traces with names adjusted for interval"""
    traces = []
    for ma_col in ['50d_MA', '200d_MA']:
        if ma_col in df.columns:
            # Extract the number of days from column name
            days = int(ma_col.split('d')[0])

            name = {
                '1d': f'{days} day MA',
                '1wk': f'{days//5} week MA',
            }[interval]
            traces.append(go.Scatter(
                x=df.index, y=df[ma_col],
                mode='lines', name=name,
                line=dict(color='blue' if '50d' in ma_col else 'red', width=2)
            ))
    return traces


def create_volume_trace(df, mc_style):
    """Create volume trace"""
    cl = futil.get_volume_colors(mc_style)
    colors = [cl['up'] if c >= o
              else cl['down'] for o, c in zip(df['Open'], df['Close'])]
    return go.Bar(x=df.index, y=df['Volume'], name='Volume',
                  marker_color=colors, opacity=0.5)


def create_volume_ma_trace(df, interval):
    """Create volume moving average trace with name adjusted for interval"""
    name = '50-day Volume MA'
    if interval == '1wk':
        name = '10-week Volume MA'
    return go.Scatter(
        x=df.index, y=df['Volume_MA50'],
        mode='lines', name=name,
        line=dict(color='purple', width=2)
    )


def create_rs_trace(rs_ratio):
    """Create Relative Strength trace"""
    return go.Scatter(
        x=rs_ratio.index, y=rs_ratio,
        mode='lines', name='RS',
        line=dict(color='green', width=2)
    )


#------------------------------------------------------------------------------
# The Plot Function
#------------------------------------------------------------------------------

def plot(symbol, period='2y', interval='1d', ref_ticker=None,
         hides_nontrading=True, market_color_style=MarketColorStyle.AUTO,
         out_dir='out'):
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
        the period data to download. Valid values are 6mo, 1y, 2y, 5y, 10y,
        ytd, max.

        * mo  -- monthes
        * y   -- years
        * ytd -- year to date
        * max -- all data

    interval: str
        The interval for data points ('1d' for daily, '1wk' for weekly; default
        is '1d').
    ref_ticker : str, optional
        The reference ticker for calculating Relative Strength. Defaults to
        '^GSPC' (S&P 500) or '^TWII' (Taiwan Weighted Index) for Taiwan stocks.
    hides_nontrading : bool, optional
        Whether to hide non-trading periods. Default is True.
    market_color_style : MarketColorStyle, optional
        Color style for market data visualization. Default is
        MarketColorStyle.AUTO.
    out_dir : str, optional
        Directory to save the output HTML file. Default is 'out'.

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
    rs_ratio = relative_strength(df['Close'], def_ref['Close'], interval)

    # Calculate moving averages
    df = calc_moving_averages(df, interval, [50, 200])
    df = calc_volume_moving_average(df, interval, 50)

    # Create subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        vertical_spacing=0.01,
                        row_heights=[0.5, 0.3, 0.2],
                        figure=go.Figure(layout=go.Layout(height=1000)))

    # Add traces
    mc_style = decide_market_color_style(ticker, market_color_style)

    fig.add_trace(create_candlestick_trace(df, mc_style))
    for trace in create_moving_average_traces(df, interval):
        fig.add_trace(trace)

    fig.add_trace(create_rs_trace(rs_ratio), row=2, col=1)
    fig.add_hline(y=100, line_dash="dash", line_color="gray", row=2, col=1)

    fig.add_trace(create_volume_trace(df, mc_style), row=3, col=1)
    fig.add_trace(create_volume_ma_trace(df, interval), row=3, col=1)

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        title=f'{symbol} {interval} '
              f'({df.index.values[0]}~{df.index.values[-1]})',
        title_x=0.5, title_y=0.92,
        legend=dict(yanchor='bottom', y=0.01, xanchor="left", x=0.01),

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x3', title='Price', side='right'),
        xaxis2=dict(anchor='free'),
        yaxis2=dict(title='IBD Relative Strength', side='right'),
        yaxis3=dict(title='Volume', side='right'),

        xaxis_rangeslider_visible=False,
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
    fn = file_util.gen_fn_info(symbol, interval, df.index.values[-1], __file__)
    fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    plot('TSLA', interval='1wk')

