
import unittest
import pysfg
from pathlib import Path

import importlib.util

path = Path(__file__)
dir_path = path.parent
spec = importlib.util.spec_from_file_location("scripts.timescan", dir_path / Path("../scripts/timescan.py"))
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

class TestScriptTimescan(unittest.TestCase):
    config_path = Path("./")
    def test_run0(self):
        config = {
            "intensity_data": "data/dynamic_test_data.dat",
            "out": "delme.json",
        }
        script.run(config, self.config_path)

    def test_run1(self):
        config = {
            "intensity_data": "data/dynamic_test_data.dat",
            "out": "delme.json",
            "background": 300,
        }
        script.run(config, self.config_path)

    def test_run2(self):
        config = {
            "intensity_data": "data/dynamic_test_data.dat",
            "out": "delme.json",
            "background": 300,
            "norm": "../tutorial/cache/gold_1.json",
        }
        script.run(config, self.config_path)




if __name__ == '__main__':
    unittest.main()
