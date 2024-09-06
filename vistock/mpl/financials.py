"""
This module provides a function to plot financial data for a given stock symbol
using mplfinance. The financial data includes Basic EPS and Operating Revenue,
and the plots are generated with different chart styles. The function supports
saving plots as PNG files in a specified directory.

The main function in this module is `plot`, which generates financial charts
for a stock symbol with support for various mplfinance styles and saves the
plots as PNG files.
"""
__software__ = "Financial Chart"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/09/07 (initial version) ~ 2024/09/07 (last revision)"

__all__ = ['plot']

import pandas as pd
import mplfinance as mpf

from .. import tw
from .. import file_utils
from . import mpf_utils as mpfu
from ..yf_utils import fetch_financials


def plot(symbol, style='checkers', out_dir='out'):
    """Plots the financial data of a stock symbol using mplfiance.

    The function fetches Basic EPS and Operating Revenue for the given stock
    symbol from Yahoo Finance, with data divided into quarterly and annual
    segments. The data is plotted using mplfinance with different chart styles
    as specified by the `style` parameter. Dummy OHLC data is generated for
    plotting purposes, with Basic EPS and Operating Revenue plotted on
    separate y-axes.

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

        Default is 'checkers'.

    out_dir : str, optional
        Directory to save the output HTML file. Default is 'out'.
    """
    def create_dummy_ohlc(index, value):
        data = {}
        for column in ['Open', 'High', 'Low', 'Close']:
            data[column] = value
        return pd.DataFrame(data, index=index)

    ticker = tw.as_yfinance(symbol)

    for frequency in ['quarterly', 'annual']:
        df = fetch_financials(
            ticker, fields=['Basic EPS', 'Operating Revenue'],
            frequency=frequency
        )
        if df.empty:
            continue
        ohlc_dummy = create_dummy_ohlc(df.index, df['Basic EPS'])
        eps = mpf.make_addplot(
            df['Basic EPS'], panel='main', linestyle='-',
            label='Basic EPS',
            secondary_y=False,
        )
        rev = mpf.make_addplot(
            df['Operating Revenue'], panel='main', linestyle='--',
            label='Operating Revenue', ylabel='Operating Revenue',
            secondary_y=True,
        )
        fig, axes = mpf.plot(
            ohlc_dummy, type='line', addplot=[eps, rev], volume=False,
            returnfig=True, style=style, ylabel='Basic EPS',
            title=f"{symbol} Financials" if frequency=='quarterly' else '',
            figratio=(3, 1),
        )
        axes[0].legend(loc='upper right')
        axes[1].legend(loc='upper left')
        axes[0].text(0.5, 1.02, f"{frequency.capitalize()}",
                     ha='center', va='bottom', fontsize=14,
                     transform=axes[0].transAxes)
    # Show the figure
    mpf.show()

    # Save the figure
    out_dir = file_utils.make_dir(out_dir)
    fn = file_utils.gen_fn_info(symbol, '', df.index[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png', bbox_inches='tight')


if __name__ == "__main__":
    mpfu.use_mac_chinese_font()
    plot('AAPL')

