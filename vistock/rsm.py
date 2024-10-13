"""
Mansfield Relative Strength (RSM) Module
-----------------------------------------

This module provides functions for calculating and ranking stocks based on
Mansfield Relative Strength (RSM) and related metrics. It includes methods
to compute Dorsey Relative Strength (RSD), Mansfield Relative Strength (RSM)
using both Simple Moving Average (SMA) and Exponential Moving Average (EMA),
as well as functionality to rank stocks against a benchmark index.

Examples:
~~~~~~~~~
To calculate RSM for a list of stock tickers and rank them:

>>> tickers = ['AAPL', 'MSFT', 'GOOGL']
>>> rank = ranking(tickers, period='2y', interval='1wk', window=52)
>>> print(rank.head())

To compute Mansfield Relative Strength using SMA for specific close prices:

>>> closes = pd.Series([...])  # Example closing prices
>>> closes_index = pd.Series([...])  # Example index closing prices
>>> rsm = mansfield_relative_strength(closes, closes_index, window=52)
>>> print(rsm)

See Also:
~~~~~~~~~
- `Mansfield Relative Strength | ChartMill.com
  <https://www.chartmill.com/documentation/technical-analysis/indicators/
  35-Mansfield-Relative-Strength>`_
- `How to create the Mansfield Relative Performance Indicator - Stage Analysis
  <https://www.stageanalysis.net/blog/4266/
  how-to-create-the-mansfield-relative-performance-indicator>`_

"""
__version__ = "5.3"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/23 (initial version) ~ 2024/10/13 (last revision)"

__all__ = [
    'mansfield_relative_strength',
    'dorsey_relative_strength',
    'rankings',
]

import numpy as np
import pandas as pd
import yfinance as yf

from .ta import simple_moving_average, exponential_moving_average
from . import yf_utils as yfu
from .ranking_utils import append_ratings, move_columns_to_end


#------------------------------------------------------------------------------
# Relative (Price) Stength
#------------------------------------------------------------------------------

def mansfield_relative_strength(closes, closes_index, window, ma='SMA'):
    """
    Calculate Mansfield Relative Strength (RSM) for given close prices, index
    close prices, and window size using a given moving average method ('SMA'
    or 'EMA').

    Parameters
    ----------
    closes: pandas.Series
        Series of closing prices for the stock.
    closes_index: pandas.Series
        Series of closing prices for the benchmark index.
    window: int
        Window size for calculating the Simple Moving Average of the Dorsey
        Relative Strength.
    ma: str, optional
        Moving average type ('SMA', 'EMA'). Default to 'SMA'.

    Returns
    -------
    pandas.Series
        Series containing the calculated Mansfield Relative Strength (RSM)
        values with given moving average method.

    Examples
    --------
    >>> stock_closes = pd.Series([100, 105, 110],
    ...     index=pd.date_range(start='2024-01-01', periods=3, freq='D'))
    >>> index_closes = pd.Series([2000, 2050, 2100],
    ...     index=pd.date_range(start='2024-01-01', periods=3, freq='D'))
    >>> mansfield_relative_strength(stock_closes, index_closes, window=2)
    2024-01-01    5.000000
    2024-01-02    5.097847
    2024-01-03    5.238095
    dtype: float64
    >>> mansfield_relative_strength_with_ema(stock_closes, index_closes,
    ...     window=2, ma='EMA')
    2024-01-01    5.000000
    2024-01-02    5.097847
    2024-01-03    5.238095
    dtype: float64
    """
    # Select the MA function based on the 'ma' parameter
    try:
        ma_func = {
            'SMA': simple_moving_average,
            'EMA': exponential_moving_average,
        }[ma]
    except KeyError:
        raise ValueError("Invalid ma type. Must be 'SMA' or 'EMA'.")

    closes = closes.ffill()
    closes_index = closes_index.ffill()
    rsd = dorsey_relative_strength(closes, closes_index)
    rsm = ((rsd / ma_func(rsd, window)) - 1) * 100
    return rsm.round(2)


def dorsey_relative_strength(closes, closes_index):
    """
    Calculate Dorsey Relative Strength (RSD) for given close prices and index
    close prices.

    Parameters
    ----------
    closes: pandas.Series
        Series of closing prices for the stock.

    closes_index: pandas.Series
        Series of closing prices for the benchmark index.

    Returns
    -------
    pandas.Series
        Series containing the calculated Dorsey Relative Strength (RSD) values.
    """
    return (closes / closes_index) * 100

#------------------------------------------------------------------------------
# EPS Relative Strength
#------------------------------------------------------------------------------

def relative_strength_vs_benchmark(metric_series, bench_series, window=4):
    """
    Calculate the relative strength of a financial metric relative to a
    benchmark index.

    This function computes the relative strength of a financial metric by
    comparing each value to the average over a specified window, and calculates
    the relative strength.

    Parameters
    ----------
    metric_series: pd.Series or array-like
        A series or array-like object of financial metric values for a stock.
        This will be converted to a pandas Series.
    bench_series: pd.Series or array-like
        A series or array-like object of financial metric values for the
        benchmark index. This will be converted to a pandas Series.
    window: int, optional
        The number of periods over which to calculate the moving average (
        default is 4).

    Returns
    -------
    pd.Series
        A series containing the relative strength of the metric compared to the
        benchmark index.
    """
    # Ensure inputs are pandas Series
    if not isinstance(metric_series, pd.Series):
        metric_series = pd.Series(metric_series)
    if not isinstance(bench_series, pd.Series):
        bench_series = pd.Series(bench_series)

    # Align and interpolate missing data
    length = min(len(metric_series), len(bench_series))
    metric_series = metric_series.infer_objects().interpolate()[-length:]
    bench_series = bench_series.infer_objects().interpolate()[-length:]

    # Calculate the moving average
    avg_metric = metric_series.rolling(window=window, min_periods=1).mean()
    avg_bench = bench_series.rolling(window=window, min_periods=1).mean()

    # Calculate percentage change relative to the moving average
    metric_change = (metric_series - avg_metric) / (
            np.minimum(np.abs(avg_metric), np.abs(metric_series)) + 1e-8)
    bench_change = (bench_series - avg_bench) / (
            np.minimum(np.abs(avg_bench), np.abs(bench_series)) + 1e-8)

    # Calculate Relative Strength and convert to percentage
    rsm_values = (metric_change.values - bench_change.values) * 100

    # Return result as a Series with the original index
    rsm = pd.Series(rsm_values, index=metric_series.index)

    # Replace inf and -inf with NaN
    rsm = rsm.replace([np.inf, -np.inf], np.nan)

    return rsm.round(2)


#------------------------------------------------------------------------------
# Ranking
#------------------------------------------------------------------------------

def rankings(tickers, ticker_ref='^GSPC',
             period='2y', interval='1wk', ma="SMA", rating_method='rank'):
    """
    Rank stocks based on their Mansfield Relative Strength (RSM) against an
    index benchmark.

    Parameters
    ----------
    tickers : list of str
        List of stock tickers to rank.

    ticker_ref : str, optional
        Ticker symbol of the benchmark index. Defaults to '^GSPC' (S&P 500).

    period : str, optional
        Period for retrieving historical data ('6mo', '1y', '2y', '5y', 'ytd',
        'max'). Defaults to '2y' (two years).

    interval : str, optional
        Interval for historical data ('1d', '1wk'). Defaults to '1wk' (one
        week).

    ma : str, optional
        Moving average type ('SMA' for Simple Moving Average or 'EMA' for
        Exponential Moving Average). Defaults to 'SMA'.

    rating_method : str, optional
        Method for calculating stock ratings. Either 'rank' (based on relative
        ranking) or 'qcut' (based on quantiles). Defaults to 'rank'.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing ranked stock data with relative strength and
        other metrics.
    """
    # Set moving average windows based on the interval
    try:
        rs_win = { '1d': 252, '1wk': 52}[interval]
        ma_wins = { '1d': [50, 150], '1wk': [10, 30]}[interval]
        vma_win = { '1d': 50, '1wk': 10}[interval]
    except KeyError:
        raise ValueError("Invalid interval. " "Must be '1d', or '1wk'.")

    stock_df = build_stock_rs_df(tickers=tickers, ticker_ref=ticker_ref,
                                 period=period, interval=interval, ma=ma)
    stock_df = stock_df.sort_values(by='RS', ascending=False)

    rs_columns = ['RS', '1 Month Ago', '3 Months Ago',
                  '6 Months Ago', '9 Months Ago']
    rating_columns = ['Rating (RS)', 'Rating (1M)', 'Rating (3M)',
                      'Rating (6M)', 'Rating (9M)']
    ranking_df = append_ratings(stock_df, rs_columns,
                                rating_columns, method=rating_method)

    ranking_df = move_columns_to_end(
        ranking_df,
        [
            'Price',
            '52W pos',
            *[f'MA{w}' for w in ma_wins],
            f'Volume / VMA{vma_win}',
        ],
    )
    return ranking_df


def build_stock_rs_df(tickers, ticker_ref='^GSPC',
                      period='2y', interval='1wk', ma="SMA"):
    """
    Build a DataFrame of stocks ranked by their Mansfield Relative Strength
    (RSM) against a benchmark index.

    Parameters
    ----------
    tickers : list of str
        List of stock tickers to include in the ranking.

    ticker_ref : str, optional
        Ticker symbol of the benchmark index. Defaults to '^GSPC' (S&P 500).

    period : str, optional
        Period for historical data ('6mo', '1y', '2y', '5y', 'ytd', 'max').
        Defaults to '2y' (two years).

    interval : str, optional
        Interval for historical data ('1d', '1wk'). Defaults to '1wk' (one week).

    ma : str, optional
        Moving average type ('SMA' for Simple Moving Average or 'EMA' for
        Exponential Moving Average).  Defaults to 'SMA'.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing relative strength values, historical data, and
        moving averages for each stock.
    """
    # Select the MA function based on the 'ma' parameter
    try:
        ma_func = {
            'SMA': simple_moving_average,
            'EMA': exponential_moving_average,
        }[ma]
    except KeyError:
        raise ValueError("Invalid moving average type. Must be 'SMA' or 'EMA'.")

    # Set moving average windows based on the interval
    try:
        rs_win = { '1d': 252, '1wk': 52}[interval]
        ma_wins = { '1d': [50, 150], '1wk': [10, 30]}[interval]
        vma_win = { '1d': 50, '1wk': 10}[interval]
    except KeyError:
        raise ValueError("Invalid interval. " "Must be '1d', or '1wk'.")

    # Fetch data for stocks and index
    df_all = yf.download([ticker_ref] + tickers,
                         period=period, interval=interval)
    df_ref = df_all.xs(ticker_ref, level='Ticker', axis=1)
    print("Num of downloaded stocks: "
          f"{len(df_all.columns.get_level_values('Ticker').unique())}")

    rows = []
    price_ma = {}
    for ticker in tickers:
        df = df_all.xs(ticker, level='Ticker', axis=1)
        rsm = mansfield_relative_strength(df['Close'], df_ref['Close'],
                                          rs_win, ma=ma)
        for win in ma_wins:
            price_ma[f'{win}'] = ma_func(df['Close'], win).round(2)
        vol_div_vma = (df['Volume'] / ma_func(df['Volume'], vma_win)).round(2)

        end_date = rsm.index[-1]

        # Calculate position in 52W range
        high_52w = df['Close'].rolling(window=252, min_periods=1).max().iloc[-1]
        low_52w = df['Close'].rolling(window=252, min_periods=1).min().iloc[-1]
        current_price = df['Close'].asof(end_date)
        range_position = (current_price - low_52w) / (high_52w - low_52w)

        # Construct DataFrame for current stock
        row = {
            'Ticker': ticker,
            'RS': rsm.asof(end_date),
            '1 Week Ago': rsm.asof(end_date - pd.DateOffset(weeks=1)),
            '1 Month Ago': rsm.asof(end_date - pd.DateOffset(months=1)),
            '3 Months Ago': rsm.asof(end_date - pd.DateOffset(months=3)),
            '6 Months Ago': rsm.asof(end_date - pd.DateOffset(months=6)),
            '9 Months Ago': rsm.asof(end_date - pd.DateOffset(months=9)),
            'Price': df['Close'].asof(end_date).round(2),
            '52W pos': range_position.round(2),
            **{f'MA{w}': price_ma[f'{w}'].iloc[-1] for w in ma_wins},
            f'Volume / VMA{vma_win}': vol_div_vma.iloc[-1],
        }
        rows.append(row)

    # Combine rows into a single DataFrame
    stock_df = pd.DataFrame(rows)

    return stock_df


#------------------------------------------------------------------------------
# Unit Test
#------------------------------------------------------------------------------

def main(period='2y', ma="EMA", out_dir='out'):
    import os
    from datetime import datetime
    from .stock_indices import get_tickers

    code = 'SPX+DJIA+NDX+SOX'
    code = 'SOX'
    #code = 'SPX+DJIA+NDX+RUI+SOX'
    tickers = get_tickers(code)

    # cases of missing 'Basic EPS' field.
    #tickers = ['3036A.TW', '2882B.TW', '8349A.TWO', '2887Z1.TW']

    # case of empty financials DataFrame
    #tickers = ['910861.TW']

    rank = rankings(tickers, period=period, interval='1wk', ma=ma)
    print(rank.head(10))

    # Save to CSV
    print("\n\n***")
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    filename = f'{code}_stocks_{period}_{ma}_{today}.csv'
    rank.to_csv(os.path.join(out_dir, filename), index=False)
    print(f'Your "{filename}" is in the "{out_dir}" folder.')
    print("***\n")


if __name__ == "__main__":
    import time

    start_time = time.time()
    main(ma="SMA")
    print(f"Execution time: {time.time() - start_time:.4f} seconds")
