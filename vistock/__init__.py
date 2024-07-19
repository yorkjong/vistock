"""
Initialize vistock package.
"""
__software__ = "Visualizing Stocks"
__version__ = "0.2.6"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/07/19 (last revision)"

__all__ = [
    'mpl',      # plot with mplfinance (using matplotlib internal)
    'plotly',   # plot with Plotly
    'tw',       # handle stocks of Taiwan markets
]

from . import mpl
from . import plotly
from . import tw

