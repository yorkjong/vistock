# -*- coding: utf-8 -*-
"""
Visualize a PBV (means price-by-volume, also called volume profile) for a given
stock. Here the PBV occupies a split of a 4-split chart.
"""
__software__ = "Volume Profile 4-split with Plotly"
__version__ = "1.2"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/09 (last revision)"

__all__ = ['plot']

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from . import fig_util as futil


def plot(ticker='TSLA', period='12mo', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42):
    """Visualize a PBV (means price-by-volume, also called volume profile) for a
    given stock. Here the PBV occupies a split of a 4-split chart. This chart
    also includes candlestick, MA lines, volume, and volume MA line.

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
    ma_nitems: int Sequence
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int
        the number of data items to calculate the volume moving average.
    total_bins: int
        the number of bins to calculate comulative volume for bins.
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Initialize empty plot with marginal subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        column_width=[0.8, 0.2],
        row_heights=[0.7, 0.3],
        #shared_xaxes="columns",
        #shared_yaxes="rows",
        #subplot_titles=["Price", "Price Bins", "Volume", ""]
        horizontal_spacing=0.01,
        vertical_spacing=0.03,
        figure=go.Figure(layout=go.Layout(height=720))
    )
    #print(fig)

    # Plot the candlestick chart
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC',
    )
    fig.add_trace(candlestick, row=1, col=1)

    # Add moving averages to the figure
    ma_colors = ('orange', 'red', 'green', 'blue', 'brown')
    for d, c in zip(ma_nitems, ma_colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                        line=dict(color=f'{c}', width=2), opacity=0.5)
        fig.add_trace(ma, row=1, col=1)

    # Add volume trace to 2nd row
    colors = ['green' if o - c >= 0
            else 'red' for o, c in zip(df['Open'], df['Close'])]
    volume = go.Bar(x=df.index, y=df['Volume'], name='Volume',
                    marker_color=colors)
    fig.add_trace(volume, row=2, col=1)

    # Add moving average volume to 2nd row
    df[f'vma{vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()
    vma = go.Scatter(x=df.index, y=df[f'vma{vma_nitems}'],
                     name=f'VMA {vma_nitems}',
                     line=dict(color='purple', width=2))
    fig.add_trace(vma, row=2, col=1)

    # Add Price by Volume (Volume Profile) chart
    bin_size = (max(df['High']) - min(df['Low'])) / total_bins
    bin_round = lambda x: bin_size * round(x / bin_size)
    bin = df['Volume'].groupby(df['Close'].apply(lambda x: bin_round(x))).sum()
    fig.add_trace(
        go.Bar(
            y=bin.keys(),   # Price
            x=bin.values,   # Bin Comulative Volume
            text=bin,       # (price, volume) pairs
            name="Price Bins",
            orientation="h",    # 'v', 'h'
            marker_color="brown",
            texttemplate="%{x:3.2f}",
            hoverinfo="y",   # 'x', 'y', 'x+y'
            opacity=0.5
        ),
        row=1, col=2
    )

    # Update layout for removing non-trading dates
    futil.remove_nontrading(fig, df, interval)

    # Update layout
    fig.update_layout(
        title=f'{ticker} {interval} '
              f'({df.index.values[0]}~{df.index.values[-1]})',
        title_x=0.5, title_y=.9,
        legend=dict(yanchor='top', xanchor="left", x=1.069),

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x3', side='left', title='Price (USD)'),

        xaxis2=dict(title='Bin Comulative Volume'),
        yaxis2=dict(side='right', title='Price (USD)'),

        yaxis3=dict(side='left', title='Volume'),

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
    fig.write_html(f'{info}_pbv4s.html')



if __name__ == '__main__':
    plot('TSLA')

