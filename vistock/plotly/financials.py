"""
This module provides functions to plot financial data for a given stock symbol
using Plotly. The financial data includes Basic EPS and Operating Revenue, and
the plots are divided into quarterly and annual sections. The generated plots
can be customized with different Plotly templates and saved as HTML and PNG
files.
"""
__software__ = "Financial Chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/09/07 (initial version) ~ 2024/09/07 (last revision)"

__all__ = ['plot']

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .. import tw
from .. import file_utils
from ..yf_utils import fetch_financials


def plot(symbol, template='plotly', out_dir='out'):
    """Plots the financial data of a stock symbol using Plotly.

    The function fetches Basic EPS and Operating Revenue for the given stock
    symbol from Yahoo Finance, with data divided into quarterly and annual
    segments. The data is plotted using two subplots, one for each frequency.
    The primary y-axis displays Basic EPS, and the secondary y-axis displays
    Operating Revenue. The chart's layout is customizable through the
    `template` parameter.

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
            continue
        fig.add_trace(
            go.Scatter(x=df.index, y=df['Basic EPS'], name='Basic EPS'),
            row=row, col=1
        )
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
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == "__main__":
    plot('AAPL')

