
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
    config_path = Path("./")
    def test_run0(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run1(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run2(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": 300,
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run3(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "norm_data": 1,
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run4(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": "data/bg_quartz.dat",
            "norm_data": "delme.json",
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run5(self):
        config = {
            "intensity_data": "data/sc_quartz.dat",
            "background_data": 300,
            "norm_data": 1,
            "calibration": {"vis_wl": 800},
            "out": "delme.json",
        }
        script.run(config, self.config_path)


if __name__ == '__main__':
    unittest.main()
