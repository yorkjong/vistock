"""
Common utility for file operations.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/20 (initial version) ~ 2023/02/20 (last revision)"

__all__ = [
    'gen_fn_info',
]

import os


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


