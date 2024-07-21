"""
Common utility for Plotly figures.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/09 (initial version) ~ 2024/07/13 (last revision)"

__all__ = [
    'get_candlestick_colors',
    'get_volume_colors',
    'hide_nontrading_periods',
    'add_crosshair_cursor',
    'add_hovermode_menu',
]

import pandas as pd
from ..util import MarketColorStyle


def get_candlestick_colors(market_color_style=MarketColorStyle.WESTERN):
    colors = {
        'increasing_line_color': '#32a455',
        'increasing_fillcolor': 'rgba(50, 164, 85, 0.4)',
        'decreasing_line_color': '#d71917',
        'decreasing_fillcolor': 'rgba(215, 25, 23, 0.4)'
    }

    if market_color_style == MarketColorStyle.WESTERN:
        return colors
    else:
        return {
            'increasing_line_color': colors['decreasing_line_color'],
            'increasing_fillcolor': colors['decreasing_fillcolor'],
            'decreasing_line_color': colors['increasing_line_color'],
            'decreasing_fillcolor': colors['increasing_fillcolor'],
        }


def get_volume_colors(market_color_style=MarketColorStyle.WESTERN):
    if market_color_style == MarketColorStyle.WESTERN:
        return {
            'up': 'green',
            'down': 'red'
        }
    else:
        return {
            'up': 'red',
            'down': 'green'
        }

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
    dt_all = pd.date_range(start=df.index[0], end=df.index[-1], freq=freq)
    dt_breaks = dt_all.difference(df.index)

    # Calculate dvalue in milliseconds
    dvalue = 86400 * 1000   # 1 day in milliseconds
    if interval.endswith('m'):      # minute
        dvalue = 60 * int(interval.replace('m', '')) * 1000
    elif interval.endswith('h'):    # hour
        dvalue = 3600 * int(interval.replace('h', '')) * 1000

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

