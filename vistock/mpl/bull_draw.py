"""
Visualize a Bull-Run Drawdown chart for a stock.
"""
__software__ = "BullRun Drawdown"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/21 (initial version) ~ 2024/07/21 (last revision)"

__all__ = [ 'plot' ]

import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mplfinance as mpf

from .. import tw
from .. import file_util


def plot(ticker='TSLA', period='1y', interval='1d', legend_loc='best'):
    """Visualize bull run and drawdown indicators on a stock price chart.

    This function downloads stock data for the specified ticker and period,
    calculates the drawdown and bull run indicators, and visualizes them using
    mplfinance.

    Parameters
    ----------
    ticker
        the ticker name (default is 'TSLA')
    period
        the period (default is '1y' that means 1 year)
    interval
        the interval (default is '1d' that means 1 day)
    legend_loc
        the location of the legend (default is 'best')
        Valid locations are
            best
            upper right
            upper left
            lower left
            lower right
            right
            center left
            center right
            lower center
            upper center
            center
    """
    # Download stock data
    ticker = tw.as_yfinance(ticker)
    df = yf.Ticker(ticker).history(period=period, interval=interval)

    # Calculate drawdown and bull run
    df['Drawdown'] = calculate_drawdown(df)
    df['BullRun'] = calculate_bull_run(df)

    # Add Bull Run and Drawdown indicators
    bull_run_addplot = mpf.make_addplot(
        df['BullRun'], type='bar', color='blue', alpha=0.5,
        panel=0, secondary_y=True, ylabel='BullRun and Drawdown')
    drawdown_addplot = mpf.make_addplot(
        df['Drawdown'], type='bar', color='orange', alpha=0.5,
        panel=0, secondary_y=True)

    # Add Volume Moving Average
    vma = mpf.make_addplot(
        df['Volume'], mav=50,
        type='line', linestyle='',
        panel=1)

    # Plot candlesticks price, bull-run, drawdown, volume, and volume MA
    fig, axes = mpf.plot(
        df, type='line',
        volume=True, addplot=[bull_run_addplot, drawdown_addplot, vma],
        style='yahoo', figsize=(16, 8),
        returnfig=True
    )

    # Move indicators y-axis to the left and price & volume y-axis to the right
    for ax in axes:
        if ax.get_ylabel() == 'BullRun and Drawdown':
            ax.yaxis.tick_left()
            ax.yaxis.set_label_position("left")
        else:
            ax.yaxis.tick_right()
            ax.yaxis.set_label_position("right")

    # Plot legend
    legend = [
        Line2D([0], [0], color='blue', lw=4, label='Bull Run'),
        Line2D([0], [0], color='orange', lw=4, label='Drawdown'),
    ]
    axes[0].legend(handles=legend, loc=legend_loc)

    # Convert datetime index to string format suitable for display
    if interval.endswith('m') or interval.endswith('h'):
        df.index = df.index.strftime('%Y-%m-%d %H:%M')
    else:
        df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(
        f"{ticker} {interval} ({df.index.values[0]}~{df.index.values[-1]})",
        y=0.93
    )

    # Show
    mpf.show()  # plt.show()

    # Write the figure to an PNG file
    out_dir = file_util.make_dir(out_dir)
    fn = file_util.gen_fn_info(symbol, interval, df.index.values[-1], __file__)
    fig.savefig(f'{out_dir}/{fn}.png')


#------------------------------------------------------------------------------
# Help Functions
#------------------------------------------------------------------------------

def calculate_bull_run(df):
    """
    Calculate the bull-run for each 'Close' price in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing stock data with a 'Close' column.

    Returns
    -------
    pandas.Series
        Series representing the bull-run values.
    """
    df['Daily_Return'] = df['Close'].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
    df['Drawdown'] = df['Cumulative_Return'] / df['Cumulative_Return'].cummax() - 1
    drawdown_threshold = np.percentile(df['Drawdown'].dropna(), 80)

    bull_run = 0
    max_price = df['Close'].iloc[0]
    bull_runs = []

    for price, returns in zip(df['Close'], df['Daily_Return']):
        if price > max_price:
            max_price = price

        if returns > 0:
            bull_run += returns
        elif (max_price - price) / max_price > drawdown_threshold:
            bull_run = 0
            max_price = price

        bull_runs.append(bull_run)

    return bull_runs


def calculate_rolling_drawdown(data, window=60):
    """
    Calculate the rolling drawdown for each price in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing stock data with a 'High', 'Close' columns.
    window: int
        window size to rolling.

    Returns
    -------
    pandas.Series
        Series representing the rolling drawdown values.
    """
    rolling_max = data['High'].rolling(window=window, min_periods=1).max()
    drawdown = (data['Close'] - rolling_max) / rolling_max
    return drawdown


def calculate_drawdown(df):
    """
    Calculate the drawdown for each price in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing stock data with a 'High', 'Close' columns.

    Returns
    -------
    pandas.Series
        Series representing the drawdown values.
    """
    peak = df['High'].expanding(min_periods=1).max()
    drawdown = (df['Close'] - peak) / peak
    return drawdown


def calculate_drawdown_v2(df):
    """
    Calculate the drawdown for each price in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing stock data with a 'Close' column.

    Returns
    -------
    pandas.Series
        Series representing the drawdown values.
    """
    peak = df['Close'].expanding(min_periods=1).max()
    drawdown = (df['Close'] - peak) / peak
    return drawdown

#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------

if __name__ == '__main__':
    plot('TSLA')


