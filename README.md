# Read Me
## Visualizing Stocks
`vistock` is an open source package that provides a lot of plot() functions for visualizing stocks. For those who just want to use it directly without knowing too many details, I also provide a Colab notebook file, which can be used to plot stock charts you want after simply filling out parameters on the Colab Forms.

- **Website:** [vistock.netlify.app](https://vistock.netlify.app) (or [vistock.vercel.app](https://vistock.vercel.app))
- **Usage demo:**
  - [github.com/yorkjong/vistock/blob/main/notebooks/vistock_demo.ipynb](https://github.com/yorkjong/vistock/blob/main/notebooks/vistock_demo.ipynb)
  - [github.com/yorkjong/vistock/blob/main/notebooks/profile_demo.ipynb](https://github.com/yorkjong/vistock/blob/main/notebooks/profile_demo.ipynb)
  - [github.com/yorkjong/vistock/blob/main/notebooks/bull_draw.ipynb](https://github.com/yorkjong/vistock/blob/main/notebooks/bull_draw.ipynb)
- **Test code:** [github.com/yorkjong/vistock/tree/main/tests](https://github.com/yorkjong/vistock/tree/main/tests)
- **Documentation:** [vistock.netlify.app/modules.html](https://vistock.netlify.app/modules.html) (or [vistock.vercel.app/modules.html](https://vistock.vercel.app/modules.html))
- **Source code:** [github.com/yorkjong/vistock](https://github.com/yorkjong/vistock)
- **Bug reports:** [github.com/yorkjong/vistock/issues](https://github.com/yorkjong/vistock/issues)

## Getting Started on Colab

1. Click [vistock_demo.ipynb](https://colab.research.google.com/github/yorkjong/vistock/blob/main/notebooks/vistock_demo.ipynb) to open it in Colab.
2. Sign in your Google account if required.
3. Follow the steps in the demonstration video below.
   1. ~Install vistock from GitHub~
      * ~Click the ► button to start install~
      * ~We can see `[ ]` symbol at the begin of a cell. It will be changed to ► button while the mouse cursor over it.~
   2. Fill parameters of a form.
   3. Manually click ► button (means "start run") to plot a chart.
      * The vistock will be installed automatically if it is not done yet.
      * After running a cell manually, it will auto-run if you change the selected parameter value.

<video src="https://github.com/user-attachments/assets/21e44415-a489-4a72-a813-31a340788443"  doncontrols="controls" style="max-width: 640px;">
</video>


## Dive into it on your computer.

1. Install vistock from GitHub

    ```sh
    git clone https://github.com/yorkjong/vistock.git
    ```

2. Run a test code.

    There are two test code in `vistock/tests` folder.

    * [test_plotly.py](https://github.com/yorkjong/vistock/blob/main/tests/test_plotly.py) -- for Plotly version
    * [test_mpl.py](https://github.com/yorkjong/vistock/blob/main/tests/test_mpl.py) -- for mplfinance version

    Run a test code:
    ```sh
    cd vistock/tests
    python test_plotly.py
    ```

    This test code will show stock charts and save them into interactie html files.
    You can double-clicked a output file to open it on your browser.

![TSLA_1d_20230227_0000_pbv2s](https://user-images.githubusercontent.com/11453572/224471104-c6a998eb-368a-4de5-ac01-409bbe04be77.png)

3. Enjoy the demo code.
    The demo code called [vstock_demo.ipynb](https://github.com/yorkjong/vistock/blob/main/notebooks/vistock_demo.ipynb). You can open it on your Jupyter Notebook environment.

[//]: # (This may be the most platform independent comment)
