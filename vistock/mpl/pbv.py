"""
Visualize a PBV (means price-by-volume, also called volume profile) for a given
stock. Here the PBV is overlaid with the price subplot (total 2 subplots).
"""
__software__ = "Volume Profile 2-split with mplfinace"
__version__ = "1.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/20 (last revision)"

__all__ = ['plot']

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

from .. import tw
from .. import file_util


def plot(symbol='TSLA', period='12mo', interval='1d',
         ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
         total_bins=42, legend_loc='best'):
    """Plot a price-by-volume, PBV (also called volume profile) figure for a
    given stock.

    Here the PBV is overlaid with the price subplot. This figure consists of
    two subplots: a price subplot and a volume subplot. The former includes
    price candlesticks, price moving average lines, while the latter includes
    a trading volume histogram and a volume moving average line.

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
        a sequence to list the number of data items to calclate moving averges.
    vma_nitems: int
        the number of data items to calculate the volume moving average.
    total_bins: int
        the number of bins to calculate comulative volume for bins.
    legend_loc: str
        the location of the legend. Valid locations are
            * 'best'
            * 'upper right'
            * 'upper left'
            * 'lower left'
            * 'lower right'
            * 'right'
            * 'center left'
            * 'center right'
            * 'lower center'
            * 'upper center'
            * 'center'
    """
    # Download stock data
    symbol = tw.as_yfinance(symbol)
    df = yf.Ticker(symbol).history(period=period, interval=interval)

    # Add Volume Moving Average
    vma = mpf.make_addplot(df['Volume'], mav=vma_nitems,
                           type='line', linestyle='', color='purple', panel=1)

    # Make a customized color style
    mc = mpf.make_marketcolors(base_mpf_style='yahoo')
    s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc)

    # Plot candlesticks MA, volume, volume MA, RSI
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')
    fig, axes = mpf.plot(
        df, type='candle',                  # candlesticks
        mav=ma_nitems, mavcolors=colors,    # moving average lines
        volume=True, addplot=[vma],         # volume, volume MA
        style=s, figsize=(16, 8),
        returnfig=True
    )
    axes[0].legend([f'MA {d}' for d in ma_nitems], loc=legend_loc)
    df.index = df.index.strftime('%Y-%m-%d %H:%M')
    fig.suptitle(f"{symbol} {interval} "
                 f"({df.index.values[0]}~{df.index.values[-1]})",
                 y=0.93)

    # Volume Profile (i.e., Price by Volume)

    bin_size = (max(df['High']) - min(df['Low'])) / total_bins
    bin_round = lambda x: bin_size * round(x / bin_size)
    bin = df['Volume'].groupby(df['Close'].apply(lambda x: bin_round(x))).sum()

    ax = fig.add_axes(axes[0].get_position())
    ax.set_axis_off()
    ax.set_xlim(right=1.2*max(bin.values))
    ax.barh(
        y=bin.keys(),       # price
        width=bin.values,   # bin comulative volume
        height=0.75*bin_size,
        align='center',
        color='cyan',
        alpha=0.4
    )

    # Show the figure
    mpf.show()

    # Write the figure to an PNG file
    fn = file_util.gen_fn_info(symbol, interval, df.index.values[-1], __file__)
    fig.savefig(f'{fn}.png')


if __name__ == '__main__':
    plot('TSLA')
