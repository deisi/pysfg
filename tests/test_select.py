import unittest
import pysfg
import numpy as np


class TestSelectorPP(unittest.TestCase):
    # This is a 4D numpy test data set.
    data = np.arange(256).reshape(4, 4, 2, 8)

    def test_input0(self):
        p = pysfg.select.SelectorPP()
        self.assertTrue(np.all(self.data[p.tselect] == self.data))

    def test_input1(self):
        p = pysfg.select.SelectorPP(pixel=slice(6))
        self.assertTrue(np.all(self.data[p.tselect] == self.data[:, :, :, slice(6)]))

    def test_input3(self):
        p = pysfg.select.SelectorPP(spectra=1)
        self.assertTrue(np.all(self.data[p.tselect] == self.data[:, :, 1, :]))

    def test_input4(self):
        p = pysfg.select.SelectorPP(pp_delays=[0, 3])
        self.assertTrue(np.all(self.data[p.tselect] == self.data[slice(0, 3), :, :, :]))

    def test_input4(self):
        p = pysfg.select.SelectorPP(scans=slice(2))
        self.assertTrue(np.all(self.data[p.tselect] == self.data[:, slice(2), :, :]))


if __name__ == '__main__':
    unittest.main()
