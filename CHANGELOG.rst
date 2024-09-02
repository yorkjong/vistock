Change Log
==========
TODO
----
* To support Alexander Elder's technical indicators, such as Force Index,
  Elder Ray Index and stock charts with his trading systems.
* To support other useful Technical Indicators.
* To support IBD EPS RS
* To support 3-month RS (original 1-year RS)
* To support Revenue growth RS

0.5.0
-----------------
* Added the support of Stan Weinstein's Relative Strength and stock chart
  convention
  * Added rsm module for rating stocks based on Mansfield Relative Strength (RSM)
    and related metrics.
  * Added `rsm_rating.ipynb` notebook to demonstrate ranking functionality
  * Added mansfield (plotly version) module for ploting Mansfield Stock Charts
  * Added mansfield (mpl version) module for ploting Mansfield Stock Charts
  * Added 'A Week Algo' columns to the ranking table
  * Added 'Price / MA{n}' columns to the ranking table
  * Added 'Volume / VMA{n}' column to the ranking table
  * Added 'EPS RS (%)' column to the ranking table
* Refined ibd.rankings function
  * Added 'Price' column for rankings generated stock table
  * Added 'Name' column for rankings generated Taiwan stock table
  * Applied batch download to improve the performance of stock data download

0.4.1 [2024-08-22]
------------------
* Add 'template' parameter to plot function (plotly version) and update test
  cases.
* Update .rst files with sphinx-apidoc
  * `sphinx-apidoc -o docs vistock`
* Updated docstrings to conform to reStructuredText standards
* Improved the UI of ibs_rs_line.ipynb

0.4.0 [2024-08-19]
------------------
* Added the support the stock chart and table with IBD RS line and rating.
  * Added ibd_rs_line.ipynb to test IBD relative functions
  * Added ibd_rs_cmp modules (both mpl and plotly version) to plot IBD RS
  * Added ibd_rs modules (both mpl and plotly version) to plot IBD RS line
  * Added ibd module to support IBD Rating and Ranking
  * Added ibd_rs_rating.ipynb to demo ibd module
  * Added stock_indices module to get tickers of a given source index
  * Extended tw module to get tickers of a given source exchange
* Improved Performance
  * Applied requests_cache to improve the execxution time
  * Added caching mechanism to value_from_key and similar_keys methods
* Other features
  * Added style parameter for plot functions (mplfinance version)
  * Added hides_nontrading parameter for plot functions (mplfinance version)
    Comparison lines
  * vistock/util.py: Added the support of .TWO to decide_market_color_style
  * vistock/util.py: Added doctest to decide_market_color_style
  * vistock/mpl/rsi.py: Created ta module and replaced talib package with ta
    module

0.3.2 [2024-07-22]
------------------
* vistock/mpl: Added market_color_style argument to stock plot functions
* vistock/plotly: Added market_color_style argument to stock plot functions

0.3.1 [2024-07-21]
------------------
* Added the support of bull-run and drawdown stock chart (mplfinance version)
* Added the support of bull-run and drawdown stock chart (Plotly version)

0.3.0 [2024-07-19]
------------------
* Added Turnover Profile feature
* Made both price axes have the same scale and range (Plotly version)
* Added 'hbar_align_on_right' parameter pbv2s.plot function to allow the
  starting position of the horizontal bars on the right.

0.2.5 [2023-02-20]
------------------
* Renamed parameter 'ticker' to 'symbol'
* Renamed folder 'examples' to 'notebooks'
* Added chinese stock name support for Taiwan stocks
* Applied __file__ to generate output filenames
* Added parameter "out_dir" to plot functions

0.2.4 [2023-02-14]
------------------
* vistock.plotly: Added "hides_nontrading" parameter to plot functions
* vistock_demo.ipynb: Added "hides_nontrading" parameter to Plotly forms
* Added files for sphinx document generator

0.2.3 [2023-02-13]
------------------
* vistock_demo.ipynb: Fixed "NameError: name 'sys' is not defined
* vistock_demo.ipynb: Added "total_bins" parameter to the "mplfinance:interval
  of intraday" form.
* vistock_demo.ipynb: Added Explanation cells to explain parameters and forms

0.2.2 [2023-02-13]
------------------
* Fixed remove_nontrading issue on interval < 1day
* Added "total_bins" parameter to forms on vistock_demo.ipynb

0.2.1 [2023-02-11]
------------------
* Added the version number to 0.2.1
* Filled README.md
* Appled 4 Colab Forms to vistock_demo.ipynb for demo
* Added "interval" parameter for all plot functions
* Refined output filenames for all plot functions
* Fine tuned the legend location for all plotly plot functions
* Refined titles and output finename
* Added test_mpl.py
* Renamed test_on_plotly.py to test_plotly.py
* Fine tuned colors

0.2.0 [2023-02-09]
------------------
* Add vistock_demo.ipynb
* Add test_on_ploly.py
* Add hovermode dropdown menu

0.1 [2023-02-07]
----------------
* Initial version
* Extracted from ViStock.ipynb
