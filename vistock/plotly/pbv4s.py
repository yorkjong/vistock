# -*- coding: utf-8 -*-
"""
Visualize a PBV (means price-by-volume, also called volume profile) for a given
stock. Here the PBV occupies a split of a 4-split chart.
"""
__software__ = "Volume Profile 4-split with Plotly"
__version__ = "1.02"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/08 (last revision)"

__all__ = ['plot']

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def plot(ticker='TSLA', period='12mo',
         ma_days=(5, 10, 20, 50, 150), vma_days=50,
         total_bins=42):
    """Visualize a PBV (means price-by-volume, also called volume profile) for a
    given stock. Here the PBV occupies a split of a 4-split chart. This chart
    also includes candlestick, MA lines, volume, and volume MA line.

    Parameters
    ----------
    ticker: str
        the ticker name.
    period: str
        the period ('12mo' means 12 monthes)
    ma_days: int Sequence
        a sequence to list days of moving averge lines.
    vma_days: int
        days of the volume moving average line.
    total_bins: int
        the number of bins to calculate comulative volume for bins.
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period)

    # Initialize empty plot with marginal subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        column_width=[0.75, 0.25],
        row_heights=[0.7, 0.3],
        #shared_xaxes="columns",
        #shared_yaxes="rows",
        #subplot_titles=["Price", "Price Bins", "Volume", ""]
        horizontal_spacing=0.01,
        vertical_spacing=0.03,
        figure=go.Figure(layout=go.Layout(width=1280, height=720))
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
    for d, c in zip(ma_days, ma_colors):
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
    df[f'vma{vma_days}'] = df['Volume'].rolling(window=vma_days).mean()
    vma = go.Scatter(x=df.index, y=df[f'vma{vma_days}'],
                     name=f'VMA {vma_days}', line=dict(color='purple', width=2))
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

    # Remove non-trading dates
    df.index = df.index.strftime('%Y-%m-%d')
    dt_all = pd.date_range(start=df.index.values[0], end=df.index.values[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    trade_date = [d for d in df.index.values]
    dt_breaks = list(set(dt_all) - set(trade_date))
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    # Update layout
    fig.update_layout(
        title=f'{ticker}: {df.index.values[0]}~{df.index.values[-1]}',
        title_x=0.5, title_y=.9,

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x3', side='left', title='Price (USD)'),

        xaxis2=dict(title='Bin Comulative Volume'),
        yaxis2=dict(side='right', title='Price (USD)'),

        yaxis3=dict(side='left', title='Volume'),

        legend=dict(yanchor='middle', y=0.5, xanchor="left", x=0.01),
        xaxis_rangeslider_visible=False,
    )

    # Add crosshair cursor
    fig.update_yaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_xaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_layout(hovermode='x')    # 'x', 'y', 'closest', False,
                                        # 'x unified', 'y unified'

    # Add a dropdown menu for selecting a hovermode
    hovermodes = ('x', 'y', 'closest', 'x unified', 'y unified')
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(args=[dict(hovermode=m)],
                         label=m, method="relayout") for m in hovermodes
                ]),
                showactive=True,
                xanchor='left', yanchor='bottom',
                x=0, y=1.05
            ),
        ],
        annotations=[dict(
            text="hovermode:", showarrow=False,
            x=0, y=1.15, xref="paper", yref="paper", align="left"
        )],
    )

    # Show and save the figure
    fig.show()
    fig.write_html(f'{ticker}_{df.index.values[-1]}_pbv4s.html')


if __name__ == '__main__':
    plot('TSLA')

