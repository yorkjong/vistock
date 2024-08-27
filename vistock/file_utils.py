"""
Common utility for file operations.
"""
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/20 (initial version) ~ 2023/02/20 (last revision)"

__all__ = [
    'make_dir',
    'gen_fn_info',
]

import os
import re


def is_valid_windows_dir_name(name):
    """Check if a directory name is valid on Windows.

    Args:
        name (str): the input directory name.

    Returns:
        bool: True if valid; False otherwise.

    Examples:
        >>> is_valid_windows_dir_name(':')
        False
        >>> is_valid_windows_dir_name('out?')
        False
        >>> is_valid_windows_dir_name('out')
        True
    """
    regex = r'^[A-Za-z0-9_\-\.]+$'

    if re.match(regex, name) and \
       not name.endswith(".") and \
       not name.endswith(" ") and \
       not re.search(r'[\\/:*?"<>|]', name):
        return True
    else:
        return False


def make_dir(directory_path):
    """
    Creates a directory at the given path and returns the original path
    string if it is valid. Returns an empty string if the path is invalid.

    Args:
        directory_path (str): A string representing the directory path.

    Returns:
        str: A string representing the original directory path if it is valid,
        otherwise an empty string.

    Examples:
        >>> make_dir("./out/")
        'out'
        >>> make_dir(":")  # ':' is not a valid character for directory names.
        ''
    """
    directory_path = os.path.normpath(directory_path)
    if not is_valid_windows_dir_name(directory_path):
        return ""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return directory_path
    except OSError:
        return ""


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


if __name__ == "__main__":
    import doctest
    doctest.testmod()

