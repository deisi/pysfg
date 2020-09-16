
import unittest
import pysfg
import numpy as np
import os
from pathlib import Path

path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))

class TestCalibration(unittest.TestCase):

    def test_calibration(self):
        os.chdir(dir_path)
        central_wl = 674
        vis_wl = 800
        calib_central_wl = 670
        calib_coeff = np.array([3.42740e-02, 6.42101e+02])
        c = pysfg.calibration.Calibration(
            central_wl,
            vis_wl,
            calib_central_wl,
            calib_coeff
        )
        self.assertListEqual(
            c.wavenumber.tolist(),
            np.load(Path("results/wavenumber.npy")
            ).tolist())

    def test_from_victor_file_wavenumber(self):
        os.chdir(dir_path)
        wv = pysfg.calibration.from_victor_file_wavenumber(Path("data/sc_quartz.dat"))
        self.assertListEqual(wv.tolist(), np.load(Path("results/wavenumber_victor.npy")).tolist())

    def test_from_vivian_file(self):
        os.chdir(dir_path)
        wv = pysfg.calibration.from_vivian_file(Path("data/gold.dat"))
        self.assertListEqual(wv.wavenumber.tolist(), np.load(Path("results/wavenumber_vivian.npy")).tolist())

if __name__ == '__main__':
    unittest.main()
