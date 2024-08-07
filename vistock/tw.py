"""
Handle stocks of Taiwan markets.

This module provides functions and classes to interact with Taiwan stock markets,
including TWSE (Taiwan Stock Exchange), TPEx (Taipei Exchange), and ESB (Emerging
Stock Board). It offers functionality to convert stock symbols, fetch stock data,
and retrieve lists of tickers for different markets.

Main features:
- Convert stock symbols to yfinance compatible format
- Fetch stock data from various Taiwan stock markets
- Retrieve lists of tickers for TWSE, TPEx, and ESB
- Find similar stocks based on name or code

Usage:
    import tw

    # Convert a stock symbol
    yf_symbol = tw.as_yfinance('台積電')

    # Find similar stocks
    similar = tw.similar_stocks('印度')

    # Get TWSE tickers
    twse_tickers = tw.get_twse_tickers()

    # Get TWSE tickers
    tickers = tw.get_tickers('TWSE')
"""
__version__ = "1.4"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/19 (initial version) ~ 2024/08/07 (last revision)"

__all__ = [
    'as_yfinance',
    'similar_stocks',
    'get_twse_tickers',
    'get_tpex_tickers',
    'get_esb_tickers',
    'get_all_tickers',
    'get_tickers',
]

import functools
import unicodedata

import requests
from bs4 import BeautifulSoup


#------------------------------------------------------------------------------
# Utility Functions
#------------------------------------------------------------------------------

def is_chinese(char):
    """
    Check if a character is a Chinese character.

    Args:
        char (str): The character to be checked.

    Returns:
        bool: True if the character is Chinese, False otherwise.

    Examples:
        >>> is_chinese('A')
        False
        >>> is_chinese('中')
        True
    """
    return unicodedata.category(char[0]) == 'Lo'


#------------------------------------------------------------------------------
# Crawler
#------------------------------------------------------------------------------

class Crawler:
    """
    A class for crawling stock data from Taiwan stock market websites.

    This class provides methods to fetch stock information and convert
    stock symbols to yfinance compatible format.

    stock data is from 'https://isin.twse.com.tw/isin/C_public.jsp'.
    """
    @staticmethod
    def _get_name_code_pair(symbol, str_mode):
        """Get (name, code) pair from a given symbol.

        Here the symbol may be a stock name or a stock code.

        Args:
            symbol (str): stock name or stock code.
            str_mode (int): a parameter of GET requests.

        Returns:
            (str, str): a name-code pair of first found stock.
        """
        url = 'https://isin.twse.com.tw/isin/C_public.jsp'
        params = {'strMode': str_mode}
        response = requests.get(url, params=params)
        soup = BeautifulSoup(response.text, 'html5lib')
        #table = soup.find('tbody')
        #rows = table.find_all('tr')
        rows = soup.find_all('tr')
        for row in rows:
        #for row in rows[2:]:
            col0 = row.find('td')
            code_name = col0.text.split()
            if len(code_name) == 2:
                code, name = code_name
                if symbol == name or symbol == code:
                    return name, code
        return None, None


    @staticmethod
    def as_yfinance(symbol):
        """
        Convert a given stock symbol into yfinance compatible stock symbol.

        Args:
            symbol (str): the input symbol

        Returns:
            str: the yfinance compatible stock symbol.

        Examples:
            #>>> Crawler.as_yfinance("台積電")
            #'2330.TW'
            #>>> Crawler.as_yfinance("2330")
            #'2330.TW'
            #>>> Crawler.as_yfinance("元太")
            #'8069.TWO'
        """
        # for a listed stock
        _, code = Crawler._get_name_code_pair(symbol, 2)
        if code:
            return f'{code}.TW'

        # for an OTC stock
        _, code = Crawler._get_name_code_pair(symbol, 4)
        if code:
            return f'{code}.TWO'

        # for an ESB stock. ESB stands for Emerging Stock Board (also called
        # Emerging Stock Market, or Emerging OTC)
        _, code = Crawler._get_name_code_pair(symbol, 5)
        if code:
            return f'{code}.TWO'

        return symbol


#------------------------------------------------------------------------------
# Open API
#------------------------------------------------------------------------------

class OpenAPI:
    """
    A class for interacting with Taiwan stock market Open APIs.

    This class provides methods to fetch stock data, convert symbols,
    and retrieve stock information using various Open APIs.
    """

    @staticmethod
    def get_columns(url, column_names):
        """
        Fetches JSON data from the specified URL and extracts the specified
        columns.

        Args:
            url (str): The URL of the JSON data.
            column_names (list): A list of column names to extract.

        Returns:
            list: A list of the extracted columns, each column being a list.
                   Returns a list of empty lists if an error occurs.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_rows = response.json()
            columns = []
            for col in column_names:
                columns.append([row[col] for row in json_rows])
            return columns
        except Exception as e:
            return ([] for _ in column_names)


    @staticmethod
    def value_from_key(key, url, key_field, value_field):
        """Get the value of a given key that is looked-up from an Open API
        response table.

        Args:
            key (str): a key to look-up
            url (str): the URL of an Open API request.
            key_field (str): the name of a key field.
            value_field (str): the name of a value field.

        Returns:
            str: the got value for success, None otherwise.
        """
        cols = OpenAPI.get_columns(url, [key_field, value_field])
        for k, v in zip(*cols):
            if key == k:
                return v
        return None


    @staticmethod
    def similar_keys(key, url, key_field, value_field):
        """Get (key, value) pairs with similar keys that are looked-up from an
        Open API response table.

        Args:
            key (str): the key to look-up
            url (str): the URL of an Open API request.
            key_field (str): the name of a key field.
            value_field (str): the name of a value field.

        Returns:
            [(str, str)]: a list of key-value pairs representing the similar
                          stocks.
        """
        cols = OpenAPI.get_columns(url, [key_field, value_field])
        pairs = []
        for k, v in zip(*cols):
            if key in k:
                pairs += [(k, v)]
        return pairs


    @staticmethod
    def yfinance_symbol_from_name(name):
        """Get yfinance compatible symbol from a Taiwan stock name.

        Args:
            name (str): the Taiwan stock name.
        Returns:
            str: the yfinance compatible symbol.
        Examples:
            >>> OpenAPI.yfinance_symbol_from_name("台積電")
            '2330.TW'
            >>> OpenAPI.yfinance_symbol_from_name("元太")
            '8069.TWO'
            >>> OpenAPI.yfinance_symbol_from_name("星宇航空")
            '2646.TWO'
        """
        # for a listed stock
        listed_stock_code = functools.partial(
            OpenAPI.value_from_key,
            url='https://openapi.twse.com.tw/v1/'
                'exchangeReport/STOCK_DAY_AVG_ALL',
            key_field='Name',
            value_field='Code'
        )

        # for an OTC stock
        OTC_stock_code = functools.partial(
            OpenAPI.value_from_key,
            url='https://www.tpex.org.tw/openapi/v1/'
                'tpex_mainboard_daily_close_quotes',
            key_field='CompanyName',
            value_field='SecuritiesCompanyCode'
        )

        # for an ESB stock. ESB stands for Emerging Stock Board (also called
        # Emerging Stock Market, or Emerging OTC)
        ESB_stock_code = functools.partial(
            OpenAPI.value_from_key,
            url='https://www.tpex.org.tw/openapi/v1/'
                'tpex_esb_latest_statistics',
            key_field='CompanyName',
            value_field='SecuritiesCompanyCode'
        )

        code = listed_stock_code(name)
        if code:
            return f'{code}.TW'
        code = OTC_stock_code(name)
        if code:
            return f'{code}.TWO'
        code = ESB_stock_code(name)
        if code:
            return f'{code}.TWO'
        return name


    @staticmethod
    def stock_name(code):
        """Get stock name from its code.

        Args:
            code (str): a Taiwan stock code.
        Returns:
            str: the Taiwan stock name.
        Examples:
            >>> OpenAPI.stock_name('2330')
            '台積電'
            >>> OpenAPI.stock_name('8069')
            '元太'
            >>> OpenAPI.stock_name('2646')
            '星宇航空'
        """
        code = code.replace('.TWO', '').replace('.TW', '')
        name = OpenAPI.listed_stock_name(code)
        if name:
            return name
        name = OpenAPI.OTC_stock_name(code)
        if name:
            return name
        name = OpenAPI.ESB_stock_name(code)
        if name:
            return name
        return code


    @staticmethod
    def yfinance_symbol_from_code(code):
        """Get yfinance compatible symbol from a Taiwan stock code.

        Args:
            code (str): the Taiwan stock code.
        Returns:
            str: the yfinance compatible symbol.
        Examples:
            >>> OpenAPI.yfinance_symbol_from_code("2330")
            '2330.TW'
            >>> OpenAPI.yfinance_symbol_from_code("8069")
            '8069.TWO'
            >>> OpenAPI.yfinance_symbol_from_code("2646")
            '2646.TWO'
        """
        name = OpenAPI.listed_stock_name(code)
        if name:
            return f'{code}.TW'
        name = OpenAPI.OTC_stock_name(code)
        if name:
            return f'{code}.TWO'
        name = OpenAPI.ESB_stock_name(code)
        if name:
            return f'{code}.TWO'
        return code


# for a listed stock
OpenAPI.listed_stock_name = functools.partial(
    OpenAPI.value_from_key,
    url='https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL',
    key_field='Code',
    value_field='Name'
)

# for an OTC stock
OpenAPI.OTC_stock_name = functools.partial(
    OpenAPI.value_from_key,
    url='https://www.tpex.org.tw/openapi/v1/'
        'tpex_mainboard_daily_close_quotes',
    key_field='SecuritiesCompanyCode',
    value_field='CompanyName'
)

# for an ESB stock
OpenAPI.ESB_stock_name = functools.partial(
    OpenAPI.value_from_key,
    url='https://www.tpex.org.tw/openapi/v1/tpex_esb_latest_statistics',
    key_field='SecuritiesCompanyCode',
    value_field='CompanyName'
)


#------------------------------------------------------------------------------
# Public Functions
#------------------------------------------------------------------------------

@functools.lru_cache
def as_yfinance(symbol):
    """
    Convert a given stock symbol into yfinance compatible stock symbol.

    This function handles different types of input:
    - If the input is already in yfinance format (ends with .TW or .TWO), it's
        returned as is.
    - If the input is in Chinese, it's treated as a stock name and converted to
        a code.
    - If the input starts with a digit, it's treated as a Taiwan stock code and
        the appropriate suffix (.TW or .TWO) is added.
    - For other inputs (e.g., non-Taiwan stocks), the symbol is returned
        unchanged.

    Args:
        symbol (str): the input symbol.

    Returns:
        str: the yfinance compatible stock symbol.

    Examples:
        >>> as_yfinance('TSLA')
        'TSLA'
        >>> as_yfinance('台積電')
        '2330.TW'
        >>> as_yfinance('2330')
        '2330.TW'
        >>> as_yfinance('元太')
        '8069.TWO'
        >>> as_yfinance('星宇航空')
        '2646.TWO'
    """
    if symbol.endswith('.TW') or symbol.endswith('.TWO'):
        return symbol
    if is_chinese(symbol[0]):
        #return Crawler.as_yfinance(symbol)
        return OpenAPI.yfinance_symbol_from_name(symbol)
    if symbol[0].isdigit():
        #return Crawler.as_yfinance(symbol)
        return OpenAPI.yfinance_symbol_from_code(symbol)
    return symbol


def similar_stocks(symbol):
    """Get similar stock of a given stock.

    Args:
        symbol (str): a stock name or a stock code.

    Returns:
        [(str, str)]: a list of stock name-code pairs.

    Examples:
        >>> similar_stocks('印度')
        [('富邦印度', '00652'), ('富邦印度正2', '00653L'), ('富邦印度反1', '00654R')]
        >>> similar_stocks('永豐美國')
        [('永豐美國500大', '00858'), ('永豐美國科技', '00886')]
    """
    # for listed stocks
    similar_listed_stocks = functools.partial(
        OpenAPI.similar_keys,
        url='https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL',
        key_field='Name',
        value_field='Code'
    )

    # for OTC stocks
    similar_OTC_stocks = functools.partial(
        OpenAPI.similar_keys,
        url='https://www.tpex.org.tw/openapi/v1/'
            'tpex_mainboard_daily_close_quotes',
        key_field='CompanyName',
        value_field='SecuritiesCompanyCode'
    )

    # for ESB stocks
    similar_ESB_stocks = functools.partial(
        OpenAPI.similar_keys,
        url='https://www.tpex.org.tw/openapi/v1/tpex_esb_latest_statistics',
        key_field='CompanyName',
        value_field='SecuritiesCompanyCode'
    )

    name = OpenAPI.stock_name(symbol)
    stocks = similar_listed_stocks(name)
    if stocks:
        return stocks
    stocks = similar_OTC_stocks(name)
    if stocks:
        return stocks
    return similar_ESB_stocks(name)

#------------------------------------------------------------------------------

def get_twse_tickers():
    """
    Fetch the list of tickers for companies listed on the Taiwan Stock
    Exchange (TWSE).

    Retrieves ticker symbols from the TWSE Open API.

    Returns:
        list: A list of TWSE ticker symbols.

    Examples:
        >>> tickers = get_twse_tickers()
        >>> print(tickers[:5])
        ['0050.TW', '0051.TW', '0052.TW', '0053.TW', '0055.TW']
    """
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    (codes,) = OpenAPI.get_columns(url, ["Code"])
    return [f'{c}.TW' for c in codes]


def get_tpex_tickers():
    """
    Fetch the list of tickers for companies listed on the Taipei Exchange
    (TPEx).

    Retrieves ticker symbols from the TPEx Open API.

    Returns:
        list: A list of TPEx ticker symbols.

    Examples:
        >>> tickers = get_tpex_tickers()
        >>> '8069.TWO' in tickers
        True
    """
    url = "https://www.tpex.org.tw/openapi/v1/tpex_daily_market_value"
    (codes,) = OpenAPI.get_columns(url, ["SecuritiesCompanyCode"])
    return [f'{c}.TWO' for c in codes]


def get_esb_tickers():
    """
    Fetch the list of tickers for companies listed on the Emerging Stock
    Board (ESB) of the Taipei Exchange.

    Retrieves ticker symbols from the TPEx Open API.

    Returns:
        list: A list of ESB ticker symbols.

    Examples:
        >>> tickers = get_esb_tickers()
        >>> print(tickers[:5])
        ['9957.TWO', '2646.TWO', '5859.TWO', '6434.TWO', '1480.TWO']
    """
    url = "https://www.tpex.org.tw/openapi/v1/tpex_esb_capitals_rank"
    (codes,) = OpenAPI.get_columns(url, ["SecuritiesCompanyCode"])
    return [f'{c}.TWO' for c in codes]


def get_all_tickers():
    """
    Fetch a combined list of tickers from multiple major stock market indices.

    This function aggregates ticker symbols from the following indices:
    - Taiwan Stock Exchange, TWSE
    - Taipei Exchange, TPEX
    - Emerging Stock Board of the Taipei Exchange, ESB

    Returns:
        list: A list of unique ticker symbols from the specified indices.

    Examples:
        >>> tickers = get_all_tickers()
        >>> len(tickers) > 2000
        True
        >>> '2330.TW' in tickers
        True
        >>> '8069.TWO' in tickers
        True
    """
    return list(set(get_twse_tickers()) |
                set(get_tpex_tickers()) |
                set(get_esb_tickers()))


def get_tickers(source):
    """
    Retrieve a list of tickers for the specified exchange in Taiwan.

    Args:
        source (str): The common abbreviation for the exchange or market sector.
            Possible values include:
            - 'TWSE': Taiwan Stock Exchange
            - 'TPEX': Taipei Exchange
            - 'ESB': Emerging Stock Board
            - 'ALL': All available tickers across the specified exchanges

    Returns:
        list: A list of tickers for the given exchange or market sector.

    Raises:
        KeyError: If the provided exchange abbreviation is not recognized.

    Examples:
        >>> len(get_tickers('TWSE')) >= 1200
        True
        >>> len(get_tickers('TPEX')) >= 800
        True
        >>> len(get_tickers('ESB')) >= 300
        True
        >>> len(get_tickers('ALL')) >= (1200 + 800 + 300)
        True
        >>> get_tickers('UNKNOWN')
        Traceback (most recent call last):
            ...
        KeyError: "Exchange abbreviation 'UNKNOWN' not found."
    """
    dic = {
        'TWSE': get_twse_tickers,
        'TPEX': get_tpex_tickers,
        'ESB': get_esb_tickers,
        'ALL': get_all_tickers,
    }
    try:
        return dic[source.upper()]()
    except KeyError:
        raise KeyError(f"Exchange abbreviation '{source}' not found.")


#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------


if __name__ == '__main__':
    import doctest
    doctest.testmod()

