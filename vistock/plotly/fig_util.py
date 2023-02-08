# -*- coding: utf-8 -*-
"""
Common utility for Plotly figure.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/09 (initial version) ~ 2023/02/09 (last revision)"


__all__ = ['add_crosshair_cursor', 'add_hovermode_menu']

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



