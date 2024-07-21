"""
Utility for mplfinance.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/22 (initial version) ~ 2024/07/22 (last revision)"

__all__ = [ 'decide_mpf_style' ]

import mplfinance as mpf
from ..util import MarketColorStyle


def decide_mpf_style(base_mpf_style='yahoo',
                     market_color_style=MarketColorStyle.WESTERN):
    """
    Determine the mplfinance style based on the base style and market color style.

    Parameters:
        base_mpf_style (str): The base mplfinance style to use. Default is
            'yahoo'.
        market_color_style (MarketColorStyle): The market color style to use.
            Default is MarketColorStyle.WESTERN.

    Returns:
        dict: The mplfinance style dictionary with the appropriate market colors.
    """
    style = mpf.make_mpf_style(base_mpf_style=base_mpf_style)
    if market_color_style == MarketColorStyle.WESTERN:
        return style

    mk_colors = style['marketcolors']
    reversed_mk_colors = mpf.make_marketcolors(
        up=mk_colors['candle']['down'],
        down=mk_colors['candle']['up'],
        edge={'up': mk_colors['edge']['down'], 'down': mk_colors['edge']['up']},
        wick={'up': mk_colors['wick']['down'], 'down': mk_colors['wick']['up']},
        ohlc={'up': mk_colors['ohlc']['down'], 'down': mk_colors['ohlc']['up']},
        volume={'up': mk_colors['volume']['down'], 'down': mk_colors['volume']['up']},
    )

    # Define a new style with reversed colors
    style = mpf.make_mpf_style(base_mpf_style='yahoo',
                               marketcolors=reversed_mk_colors)
    return style

