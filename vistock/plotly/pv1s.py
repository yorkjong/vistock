# -*- coding: utf-8 -*-
"""
Show a price-and-volume overlaid stock chart.
* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
__software__ = "Price and Volume overlaid stock chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/09 (last revision)"

__all__ = ['plot']

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

from . import fig_util as futil


def plot(ticker='TSLA', period='12mo', interval='1d',
         ma_days=(5, 10, 20, 50, 150), vma_days=50):
    """Plot a stock chart that shows candlesticks, price moving-average lines,
    a volume bar chart, and a volume moving-average line in a single subplot.

    Parameters
    ----------
    ticker: str
        the ticker name.
    period: str
        the period ('12mo' means 12 monthes).
        Valid values are 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
    interval: str
        the interval of an OHLC item.
        Valid values are 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo,
        3mo. Intraday data cannot extend last 60 days:
        * 1m - max 7 days within last 30 days
        * up to 90m - max 60 days
        * 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)
    ma_days: int Sequence
        a sequence to list days of moving averge lines.
    vma_days: int
        days of the volume moving average line.
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Add the candlestick chart
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC'
    )
    fig = go.Figure(data=[candlestick])

    # Add moving averages to the figure
    ma_colors = ('orange', 'red', 'green', 'blue', 'brown')
    for d, c in zip(ma_days, ma_colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                        line=dict(color=f'{c}', width=2))
        fig.add_trace(ma)

    # Create separate y-axis for volume
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume', yaxis='y2',
                    marker_color='orange', opacity=0.3)
    fig.add_trace(volume)

    # Add the volume moving average line
    df[f'vma{vma_days}'] = df['Volume'].rolling(window=vma_days).mean()
    vma = go.Scatter(x=df.index, y=df[f'vma{vma_days}'],
                     name=f'VMA{vma_days}', yaxis='y2',
                     line=dict(color='purple'))
    fig.add_trace(vma)

    # Update layout for removing non-trading dates
    futil.remove_nontrading(fig, df, interval)

    # Update layout
    fig.update_layout(
        height=720,
        title=f'{ticker} {interval} '
              f'({df.index.values[0]}~{df.index.values[-1]})',
        title_x=0.5, title_y=.9,
        legend=dict(yanchor='top', xanchor="left", x=1.042),

        yaxis=dict(title='Price (USD)', side='right', overlaying='y2'),
        yaxis2=dict(title='Volume', side='left', showgrid=False),

        xaxis_rangeslider_visible=False,
    )

    # For Crosshair cursor
    futil.add_crosshair_cursor(fig)
    futil.add_hovermode_menu(fig)

    # Show the figure
    fig.show()

    # Write the figure to an HTML file
    info = f'{ticker}_{interval}_{df.index.values[-1]}'
    info = info.translate({ord(i): None for i in ':-'})   # remove ':', '-'
    info = info.replace(' ', '_')
    fig.write_html(f'{info}_pv1s.html')


if __name__ == '__main__':
    plot('TSLA')
