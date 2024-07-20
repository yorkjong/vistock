"""
Utility Functons to calculate bull-run and drawdown.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/21 (initial version) ~ 2024/07/21 (last revision)"

import numpy as np


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

