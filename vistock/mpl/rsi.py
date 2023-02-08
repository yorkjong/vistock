# -*- coding: utf-8 -*-
"""
Plot a 3-split (price, volume, RSI) stock chart.
* Data from yfinance
* Plot with mplfinance
* RSI from TA-Lib
"""
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
from talib import abstract

__software__ = "Stock chart of price, volume, and RSI"
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2023/02/08 (last revision)"
__all__ = ['plot']


def plot(ticker='TSLA', period='12mo', ma_days=(5, 10, 20, 50, 150),
         vma_days=50, legend_loc='best'):
    """Show a stock figure that consists 3 suplots: a price subplot, a
    volume subplot, and a RSI subplot. The price subplot shows price
    candlesticks, and price moving-average lines. The volume subplot shows a
    volume bar chart and a volume moving average line.

    Parameters
    ----------
    ticker: str
        the ticker name.
    period: str
        the period ('12mo' means 12 monthes)
    ma_days: int Sequence
        a sequence to list days of moving averge lines.
    vma_days: int
        days of the volume moving average line.
    legend_loc: str
        the location of the legend. Valid locations are
            'best'
            'upper right'
            'upper left'
            'lower left'
            'lower right'
            'right'
            'center left'
            'center right'
            'lower center'
            'upper center'
            'center'
    """
    # Download stock data
    df = yf.Ticker(ticker).history(period=period)

    # Add Volume Moving Average
    vma = mpf.make_addplot(df['Volume'], mav=vma_days,
                           type='line', linestyle='', panel=1)

    # Add RSI
    RSI = lambda df, period: abstract.RSI(df, timeperiod=period)
    rsi = mpf.make_addplot(RSI(df['Close'], 14), panel=2, ylabel='RSI')

    # Plot candlesticks MA, volume, volume MA, RSI
    fig, axes = mpf.plot(
        df, type='candle', mav=ma_days,     # candlestick and MA
        volume=True, addplot=[vma, rsi],    # volume, volume MA, RSI
        style='yahoo', figsize=(16, 8),
        returnfig=True
    )
    axes[0].legend([f'MA {d}' for d in ma_days], loc=legend_loc)
    df.index = df.index.strftime('%Y-%m-%d')
    fig.suptitle(f"{ticker}: {df.index.values[0]}~{df.index.values[-1]}",
                 y=0.93)

    # Show and save
    mpf.show()
    fig.savefig(f'{ticker}_{df.index.values[-1]}_rsi.png')


if __name__ == '__main__':
    plot('TSLA')

