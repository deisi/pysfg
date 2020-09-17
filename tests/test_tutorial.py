import unittest
import sys
import os
import subprocess
import pysfg
from pathlib import Path

# This makes it possible to run this test script from everywhere.
path = Path(__file__)
dir_path = path.parent  # The path of this files, so all paths are relative to this file.

class TestTutorial(unittest.TestCase):

    def test_simple_gold(self):
        subprocess.call([
            sys.executable,
            dir_path / Path("../scripts/static_spectra.py"),
            dir_path / Path("../tutorial/simple_gold.yaml"),
        ])
        gold1 = pysfg.spectrum.json_to_spectrum(dir_path / Path("../tutorial/cache/gold_1.json"))
        gold2 = pysfg.spectrum.json_to_spectrum(dir_path / Path("../tutorial/cache/gold_2.json"))

        self.assertEqual(gold1.basesubed.mean(), 684.2034375)
        self.assertEqual(gold2.basesubed.mean(), 3355.231034482759)

    def test_simple_spectrum(self):
        subprocess.call([
            sys.executable,
            dir_path / Path("../scripts/static_spectra.py"),
            dir_path / Path("../tutorial/simple_spectrum.yaml"),
        ])
        sp = pysfg.spectrum.json_to_spectrum(dir_path / Path("../tutorial/cache/sc_d2o-dopc_static.json"))
        self.assertEqual(sp.normalized.mean(), 0.033241848025088234)
        self.assertEqual(sp.wavenumber.mean(), 2607.12017)

    def test_timescan(self):
        subprocess.call([
            sys.executable,
            dir_path / Path("../scripts/timescan.py"),
            dir_path / Path("../tutorial/timescan.yaml"),
        ])
        pumped = pysfg.spectrum.json_to_pumpprobe(dir_path / Path('../tutorial/cache/pumped.json'))
        probed = pysfg.spectrum.json_to_pumpprobe(dir_path / Path('../tutorial/cache/probed.json'))
        self.assertEqual(pumped.normalized.mean(), 0.14001896355614948)
        self.assertEqual(probed.normalized.mean(), 0.139687242787185)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)

    def test_bleach(self):
        subprocess.call([
            sys.executable,
            dir_path / Path("../scripts/bleach.py"),
            dir_path / Path("../tutorial/bleach.yaml"),
        ])
        bleach = pysfg.spectrum.json_to_bleach(dir_path / Path("../tutorial/cache/bleach.json"))
        bleachR = pysfg.spectrum.json_to_bleach(dir_path / Path("../tutorial/cache/bleach1.json"))

        self.assertEqual(bleach.normalized.mean(), -0.0018385374879113302)
        self.assertEqual(bleachR.normalized.mean(), 0.9912969632787191)

    def test_trace(self):
        subprocess.call([
            sys.executable,
            dir_path / Path("../scripts/trace.py"),
            dir_path / Path("../tutorial/trace.yaml"),
        ])
        hf = pysfg.json_to_trace(dir_path / Path('../tutorial/cache/hf.json'))
        lf = pysfg.json_to_trace(dir_path / Path('../tutorial/cache/lf.json'))

        self.assertEqual(hf.bleach.mean(), -0.0034646422689189192)
        self.assertEqual(lf.bleach.mean(), -0.002123050252486773)
        self.assertEqual(hf.bleachE.mean(), 0.001824992816938757)
        self.assertEqual(lf.bleachE.mean(), 0.0015999242125543753)
        self.assertEqual(hf.pp_delay.mean(), 2488.5714285714284)


if __name__ == '__main__':
    unittest.main()
