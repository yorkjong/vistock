"""
Initialize vistock package.
"""
__software__ = "Visualizing Stocks"
__version__ = "0.8.0"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/02 (initial version) ~ 2024/10/01 (last revision)"

__all__ = [
    'mpl',              # plot with mplfinance (using matplotlib internal)
    'plotly',           # plot with Plotly
    'tw',               # handle stocks of Taiwan markets
    'ibd',              # functions for IBD RS and IBD RS Rating&Ranking
    #'rsw',              # functions for RSM and RSM Rating&Ranking
    'stock_indices',    # functions for Stock Indices
]

from . import mpl
from . import plotly
from . import tw
from . import ibd
#from . import rsm
from . import stock_indices

