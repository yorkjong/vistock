"""
Visualize a profile chart (eigher Volume Profile or Turnover Profile) with
4-section layout for a given stock.
"""
__software__ = "Volume Profile with Plotly 2x2 subplots"
__version__ = "2.5"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/08/20 (last revision)"

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
from . import fig_utils as futil
from ..util import MarketColorStyle, decide_market_color_style


def _plot(df, ticker, market_color_style, profile_field='Volume',
          period='1y', interval='1d',
          ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
          template='plotly', hides_nontrading=True):
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

    # Plot the candlestick chart
    mc_style = decide_market_color_style(ticker, market_color_style)
    mc_colors = futil.get_candlestick_colors(mc_style)
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Candle',
        **mc_colors
    )
    fig.add_trace(candlestick, row=1, col=1)

    # Add moving averages to the figure
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    for d, c in zip(ma_nitems, colors):
        df[f'ma{d}'] = df['Close'].rolling(window=d).mean()
        ma = go.Scatter(x=df.index, y=df[f'ma{d}'], name=f'MA {d}',
                        line=dict(color=f'{c}', width=2), opacity=0.5)
        fig.add_trace(ma, row=1, col=1)

    # Add volume trace to 2nd row
    cl = futil.get_volume_colors(mc_style)
    colors = [cl['up'] if c >= o
              else cl['down'] for o, c in zip(df['Open'], df['Close'])]
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
    bin = df[profile_field].groupby(
            df['Close'].apply(lambda x: bin_round(x))).sum()
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

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Update layout
    fig.update_layout(
        legend=dict(yanchor='top', xanchor="left", x=1.069),

        xaxis=dict(anchor='free'),
        yaxis=dict(anchor='x3', side='left', title='Price'),

        xaxis2=dict(title=f'Bin Comulative {profile_field}'),
        yaxis2=dict(side='right', title='Price'), # Bin Price

        yaxis3=dict(side='left', title='Volume'),

        xaxis_rangeslider_visible=False,
        template=template,
    )
    # Update the layout to set the same range for both y-axes
    # This ensures that both price axes have the same scale and range
    y_range = [min(df['Close']) * 0.95, max(df['Close']) * 1.05]
    fig.update_layout(
        yaxis=dict(range=y_range),
        yaxis2=dict(range=y_range)
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
    @staticmethod
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
             market_color_style=MarketColorStyle.AUTO,
             template='plotly', hides_nontrading=True, out_dir='out'):
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

        period: str, optional
            the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
            1y, 2y, 5y, 10y, ytd, max. Default is '1y'.

            - d   -- days
            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval: str, optional
            the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
            60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Default is '1d'.

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
            a sequence to list the number of data items to calclate moving
            averges.
        vma_nitems: int
            the number of data items to calculate the volume moving average.
        total_bins: int
            the number of bins to calculate comulative volume for bins.
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

        # Plot
        fig = _plot(df, ticker, market_color_style, 'Volume',
                    period, interval, ma_nitems, vma_nitems,
                    total_bins, template, hides_nontrading)
        fig.update_layout(
            title=f'{symbol} - {interval} ({df.index[0]} to {df.index[-1]})',
            title_x=0.5, title_y=.9,
        )

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info(symbol, interval, df.index[-1],
                                   'volume_prf')
        fig.write_html(f'{out_dir}/{fn}.html')


class Turnover:
    '''Turnover Profile

    Here "turnover" means "trading value" (= price * volume)
    '''
    @staticmethod
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50, total_bins=42,
             market_color_style=MarketColorStyle.AUTO,
             template='plotly', hides_nontrading=True, out_dir='out'):
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

        period: str, optional
            the period data to download. Valid values are 1d, 5d, 1mo, 3mo, 6mo,
            1y, 2y, 5y, 10y, ytd, max. Default is '1y'.

            - d   -- days
            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval: str, optional
            the interval of an OHLC item. Valid values are 1m, 2m, 5m, 15m, 30m,
            60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Default is '1d'.

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
            a sequence to list the number of data items to calclate moving
            averges.
        vma_nitems: int
            the number of data items to calculate the volume moving average.
        total_bins: int
            the number of bins to calculate comulative volume for bins.
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
        df['Turnover'] = df['Close'] * df['Volume']

        # Plot
        fig = _plot(df, ticker, market_color_style, 'Turnover',
                    period, interval, ma_nitems, vma_nitems,
                    total_bins, template, hides_nontrading)
        fig.update_layout(
            title=f'{symbol} - {interval} ({df.index[0]} to {df.index[-1]})',
            title_x=0.5, title_y=.9,
        )

        # Show the figure
        fig.show()

        # Write the figure to an HTML file
        out_dir = file_util.make_dir(out_dir)
        fn = file_util.gen_fn_info(symbol, interval, df.index[-1],
                                   'turnover_prf')
        fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == '__main__':
    Volume.plot('TSLA')
    Turnover.plot('TSLA')

