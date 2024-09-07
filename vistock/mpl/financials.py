"""
This module provides a function to plot financial data for a given stock symbol
using mplfinance. The financial data includes Basic EPS and Operating Revenue,
and the plots are generated with different chart styles as specified by the `style` parameter.
The function supports saving plots as PNG files in a specified directory.

The main function in this module is `plot`, which generates financial charts
for a stock symbol with support for various mplfinance styles and saves the
plots as PNG files.

The plot includes two subplots:
1. Quarterly financial data.
2. Annual financial data.

The function also saves the plot as a PNG file in the specified `out_dir`
after generating the chart using mplfinance.

See Also:

- `mplfinance/examples/external_axes.ipynb
  <https://github.com/matplotlib/mplfinance/blob/master/examples/
  external_axes.ipynb>`_
"""
__software__ = "Financial Chart"
__version__ = "1.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/09/07 (initial version) ~ 2024/09/07 (last revision)"

__all__ = ['plot']

import pandas as pd
import yfinance as yf
import mplfinance as mpf

from .. import tw
from .. import file_utils
from . import mpf_utils as mpfu
from ..yf_utils import fetch_financials


def plot(symbol, style='yahoo', out_dir='out'):
    """Plots the financial data of a stock symbol using mplfinance.

    The function fetches Basic EPS, Operating Revenue, Trailing EPS, and
    Forward EPS for the given stock symbol from Yahoo Finance, with data
    divided into quarterly and annual segments. The data is plotted using
    mplfinance with different chart styles as specified by the `style`
    parameter. Dummy OHLC data is generated for plotting purposes, with Basic
    EPS and Operating Revenue plotted on separate y-axes.

    The function also saves the plot as a PNG file in the specified `out_dir`
    after generating the chart using mplfinance.

    Parameters
    ----------
    symbol: str
        The stock symbol to analyze.

    style: str, optional
        The chart style to use. Common styles include:

        - 'yahoo': Yahoo Finance style
        - 'charles': Charles style
        - 'tradingview': TradingView style
        - 'binance': Binance style
        - 'binancedark': Binance dark mode style
        - 'mike': Mike style (dark mode)
        - 'nightclouds': Dark mode with sleek appearance
        - 'checkers': Checkered style
        - 'ibd': Investor's Business Daily style
        - 'sas': SAS style
        - 'starsandstripes': Stars and Stripes style
        - 'kenan': Kenan style
        - 'blueskies': Blue Skies style
        - 'brasil': Brasil style

        Default is 'yahoo'.

    out_dir : str, optional
        Directory to save the output HTML file. Default is 'out'.
    """
    ticker = tw.as_yfinance(symbol)

    # Fetch trailing and forward EPS from yf.info
    info = yf.Ticker(ticker).info
    trailing_eps = info.get('trailingEps', '')
    forward_eps = info.get('forwardEps', '')

    # Create an mplfinance figure with style and figsize
    fig = mpf.figure(style=style, figsize=(10, 8))
    ax1 = fig.add_subplot(2, 1, 1)  # Add first subplot
    ax2 = fig.add_subplot(2, 1, 2)  # Add second subplot

    for ax, freq in zip([ax1, ax2], ['quarterly', 'annual']):
        df = fetch_financials(
            ticker, fields=['Basic EPS', 'Operating Revenue'], frequency=freq
        )
        if df.empty:
            return

        # Plot Basic EPS on primary y-axis
        ax.plot(df.index, df['Basic EPS'],
                label='Basic EPS', linestyle='-', color='blue')
        ax.set_ylabel('Basic EPS', color='blue')

        # Create a secondary y-axis for Operating Revenue
        ax_twin = ax.twinx()
        ax_twin.plot(df.index, df['Operating Revenue'],
                     label='Operating Revenue', linestyle='--', color='green')
        ax_twin.set_ylabel('Operating Revenue', color='green')

        # Add Trailing EPS and Forward EPS to the annual subplot
        if freq == 'quarterly':
            # Trailing EPS: last available date in the quarterly data
            last_date = df.index[-1]
        elif trailing_eps and forward_eps:   # freq == 'annual'
            ax.plot([last_date], [trailing_eps], 'ro',
                    label='Trailing EPS', markersize=8)

            # Forward EPS: one year after the last available date
            future_date = last_date + pd.DateOffset(years=1)
            ax.plot([future_date], [forward_eps], 'rx',
                    label='Forward EPS', markersize=8)

        # Disable grid for the secondary y-axis
        ax_twin.grid(False)

        # Add legends and titles
        ax.legend(loc='center left')
        ax_twin.legend(loc='center right')
        ax.set_title(f"{freq.capitalize()}")

    fig.suptitle(f"{symbol} Financials", fontsize=16)

    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(symbol, '', df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == "__main__":
    mpfu.use_mac_chinese_font()
    plot('台積電')
    plot('AAPL')

