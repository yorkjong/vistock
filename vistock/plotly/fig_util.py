"""
Common utility for Plotly figures.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/09 (initial version) ~ 2023/02/20 (last revision)"

__all__ = [
    'hide_nontrading_periods',
    'add_crosshair_cursor',
    'add_hovermode_menu',
    'gen_fn_info',
]

import os
import pandas as pd


#------------------------------------------------------------------------------

def hide_nontrading_periods(fig, df, interval):
    """Hide non-tranding time-periods.

    This function can hide certain time-periods to avoid the gaps at
    non-trading time-periods.

    Parameters
    ----------
    fig: plotly.graph_objects.figure
        the figure
    df: pandas.DataFrame
        the stock table
    interval: str
        the interval of an OHLC item.
        Valid values are 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo,
        3mo. Intraday data cannot extend last 60 days:
            * 1m - max 7 days within last 30 days
            * up to 90m - max 60 days
            * 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
              Yahoo does)
    """
    # Convert aliases from `interval` to `freq`
    # These aliases represent 'month', 'minute', 'hour', 'day', and 'week'.
    freq = interval
    interval_aliases = ('mo', 'm', 'h', 'd', 'wk')
    freq_aliases = ('M', 'min', 'H', 'D', 'W')
    for i, f in zip(interval_aliases, freq_aliases):
        freq = freq.replace(i, f)

    # Calculate nontrading time-periods
    #df.index = df.index.strftime('%Y-%m-%d %H:%M')
    dt_all = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    dt_trade = [d for d in df.index]
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d %H:%M") if not d in dt_trade]

    # Calculate dvalue in milliseconds
    dvalue = (dt_all[1] - dt_all[0]).total_seconds() * 1000     # unit in msec

    # Update xaxes to hide non-trading time-periods
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks, dvalue=dvalue)])

#------------------------------------------------------------------------------

def add_crosshair_cursor(fig):
    """Add crosshair cursor to a given figure.

    Parameters
    ----------
    fig: plotly.graph_objects.Figure
        the figure
    """
    fig.update_yaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_xaxes(
        spikemode='across', spikesnap='cursor',
        spikethickness=1, spikedash='solid', spikecolor='grey')
    fig.update_layout(hovermode='x')    # 'x', 'y', 'closest', False,
                                        # 'x unified', 'y unified'


def add_hovermode_menu(fig, x=0, y=1.05):
    """Add a dropdown menu for selecting a hover mode.

    Parameters
    ----------
    fig: plotly.graph_objects.Figure
        the figure.
    x: int
        the x position of the menu
    y: int
        the y position of the menu
    """
    hovermodes = ('x', 'y', 'closest', 'x unified', 'y unified')
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(args=[dict(hovermode=m)],
                         label=m, method="relayout") for m in hovermodes
                ]),
                showactive=True,
                xanchor='left', yanchor='bottom',
                x=x, y=y
            ),
        ],
        annotations=[dict(
            text="hovermode:", showarrow=False,
            x=x, y=y+0.1, xref="paper", yref="paper", align="left"
        )],
    )

#------------------------------------------------------------------------------

def gen_fn_info(symbol, interval, date, module):
    """Generate the information string for the output filename of a stock.

    Args:
        symbol (str): the stock symbol.
        interval (str): the interval of an OHLC item.
        date (str): last date of the stock data.
        module (str): filename of the module.

    Returns:
        str: a filename concatenated above information.

    Examples:
        >>> gen_fn_info('TSLA', '1d', '2023-02-17 00:00', 'plotly/pbv2s.py')
        'TSLA_1d_20230217_0000_pbv2s'
    """
    module, _ = os.path.splitext(os.path.basename(module))
    fn = f'{symbol}_{interval}_{date}_{module}'
    fn = fn.translate({ord(i): None for i in ':-'})   # remove ':', '-'
    fn = fn.replace(' ', '_')
    return fn

#------------------------------------------------------------------------------

