"""
This module provides a function to plot financial data for a given stock symbol
using Plotly. The data includes Basic EPS, Operating Revenue, Trailing EPS,
and Forward EPS (if available), plotted on two subplots with customizable
styles via the `template` parameter.

The `plot` function generates:

1. Quarterly financial data.
2. Annual financial data, with markers for Trailing EPS and Forward EPS.

The plot is saved as an HTML file in the specified `out_dir`, with support
for interactive exploration.
"""
__software__ = "Financial Chart"
__version__ = "1.2"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/09/07 (initial version) ~ 2024/09/07 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_utils
from ..yf_utils import fetch_financials


def plot(symbol, template='plotly', out_dir='out'):
    """Plots the financial data of a stock symbol using Plotly.

    The function fetches Basic EPS, Operating Revenue, Trailing EPS, and
    Forward EPS for the given stock symbol from Yahoo Finance, with data
    divided into quarterly and annual segments. The data is plotted using two
    subplots, one for each frequency. The primary y-axis displays Basic EPS,
    and the secondary y-axis displays Operating Revenue. The chart's layout is
    customizable through the `template` parameter.

    The function also saves the plot as a PNG file in the specified `out_dir`
    after generating the HTML plot using Plotly.

    Parameters
    ----------
    symbol: str
        The stock symbol to analyze.
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

    out_dir : str, optional
        Directory to save the output HTML file. Default is 'out'.
    """
    ticker = tw.as_yfinance(symbol)

    # Fetch trailing and forward EPS from yf.info
    info = yf.Ticker(ticker).info
    trailing_eps = info.get('trailingEps', '')
    forward_eps = info.get('forwardEps', '')

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.5, 0.5],
        specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
        subplot_titles=("Quarterly", "Annual"),
    )

    for freq, row in zip(['quarterly', 'annual'], [1, 2]):
        df = fetch_financials(
            ticker, fields=['Basic EPS', 'Operating Revenue', 'Total Revenue'],
            frequency=freq
        )
        if df.empty:
            return

        # Add Basic EPS trace
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Basic EPS'], name='Basic EPS'),
            row=row, col=1
        )

        # Add Trailing EPS and Forward EPS to the annual subplot
        if freq == 'quarterly':
            # Trailing EPS: last available date in the quarterly data
            last_date = df.index[-1]
        elif trailing_eps and forward_eps:   # freq == 'annual'
            fig.add_trace(
                go.Scatter(x=[last_date], y=[trailing_eps],  mode='markers',
                           marker=dict(color='red', symbol='circle'),
                           name='Trailing EPS'),
                row=row, col=1
            )

            # Forward EPS: one year after the last available date
            future_date = last_date + pd.DateOffset(years=1)
            fig.add_trace(
                go.Scatter(x=[future_date], y=[forward_eps],  mode='markers',
                           marker=dict(color='orange', symbol='x'),
                           name='Forward EPS'),
                row=row, col=1
            )

        # Add Operating Revenue trace
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Operating Revenue'],
                       name='Operating Revenue', line=dict(dash='dot')),
            row=row, col=1, secondary_y=True
        )

    fig.update_layout(
        title_text=f"{symbol} Financials",
        yaxis1=dict(title="Basic EPS"),
        yaxis2=dict(title="Operating Revenue"),
        yaxis3=dict(title="Basic EPS"),
        yaxis4=dict(title="Operating Revenue"),
        template=template,
    )

    fig.show()

    # Save the figure
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(symbol, '', df.index[-1], __file__)
    fig.write_html(f'{out_dir}/{fn}.html')


if __name__ == "__main__":
    plot('NVDA')
    plot('聯發科')

