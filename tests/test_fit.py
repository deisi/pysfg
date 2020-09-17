import unittest
import numpy as np
import pysfg
import os
from pathlib import Path

path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))


class TestFit(unittest.TestCase):
    fname = dir_path / Path("data/hf_fit.json")
    fit = pysfg.fit.from_json(fname)
    fname = dir_path / Path("data/hf.json")
    trace = pysfg.spectrum.json_to_trace(fname)
    names = ('Amp', 't1', 't2', 'c', 'mu', 'sigma', 'offset')
    values = np.array([
            0.04214828832052553, 1.9180505095653873, 0.7, 0.8522686370227969,
            0.09875831471606718, 0.15, -0.9764127927695034
    ])
    params = dict(zip(names, values))

    def test_from_json(self):
        res = np.sum(np.abs(self.fit.minuit.np_values() - self.values))
        self.assertLess(res, 0.001)

    def test_four_level_model_init(self):
        pysfg.fit.TraceFourLevel(
            self.trace.pp_delay, self.trace.bleach, self.trace.bleachE,
            **self.params
        )

    def test_to_json(self):
        fname = dir_path / Path("fit.json")
        self.fit.to_json(fname)
        fit = pysfg.fit.from_json(fname)
        self.assertListEqual(fit.y.tolist(), self.fit.y.tolist())




if __name__ == '__main__':
    unittest.main()
