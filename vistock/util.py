"""
Utility Functions for vistock package.
"""
__version__ = "1.1"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2024/07/22 (initial version) ~ 2024/07/24 (last revision)"

__all__ = [
    'MarketColorStyle',
    'decide_market_color_style',
]

from enum import Enum


# Enum for market color styles
class MarketColorStyle(Enum):
    WESTERN = "western"
    EASTERN = "eastern"
    AUTO = "auto"


def decide_market_color_style(ticker='TSLA', style=MarketColorStyle.AUTO):
    """Determine the market color style based on the given ticker and specified
    style.

    Parameters:
        ticker (str): The stock ticker symbol. Default is 'TSLA'.
        style (MarketColorStyle): The desired market color style. Default is
            MarketColorStyle.AUTO.

    Returns:
        MarketColorStyle: The determined market color style (EASTERN, WESTERN,
        or based on the ticker if AUTO is chosen).
    """
    if style != MarketColorStyle.AUTO:
        return style

    # Define suffixes for Eastern and Western markets
    eastern_markets = [
        '.TW', '.TWO', '.HK', '.T', '.SS', '.SZ', '.KS', '.KL', '.SI'
    ]

    # Check if ticker belongs to Eastern markets
    for suffix in eastern_markets:
        if ticker.endswith(suffix):
            return MarketColorStyle.EASTERN

    # Default to US market colors for unspecified markets or tickers without suffix
    return MarketColorStyle.WESTERN

