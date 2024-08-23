"""
Technical Analysis
"""
__version__ = "1.1"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/31 (initial version) ~ 2024/08/23 (last revision)"

__all__ = [
    'simple_moving_average',
    'exponential_moving_average',
    'rsi',
]


def simple_moving_average(values, window):
    """
    Calculate Simple Moving Average (SMA) for given values and window size.

    Parameters
    ----------
    values : pandas.Series
        Series of values for which to calculate the SMA.

    window : int
        Number of periods over which to calculate the SMA.

    Returns
    -------
    pandas.Series
        Series containing the calculated Simple Moving Average (SMA) values.

    Examples
    --------
    >>> values = pd.Series([100, 105, 110, 115, 120],
    ... index=pd.date_range(start='2024-01-01', periods=5, freq='D'))
    >>> simple_moving_average(values, window=3)
    2024-01-01      NaN
    2024-01-02      NaN
    2024-01-03    105.0
    2024-01-04    110.0
    2024-01-05    115.0
    dtype: float64
    """
    return values.rolling(window=window).mean()


def exponential_moving_average(values, window, adjust=False):
    """
    Calculate Exponential Moving Average (EMA) for given values and window size.

    Parameters
    ----------
    values : pandas.Series
        Series of values for which to calculate the EMA.

    window : int
        Number of periods over which to calculate the EMA.

    adjust : bool, optional
        Whether to adjust the EMA calculation (default is False).

    Returns
    -------
    pandas.Series
        Series containing the calculated Exponential Moving Average (EMA)
        values.
    Examples
    --------
    >>> values = pd.Series([100, 105, 110, 115, 120],
    ... index=pd.date_range(start='2024-01-01', periods=5, freq='D'))
    >>> exponential_moving_average(values, window=3)
    2024-01-01    100.000000
    2024-01-02    100.000000
    2024-01-03    102.666667
    2024-01-04    107.111111
    2024-01-05    112.074074
    dtype: float64
    """
    return values.ewm(span=window, adjust=adjust).mean()


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

