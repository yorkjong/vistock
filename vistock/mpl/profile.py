"""
Visualize a Volume Profile (or Turnover Profile) for a stock.
"""
__software__ = "Profile 2-split with mplfinace"
__version__ = "3.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/09/05 (last revision)"

__all__ = [
    'Volume',   # Volume Profile, i.e., PBV (Price-by-Volume) or Volume-by-Price
    'Turnover', # Turnover Profile
]

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

from .. import tw
from .. import file_utils
from ..utils import MarketColorStyle, decide_market_color_style
from . import mpf_utils as mpfu


def _plot(df, mpf_style, profile_field='Volume', period='1y', interval='1d',
          ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
          total_bins=42, legend_loc='best', hides_nontrading=True):
    # Calculate price moving average
    for n in ma_nitems:
        df[f'MA {n}'] = df['Close'].rolling(window=n).mean()
    colors = ('orange', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow')

    # Calculate volume moving averaage
    df[f'VMA {vma_nitems}'] = df['Volume'].rolling(window=vma_nitems).mean()

    # Create subplots
    addplot = [
        # Plot of Price Moving Average
        *[mpf.make_addplot(df[f'MA {n}'], panel=0, label=f'MA {n}', color=c)
            for n, c in zip(ma_nitems, colors)],

        # Plot of Volume Moving Average
        mpf.make_addplot(df[f'VMA {vma_nitems}'], panel=1,
                         label=f'VMA {vma_nitems}', color='purple'),
    ]

    # Plot candlesticks MA, volume, volume MA, RSI
    fig, axes = mpf.plot(
        df, type='candle',              # candlesticks
        volume=True, addplot=addplot,   # MA, volume, volume MA
        figratio=(2, 1), figscale=1.2,
        style=mpf_style,
        show_nontrading=not hides_nontrading,
        returnfig=True,
    )
    # Set location of legends
    for ax in axes:
        if ax.legend_:
            ax.legend(loc=legend_loc)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')

    # Add Profile (e.g., Volume Profile or Turnover Profile)
    bin_size = (max(df['High']) - min(df['Low'])) / total_bins
    bin_round = lambda x: bin_size * round(x / bin_size)
    bin = df[profile_field].groupby(
            df['Close'].apply(lambda x: bin_round(x))).sum()
    ax = fig.add_axes(axes[0].get_position(), sharey=axes[0], frameon=False)
    ax.barh(
        y=bin.keys(),       # price
        width=bin.values,   # bin comulative volume/turnover
        height=0.75*bin_size,
        align='center',
        color='cyan',
        alpha=0.2
    )

    # Set x ticks of the Profile
    ax.set_xlim(right=1.2*max(bin.values))
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    # Set x label of the Profile
    ax.set_xlabel(f'Bin Cumulative {profile_field}')
    if profile_field == 'Turnover':
        ax.set_xlabel('Bin Cumulative Turnover (Price*Volume)')
    ax.xaxis.set_label_position('top')

    # Disable gridlines on the secondary ax
    ax.grid(False)

    return fig


class Volume:
    """Volume Profile, i.e., PBV (Price-by-Volume) or Volume-by-Price
    """
    @staticmethod
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
             total_bins=42, legend_loc='best',
             market_color_style=MarketColorStyle.AUTO,
             style='binancedark', hides_nontrading=True, out_dir='out'):
        """Plot a price-by-volume, PBV (also called volume profile) figure for a
        given stock.

        Here the PBV is overlaid with the price subplot. This figure consists of
        two subplots: a price subplot and a volume subplot. The former includes
        price candlesticks, price moving average lines, while the latter
        includes a trading volume histogram and a volume moving average line.

        Parameters
        ----------
        symbol: str
            the stock symbol.

        period: str, optional
            the period data to download (default is '1y'). Valid values are
            1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.

            - d   -- days
            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval: str, optional
            the interval of an OHLC item (default is '1d'). Valid values are
            1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

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

        legend_loc: str, optional
            the location of the legend (default is 'best').
            Valid locations are

            - 'best'
            - 'upper right'
            - 'upper left'
            - 'lower left'
            - 'lower right'
            - 'right'
            - 'center left'
            - 'center right'
            - 'lower center'
            - 'upper center'
            - 'center'

        market_color_style: MarketColorStyle, optional
            The market color style to use. Default is MarketColorStyle.AUTO.

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

        hides_nontrading: bool, optional
            Whether to hide non-trading periods. Default is True.
        out_dir: str, optional
            the output directory for saving figure.
        """
        # Download stock data
        ticker = tw.as_yfinance(symbol)
        df = yf.Ticker(ticker).history(period=period, interval=interval)

        # Plot
        mc_style = decide_market_color_style(ticker, market_color_style)
        mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                          market_color_style=mc_style)
        fig = _plot(df, mpf_style, 'Volume', period, interval,
                    ma_nitems, vma_nitems, total_bins,
                    legend_loc, hides_nontrading)
        fig.suptitle(
            f"{symbol} - {interval} ({df.index[0]} to {df.index[-1]})",
        )

        # Show the figure
        mpf.show()

        # Write the figure to an PNG file
        out_dir = file_utils.make_dir(out_dir)
        fn = file_utils.gen_fn_info(ticker, interval, df.index[-1],
                                   'volume_prf')
        fig.savefig(f'{out_dir}/{fn}.png')


class Turnover:
    '''Turnover Profile

    Here "turnover" means "trading value" (= price * volume)
    '''
    @staticmethod
    def plot(symbol='TSLA', period='1y', interval='1d',
             ma_nitems=(5, 10, 20, 50, 150), vma_nitems=50,
             total_bins=42, legend_loc='best',
             market_color_style=MarketColorStyle.AUTO,
             style='binancedark', hides_nontrading=True, out_dir='out'):
        """Plot a turnover profile figure for a given stock.

        Here the provile is overlaid with the price subplot. This figure
        consists of two subplots: a price subplot and a volume subplot. The
        former includes price candlesticks, price moving average lines, while
        the latter includes a trading volume histogram and a volume moving
        average line.

        Parameters
        ----------
        symbol: str
            the stock symbol.

        period: str, optional
            the period data to download (default is '1y'). Valid values are
            1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.

            - d   -- days
            - mo  -- monthes
            - y   -- years
            - ytd -- year to date
            - max -- all data

        interval: str, optional
            the interval of an OHLC item (default is '1d'). Valid values are
            1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

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

        legend_loc: str, optional
            the location of the legend (default is 'best').
            Valid locations are

            - 'best'
            - 'upper right'
            - 'upper left'
            - 'lower left'
            - 'lower right'
            - 'right'
            - 'center left'
            - 'center right'
            - 'lower center'
            - 'upper center'
            - 'center'

        market_color_style: MarketColorStyle, optional
            The market color style to use. Default is MarketColorStyle.AUTO.

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

        hides_nontrading: bool, optional
            Whether to hide non-trading periods. Default is True.
        out_dir: str, optional
            the output directory for saving figure.
        """
        # Download stock data
        ticker = tw.as_yfinance(symbol)
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        df['Turnover'] = df['Close'] * df['Volume']

        # Plot
        mc_style = decide_market_color_style(ticker, market_color_style)
        mpf_style = mpfu.decide_mpf_style(base_mpf_style=style,
                                          market_color_style=mc_style)
        fig = _plot(df, mpf_style, 'Turnover', period, interval,
                    ma_nitems, vma_nitems, total_bins,
                    legend_loc, hides_nontrading)
        fig.suptitle(
            f"{symbol} - {interval} ({df.index[0]} to {df.index[-1]})",
        )

        # Show the figure
        mpf.show()

        # Write the figure to an PNG file
        out_dir = file_utils.make_dir(out_dir)
        fn = file_utils.gen_fn_info(ticker, interval, df.index[-1],
                                   'turnover_prf')
        fig.savefig(f'{out_dir}/{fn}.png')


if __name__ == '__main__':
    mpfu.use_mac_chinese_font()
    Volume.plot('TSLA')
    Volume.plot('台積電')
    Turnover.plot('台積電')

