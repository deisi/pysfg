import unittest
import sys
import os
import subprocess
import pysfg
from pathlib import Path

class TestTutorial(unittest.TestCase):

    def test_simple_gold(self):
        subprocess.call([
            sys.executable,
            "../scripts/static_spectra.py",
            "simple_gold.yaml",
        ])
        gold1 = pysfg.spectrum.json_to_spectrum("cache/gold_1.json")
        gold2 = pysfg.spectrum.json_to_spectrum("cache/gold_2.json")

        self.assertEqual(gold1.basesubed.mean(), 684.2034375)
        self.assertEqual(gold2.basesubed.mean(), 3355.231034482759)

    def test_simple_spectrum(self):
        subprocess.call([
            sys.executable,
            "../scripts/static_spectra.py",
            "simple_spectrum.yaml",
        ])
        sp = pysfg.spectrum.json_to_spectrum("cache/sc_d2o-dopc_static.json")
        self.assertEqual(sp.normalized.mean(), 0.033241848025088234)
        self.assertEqual(sp.wavenumber.mean(), 2607.12017)

    def test_timescan(self):
        subprocess.call([
            sys.executable,
            "../scripts/timescan.py",
            "timescan.yaml",
        ])
        pumped = pysfg.spectrum.json_to_pumpprobe('cache/pumped.json')
        probed = pysfg.spectrum.json_to_pumpprobe('cache/probed.json')
        self.assertEqual(pumped.normalized.mean(), 0.14001896355614948)
        self.assertEqual(probed.normalized.mean(), 0.139687242787185)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)

    def test_bleach(self):
        subprocess.call([
            sys.executable,
            "../scripts/bleach.py",
            "bleach.yaml",
        ])
        bleach = pysfg.spectrum.json_to_bleach("cache/bleach.json")
        bleachR = pysfg.spectrum.json_to_bleach("cache/bleach1.json")

        self.assertEqual(bleach.normalized.mean(), -0.0018385374879113302)
        self.assertEqual(bleachR.normalized.mean(), 0.9912969632787191)

    def test_trace(self):
        subprocess.call([
            sys.executable,
            "../scripts/trace.py",
            "trace.yaml",
        ])
        hf = pysfg.json_to_trace('cache/hf.json')
        lf = pysfg.json_to_trace('cache/lf.json')

        self.assertEqual(hf.bleach.mean(), -0.0034646422689189192)
        self.assertEqual(lf.bleach.mean(), -0.002123050252486773)
        self.assertEqual(hf.bleachE.mean(), 0.001824992816938757)
        self.assertEqual(lf.bleachE.mean(), 0.0015999242125543753)
        self.assertEqual(hf.pp_delay.mean(), 2488.5714285714284)


if __name__ == '__main__':
    os.chdir(Path("../tutorial"))
    unittest.main()
