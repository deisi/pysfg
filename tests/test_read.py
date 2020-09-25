import unittest
from datetime import datetime
import pysfg
import numpy as np
import os
from pathlib import Path


path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))


class TestSpectrum(unittest.TestCase):

    def test_victor_data_file(self):
        data = pysfg.read.victor.data_file(dir_path / Path("data/sc_quartz.dat"))
        self.assertListEqual(
            list(data['data'].mean((0, 1, 3))),
            [1489.2145833333334, 1517.4754166666667, 304.14729166666666]
        )
        self.assertEqual(data['central_wl'], 674.0)
        self.assertEqual(data['vis_wl'], 811.7)
        self.assertEqual(data['calib_central_wl'], 670)
        self.assertListEqual(list(data['calib_coeff']), [0.034274, 642.101])

    def test_spe_data_file(self):
        data = pysfg.read.spe.data_file(dir_path / Path("data/sample.spe"))
        self.assertEqual(data['wavelength'].mean(), 659.8415138476689)
        self.assertEqual(data['data'].mean(), 650.79125)
        self.assertEqual(data['created'], datetime(2018, 7, 26, 17, 18, 17))

    def test_spe_data_file_v2(self):
        data = pysfg.read.spe.data_file(dir_path / Path("data/sample_v2.spe"))
        self.assertAlmostEqual(data['data'].mean(), 588.4231, places=4)
        self.assertAlmostEqual(data['wavelength'].mean(), 699.8086142681037, places=4)
        self.assertEqual(data['ExperimentTimeLocal'], datetime(2017, 3, 2, 14, 28, 52))

if __name__ == '__main__':
    unittest.main()
