"""
IBD RS (Relative Strength) Rating Module
----------------------------------------

This module provides tools for analyzing and ranking stocks based on their
relative strength compared to a benchmark index, inspired by the Investor's
Business Daily (IBD) methodology.

Key Features:
~~~~~~~~~~~~~
- Relative strength calculation
- Stock and industry ranking generation
- Rating-based filtering of rankings

Usage:
~~~~~~
::

    import ibd
    from .ranking_utils import append_ratings, groupby_industry

    tickers = ['MSFT', 'NVDA', 'AAPL', 'GOOGL', 'AMZN', 'TSLA']
    stock_df = build_stock_rs_df(tickers)
    stock_df = stock_df.sort_values(by='RS', ascending=False)

    rs_columns = ['RS', '1 Month Ago', '3 Months Ago', '6 Months Ago']
    stock_df = append_ratings(stock_df, rs_columns)

    columns =  ['Sector', 'Ticker'] + rs_columns
    industry_df = groupby_industry(stock_df, columns, key='RS')

    industry_df = industry_df.sort_values(by='RS', ascending=False)
    industry_df = append_ratings(industry_df, rs_columns)

    industry_df = industry_df.rename(columns={
        'Ticker': 'Tickers',
    })

See Also:
~~~~~~~~~
- `RS Rating — Indicator by Fred6724 — tradingview
  <https://www.tradingview.com/script/pziQwiT2/>`_
- `Relative Strength (IBD Style) — Indicator by Skyte — TradingView
  <https://www.tradingview.com/script/SHE1xOMC-Relative-Strength-IBD-Style/>`_

  - `relative-strength/rs_ranking.py at main · skyte/relative-strength
    <https://github.com/skyte/relative-strength/blob/main/rs_ranking.py>`_

- `Exclusive IBD Ratings | Stock News & Stock Market Analysis - IBD
  <https://www.investors.com/ibd-university/
  find-evaluate-stocks/exclusive-ratings/>`_
"""
__version__ = "5.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/05 (initial version) ~ 2024/10/07 (last revision)"

__all__ = [
    'relative_strength',
    'relative_strength_3m',
    'build_stock_rs_df',
    'ma_window_size',
]

import numpy as np
import pandas as pd
import yfinance as yf

import vistock.yf_utils as yfu
from .ranking_utils import append_ratings, groupby_industry


#------------------------------------------------------------------------------
# IBD RS (Relative Strength) Rating
#------------------------------------------------------------------------------

def relative_strength(closes, closes_ref, interval='1d'):
    """
    Calculate the relative strength of a stock compared to a reference index.

    Relative Strength (RS) is a metric used to evaluate the performance of a
    stock relative to a benchmark index. A higher RS rating indicates that the
    stock has outperformed the index, while a lower RS rating suggests
    underperformance.

    This function calculates the RS rating by comparing the quarter-weighted
    growth of the stock's closing prices to the quarter-weighted growth of
    the reference index's closing prices over the past year. The formula is as
    follows:

    ::

        growth = (current - previous) / previous
        gf = current/previous = growth + 1
        relative_rate = gf_stock / gf_index
        relative_strength = relative_rate * 100

    Here gf means "growth factor", i.e., "price ratio"

    The quarter-weighted growth is calculated using the `weighted_growth`
    function.

    Parameters
    ----------
    closes: pd.Series
        Closing prices of the stock.

    closes_ref: pd.Series
        Closing prices of the reference index.

    interval: str, optional
        The frequency of the data points. Must be one of '1d' for daily data,
        '1wk' for weekly data, or '1mo' for monthly data. Defaults to '1d'.

    Returns
    -------
    pd.Series
        Relative strength values for the stock.

    Example
    -------
    >>> stock_closes = pd.Series([100, 102, 105, 103, 107])
    >>> index_closes = pd.Series([1000, 1010, 1015, 1005, 1020])
    >>> rs = relative_strength(stock_closes, index_closes)

    """
    growth_stock = weighted_growth(closes, interval)
    growth_ref = weighted_growth(closes_ref, interval)
    rs = (1 + growth_stock) / (1 + growth_ref) * 100
    return round(rs, 2)


def weighted_growth(closes, interval):
    """
    Calculate the performance of the last year, with the most recent quarter
    weighted double.

    This function calculates growths (returns) for each of the last four
    quarters and applies a weighting scheme that emphasizes recent performance.
    The most recent quarter is given a weight of 40%, while each of the three
    preceding quarters are given a weight of 20%.

    Here is the formula for calculating the return:

        RS Return = 40% * P3 + 20% * P6 + 20% * P9 + 20% * P12
        With
        P3 = Performance over the last quarter (3 months)
        P6 = Performance over the last two quarters (6 months)
        P9 = Performance over the last three quarters (9 months)
        P12 = Performance over the last four quarters (12 months)

    Parameters
    ----------
    closes: pd.Series
        Closing prices of the stock/index.
    interval: str, optional
        The frequency of the data points. Must be one of '1d' for daily
        data, '1wk' for weekly data, or '1mo' for monthly data.

    Returns
    -------
    pd.Series: Performance values of the stock/index.

    Example
    -------
    >>> closes = pd.Series([100, 102, 105, 103, 107, 110, 112])
    >>> weighted_perf = weighted_growth(closes)
    """
    # Calculate performances over the last quarters
    p1 = quarters_growth(closes, 1, interval) # over the last quarter
    p2 = quarters_growth(closes, 2, interval) # over the last two quarters
    p3 = quarters_growth(closes, 3, interval) # over the last three quarters
    p4 = quarters_growth(closes, 4, interval) # over the last four quarters
    return (2 * p1 + p2 + p3 + p4) / 5


def quarters_growth(closes, n, interval):
    """
    Calculate the growth (percentage change) over the last n quarters.

    This function uses 63 trading days (252 / 4) as an approximation for
    one quarter. This is based on the common assumption of 252 trading
    days in a year.

    Parameters
    ----------
    closes: pd.Series
        Closing prices of the stock or index.

    n: int
        Number of quarters to look back.

    interval: str, optional
        The frequency of the data points. Must be one of '1d' for daily data,
        '1wk' for weekly data, or '1mo' for monthly data.

    Returns
    -------
    pd.Series
        The return (percentage change) over the last n quarters.

    Example
    -------
    >>> closes = pd.Series([100, 102, 105, 103, 107, 110, 112])
    >>> quarterly_growth = quarters_growth(closes, 1)
    """
    quarter = {
        '1d': 252//4,   # 252 trading days in a year
        '1wk': 52//4,   # 52 weeks in a year
        '1mo': 12//4,   # 12 months in a year
    }[interval]
    periods = min(len(closes) - 1, quarter * n)

    grwoth = closes.ffill().pct_change(periods=periods, fill_method=None)
    return grwoth.fillna(0)


#------------------------------------------------------------------------------
# IBD's 3-Month Relative Strength
#------------------------------------------------------------------------------

def relative_strength_3m(closes, closes_ref, interval='1d'):
    """
    Calculate the 3-Month Relative Strength of a stock compared to a reference
    index, based on price performance (growths).

    The 3-Month Relative Strength Rating (RS Rating) measures the stock's
    price performance against a benchmark index over a recent three-month
    period. This rating is designed to help investors quickly gauge the
    strength of a stock's performance relative to the market.

    Parameters
    ----------
    closes: pd.Series
        Closing prices of the stock.

    closes_ref: pd.Series
        Closing prices of the reference index.

    interval: str, optional
        The frequency of the data points. Must be one of '1d' for daily data,
        '1wk' for weekly data, or '1mo' for monthly data. Defaults to '1d'.

    Returns
    -------
    pd.Series
        3-Month relative strength values for the stock, rounded to two decimal
        places. The values represent the stock's performance relative to the
        benchmark index, with 100 indicating parity.
    """
    # Determine the number of trading days for the specified interval
    span = {
        '1d': 252 // 4,  # a 3-month period based on 252 trading days in a year
        '1wk': 52 // 4,  # 13 weeks (3 months) for weekly data
        '1mo': 12 // 4,  # 3 months for monthly data
    }[interval]

    return relative_strength_with_span(closes, closes_ref, span)


def relative_strength_with_span(closes, closes_ref, span):
    """
    Calculate the relative strength of a stock compared to a reference index
    based on price performance (growths), over a specified period.

    Parameters
    ----------
    closes: pd.Series
        Closing prices of the stock.

    closes_ref: pd.Series
        Closing prices of the reference index.

    span: int
        The span (number of periods) to calculate the exponential moving
        average (EMA) for the growth factors.

    Returns
    -------
    pd.Series
        Relative strength values for the stock, rounded to two decimal places.
        The values represent the stock's performance relative to the benchmark
        index, with 100 indicating parity.
    """
    # Calculate daily growths (returns) for the stock and reference index
    growth_stock = closes.pct_change(fill_method=None).fillna(0)
    growth_ref = closes_ref.pct_change(fill_method=None).fillna(0)

    # Calculate daily growth factors
    gf_stock = growth_stock + 1
    gf_ref = growth_ref + 1

    # Calculate the Exponential Moving Average (EMA) of the growth factors
    ema_gf_stock = gf_stock.ewm(span=span, adjust=False).mean()
    ema_gf_ref = gf_ref.ewm(span=span, adjust=False).mean()

    # Calculate the cumulative growth factors
    cum_gf_stock = ema_gf_stock.rolling(window=span,
                                        min_periods=1).apply(np.prod, raw=True)
    cum_gf_ref = ema_gf_ref.rolling(window=span,
                                    min_periods=1).apply(np.prod, raw=True)

    # Calculate the relative strength (RS)
    rs = cum_gf_stock / cum_gf_ref * 100

    return rs.round(2)  # Return the RS values rounded to two decimal places


#------------------------------------------------------------------------------
# IBD RS Ranking (with RS rating)
#------------------------------------------------------------------------------

def ranking(tickers, ticker_ref='^GSPC', period='2y', interval='1d',
            rs_window='12mo'):
    """
    Rank stocks based on their IBD Relative Strength against an index
    benchmark.

    Parameters
    ----------
    tickers: list of str
        List of stock tickers to rank.

    ticker_ref: str, optional
        Ticker symbol of the benchmark. Default to '^GSPC' (S&P 500)

    period: str, optional
        Period for historical data ('6mo', '1y', '2y', '5y', 'ytd', 'max').
        Default to '2y' (two years).

    interval: str, optional
        Interval for historical data ('1d', '1wk', '1mo').
        Default to '1wk' (one week).

    rs_window: str, optional
        Specify the time window ('3mo' or '12mo') for Relative Strength
        calculation. Default to '12mo'.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the ranked stocks.

    Example
    -------
    >>> tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    >>> stock_rankings  = ranking(tickers)
    >>> print(stock_rankings.head())
    """
    # Select the appropriate relative strength function based on the rs_window
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_window]

    # Fetch data for stock and index
    df = yf.download([ticker_ref] + tickers, period=period, interval=interval)
    df = df.xs('Close', level='Price', axis=1)

    # Fetch info for stocks
    info = yfu.download_tickers_info(tickers, ['sector', 'industry'])

    rs_data = []
    for ticker in tickers:
        rs = rs_func(df[ticker], df[ticker_ref], interval)
        end_date = rs.index[-1]

        # Calculate max values for the specified time periods
        one_week_ago = end_date - pd.DateOffset(weeks=1)
        one_month_ago = end_date - pd.DateOffset(months=1)
        three_months_ago = end_date - pd.DateOffset(months=3)
        six_months_ago = end_date - pd.DateOffset(months=6)

        rs_data.append({
            'Ticker': ticker,
            'Price': df[ticker].asof(end_date).round(2),
            'Sector': info[ticker]['sector'],
            'Industry': info[ticker]['industry'],
            'Relative Strength': rs.asof(end_date),
            '1wk..end': rs.loc[one_week_ago:end_date].max(),
            '1mo..1wk': rs.loc[one_month_ago:one_week_ago].max(),
            '3mo..1mo': rs.loc[three_months_ago:one_month_ago].max(),
            '6mo..3mo': rs.loc[six_months_ago:three_months_ago].max(),
        })

    # Create DataFrame from RS data
    ranking_df = pd.DataFrame(rs_data)

    # Rank based on Relative Strength
    rank_columns = ['Rank (%)',
                    '1mo..1wk (%)', '3mo..1mo (%)',  '6mo..3mo (%)']
    rs_columns = ['Relative Strength',
                  '1mo..1wk', '3mo..1mo', '6mo..3mo']
    for rank_col, rs_col in zip(rank_columns, rs_columns):
        rank_pct = ranking_df[rs_col].rank(pct=True)
        ranking_df[rank_col] = (rank_pct * 100).round(2)

    # Sort by current rank
    ranking_df = ranking_df.sort_values(by='Rank (%)', ascending=False)

    # Calculate average RS for each industry
    industry_rs = ranking_df.groupby('Industry')[
        'Relative Strength'].mean().round(2).reset_index()
    industry_rs.columns = ['Industry', 'Industry RS']

    # Rank industries based on average Relative Strength
    rank_pct = industry_rs['Industry RS'].rank(pct=True)
    industry_rs['Industry Rank (%)'] = (rank_pct * 100).round(2)

    # Merge industry rankings back into stock DataFrame
    ranking_df = pd.merge(ranking_df, industry_rs, on='Industry', how='left')

    return ranking_df


#------------------------------------------------------------------------------
# Build Stock RS DataFrame
#------------------------------------------------------------------------------

def build_stock_rs_df(tickers, ticker_ref='^GSPC', period='2y', interval= '1d',
                      rs_window='12mo'):
    """
    Analyzes stocks and calculates relative strength (RS) for the given stock
    tickers compared to a reference index. Returns a DataFrame of stock
    rankings.

    Parameters
    ----------
    tickers: list
        A list of stock tickers to analyze.

    ticker_ref: str, optional
        The ticker symbol for the reference index. Defaults to '^GSPC' (S&P
        500).

    period: str, optional
        The period for which to fetch historical data. Defaults to '2y' (two
        years).

    interval: str, optional
        The frequency of the data points. Must be one of '1d' for daily data,
        '1wk' for weekly data, or '1mo' for monthly data. Defaults to '1d'.

    rs_window: str, optional
        Specify the time window ('3mo' or '12mo') for Relative Strength
        calculation.  Defaults to '12mo'.

    Returns
    -------
    pd.DataFrame
        DataFrame containing stock rankings with columns:
        Ticker, Price, Sector, Industry, RS (current), RS (1 month ago),
        RS (3 months ago), RS (6 months ago).
    """
    # Select the appropriate relative strength function based on the rs_window
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_window]

    # Batch download stock data
    df = yf.download([ticker_ref] + tickers, period=period, interval=interval)
    df = df.xs('Close', level='Price', axis=1)

    # Batch download stock info
    info = yfu.download_tickers_info(tickers, ['sector', 'industry'])

    # Calculate RS values for all stocks
    rs_data = []
    for ticker in tickers:
        rs_series = rs_func(df[ticker], df[ticker_ref], interval)
        end_date = rs_series.index[-1]

        rs_data.append({
            'Ticker': ticker,
            'Price': df[ticker].asof(end_date).round(2),
            'Sector': info[ticker]['sector'],
            'Industry': info[ticker]['industry'],
            'RS': rs_series.asof(end_date),
            '1 Month Ago': rs_series.asof(end_date - pd.DateOffset(months=1)),
            '3 Months Ago': rs_series.asof(end_date - pd.DateOffset(months=3)),
            '6 Months Ago': rs_series.asof(end_date - pd.DateOffset(months=6)),
        })

    # Create DataFrame from RS data
    stock_df = pd.DataFrame(rs_data)

    return stock_df


#------------------------------------------------------------------------------
# Misc Help Functions
#------------------------------------------------------------------------------

def ma_window_size(interval, days):
    """
    Calculate moving average window size based on IBD (Investor's Business
    Daily) convention.

    This function adjusts the window size for weekly data to maintain
    consistency with daily calculations.

    Parameters
    ----------
    interval: str
        The data interval. Must be either '1d' for daily or '1wk' for weekly.

    days: int
        Number of calendar days for the desired moving average period.

    Returns
    -------
    int
        Calculated window size (number of data points) for the moving average.

    Raises
    ------
    ValueError
        If an unsupported interval is provided (not '1d' or '1wk').

    Examples
    --------
    >>> ma_window_size('1d', 50)
    50
    >>> ma_window_size('1wk', 50)
    10
    """
    if interval == '1d':
        return days
    elif interval == '1wk':
        return days // 5  # 1 week = 5 trading days
    else:
        raise ValueError("interval must be either '1d' or '1wk'")


#------------------------------------------------------------------------------
# Unit Test
#------------------------------------------------------------------------------

def test_ranking(period='2y', rs_window='12mo', out_dir='out'):
    import os
    from datetime import datetime
    from vistock.stock_indices import get_tickers

    #code = 'SPX+DJIA+NDX+SOX'
    code = 'SPX'
    tickers = get_tickers(code)
    remove_tickers = ['HBAN', 'SW', 'BRK.B', 'VLTO', 'ARM', 'SOLV', 'GEV', 'BF.B']
    tickers = [t for t in tickers if t not in remove_tickers]

    rank = ranking(tickers, period=period, interval='1d', rs_window=rs_window)
    print(rank.head(10))

    # Save to CSV
    print("\n\n***")
    os.makedirs(out_dir, exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    filename = f'{code}_stocks_{period}_ibd{rs_window}_{today}.csv'
    rank.to_csv(os.path.join(out_dir, filename), index=False)
    print(f'Your "{filename}" is in the "{out_dir}" folder.')
    print("***\n")

#------------------------------------------------------------------------------

def test(min_rating=80, rating_method='qcut',
         rs_window='12mo', out_dir='out'):
    '''
    Parameters
    ----------
    min_rating: int, optional
        The minimum rating for a stock to be included in the rankings.
        Defaults to 80.

    out_dir: str, optional
        The output directory to store CSV tables. Defaults to 'out'.
    '''
    import os
    from datetime import datetime
    import vistock.stock_indices as si

    code = 'SPX'
    tickers = si.get_tickers(code)

    stock_df = build_stock_rs_df(tickers, rs_window=rs_window)
    stock_df = stock_df.sort_values(by='RS', ascending=False)

    rs_columns = ['RS', '1 Month Ago', '3 Months Ago', '6 Months Ago']
    stock_df = append_ratings(stock_df, rs_columns, method=rating_method)

    columns =  ['Sector', 'Ticker'] + rs_columns
    industry_df = groupby_industry(stock_df, columns, key='RS')

    industry_df = industry_df.sort_values(by='RS', ascending=False)
    industry_df = append_ratings(industry_df, rs_columns, method=rating_method)

    industry_df = industry_df.rename(columns={
        'Ticker': 'Tickers',
    })

    if stock_df.empty or industry_df.empty:
        print("Not enough data to generate rankings.")
        return

    print('Stock Rankings:')
    print(stock_df[stock_df["Rating (RS)"] >= min_rating])

    print('\n\nIndustry Rankings:')
    print(industry_df)

    # Save to CSV
    print("\n\n***")
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs(out_dir, exist_ok=True)
    for table, kind in zip([stock_df, industry_df],
                           ['stocks', 'industries']):
        filename = f'rs_{kind}_{rs_window}_{rating_method}_{today}.csv'
        table.to_csv(os.path.join(out_dir, filename), index=False)
        print(f'Your "{filename}" is in the "{out_dir}" folder.')
    print("***\n")


if __name__ == "__main__":
    import time

    start_time = time.time()
    #test_ranking(rs_window='3mo')
    test(rating_method='qcut', rs_window='3mo')
    print(f"Execution time: {time.time() - start_time:.4f} seconds")

