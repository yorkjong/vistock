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

    stock_df = rankings(tickers, rs_window=rs_window,
                        rating_method=rating_method)

    rs_columns = ['RS', '3mo:1mo max', '6mo:3mo max', '9mo:6mo max']
    columns =  ['Sector', 'Ticker'] + rs_columns
    industry_df = groupby_industry(stock_df, columns, key='RS')

    industry_df = industry_df.sort_values(by='RS', ascending=False)
    rating_columns = ['Rating (RS)', 'Rating (3M:1M max)',
                      'Rating (6M:3M max)', 'Rating (9M:6M max)']
    industry_df = append_ratings(industry_df, rs_columns,
                                 rating_columns, method=rating_method)

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
__version__ = "5.4"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/08/05 (initial version) ~ 2024/10/13 (last revision)"

__all__ = [
    'relative_strength',
    'relative_strength_3m',
    'rankings',
    'ma_window_size',
]

import numpy as np
import pandas as pd
import yfinance as yf

import vistock.yf_utils as yfu
from .ranking_utils import *


#------------------------------------------------------------------------------
# IBD Relative Strength (1-Year Version)
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
# IBD Relative Strength (3-Month Version)
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
# IBD RS Rankings
#------------------------------------------------------------------------------

def rankings(tickers, ticker_ref='^GSPC', period='2y', interval='1d',
             rs_window='12mo', rating_method='rank'):
    """
    Analyze stocks and generate a ranking table for individual stocks and
    industries based on Relative Strength (RS).

    This function calculates Relative Strength (RS) for the given stocks
    compared to a reference index, then ranks both individual stocks and
    industries according to their RS values. It provides historical RS data and
    rating rankings.

    Parameters
    ----------
    tickers : list of str
        A list of stock tickers to analyze.

    ticker_ref : str, optional
        The ticker symbol for the reference index. Defaults to '^GSPC' (S&P
        500).

    period : str, optional
        The period for which to fetch historical data. Defaults to '2y' (two
        years).

    interval : str, optional
        The frequency of the data points. Must be one of '1d' for daily data,
        '1wk' for weekly data, or '1mo' for monthly data. Defaults to '1d'.

    rs_window : str, optional
        The time window ('3mo' or '12mo') for calculating Relative Strength
        (RS). Defaults to '12mo'.

    rating_method : str, optional
        The method to calculate ratings. Either 'rank' (based on relative
        ranking) or 'qcut' (based on quantiles). Defaults to 'rank'.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing stock rankings and RS ratings.
    """
    # Set moving average windows based on the interval
    try:
        ma_wins = { '1d': [50, 200], '1wk': [10, 40]}[interval]
        vma_win = { '1d': 50, '1wk': 10}[interval]
    except KeyError:
        raise ValueError("Invalid interval. " "Must be '1d', or '1wk'.")

    stock_df = build_stock_rs_df(tickers=tickers, ticker_ref=ticker_ref,
                                 period=period, interval=interval,
                                 rs_window=rs_window)
    stock_df = stock_df.sort_values(by='RS', ascending=False)

    rs_columns = ['RS', '3mo:1mo max', '6mo:3mo max', '9mo:6mo max']
    rating_columns = ['Rating (RS)', 'Rating (3M:1M)', 'Rating (6M:3M)',
                      'Rating (9M:6M)']
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


def build_stock_rs_df(tickers, ticker_ref='^GSPC', period='2y', interval= '1d',
                      rs_window='12mo'):
    """
    Fetch historical stock data and calculate Relative Strength (RS) for the
    given stock tickers compared to a reference index.

    This function returns a DataFrame that includes the RS values and
    historical max RS values over different periods for each stock.

    Parameters
    ----------
    tickers : list of str
        A list of stock tickers to analyze.

    ticker_ref : str, optional
        The ticker symbol for the reference index. Defaults to '^GSPC' (S&P
        500).

    period : str, optional
        The period for which to fetch historical data. Defaults to '2y' (two
        years).

    interval : str, optional
        The frequency of the data points. Must be one of '1d' (daily), '1wk'
        (weekly), or '1mo' (monthly). Defaults to '1d'.

    rs_window : str, optional
        The time window for calculating Relative Strength. Either '3mo' for
        short-term or '12mo' for long-term RS. Defaults to '12mo'.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing stock rankings with the following columns:
        'Ticker', 'Price', 'Sector', 'Industry', 'RS' (current),
        'RS (1wk:max)', 'RS (1mo:max)', 'RS (3mo:max)', 'RS (6mo:max)',
        'RS (9mo:max)'.
    """
    # Select the appropriate relative strength function based on the rs_window
    rs_func = {
        '3mo': relative_strength_3m,
        '12mo': relative_strength,
    }[rs_window]

    # Set moving average windows based on the interval
    try:
        ma_wins = { '1d': [50, 200], '1wk': [10, 40]}[interval]
        vma_win = { '1d': 50, '1wk': 10}[interval]
    except KeyError:
        raise ValueError("Invalid interval. " "Must be '1d', or '1wk'.")

    # simple moving average function
    sma = lambda x, win: x.rolling(window=win, min_periods=1).mean()

    # Batch download stock price data
    df_all = yf.download([ticker_ref] + tickers,
                         period=period, interval=interval)
    df_ref = df_all.xs(ticker_ref, level='Ticker', axis=1)

    # Batch download stock info
    info = yfu.download_tickers_info(tickers, ['sector', 'industry'])

    rs_data = []
    price_ma = {}
    for ticker in tickers:
        df = df_all.xs(ticker, level='Ticker', axis=1)

        # Caluclate Moving Average
        for win in ma_wins:
            price_ma[f'{win}'] = sma(df['Close'], win).round(2)
        vol_div_vma = (df['Volume'] / sma(df['Volume'], vma_win)).round(2)

        # Calculate Relative Strengths
        rs = rs_func(df['Close'], df_ref['Close'], interval)
        end_date = rs.index[-1]

        # Calculate max values for the specified time periods
        one_week_ago = end_date - pd.DateOffset(weeks=1)
        one_month_ago = end_date - pd.DateOffset(months=1)
        three_months_ago = end_date - pd.DateOffset(months=3)
        six_months_ago = end_date - pd.DateOffset(months=6)
        nine_months_ago = end_date - pd.DateOffset(months=9)

        # Calculate position in 52W range
        high_52w = df['Close'].rolling(window=252, min_periods=1).max().iloc[-1]
        low_52w = df['Close'].rolling(window=252, min_periods=1).min().iloc[-1]
        current_price = df['Close'].asof(end_date)
        range_position = (current_price - low_52w) / (high_52w - low_52w)

        rs_data.append({
            'Ticker': ticker,
            'Sector': info[ticker]['sector'],
            'Industry': info[ticker]['industry'],
            'RS': rs.asof(end_date),
            '1wk:end max': rs.loc[one_week_ago:end_date].max(),
            '1mo:1wk max': rs.loc[one_month_ago:one_week_ago].max(),
            '3mo:1mo max': rs.loc[three_months_ago:one_month_ago].max(),
            '6mo:3mo max': rs.loc[six_months_ago:three_months_ago].max(),
            '9mo:6mo max': rs.loc[nine_months_ago:six_months_ago].max(),
            'Price': df['Close'].asof(end_date).round(2),
            '52W pos': range_position.round(2),
            **{f'MA{w}': price_ma[f'{w}'].iloc[-1] for w in ma_wins},
            f'Volume / VMA{vma_win}': vol_div_vma.iloc[-1],
        })

    # Create DataFrame from RS data
    stock_df = pd.DataFrame(rs_data)

    return stock_df


#------------------------------------------------------------------------------
# Unit Test
#------------------------------------------------------------------------------

def main(min_rating=80, rating_method='qcut',
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

    stock_df = rankings(tickers, rs_window=rs_window,
                        rating_method=rating_method)

    rs_columns = ['RS', '3mo:1mo max', '6mo:3mo max', '9mo:6mo max']
    columns =  ['Sector', 'Ticker'] + rs_columns
    industry_df = groupby_industry(stock_df, columns, key='RS')

    industry_df = industry_df.sort_values(by='RS', ascending=False)
    rating_columns = ['Rating (RS)', 'Rating (3M:1M max)',
                      'Rating (6M:3M max)', 'Rating (9M:6M max)']
    industry_df = append_ratings(industry_df, rs_columns,
                                 rating_columns, method=rating_method)

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
    main(rating_method='qcut', rs_window='3mo')
    print(f"Execution time: {time.time() - start_time:.4f} seconds")

