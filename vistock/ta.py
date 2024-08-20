"""
Technical Analysis
"""
__version__ = "1.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/31 (initial version) ~ 2024/07/31 (last revision)"

__all__ = [
    'rsi',
]


def rsi(data, periods=14):
    """
    Calculate the Relative Strength Index (RSI) for a given dataset.

    RSI is a momentum oscillator that measures the speed and change of price
    movements.  It oscillates between 0 and 100 and is typically used to
    identify overbought or oversold conditions in a market.

    Parameters:
    -----------
    data : pandas.Series
        A pandas Series containing the price data (typically closing prices)
        for which the RSI is to be calculated.

    periods : int, optional, default: 14
        The number of periods to use for the RSI calculation. A typical value
        is 14.

    Returns:
    --------
    pandas.Series
        A pandas Series containing the RSI values for the given data.

    Example:
    --------
    >>> import pandas as pd
    >>> import yfinance as yf
    >>> df = yf.download('AAPL', start='2023-01-01', end='2024-01-01')
    >>> df['RSI'] = rsi(df['Close'], periods=14)
    >>> df['RSI'].tail()
    """

    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

