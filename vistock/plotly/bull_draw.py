"""
Visualize a BullRun and Drawdown for a stock.
"""
__software__ = "BullRun & Drawdown"
__version__ = "1.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/21 (initial version) ~ 2024/08/20 (last revision)"

__all__ = [ 'plot' ]

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_utils
from . import fig_utils as futil
from ..bull_draw_utils import calculate_bull_run, calculate_drawdown
from ..utils import MarketColorStyle, decide_market_color_style


def plot(symbol='TSLA', period='1y', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         market_color_style=MarketColorStyle.AUTO,
         template='plotly', hides_nontrading=True, out_dir='out'):
    """Plot a stock figure that consists of two subplots: a price subplot and
    a volume subplot.

    The price subplot includes price lines, bull-run bar cahrt, and drawdown
    bar chart, while the volume subplot includes a volume histogram and a
    volume moving average line.

    Parameters
    ----------
    symbol: str
        the stock symbol.

    period: str, optional
        the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
        1y, 2y, 5y, 10y, ytd, max. Default is '1y'

        - d   -- days
        - mo  -- monthes
        - y   -- years
        - ytd -- year to date
        - max -- all data

    interval: str, optional
        the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
        60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Default is '1d'

        - m  -- minutes
        - h  -- hours
        - wk -- weeks
        - mo -- monthes

        Intraday data cannot extend last 60 days:

        - 1m - max 7 days within last 30 days
        - up to 90m - max 60 days
        - 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)

    ma_nitems: sequence of int
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int
        the number of data items to calculate the volume moving average.
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
    """
    # Download stock data
    ticker = tw.as_yfinance(symbol)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        #shared_xaxes=True,
        vertical_spacing=0.03,
        specs=[
            [{"secondary_y": True}],    # row 1, col 1
            [{"secondary_y": False}]    # row 2, col 1
        ],
        figure=go.Figure(layout=go.Layout(height=720))
    )

    # Add moving averages to the figure
    price = go.Scatter(x=df.index, y=df['Close'], name=f'Price',
                line=dict(color='brown', width=2), yaxis='y2'
            )
    fig.add_trace(price)

    # Automaticly decide market color style
    mc_style = decide_market_color_style(ticker, market_color_style)

    # Add bull-run trace to the figure
    cl = get_bullrun_color(mc_style)
    df['BullRun'] = calculate_bull_run(df)
    drawdown = go.Bar(x=df.index, y=df['BullRun'], name='BullRun',
                    marker_color=cl, opacity=0.5)
    fig.add_trace(drawdown)

    # Add drawdown trace to the figure
    cl = get_drawdown_color(mc_style)
    df['Drawdown'] = calculate_drawdown(df)
    drawdown = go.Bar(x=df.index, y=df['Drawdown'], name='Drawdown',
                    marker_color=cl, opacity=0.5)
    fig.add_trace(drawdown)

    # Get volume colors
    cl = futil.get_volume_colors(mc_style)

    # Add close-low diff trace to the figure
    df['Close-Low'] = (df['Close'] - df['Low']) / df['Close']
    diff = go.Bar(x=df.index, y=df['Close-Low'], name='Close-Low',
                  marker_color=cl['up'], opacity=0.5)
    fig.add_trace(diff)

    # Add close-high diff trace to the figure
    df['Close-High'] = (df['Close'] - df['High']) / df['Close']
    diff = go.Bar(x=df.index, y=df['Close-High'], name='Close-High',
                    marker_color=cl['down'], opacity=0.5)
    fig.add_trace(diff)

    fig.update_layout(barmode='overlay')

    # Add volume trace to 2nd row
    colors = [cl['up'] if c >= o
              else cl['down'] for o, c in zip(df['Open'], df['Close'])]
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume',
                    marker_color=colors, opacity=0.5)
    fig.add_trace(volume, row=2, col=1)

    # Add moving average volume to 2nd row
    df['vma50'] = df['Volume'].rolling(window=50).mean()
    vma50 = go.Scatter(x=df.index, y=df['vma50'], name='VMA 50',
                       line=dict(color='purple', width=2))
    fig.add_trace(vma50, row=2, col=1)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        title=f'{symbol} - {interval} ({df.index[0]} to {df.index[-1]})',
        title_x=0.5, title_y=.9,

        xaxis=dict(anchor='free'),
        yaxis=dict(title='BullRun and Drawdown', side='left', anchor='x3'),
        yaxis2=dict(title='Price', side='right', anchor='x3'),
        yaxis3=dict(title='Volume', side='right'),

        legend=dict(yanchor='middle', y=0.5, xanchor="left", x=0.01),
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
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


def get_bullrun_color(market_color_style=MarketColorStyle.WESTERN):
    if market_color_style == MarketColorStyle.WESTERN:
        return 'blue'
    else:
        return 'orange'


def get_drawdown_color(market_color_style=MarketColorStyle.WESTERN):
    if market_color_style == MarketColorStyle.WESTERN:
        return 'orange'
    else:
        return 'blue'


if __name__ == '__main__':
    plot('TSLA')

