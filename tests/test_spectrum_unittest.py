"""Unittest module for the pysfg.spectrum module."""


import unittest
import numpy as np
import pysfg
from scipy.stats import norm as gaussian


class TestSpectrum(unittest.TestCase):
    pixel = np.arange(1, 1600)
    wavenumber = pixel[::-1]
    intensity = gaussian(750, 100).pdf(pixel)*100 + 1
    baseline = np.ones_like(intensity)
    intensityE = (intensity - 0.9)*0.1
    norm = gaussian(800, 140).pdf(pixel)*1000
    sp = pysfg.spectrum.Spectrum(
        intensity, baseline, norm, wavenumber, intensityE, pixel
    )

    def test_basesubed(self):
        self.assertEqual(np.all(self.sp.basesubed == self.intensity - 1), True)

    def test_normalized(self):
        self.assertEqual(np.all(self.sp.normalized == (self.intensity - 1)/self.norm), True)

    def test_to_and_from_json(self):
        self.sp.to_json("spectrum.json")
        ssp = pysfg.json_to_spectrum("./results/spectrum.json")
        # There is some numerical uncertainty
        self.assertEqual(np.all(self.sp.normalized - ssp.normalized < 0.0001), True)


class TestPumpProbe(unittest.TestCase):
    pixel = np.arange(1, 100)
    pp_delays = np.linspace(-1, 10, 20)
    wavenumber = pixel[::-1]
    xx, yy = np.meshgrid(pixel, pp_delays, sparse=True)
    intensity = 100000*gaussian(50, 30).pdf(xx)*gaussian(4, 4).pdf(yy) + 1
    baseline = np.ones_like(intensity)
    intensityE = (intensity - 0.9)*0.1
    norm = 100000*gaussian(55, 40).pdf(pixel)
    pp = pysfg.PumpProbe(
        intensity, baseline, norm, wavenumber,
        pp_delays, 2500, 80, 0.2, intensityE, pixel
    )
    intensity2 = 100000*gaussian(52, 30).pdf(xx)*gaussian(4, 4).pdf(yy) + 1
    pp2 = pysfg.PumpProbe(
        intensity2, baseline, norm, wavenumber,
        pp_delays, 2500, 80, 0.2, intensityE, pixel
    )

    def test_basesubed(self):
        self.assertTrue(np.all(self.pp.basesubed == self.intensity - 1))

    def test_normalized(self):
        self.assertTrue(np.all(self.pp.normalized == (self.intensity - 1)/self.norm))

    def test_to_and_from_json(self):
        self.pp.to_json("pumpprobe.json")
        ppp = pysfg.json_to_pumpprobe("./results/pumpprobe.json")
        self.assertTrue(np.all(self.pp.normalized - ppp.normalized < 0.0001))

    def test_PumpProbe_baseline_0(self):
        baseline = None
        pp = pysfg.PumpProbe(
            self.intensity, baseline, self.norm, self.wavenumber,
            self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
        )
        self.assertEqual(pp.basesubed.mean(), 67.76760137069422)

    def test_PumpProbe_baselines(self):
        for baseline in (1, np.ones_like(self.pixel), np.ones_like(self.intensity)):
            pp = pysfg.PumpProbe(
                self.intensity, baseline, self.norm, self.wavenumber,
                self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
            )
            self.assertEqual(pp.basesubed.mean(), 66.76760137069422)

    def test_PumpProbe_norms_0(self):
        norm = None
        pp = pysfg.PumpProbe(
            self.intensity, self.baseline, norm, self.wavenumber,
            self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
        )
        self.assertEqual(pp.normalized.mean(), 66.76760137069422)

    def test_PumpProbe_norms_1(self):
        pp = pysfg.PumpProbe(
            self.intensity, self.baseline, self.norm, self.wavenumber,
            self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
        )
        self.assertEqual(pp.normalized.mean(), 0.0823400053566616)

    def test_PumpProbe_norms_2(self):
        norm = 2
        pp = pysfg.PumpProbe(
            self.intensity, self.baseline, norm, self.wavenumber,
            self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
        )
        self.assertEqual(pp.normalized.mean(), 33.38380068534711)

    def test_PumpProbe_norms_3(self):
        norm = 100000*gaussian(55, 40).pdf(self.xx)*gaussian(2, 2).pdf(self.yy) + 1
        pp = pysfg.PumpProbe(
            self.intensity, self.baseline, norm, self.wavenumber,
            self.pp_delays, 2500, 80, 0.2, self.intensityE, self.pixel
        )
        self.assertEqual(pp.normalized.mean(), 7.731632631662137)

    def test_substration(self):
        bleach = self.pp - self.pp2
        self.assertEqual(bleach.normalized.mean(), 0.0004376967887611049)

    def test_deviation(self):
        bleach = self.pp / self.pp2
        self.assertEqual(bleach.normalized.mean(), 1.0042468628341095)


class TestBleach(unittest.TestCase):
    pixel = np.arange(1, 100)
    pp_delays = np.linspace(-1, 10, 20)
    wavenumber = pixel[::-1]
    xx, yy = np.meshgrid(pixel, pp_delays, sparse=True)
    intensity = 100000*gaussian(50, 30).pdf(xx)*gaussian(4, 4).pdf(yy) + 1
    baseline = np.ones_like(intensity)
    intensityE = (intensity - 0.9)*0.1
    norm = 100000*gaussian(55, 40).pdf(pixel)
    pp = pysfg.PumpProbe(
        intensity, baseline, norm, wavenumber,
        pp_delays, 2500, 80, 0.2, intensityE, pixel
    )
    intensity2 = 100000*gaussian(52, 30).pdf(xx)*gaussian(4, 4).pdf(yy) + 1
    pp2 = pysfg.PumpProbe(
        intensity2, baseline, norm, wavenumber,
        pp_delays, 2500, 80, 0.2, intensityE, pixel
    )
    bleach = pp - pp2

    def test_shape(self):
        self.assertTrue(self.bleach.normalized.shape == (20, 99))

    def test_trace_shape(self):
        tr = self.bleach.get_trace(slice(20, 30))
        self.assertTrue(tr.bleach.shape == (20,))

    def test_trace_result(self):
        tr = self.bleach.get_trace(slice(20, 30))
        self.assertEqual(tr.bleach.mean(), 0.005120605673482265)

    def test_to_and_from_json(self):
        self.bleach.to_json("bleach.json")
        bleach = pysfg.spectrum.json_to_bleach("./results/bleach.json")
        self.assertTrue(np.all(bleach.intensity - self.bleach.intensity < 0.0001))


class TestTrace(unittest.TestCase):
    pp_delays = np.linspace(-1, 10, 20)
    bleach = np.linspace(1, -1, 20)
    pixel = slice(30, 40)
    wavenumber = np.arange(100, 200, 5)
    wavelength = None
    delay = slice(None)
    pump_freq = 2500
    pump_width = 80
    cc_width = 3
    bleachE = bleach * 0.1
    trace = pysfg.spectrum.Trace(
        pp_delays, bleach, pixel, delay, pump_freq, pump_width, cc_width,
        bleachE, wavenumber, wavelength,
    )

    def test_to_and_from_json(self):
        self.trace.to_json("trace.json")
        tr = pysfg.spectrum.json_to_trace("./results/trace.json")
        self.assertAlmostEqual(self.trace.bleach.mean(), tr.bleach.mean())


if __name__ == '__main__':
    unittest.main()


