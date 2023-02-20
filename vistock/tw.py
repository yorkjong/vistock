"""
Handle stocks of Taiwan markets.
"""
__version__ = "1.1"
__author__ = "York <york.jong@gmail.com>"
__date__ = "2023/02/19 (initial version) ~ 2023/02/20 (last revision)"

__all__ = [
    'as_yfinance',
    'similar_stocks',
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
    """Crawl stock data from 'https://isin.twse.com.tw/isin/C_public.jsp'.
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
            >>> Crawler.as_yfinance("台積電")
            '2330.TW'
            >>> Crawler.as_yfinance("2330")
            '2330.TW'
            >>> Crawler.as_yfinance("元太")
            '8069.TWO'
        """
        # for a listed stock
        _, code = Crawler._get_name_code_pair(symbol, 2)
        if code:
            return f'{code}.TW'

        # for an OTC stock
        _, code = Crawler._get_name_code_pair(symbol, 4)
        if code:
            return f'{code}.TWO'

        # for an emerging OTC stock
        _, code = Crawler._get_name_code_pair(symbol, 5)
        if code:
            return f'{code}.TWO'

        return symbol


#------------------------------------------------------------------------------
# Open API
#------------------------------------------------------------------------------

class OpenAPI:
    """Get stock data from the OpenAPI.
    """
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
        response = requests.get(url)
        json_rows = response.json()
        for row in json_rows:
            if key == row[key_field]:
                return row[value_field]
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
        response = requests.get(url)
        json_rows = response.json()
        pairs = []
        for row in json_rows:
            if key in row[key_field]:
                pairs += [(row[key_field], row[value_field])]
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

        # for an emerging OTC stock
        EOTC_stock_code = functools.partial(
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
        code = EOTC_stock_code(name)
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
        code = code.replace('.TWO', '')
        code = code.replace('.TW', '')
        name = OpenAPI.listed_stock_name(code)
        if name:
            return name
        name = OpenAPI.OTC_stock_name(code)
        if name:
            return name
        name = OpenAPI.EOTC_stock_name(code)
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
        name = OpenAPI.EOTC_stock_name(code)
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

# for an emerging OTC stock
OpenAPI.EOTC_stock_name = functools.partial(
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

    # for emerging OTC stocks
    similar_EOTC_stocks = functools.partial(
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
    return similar_EOTC_stocks(name)


#------------------------------------------------------------------------------
# Test
#------------------------------------------------------------------------------


if __name__ == '__main__':
    import doctest
    doctest.testmod()

