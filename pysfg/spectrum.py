"""Data classes for spectroscopic SFG data"""

import logging
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.constants import speed_of_light as c0
import matplotlib.pyplot as plt


class BaseSpectrum():
    """Abstract base class for spectral data classes."""
    def __init__(
            self, intensity, baseline=None, norm=None, wavenumber=None,
            intensityE=None, pixel=None
    ):
        self._intensity = None
        self.intensity = intensity
        self.baseline = baseline
        self.norm = norm
        self.wavenumber = wavenumber
        self.intensityE = intensityE
        self.pixel = pixel

    @property
    def intensity(self):
        """Intensity values of the spectrum. Must be a 1D array"""
        return self._intensity

    @property
    def intensityE(self):
        """Uncertainty of the intensity values."""
        return self._intensityE

    @intensityE.setter
    def intensityE(self, intensityE):
        if isinstance(intensityE, type(None)):
            logging.warning("Warning. Using default error estimation of 10%")
            intensityE = self.intensity*0.1
        elif isinstance(intensityE, (float, int)):
            intensityE = self.intensity*intensityE
        if np.shape(intensityE) != self.shape:
            raise ValueError('Shape of intensityE and intensity must match')
        self._intensityE = np.array(intensityE)

    @property
    def baseline(self):
        """Baseline of the spectrum"""
        return self._baseline

    @baseline.setter
    def baseline(self, baseline):
        if isinstance(baseline, type(None)):
            baseline = np.zeros_like(self.intensity)
        else:
            baseline = np.ones_like(self.intensity) * baseline
        # Checking the shape to be really sure
        if np.shape(baseline) != self.shape:
            raise ValueError('Shape of baseline and intensity must match')
        self._baseline = np.array(baseline)

    @property
    def norm(self):
        return self._norm

    @norm.setter
    def norm(self, norm):
        if isinstance(norm, type(None)):
            norm = np.ones_like(self.intensity)
        else:
            norm = np.ones_like(self.intensity) * norm
        if np.shape(norm) != np.shape(self.intensity):
            raise ValueError('Shape of norm and intensity must match')
        self._norm = np.array(norm)

    @property
    def shape(self):
        """Shape of the intensity"""
        return np.shape(self.intensity)

    @property
    def basesubed(self):
        """Baseline subtracted intensity"""
        return self.intensity - self.baseline

    @property
    def basesubedE(self):
        raise NotImplementedError

    @property
    def normalized(self):
        """Normalized intensity"""
        return self.basesubed/self.norm

    @property
    def normalizedE(self):
        """Uncertainty of the normalized intensity.

        Implementation is not complete. Baseline and normalization uncertainty
        are currently neglected.
        """
        return self.intensityE/self.norm

    @property
    def wavenumber(self):
        """Wavenumber values of the spectrum."""
        return self._wavenumber

    @property
    def pixel(self):
        """The pixel number on the camera. This only equals the index position if the
        spectra aren't truncated initially, what they typically should be, as
        the setups have a finite bandwidth.
        """
        return self._pixel

    @pixel.setter
    def pixel(self, pixel):
        if isinstance(pixel, type(None)):
            pixel = np.arange(self.shape[-1])
        elif isinstance(pixel, slice):
            if isinstance(pixel.start, type(None)) and isinstance(pixel.stop, type(None)):
                pixel = np.arange(0, self.shape[-1])
            elif isinstance(pixel.start, type(None)) or isinstance(pixel.stop, type(None)):
                raise ValueError('Strange pixel slice: ' + pixel)
            else:
                pixel = np.arange(pixel.start, pixel.stop)
        if len(pixel) != self.shape[-1]:
            raise ValueError("Pixel shape doesn't match data shape: {} vs {}".format(
                len(pixel), self.shape)
            )
        self._pixel = pixel

    @property
    def df(self):
        """Return a pandas dataframe."""
        raise NotImplementedError

    def to_json(self, *args, **kwargs):
        """Save spectrum to json with pd.Dataframe.to_json."""
        logging.info('Saving to: %s' % args[0])
        self.df.to_json(*args, **kwargs)

    def gaussian_filter1d(self, prop, *args, **kwargs):
        """Return gaussian filtered version of prop."""
        data = getattr(self, prop)
        return gaussian_filter1d(data *args, **kwargs)

    def plot(self, x, y, *args, **kwargs):
        x = str(x)
        y = str(y)
        plt.plot(getattr(self, x), getattr(self, y), *args, **kwargs)

class PSSHG():
    """Phase Resolved SHG spectrum."""
    def __init__(self, interference, local_oszillator, sample, wavelength=None, mask=None):
        self.interference = np.array(interference)
        self.local_oszillator = np.array(local_oszillator)
        self.sample = np.array(sample)
        if isinstance(wavelength, type(None)):
            wavelength = np.arange(len(self.interference))
        self.wavelength = np.array(wavelength)
        self.mask = mask
        self.N = len(self.wavelength)

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, value):
        if isinstance(value, type(None)):
            self._mask = np.ones_like(self.time_domain, dtype=int)
        elif isinstance(value, slice):
            self._mask = np.zeros_like(self.time_domain, dtype=int)
            self._mask[value] = 1
        else:
            self._mask = np.array(value, dtype=int)

    @property
    def cross_term(self):
        return self.interference - self.local_oszillator - self.sample

    @property
    def time_domain(self):
        """Apply IFFT to signal to convert from frequency to time domain"""
        # Signal in time domain
        return np.fft.ifft(self.cross_term)

    @property
    def time_delay(self):
        """Calculate the time delay of the time_domain signal. E.g. the pulse delay
        This calculation assumes that PSSHG.wavelength is in nm."""
        return np.fft.fftfreq(self.N, np.abs(np.diff(self.THz).mean()))

    @property
    def spectrum(self):
        return np.fft.fft(self.time_domain*self.mask)

    @property
    def df(self):
        return pd.DataFrame(
            data=[self.interference, self.local_oszillator, self.sample, self.wavelength, self.mask],
            index=('interference', 'local_oszillator', 'sample', 'wavelength', 'mask'),
        )

    def to_json(self, *args, **kwargs):
        self.df.to_json(*args, **kwargs)

    @property
    def frequency(self):
        return c0/self.wavelength * 10**9

    @property
    def THz(self):
        return self.frequency * 10**-12

    def plot(self, x, y, *args, **kwargs):
        x = str(x)
        y = str(y)
        plt.plot(getattr(self, x), getattr(self, y), *args, **kwargs)


class Normalized_PSSHG():
    def __init__(self, sample, quarz):
        self.sample = sample
        self.quarz = quarz

    @property
    def spectrum(self):
        return self.sample.spectrum/self.quarz.spectrum

    @property
    def cross_term(self):
        return self.sample.cross_term/self.quarz.cross_term

    @property
    def wavelength(self):
        return self.sample.wavelength

    @property
    def mask(self):
        return self.sample.mask

    def plot(self, x, y, *args, **kwargs):
        x = str(x)
        y = str(y)
        plt.plot(getattr(self, x), getattr(self, y), *args, **kwargs)

class Spectrum(BaseSpectrum):
    def __init__(self, intensity, baseline=None, norm=None, wavenumber=None,
                 intensityE=None, pixel=None):
        """1D SFG Spectrum

        Class to encapsulate Static SFG data. Pass intensity, baseline, norm
        and wavenumber data and the class allows to subtract the baseline
        `Spectrum.basesubed` and normalize data `Spectrum.normalized`. Further
        one can export and import the data as pandas Dataframe with
        `Spectrum.df`, the `Spectrum.to_json` and the
        `spectrum.json_to_spectrum` method.

        All inputs are checked for correct shape.

        intensity: 1d array of intensity values
        baseline: 1d array of baseline values
        norm: 1d array of norm values
        wavelength: 1d array of wavelength

        """
        super().__init__(intensity, baseline, norm, wavenumber, intensityE, pixel)

    ## For unknown reasons this cant be inhereted from BaseSpectrum
    @property
    def intensity(self):
        """Intensity values of the spectrum. Must be a 1D array"""
        return self._intensity

    @intensity.setter
    def intensity(self, intensity):
        if len(np.shape(intensity)) != 1:
            raise ValueError("Intensity must be 1 D array.")
        self._intensity = np.array(intensity)

    @property
    def wavenumber(self):
        """Wavenumber values of the spectrum."""
        return self._wavenumber

    @wavenumber.setter
    def wavenumber(self, wavenumber):
        if isinstance(wavenumber, type(None)):
            # The camera records nm. Thus wavenumber order is typically
            # reversed. If we dont have the wavenumbers, we should
            # atleast have the right order.
            wavenumber = np.arange(self.shape[0], 0, -1)
        if np.shape(wavenumber) != self.shape:
            raise ValueError('Wavenumber has not the same shape as intensity')
        self._wavenumber = wavenumber

    @property
    def df(self):
        """Return a pandas dataframe."""
        columns = ('intensity', 'baseline', 'norm', 'wavenumber', 'pixel', 'intensityE')
        return pd.DataFrame(
            np.transpose([getattr(self, name) for name in columns]),
            columns=columns
        )

class PumpProbe(BaseSpectrum):
    def __init__(
            self,
            intensity,
            baseline=None,
            norm=None,
            wavenumber=None,
            pp_delay=None,
            pump_freq=None,
            pump_width=None,
            cc_width=None,
            intensityE=None,
            pixel=None,
    ):
        """Pump-Probe Spectrum class. Intensity is a 2D numpy array.

        Class to encapsulate the handling of pump-probe SFG data.
        Baselinesubtraction with `PumpProbe.basesubed`, normalization with
        `PumpProbe.normalized`. Two instances of this calss can be subtracted
        form each other to calculate the bleach:

        ```
        pumped = PumpProbe(np.random.rand(3, 10))
        probed = PumpProbe(np.random.rand(3, 10))

        bleach = pumped - probed
        ```

        Data can be saved and imported as pandas Dataframe with `PumpProbe.df`,
        `PumpProbe.to_json` and `spectrum.json_to_pumpprobe`.
        All inputs are shape checked against intensity data.

        intensity: 2d np.array with (len(pp_delay), len(wavenumber)) shape.
        baseline: int, float, 1d or 2d array. Baseline data. Is casted
          into the same shape as intensity.
        norm: same shape casting as baseline. Used for normalization
        wavenumber: 1d array with wavenumber values.
        pp_delay: 1d numpy array of pump-probe delays.

        """
        super().__init__(intensity, baseline, norm, wavenumber, intensityE, pixel)
        self.pp_delay = pp_delay
        self.pump_freq = pump_freq
        self.pump_width = pump_width
        self.cc_width = cc_width

    @property
    def pp_delay(self):
        return self._pp_delay

    @pp_delay.setter
    def pp_delay(self, pp_delay):
        if isinstance(pp_delay, type(None)):
            pp_delay = np.arange(self.shape[0])
        elif not len(pp_delay) == self.shape[0] or len(np.shape(pp_delay)) != 1:
            raise ValueError('Len of pp_delay must match shape of intensity.')
        self._pp_delay = pp_delay

    @property
    def intensity(self):
        """Intensity values of the spectrum. Must be a 1D array"""
        return self._intensity

    @intensity.setter
    def intensity(self, intensity):
        if len(np.shape(intensity)) != 2:
            raise ValueError('Intensity must be of dimenstion 2')
        self._intensity = np.array(intensity)

    @property
    def wavenumber(self):
        """Wavenumber values of the spectrum."""
        return self._wavenumber

    @wavenumber.setter
    def wavenumber(self, wavenumber):
        if len(np.shape(wavenumber)) != 1 or len(wavenumber) != self.shape[1]:
            e = "Len of wavenumber {} must match shape of intensity {}".format(
                np.shape(wavenumber), self.shape
            )
            raise ValueError(e)
        self._wavenumber = np.array(wavenumber)

    @property
    def df(self):
        """Return a long form pandas dataframe."""
        #  TODO andd pump_width, pump_pos and cc_width.
        dfs = []
        for key in ('intensity', 'baseline', 'norm', 'basesubed', 'normalized', 'intensityE', 'normalizedE'):
            df = pd.DataFrame(
                getattr(self, key),
            )
            df.insert(0, 'pp_delay', self.pp_delay)
            df.insert(0, 'name', [key for i in range(len(self.pp_delay))])

            dfs.append(df)
        df = pd.concat(dfs)
        df.reset_index(drop=True, inplace=True)

        # Add Wavenumbers
        d = dict(zip(np.arange(len(self.wavenumber)), self.wavenumber))
        d["name"] = "wavenumber"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)

        # Add Pixels numbers
        d = dict(zip(np.arange(len(self.pixel)), self.pixel))
        d["name"] = "pixel"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)
        return df

    def __sub__(self, other):
        """Returns a dictionary with all the important pump-probe data."""
        if not np.all(self.wavenumber == other.wavenumber):
            raise NotImplementedError
        if not np.all(self.pp_delay == other.pp_delay):
            raise NotImplementedError

        # This corrects for static differences in pumped and probed
        return Bleach(
            intensity=self.intensity - other.intensity,
            baseline=np.mean([self.baseline, other.baseline], 0),
            norm=np.mean([self.norm, other.norm], 0),
            wavenumber=self.wavenumber,
            pp_delay=self.pp_delay,
            basesubed=self.basesubed - other.basesubed,
            normalized=self.normalized - other.normalized,
            intensityE=np.sqrt(self.intensityE**2 + other.intensityE**2),
            pixel=self.pixel,
            normalizedE=np.sqrt(self.normalizedE**2+other.normalizedE**2),
        )

    def __truediv__(self, other):
        """Returns a dictionary with all the important pump-probe data."""
        if not np.all(self.wavenumber == other.wavenumber):
            raise NotImplementedError
        if not np.all(self.pp_delay == other.pp_delay):
            raise NotImplementedError
        return Bleach(
            intensity=self.intensity / other.intensity,
            baseline=self.baseline / other.baseline,
            norm=np.mean([self.norm, other.norm], 0),
            wavenumber=self.wavenumber,
            pp_delay=self.pp_delay,
            basesubed=self.basesubed / other.basesubed,
            normalized=self.normalized / other.normalized,
            intensityE=np.sqrt((self.intensityE/other.intensity)**2 +
                               (self.intensity*other.intensityE/other.intensity**2)**2),
            pixel=self.pixel,
            normalizedE=np.sqrt((self.normalizedE/other.normalized)**2 +
                               (self.normalized*other.normalizedE/other.normalized**2)**2),
        )


# This class is very simmilar to PumpProbe, but it doesn't impose
# Anything on the data. Maybe its not worth it and instead one should
# just use a dict here.
class Bleach():
    def __init__(
            self,
            intensity=None,
            baseline=None,
            norm=None,
            wavenumber=None,
            pp_delay=None,
            basesubed=None,
            normalized=None,
            pump_freq=None,
            pump_width=None,
            cc_width=None,
            intensityE=None,
            pixel=None,
            normalizedE=None,
    ):
        """Class to encapuslate bleach data.

        A class to handle the difference of two PumpProbe classes. It is
        basically the same as PumpProbe, but doens't check for shapes. As the
        shapes don't always need to be defined.

        It allows to export the data with `Bleach.to_json` and also generates
        DataFrames with `Bleach.df`. Data can be imported with `spectrum.json_to_bleach`

        """
        self.intensity = intensity
        self.baseline = baseline
        self.norm = norm
        self.wavenumber = wavenumber
        self.pp_delay = pp_delay
        self.basesubed = basesubed
        self.normalized = normalized
        self.pump_freq = pump_freq
        self.pump_width = pump_width
        self.cc_width = cc_width
        self.intensityE = intensityE
        self.pixel = pixel
        self.normalizedE = normalizedE
        # TODO implement getter and setter

    @property
    def df(self):
        """Return a long form pandas dataframe."""
        # TODO andd pump_width, pump_pos and cc_width.
        dfs = []
        for key in ('intensity', 'baseline', 'norm', 'basesubed', 'normalized', 'intensityE', 'normalizedE'):
            df = pd.DataFrame(
                getattr(self, key),
            )
            df.insert(0, 'pp_delay', self.pp_delay)
            df.insert(0, 'name', [key for i in range(len(self.pp_delay))])
            dfs.append(df)
        df = pd.concat(dfs, sort=False)  # We dont need it sorted.
        df.reset_index(drop=True, inplace=True)

        # Prepare wavenumber
        d = dict(zip(np.arange(len(self.wavenumber)), self.wavenumber))
        d["name"] = "wavenumber"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)

        d = dict(zip(np.arange(len(self.pixel)), self.pixel))
        d["name"] = "pixel"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)
        return df

    def to_json(self, *args, **kwargs):
        """Save spectrum to json with pd.Dataframe.to_json."""
        logging.info('Saving to: %s' % args[0])
        self.df.to_json(*args, **kwargs)

    def get_trace(
            self, pixel=slice(None), delay=slice(None),
    ):
        """Generate a Trace object form this bleach object.

        pixel refers to the `bleach.pixel` array. Steps are ignored.
        """
        if not isinstance(pixel, slice):
            raise NotImplementedError('Pixel must be slice object')
        if not isinstance(delay, slice):
            raise NotImplementedError('Delay must be slice object')

        index = np.where((self.pixel > pixel.start) & (self.pixel < pixel.stop))[0]
        pixel = (pixel.start, pixel.stop)

        # TODO add pump_width, pump_freq and cc_width
        # The zero is needed because self.pixels is per definition a 1D array

        trace = np.mean(self.normalized[delay, index], axis=1)
        pp_delay = self.pp_delay[delay]
        # Error propagation for the uncertainty of the mean
        de = self.normalizedE[delay, index]
        traceE = np.sqrt(np.sum(de**2, axis=1))/de.shape[1]
        return Trace(
            pp_delay, bleach=trace, pixel=pixel,
            delay=delay, bleachE=traceE,
        )

    def gaussian_filter1d(self, prop, *args, **kwargs):
        """Return gaussian filtered version of prop."""
        data = getattr(self, prop)
        return gaussian_filter1d(data, *args, **kwargs)

# TODO: Add type checkers
class Trace():
    def __init__(
            self, pp_delay, bleach, pixel=None, delay=None,
            pump_freq=None, pump_width=None, cc_width=None, bleachE=None,
            wavenumber=None, wavelength=None,
    ):
        """ Class to encapuslate trace data.

        pp_delay: 1D array of pump_probe delays
        bleach: 1D array of bleach values. This is NOT a bleach object
        pixel: slice of pixels used for this trace.
        delay: slice of delays selected during creation
        pump_freq: central pump frequency as int
        pump_width: spectral width of the pump freq.
        cc_wisth: temporal width of the cross correlation.
        bleachE: Uncertainty of the bleach
        """
        self.pp_delay = np.array(pp_delay)
        self.bleach = bleach
        self.pixel = pixel
        self.wavenumber = wavenumber
        self.wavelength = wavelength
        self.delay = delay
        self.pump_freq = pump_freq
        self.pump_width = pump_width
        self.cc_width = cc_width
        self.bleachE = bleachE

    @property
    def bleach(self):
        return self._bleach

    @bleach.setter
    def bleach(self, value):
        if np.shape(value) != self.pp_delay.shape:
            raise ValueError(
                "Shape of pp_delay {} and shape of bleach {} don't match".format(
                    value.shape, self.pp_delay.shape
                )
            )
        self._bleach = np.array(value)

    @property
    def bleachE(self):
        return self._bleachE

    @bleachE.setter
    def bleachE(self, value):
        self._bleachE = np.array(value) * np.ones_like(self.bleach)

    @property
    def pixel(self):
        return self._pixel

    # This allows setting pixels wiht: a slice, a list or None and in all
    # casis the result of pixel can be used as array index. The same holds true
    # for wavenumber, wavelength and delay settings.
    @pixel.setter
    def pixel(self, value):
        if isinstance(value, type(None)):
            self._pixel = slice(None)
        elif isinstance(value, slice):
            if value == slice(None):
                self._pixel = value
            else:
                self._pixel = np.arange(value.start, value.stop, value.step)
        else:
            self._pixel = np.array(value)
            if len(self._pixel.shape) != 1:
                raise ValueError("Can't use {} as pixel ".format(value))

    @property
    def wavenumber(self):
        return self._wavenumber

    @wavenumber.setter
    def wavenumber(self, value):
        if isinstance(value, type(None)):
            self._wavenumber = slice(None)
        elif isinstance(value, slice):
            if value == slice(None):
                self._wavenumber = value
            else:
                self._wavenumber = np.arange(value.start, value.stop, value.step)
        else:
            self._wavenumber = np.array(value)
            if len(self._wavenumber.shape) != 1:
                raise ValueError("Can't use {} as wavenumber".format(value))

    @property
    def wavelength(self):
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value):
        if isinstance(value, type(None)):
            self._wavelength = slice(None)
        elif isinstance(value, slice):
            if value == slice(None):
                self._wavelength = value
            else:
                self._wavelength = np.arange(value.start, value.stop, value.step)
        else:
            self._wavelength = np.array(value)
            if len(self._wavelength.shape) != 1:
                raise ValueError("Can't use {} as wavelength".format(value))

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        if isinstance(value, type(None)):
            self._delay = slice(None)
        elif isinstance(value, slice):
            if value == slice(None):
                self._delay = value
            else:
                self._delay = np.arange(value.start, value.stop, value.step)
        else:
            self._delay = np.array(value)
            if len(self._delay.shape) != 1:
                raise ValueError("Can't use {} as delay".format(value))

    @property
    def df(self):
        """Return a long form pandas dataframe."""
        # Implement a method to generate a long from dataframe from this data.
        keys = ('pp_delay', 'bleach', 'bleachE')
        df = pd.DataFrame(
            {key: getattr(self, key) for key in keys},
               ).melt(id_vars='pp_delay')
        # Slice is only used for None input.
        # Else this is a list of index values.
        # This export removes information. I'm not happy with this.
        if isinstance(self.pixel, slice):
            df['pixel_start'] = None
            df['pixel_stop'] = None
        else:
            df['pixel_start'] = np.min(self.pixel)
            df['pixel_stop'] = np.max(self.pixel)

        if isinstance(self.wavenumber, slice):
            df['wavenumber_start'] = None
            df['wavenumber_stop'] = None
        else:
            df['wavenumber_start'] = np.min(self.wavenumber)
            df['wavenumber_stop'] = np.max(self.wavenumber)

        if isinstance(self.wavelength, slice):
            df['wavelength_start'] = None
            df['wavelength_stop'] = None
        else:
            df['wavelength_start'] = np.min(self.wavelength)
            df['wavelength_stop'] = np.max(self.wavelength)

        df['cc_width'] = self.cc_width
        df['pump_freq'] = self.pump_freq
        df['pump_width'] = self.pump_width
        return df

    @property
    def dict(self):
        d = {
            "pp_delay": self.pp_delay.tolist(),
            "bleach": self.bleach.tolist(),
            "pump_freq": self.pump_freq,
            "pump_width": self.pump_width,
            "cc_width": self.cc_width,
            "bleachE": self.bleachE.tolist(),
        }
        if isinstance(self.pixel, slice):
            d['pixel'] = None
        else:
            d['pixel'] = self.pixel.tolist()
        if isinstance(self.wavenumber, slice):
            d['wavenumber'] = None
        else:
            d['wavenumber'] = self.wavenumber.tolist()
        if isinstance(self.wavelength, slice):
            d['wavelength'] = None
        else:
            d['wavelength'] = self.wavelength.tolist()
        if isinstance(self.delay, slice):
            d['delay'] = None
        else:
            d['delay'] = self.delay.tolist()
        # Only None slice is allowed. Else it is a list
        # of index values.
        return d

    def to_json(self, fname):
        """Save spectrum to json with dict to json."""
        logging.info('Saving to: %s' % fname)
        with open(Path(fname), "w") as outfile:
            json.dump(self.dict, outfile)


def json_to_spectrum(*args, **kwargs):
    """Read Spectrum for json file."""
    df = pd.read_json(*args, **kwargs)
    return Spectrum(
        intensity=df.intensity, baseline=df.baseline, norm=df.norm,
        wavenumber=df.wavenumber, intensityE=df.intensityE, pixel=df.pixel
    )


def _json_to_dict(*args, **kwargs):
    df = pd.read_json(*args, **kwargs)
    data = {}
    for name, group in df.groupby("name"):
        # Need to make a copy here to prevent error messages.
        d = group.drop("name", axis=1)
        if name == "intensity":
            data["pp_delay"] = d.pop("pp_delay")
        else:
            d.drop("pp_delay", axis=1, inplace=True)
        data[name] = d.to_numpy()

    # PandasDataframes transform to 2d arrays
    # but wavenumbers needs only one
    data["wavenumber"] = data["wavenumber"][0]
    data["pixel"] = data["pixel"][0]
    return data


def json_to_pumpprobe(*args, **kwargs):
    """Read PumpProbe from json file.
    See pandas.read_json for information.
    """
    data = _json_to_dict(*args, **kwargs)
    return PumpProbe(
        intensity=data["intensity"],
        intensityE=data['intensityE'],
        baseline=data["baseline"],
        norm=data["norm"],
        wavenumber=data["wavenumber"],
        pixel=data['pixel'],
        pp_delay=data["pp_delay"]
    )


def json_to_bleach(*args, **kwargs):
    """Read PumpProbe from json file
    See pandas.read_json for information.
    """
    data = _json_to_dict(*args, **kwargs)
    return Bleach(**data)


def json_to_trace(fname):
    with open(Path(fname)) as f:
        data = json.load(f)
    return Trace(**data)


def json_to_PSSHG(*args, **kwargs):
    data = pd.read_json(*args, **kwargs)
    return PSSHG(data.loc['interference'], data.loc['local_oszillator'], data.loc['sample'], data.loc['wavelength'], data.loc['mask'])
