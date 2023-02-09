# -*- coding: utf-8 -*-
"""
Common utility for Plotly figure.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/09 (initial version) ~ 2023/02/10 (last revision)"

__all__ = ['add_crosshair_cursor', 'add_hovermode_menu', 'remove_nontrading']

import pandas as pd


def remove_nontrading(fig, df, interval):
    """Update layout for removing non-tranding dates.

    Parameters
    ----------
    fig: plotly.graph_objects.figure
        the figure
    df: pandas.DataFrame
        the stock table
    interval: str
        the interval of an OHLC item.
        Valid values are 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
        Intraday data cannot extend last 60 days:
        * 1m - max 7 days within last 30 days
        * up to 90m - max 60 days
        * 60m, 1h - max 730 days (yes 1h is technically < 90m but this what
          Yahoo does)
    """
    freq = interval
    interval_aliases = ('m', 'h', 'd', 'wk', 'mo')
    freq_aliases = ('min', 'H', 'D', 'W', 'M')
    for i, f in zip(interval_aliases, freq_aliases):
        freq = freq.replace(i, f)

    df.index = df.index.strftime('%Y-%m-%d %H:%M')
    dt_all = pd.date_range(start=df.index.values[0], end=df.index.values[-1], freq=freq)
    dt_all = [d.strftime("%Y-%m-%d %H:%M") for d in dt_all]
    trade_date = [d for d in df.index.values]
    dt_breaks = list(set(dt_all) - set(trade_date))
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])


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
    """Add a dropdown menu (for selecting a hovermode) on a given figure.

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

