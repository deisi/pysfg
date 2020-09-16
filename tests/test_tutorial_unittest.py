import unittest
import sys
import os
import subprocess
import pysfg
from pathlib import Path

# This makes it possible to run this test script from everywhere.
path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))
working_path = dir_path.joinpath("../tutorial")

class TestTutorial(unittest.TestCase):

    def test_simple_gold(self):
        os.chdir(working_path)
        subprocess.call([
            sys.executable,
            Path("../scripts/static_spectra.py"),
            Path("simple_gold.yaml"),
        ])
        gold1 = pysfg.spectrum.json_to_spectrum(Path("cache/gold_1.json"))
        gold2 = pysfg.spectrum.json_to_spectrum(Path("cache/gold_2.json"))

        self.assertEqual(gold1.basesubed.mean(), 684.2034375)
        self.assertEqual(gold2.basesubed.mean(), 3355.231034482759)

    def test_simple_spectrum(self):
        os.chdir(working_path)
        subprocess.call([
            sys.executable,
            Path("../scripts/static_spectra.py"),
            Path("simple_spectrum.yaml"),
        ])
        sp = pysfg.spectrum.json_to_spectrum(Path("cache/sc_d2o-dopc_static.json"))
        self.assertEqual(sp.normalized.mean(), 0.033241848025088234)
        self.assertEqual(sp.wavenumber.mean(), 2607.12017)

    def test_timescan(self):
        os.chdir(working_path)
        subprocess.call([
            sys.executable,
            "../scripts/timescan.py",
            "timescan.yaml",
        ])
        pumped = pysfg.spectrum.json_to_pumpprobe(Path('cache/pumped.json'))
        probed = pysfg.spectrum.json_to_pumpprobe(Path('cache/probed.json'))
        self.assertEqual(pumped.normalized.mean(), 0.14001896355614948)
        self.assertEqual(probed.normalized.mean(), 0.139687242787185)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)
        self.assertEqual(pumped.wavenumber.mean(), 2446.1925517241384)

    def test_bleach(self):
        os.chdir(working_path)
        subprocess.call([
            sys.executable,
            Path("../scripts/bleach.py"),
            Path("bleach.yaml"),
        ])
        bleach = pysfg.spectrum.json_to_bleach(Path("cache/bleach.json"))
        bleachR = pysfg.spectrum.json_to_bleach(Path("cache/bleach1.json"))

        self.assertEqual(bleach.normalized.mean(), -0.0018385374879113302)
        self.assertEqual(bleachR.normalized.mean(), 0.9912969632787191)

    def test_trace(self):
        os.chdir(working_path)
        subprocess.call([
            sys.executable,
            Path("../scripts/trace.py"),
            Path("trace.yaml"),
        ])
        hf = pysfg.json_to_trace(Path('cache/hf.json'))
        lf = pysfg.json_to_trace(Path('cache/lf.json'))

        self.assertEqual(hf.bleach.mean(), -0.0034646422689189192)
        self.assertEqual(lf.bleach.mean(), -0.002123050252486773)
        self.assertEqual(hf.bleachE.mean(), 0.001824992816938757)
        self.assertEqual(lf.bleachE.mean(), 0.0015999242125543753)
        self.assertEqual(hf.pp_delay.mean(), 2488.5714285714284)


if __name__ == '__main__':
    unittest.main()
