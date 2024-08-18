"""
Show a price-and-volume overlaid stock chart.

* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
__software__ = "Price and Volume overlaid stock chart"
__version__ = "1.9"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/08/18 (last revision)"

__all__ = ['plot']

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

from .. import tw
from .. import file_util
from . import fig_util as futil
from ..util import MarketColorStyle, decide_market_color_style


def plot(symbol='TSLA', period='1y', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         hides_nontrading=True, market_color_style=MarketColorStyle.AUTO,
         out_dir='out'):
    """Plot a stock figure overlaying charts in a single subplot.

    These charts include candlesticks, price moving-average lines, a volume
    histogram, and a volume moving-average line.

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
    market_color_style (MarketColorStyle): The market color style to use.
        Default is MarketColorStyle.AUTO.
    out_dir: str
        the output directory for saving figure.
    """
    # Download stock data
    ticker = tw.as_yfinance(symbol)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Add the candlestick chart
    mc_style = decide_market_color_style(ticker, market_color_style)
    mc_colors = futil.get_candlestick_colors(mc_style)
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC',
        **mc_colors
    )
    fig = go.Figure(data=[candlestick])

    # Add moving averages to the figure
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    for d, c in zip(ma_nitems, colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                        line=dict(color=f'{c}', width=2))
        fig.add_trace(ma)

    # Create separate y-axis for volume
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2',
                    marker_color='orange', opacity=0.3)
    fig.add_trace(volume)

    # Add the volume moving average line
    df[f'vma{vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()
    vma = go.Scatter(x=df.index, y=df[f'vma{vma_nitems}'],
                     name=f'VMA {vma_nitems}', yaxis='y2',
                     line=dict(color='purple'))
    fig.add_trace(vma)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        height=720,
        title=f'{symbol} {interval} '
              f'({df.index[0]}~{df.index[-1]})',
        title_x=0.5, title_y=.9,
        legend=dict(yanchor='top', xanchor="left", x=1.042),

        yaxis=dict(title='Price', side='right', overlaying='y2'),
        yaxis2=dict(title='Volume', side='left', showgrid=False),

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
    fn = file_util.gen_fn_info(symbol, interval, df.index[-1], __file__)
    fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    plot('TSLA')
