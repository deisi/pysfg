
import unittest
import numpy as np
import pysfg
import os
from pathlib import Path
import matplotlib.pyplot as plt

path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))


class TestPlot(unittest.TestCase):
    figs = []
    for i in range(3):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3])
        figs.append(fig)

    def test_figures2pdf0(self):
        fname = dir_path / Path("plot.pdf")
        pysfg.plot.figures2pdf(fname, self.figs)

    def test_figures2pdf1(self):
        fname = dir_path / Path("plot")
        pysfg.plot.figures2pdf(fname, self.figs)




if __name__ == '__main__':
    unittest.main()
