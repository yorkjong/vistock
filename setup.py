from setuptools import setup, find_packages

setup(
    name='vistock',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'yfinance',
        'mplfinance',
        'plotly',
        #'kaleido',  # plotly uses this to save picture
    ],
    author='York Jong',
    author_email='york.jong@gmail.com',
    description='Visualizing Stocks'
)
