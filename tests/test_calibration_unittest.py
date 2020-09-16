
import unittest
import pysfg
import numpy as np

class TestCalibration(unittest.TestCase):

    def test_calibration(self):
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
        self.assertListEqual(c.wavenumber.tolist(), np.load("./results/wavenumber.npy").tolist())

    def test_from_victor_file_wavenumber(self):
        wv = pysfg.calibration.from_victor_file_wavenumber("./data/sc_quartz.dat")
        self.assertListEqual(wv.tolist(), np.load("./results/wavenumber_victor.npy").tolist())

    def test_from_vivian_file(self):
        wv = pysfg.calibration.from_vivian_file("./data/gold.dat")
        self.assertListEqual(wv.wavenumber.tolist(), np.load("./results/wavenumber_vivian.npy").tolist())

if __name__ == '__main__':
    unittest.main()
