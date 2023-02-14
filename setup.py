from setuptools import setup, find_packages

# this is only necessary when not using setuptools/distribute
from sphinx.setup_command import BuildDoc
cmdclass = {'build_sphinx': BuildDoc}


import vistock
name = 'vistock'

setup(
    name = name,
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
    cmdclass=cmdclass,
    command_options = {
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', vistock.__version__),
            'release': ('setup.py', vistock.__version__),
            'source_dir': ('setup.py', 'docs'),
            'build_dir': ('setup.py', 'docs/_build'),
        }
    },
)
