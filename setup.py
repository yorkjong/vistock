from setuptools import setup, find_packages

setup(
    name = 'vistock',
    version = '0.2.1',
    license = 'MIT',
    author = 'York Jong',
    author_email = 'york.jong@gmail.com',
    description = 'Visualizing Stocks'
    long_description = open('README.md').read(),
    python_requires = '>=3.6',
    packages = find_packages(),
    install_requires = [
        'pandas',
        'yfinance',
        'mplfinance',
        'plotly',
        #'kaleido',  # plotly uses this to save picture
    ],
)
