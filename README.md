# vistock -- Visualizing Stocks
`vistock` is an open source package that provides a lot of plot() function to visualizing stocks. For those who just want to use it directly without knowing too many details, I also provide a Colab notebook file, which can be used to plot the stock chart you want after simply filling out parameters on Colab Forms.

## Getting Started on Colab

1. Click [vistock_demo.ipynb](https://colab.research.google.com/github/YorkJong/vistock/blob/main/examples/vistock_demo.ipynb) to open it in Colab.
2. Sign in your Google account if required.
3. Follow the steps in the demo video below.

https://user-images.githubusercontent.com/11453572/218294149-ab0fc959-c40d-41b7-bc29-188ee5a2800f.mov


## Run it on your computer.

1. Install vistock from GitHub
    ```sh
    pip install git+https://github.com/YorkJong/vistock.git
    ```

2. Install TA-Lib optionally (used only by vistock.mpl.rsi module)
    Install TA-Lib on macOS
    ```sh
    brew install ta-lib
    pip install Ta-Lib
    ```
    Install on other platform Please ref. [Installation of Ta-Lib in Python: A Complete Guide for all Platforms](https://blog.quantinsti.com/install-ta-lib-python/)>

3. Run a test code.
    There are two test code in `vistock\tests` folder.
    * [test_plotly.py](https://github.com/YorkJong/vistock/blob/main/tests/test_plotly.py)
    * [test_mpl.py](https://github.com/YorkJong/vistock/blob/main/tests/test_mpl.py)
    Run a test code:
    ```sh
    cd vistock\tests
    python test_plotly.py
    ```
    This test code show stock charts and save them into interactie html files.
    You can double-clicked on file to open it on your browser.
4. Enjoy the demo code.
    The demo code called [vstock_demo.ipynb](https://github.com/YorkJong/vistock/blob/main/examples/vistock_demo.ipynb). You can open it on your Jupyter Notebook environment.
    
[//]: # (This may be the most platform independent comment)
