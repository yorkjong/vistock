"""
Utility for mplfinance.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/22 (initial version) ~ 2024/09/04 (last revision)"

__all__ = [
    'use_mac_chinese_font',
    'decide_mpf_style',
]

import copy
import platform

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import mplfinance as mpf
from ..utils import MarketColorStyle


def use_mac_chinese_font():
    if platform.system() != 'Darwin':
        return
    font_name = 'Arial Unicode MS'
    if font_name not in plt.rcParams['font.sans-serif']:
        plt.rcParams['font.sans-serif'].insert(0, font_name)


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

    reversed_mk_colors = copy.deepcopy(mk_colors)
    for i in ['candle', 'edge', 'wick', 'ohlc', 'volume', 'vcedge']:
        reversed_mk_colors[i] = {
            'up': mk_colors[i]['down'],
            'down': mk_colors[i]['up']
        }

    # Define a new style with reversed colors
    style = mpf.make_mpf_style(base_mpf_style=base_mpf_style,
                               marketcolors=reversed_mk_colors)
    return style

