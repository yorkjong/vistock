"""
Visualize a profile chart (eigher Volume Profile or Turnover Profile) with
2-section layout for a given stock.
"""
__software__ = "Profile with Plotly 2 subplots"
__version__ = "2.0.2"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/07/22 (last revision)"

__all__ = [
    'Volume',   # Volume Profile, i.e., PBV (Price-by-Volume) or Volume-by-Price
    'Turnover', # Turnover Profile
]

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_util
from . import fig_util as futil
from ..util import MarketColorStyle, decide_market_color_style


def _plot(df, ticker, market_color_style, profile_field='Volume',
          period='1y', interval='1d',
          ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
          hides_nontrading=True, hbar_align_on_right=True):
    # Initialize empty plot with a marginal subplot
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

    # Plot the candlestick chart
    mc_style = decide_market_color_style(ticker, market_color_style)
    mc_colors = futil.get_candlestick_colors(mc_style)
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='OHLC',
        xaxis='x2', yaxis='y2',
        **mc_colors
    )
    fig.add_trace(candlestick)

    # Add moving averages to the figure
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    for d, c in zip(ma_nitems, colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(
            x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
            line=dict(color=f'{c}', width=2),
            xaxis='x2', yaxis='y2',
        )
        fig.add_trace(ma)

    # Add Profile (e.g., Volume Profile or Turnover Profile)
    bin_size = (max(df['High']) - min(df['Low'])) / total_bins
    bin_round = lambda x: bin_size * round(x / bin_size)
    bin = df[profile_field].groupby(
            df['Close'].apply(lambda x: bin_round(x))).sum()
    vp = go.Bar(
        y=bin.keys(),   # Price
        x=bin.values,   # Bin Comulative Volume
        text=bin,       # (price, volume) pairs
        name="Price Bins",
        orientation="h",    # 'v', 'h'
        marker_color="brown",
        texttemplate="%{x:3.2f}",
        hoverinfo="y",   # 'x', 'y', 'x+y'
        opacity=0.3,
        xaxis='x', yaxis='y',
    )
    fig.add_trace(vp)

    # Add volume trace to 2nd row
    cl = futil.get_volume_colors(mc_style)
    colors = [cl['up'] if c >= o
              else cl['down'] for o, c in zip(df['Open'], df['Close'])]
    volume = go.Bar(
        x=df.index, y=df['Volume'], name='Volume',
        marker_color=colors, opacity=0.7,
        #xaxis='x2', yaxis='y3',
    )
    fig.add_trace(volume, row=2, col=1)

    # Add moving average volume to 2nd row
    df[f'vma{vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()
    vma = go.Scatter(
        x=df.index, y=df[f'vma{vma_nitems}'],
        name=f'VMA {vma_nitems}',
        line=dict(color='purple', width=2),
        #xaxis='x2', yaxis='y3'
    )
    fig.add_trace(vma, row=2, col=1)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        legend=dict(yanchor='top', xanchor="left", x=1),

        xaxis=dict(side='top', title='Bin Comulative Volume'),
        yaxis=dict(side='left', title='Bin Price (USD)'),

        xaxis2=dict(overlaying='x', side='bottom'),     # datetime
        yaxis2=dict(side='right', title='Price (USD)'),
        yaxis3=dict(side='right', title='Volume'),

        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
    )

    # Update the layout to set the same range for both y-axes
    # This ensures that both price axes have the same scale and range
    y_range = [min(df['Close']) * 0.95, max(df['Close']) * 1.05]
    fig.update_layout(
        yaxis=dict(range=y_range),
        yaxis2=dict(range=y_range)
    )

    if hbar_align_on_right:
        # change the starting position of the horizontal bars to the right
        fig.update_layout(xaxis=dict(autorange='reversed'))
        fig.update_layout(
            yaxis=dict(side='right', title='Bin Price (USD)'),
            yaxis2=dict(side='left', title='Price (USD)'),
        )

    if hides_nontrading:
        futil.hide_nontrading_periods(fig, df, interval)

    # For Crosshair cursor
    futil.add_crosshair_cursor(fig)
    futil.add_hovermode_menu(fig)

    return fig


class Volume:
    """Volume Profile, i.e., PBV (Price-by-Volume) or Volume-by-Price
    """
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
             hides_nontrading=True, hbar_align_on_right=True,
             market_color_style=MarketColorStyle.AUTO,
             out_dir='out'):
        """Plot a price-by-volume, PBV  (also called volume profile) figure for
        a given stock. This figure shows the volume distribution across price
        levels for a stock.

        Here the PBV is overlaied with the price subplot. This figure consists
        of two subplots: a price subplot and a volume subplot. The former
        includes candlestick, moving average lines, while the latter includes
        trading volume bar chart and volume moving average line.

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
            a sequence to list the number of data items to calclate moving
            averges.
        vma_nitems: int
            the number of data items to calculate the volume moving average.
        total_bins: int
            the number of bins to calculate comulative volume for bins.
        hides_nontrading: bool
            decide if hides non-trading time-periods.
        hbar_align_on_right: bool
            decide if the price-by-volume bars align on right. True to set the
            starting position of the horizontal bars to the right; False the
            left.
        market_color_style (MarketColorStyle): The market color style to use.
            Default is MarketColorStyle.AUTO.
        out_dir: str
            the output directory for saving figure.
        """
        # Download stock data
        ticker = tw.as_yfinance(symbol)
        df = yf.Ticker(ticker).history(period=period, interval=interval)

        # Plot
        fig = _plot(df, ticker, market_color_style, 'Volume',
                    period, interval, ma_nitems, vma_nitems, total_bins,
                    hides_nontrading, hbar_align_on_right)
        fig.update_layout(
            title=f'{symbol} {interval} '
                  f'({df.index.values[0]}~{df.index.values[-1]})',
            title_x=0.5, title_y=.98
        )

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info(symbol, interval, df.index.values[-1],
                                   'volume_prf')
        fig.write_html(f'{out_dir}/{fn}.html')


class Turnover:
    '''Turnover Profile

    Here "turnover" means "trading value" (= price * volume)
    '''
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
             hides_nontrading=True, hbar_align_on_right=True,
             market_color_style=MarketColorStyle.AUTO,
             out_dir='out'):
        """Plot a price-by-volume, PBV  (also called volume profile) figure for
        a given stock. This figure shows the volume distribution across price
        levels for a stock.

        Here the PBV is overlaied with the price subplot. This figure consists
        of two subplots: a price subplot and a volume subplot. The former
        includes candlestick, moving average lines, while the latter includes
        trading volume bar chart and volume moving average line.

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
            a sequence to list the number of data items to calclate moving
            averges.
        vma_nitems: int
            the number of data items to calculate the volume moving average.
        total_bins: int
            the number of bins to calculate comulative volume for bins.
        hides_nontrading: bool
            decide if hides non-trading time-periods.
        hbar_align_on_right: bool
            decide if the price-by-volume bars align on right. True to set the
            starting position of the horizontal bars to the right; False the
            left.
        market_color_style (MarketColorStyle): The market color style to use.
            Default is MarketColorStyle.AUTO.
        out_dir: str
            the output directory for saving figure.
        """
        # Download stock data
        ticker = tw.as_yfinance(symbol)
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        df['Turnover'] = df['Close'] * df['Volume']

        # Plot
        fig = _plot(df, ticker, market_color_style, 'Turnover',
                    period, interval, ma_nitems, vma_nitems, total_bins,
                    hides_nontrading, hbar_align_on_right)
        fig.update_layout(
            title=f'{symbol} {interval} '
                  f'({df.index.values[0]}~{df.index.values[-1]})',
            title_x=0.5, title_y=.98,
            xaxis=dict(title='Bin Comulative Turnover (Price*Volume)'),
        )

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info(symbol, interval, df.index.values[-1],
                                   'turnover_prf')
        fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    Volume.plot('TSLA')
    Turnover.plot('TSLA')

