from setuptools import setup, find_packages

# this is only necessary when not using setuptools/distribute
#from sphinx.setup_command import BuildDoc
#cmdclass = {'build_sphinx': BuildDoc}


name = 'vistock'
version = '0.2.4'

setup(
    name = name,
    version = version,
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
    #cmdclass=cmdclass,
    #command_options = {
    #    'build_sphinx': {
    #        'project': ('setup.py', name),
    #        'version': ('setup.py', version),
    #        'release': ('setup.py', version),
    #        'source_dir': ('setup.py', 'docs'),
    #        'build_dir': ('setup.py', 'docs/_build'),
    #    }
    #},
)
