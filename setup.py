from setuptools import setup, find_packages

setup(
    name='vistock',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'yfinance',
        'mplfinance',
        'plotly',
    ],
    author='York Jong',
    author_email='york.jong@gmail.com',
    description='Visualizing Stocks'
)
