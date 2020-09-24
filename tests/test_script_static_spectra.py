
import unittest
import pysfg
from pathlib import Path

import importlib.util

path = Path(__file__)
dir_path = path.parent
spec = importlib.util.spec_from_file_location("scripts.static_spectra", dir_path / Path("../scripts/static_spectra.py"))
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class TestScriptStaticSpectra(unittest.TestCase):
    def test_run0(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_run1(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_run2(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": 300,
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_run3(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "norm_data": 1,
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_run4(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "norm_data": "delme.json",
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_run5(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": 300,
            "norm_data": 1,
            "calibration": {"vis_wl": 800},
            "out": "delme.json",
        }
        script.run(config, dir_path)

    def test_spe0(self):
        config = {
            "intensity_data": "./data/quatz.spe",
            "background_data": 600,
            "out": "./results/quartz_spe.json",
            'calibration': {'vis_wl': 800},
        }
        script.run(config, dir_path)

    def test_spe1(self):
        config = {
            "intensity_data": "./data/sample.spe",
            "background_data": 600,
            "out": "./results/sample_spe.json",
            "norm_data": "./results/quartz_spe.json",
            "intensity_selector": {"pixel": [600, 1200]},
            'calibration': {'vis_wl': 800},
        }
        script.run(config, dir_path)

    def test_spe2(self):
        sp = pysfg.json_to_spectrum(dir_path / Path("results/sample_spe.json"))
        self.assertEqual(sp.wavenumber.mean(), 2574.93155)

    def test_spe3(self):
        sp = pysfg.json_to_spectrum(dir_path / Path("results/sample_spe.json"))
        self.assertEqual(sp.basesubed.mean(), 100.25333333333333)

    def test_spe4(self):
        sp = pysfg.json_to_spectrum(dir_path / Path("results/sample_spe.json"))
        self.assertEqual(sp.normalized.mean(), 0.14295257054703953)

    def test_spe5(self):
        config = {
            "intensity_data": "./data/quartz_v2.spe",
            "background_data": 590,
            "out": "./results/quartz_v2_spe.json",
            'calibration': {'vis_wl': 800},
        }
        script.run(config, dir_path)

    def test_spe6(self):
        sp = pysfg.json_to_spectrum(dir_path / Path("results/quartz_v2_spe.json"))
        self.assertEqual(sp.basesubed.mean(), 1647.569375)

    def test_spe7(self):
        sp = pysfg.json_to_spectrum(dir_path / Path("./results/quartz_v2_spe.json"))
        self.assertEqual(sp.wavenumber.mean(), 1796.63680625)

if __name__ == '__main__':
    unittest.main()
