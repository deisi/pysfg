import unittest
import datetime
import pysfg
import numpy as np
import os
from pathlib import Path

path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))


class TestSpectrum(unittest.TestCase):

    def test_victor_data_file(self):
        os.chdir(dir_path)
        data = pysfg.read.victor.data_file(Path("data/sc_quartz.dat"))
        self.assertListEqual(
            list(data['data'].mean((0, 1, 3))),
            [1489.2145833333334, 1517.4754166666667, 304.14729166666666]
        )
        self.assertEqual(data['central_wl'], 674.0)
        self.assertEqual(data['vis_wl'], 811.7)
        self.assertEqual(data['calib_central_wl'], 670)
        self.assertListEqual(list(data['calib_coeff']), [0.034274, 642.101])


if __name__ == '__main__':
    unittest.main()
