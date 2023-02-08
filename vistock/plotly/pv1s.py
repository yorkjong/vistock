# -*- coding: utf-8 -*-
"""
Show a price-and-volume overlaid stock chart.
* Data from yfinance
* Plot with Plotly (for candlestick, MA, volume, volume MA)
"""
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

__software__ = "Price and Volume overlaid stock chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/08 (last revision)"
__all__ = ['plot']


def plot(ticker='TSLA', period='12mo',
         ma_days=(10, 20, 50, 150), vma_days=50):
    """Plot a stock chart that shows candlesticks, price moving-average lines,
    a volume bar chart, and a volume moving-average line in a single subplot.

    Parameters
    ----------
    ticker
        the ticker name (default is 'TSLA')
    period
        the period (default is '12mo' that means 12 monthes)
    ma_days
        a sequence to list days of price moving averge lines
    vma_days
        days of volume moving average lines
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period)

    # Add the candlestick chart
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC'
    )
    fig = go.Figure(data=[candlestick])

    # Add moving averages to the figure
    ma_colors = ('red', 'green', 'blue', 'brown')
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

    # Remove non-trading dates
    df.index = df.index.strftime('%Y-%m-%d')
    dt_all = pd.date_range(start=df.index.values[0], end=df.index.values[-1])
    dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
    trade_date = [d for d in df.index.values]
    dt_breaks = list(set(dt_all) - set(trade_date))
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    # Update layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,

        title=f'{ticker}: {df.index.values[0]}~{df.index.values[-1]}',
        title_x=0.5, title_y=.85,

        yaxis=dict(title='Price (USD)', side='right', overlaying='y2'),
        yaxis2=dict(title='Volume', side='left', showgrid=False),

        legend=dict(yanchor='middle', y=0.5, xanchor="left", x=0.01)
    )

    # Add crosshair cursor
    fig.update_yaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_xaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_layout(hovermode='x')  # 'x', 'y', 'closest', False,
                                      # 'x unified', 'y unified'

    # Show the figure
    fig.show()

    fig.write_html(f'{ticker}_{df.index.values[-1]}_pv1s.html')


if __name__ == '__main__':
    plot('TSLA')

