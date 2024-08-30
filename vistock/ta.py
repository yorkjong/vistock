"""
Technical Analysis
"""
__version__ = "1.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/31 (initial version) ~ 2024/08/31 (last revision)"

__all__ = [
    'simple_moving_average',
    'exponential_moving_average',
    'rsi',
]


def simple_moving_average(values, window, min_periods=1):
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
    >>> import pandas as pd
    >>> values = pd.Series([100, 105, 110, 115, 120],
    ...         index=pd.date_range(start='2024-01-01', periods=5, freq='D'))
    >>> simple_moving_average(values, window=3)
    2024-01-01      NaN
    2024-01-02      NaN
    2024-01-03    105.0
    2024-01-04    110.0
    2024-01-05    115.0
    Freq: D, dtype: float64
    """
    return values.rolling(window=window, min_periods=min_periods).mean()


def exponential_moving_average(values, window, min_periods=1, adjust=False):
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
    >>> import pandas as pd
    >>> values = pd.Series([100, 105, 110, 115, 120],
    ...         index=pd.date_range(start='2024-01-01', periods=5, freq='D'))
    >>> exponential_moving_average(values, window=3)
    2024-01-01    100.0000
    2024-01-02    102.5000
    2024-01-03    106.2500
    2024-01-04    110.6250
    2024-01-05    115.3125
    Freq: D, dtype: float64
    """
    return values.ewm(span=window, min_periods=min_periods,
                      adjust=adjust).mean()


def rsi(data, periods=14):
    """
    Calculate the Relative Strength Index (RSI) for a given dataset.

    RSI is a momentum oscillator that measures the speed and change of price
    movements.  It oscillates between 0 and 100 and is typically used to
    identify overbought or oversold conditions in a market.

    Parameters
    ----------
    data : pandas.Series
        A pandas Series containing the price data (typically closing prices)
        for which the RSI is to be calculated.

    periods : int, optional, default: 14
        The number of periods to use for the RSI calculation. A typical value
        is 14.

    Returns
    -------
    pandas.Series
        A pandas Series containing the RSI values for the given data.

    Examples
    --------
    >>> import pandas as pd
    >>> import yfinance as yf
    >>> df = yf.download('AAPL', start='2023-01-01', end='2024-01-01')
    >>> df['RSI'] = rsi(df['Close'], periods=14)
    >>> df['RSI'].tail()
    Date
    2023-12-22    59.246142
    2023-12-26    49.031934
    2023-12-27    52.291513
    2023-12-28    47.920430
    2023-12-29    40.185177
    Name: RSI, dtype: float64
    """

    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


if __name__ == '__main__':
    import doctest, time

    start_time = time.time()
    doctest.testmod()
    print(f"Execution time: {time.time() - start_time:.4f} seconds")


