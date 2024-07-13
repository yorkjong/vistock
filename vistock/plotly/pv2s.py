"""
Show a price-and-volume separated stock chart.

* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
__software__ = "Price and Volume separated stock chart"
__version__ = "1.7"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/07/13 (last revision)"

__all__ = ['plot']

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_util
from . import fig_util as futil


def plot(symbol='TSLA', period='12mo', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         hides_nontrading=True, out_dir='out'):
    """Plot a stock figure that consists of two subplots: a price subplot and
    a volume subplot.

    The price subplot includes candlesticks, moving average lines, while
    the volume subplot includes a volume histogram and a volume moving average
    line.

    Parameters
    ----------
    symbol: str
        the stock symbol.
    period: str
        the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
        1y, 2y, 5y, 10y, ytd, max.

        * d   -- days
        * mo  -- monthes
        * y   -- years
        * ytd -- year to date
        * max -- all data

    interval: str
        the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
        60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

        * m  -- minutes
        * h  -- hours
        * wk -- weeks
        * mo -- monthes

        Intraday data cannot extend last 60 days:

        * 1m - max 7 days within last 30 days
        * up to 90m - max 60 days
        * 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)

    ma_nitems: sequence of int
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int
        the number of data items to calculate the volume moving average.
    hides_nontrading: bool
        decide if hides non-trading time-periods.
    out_dir: str
        the output directory for saving figure.
    """
    # Download stock data
    symbol = tw.as_yfinance(symbol)
    df = yf.Ticker(symbol).history(period=period, interval=interval)

    # Initialize empty plot with a marginal subplot
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        #shared_xaxes=True,
        vertical_spacing=0.03,
        figure=go.Figure(layout=go.Layout(height=720))
    )
    #print(fig)

    # Plot the candlestick chart
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC'
    )
    fig.add_trace(candlestick)

    # Add moving averages to the figure
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    for d, c in zip(ma_nitems, colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                        line=dict(color=f'{c}', width=2), opacity=0.4)
        fig.add_trace(ma)

    # Add volume trace to 2nd row
    colors = ['green' if o - c >= 0
              else 'red' for o, c in zip(df['Open'], df['Close'])]
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume',
                    marker_color=colors, opacity=0.5)
    fig.add_trace(volume, row=2, col=1)

    # Add moving average volume to 2nd row
    df[f'vma{vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()
    vma50 = go.Scatter(x=df.index, y=df[f'vma{vma_nitems}'],
                       name=f'VMA {vma_nitems}',
                       line=dict(color='purple', width=2))
    fig.add_trace(vma50, row=2, col=1)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        title=f'{symbol} {interval} '
              f'({df.index.values[0]}~{df.index.values[-1]})',
        title_x=0.5, title_y=.9,
        legend=dict(yanchor='top', xanchor="left", x=1.042),

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x2', side='right', title='Price (USD)'),
        yaxis2=dict(anchor='x', side='right', title='Volume'),

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
    plot('TSLA')

