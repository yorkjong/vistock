from setuptools import setup, find_packages
import vistock

setup(
    name = 'vistock',
    version = vistock.__version__,
    license = 'MIT',
    author = 'York Jong',
    author_email = 'york.jong@gmail.com',
    description = 'Visualizing Stocks',
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
    cmdclass = {"build_sphinx": BuildDoc},
    command_options = {
        "build_sphinx": {
            "project": ("setup.py", "vistock"),
            "version": ("setup.py", vistock.__version__),
            "release": ("setup.py", vistock.__version__),
            "source_dir": ("setup.py", "docs"),
            "build_dir": ("setup.py", "docs/_build"),
        }
    },
)
