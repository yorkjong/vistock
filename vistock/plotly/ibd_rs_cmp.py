"""
ibd_rs_cmp - A module for plotting Relative Strength (RS) comparisons of
multiple stocks.

This module provides functionality to plot the Relative Strength (RS) of
multiple stocks compared to a reference index (e.g., S&P 500 or Taiwan Weighted
Index) using Plotly. It fetches historical stock data from Yahoo Finance,
calculates RS values, and generates an interactive Plotly chart. The resulting
chart can be saved as an HTML file.

Functions:
- plot: Generates a Relative Strength comparison plot for multiple stocks.

Usage:
    To use this module, call the `plot` function with a list of stock symbols
    and desired parameters.
"""
__software__ = "IBD RS Comparison chart"
__version__ = "2.4"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/16 (initial version) ~ 2024/10/05 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from .. import tw
from .. import file_utils
from . import fig_utils as futil
from ..ibd import relative_strength, relative_strength_3m
from .. import stock_indices as si


def plot(symbols, period='2y', interval='1d', ticker_ref=None,
         rs_period='12mo',
         template='plotly', colorway=px.colors.qualitative.Set3,
         hides_nontrading=True, out_dir='out'):
    """
    Plot the Relative Strength (RS) of multiple stocks compared to a reference
    index.

    This function generates an interactive Plotly chart that compares the RS
    values of the specified stocks against a reference index (e.g., S&P 500
    or Taiwan Weighted Index).  The chart includes RS lines for each stock and
    can be customized based on the selected period and interval. The resulting
    plot is saved as an HTML file in the specified output directory.

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
        The interval for data points ('1d' for daily, '1wk' for weekly; default
        is '1d').

    ticker_ref : str, optional
        The ticker symbol of the reference index. If None, defaults to S&P
        500 ('^GSPC') or Taiwan Weighted Index ('^TWII') if the first stock
        is a Taiwan stock.

    rs_period : str, optional
        Specify the period for Relative Strength calculation ('12mo' or '3mo').
        Default to '12mo'.

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

    colorway: list or None
        Sets the default trace colors for the plot. If None, Plotly's
        default color sequence will be used. You can pass a list of custom
        colors or choose from Plotly's predefined color sequences.

        By default, this is set to `px.colors.qualitative.Set3`, which
        consists of 24 vibrant colors.

        Useful predefined color sequences include:

        - px.colors.qualitative.Light24 (24 colors, vibrant and varied)
        - px.colors.qualitative.Dark24 (24 colors, darker tones)
        - px.colors.qualitative.Pastel (26 colors, soft pastel tones)
        - px.colors.qualitative.Bold (26 colors, bold and distinct)
        - px.colors.qualitative.Alphabet (26 colors, one for each letter)
        - px.colors.qualitative.Set3 (12 colors, good for categorical data)
        - px.colors.qualitative.G10 (10 colors, general use)
        - px.colors.qualitative.T10 (10 colors, clear and bright)
        - px.colors.qualitative.Plotly (10 colors, default Plotly colors)

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
            ticker_ref = '^TWII'  # Taiwan Weighted index

    # Download data
    tickers = [tw.as_yfinance(s) for s in symbols]
    df = yf.download([ticker_ref]+tickers, period=period, interval=interval)
    df = df.xs('Close', level='Price', axis=1)

    # Select the appropriate relative strength function based on the rs_period
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_period]

    fig = go.Figure()
    for ticker, symbol in zip(tickers, symbols):
        rs = rs_func(df[ticker], df[ticker_ref], interval)
        fig.add_trace(go.Scatter(x=rs.index, y=rs, mode='lines',
                                 name=si.get_name(symbol)))
    df[f'RS {ticker_ref}'] = 100
    fig.add_trace(go.Scatter(x=df.index, y=df[f'RS {ticker_ref}'],
                             mode='lines', name=si.get_name(ticker_ref),
                             line=dict(dash='dash', color='gray')))

    # Convert datetime index to string format suitable for display
    df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        title=f'IBD Relative Strength Comparison - {interval} '
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
    if colorway:
        fig.update_layout(colorway=colorway)

    if hides_nontrading:
        futil.hide_nontrading_periods(fig, df, interval)

    # For Crosshair cursor
    futil.add_crosshair_cursor(fig)
    futil.add_hovermode_menu(fig, x=0, y=1.1)

    # Show the figure
    fig.show()

    # Write the figure to an HTML file
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info('stocks', interval, df.index[-1], __file__)
    fig.write_html(f'{out_dir}/{fn}.html')


#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------

def main():
    symbols = ['NVDA', 'MSFT', 'META', '^NDX', '^TWII']
    plot(symbols, interval='1d', template='plotly_dark')
    symbols = ['羅昇', '昆盈', '穎漢', '光聖', '所羅門']
    plot(symbols, interval='1wk', template='xgridoff')


if __name__ == '__main__':
    main()

