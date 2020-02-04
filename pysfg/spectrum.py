"""Module to deal with SFG Spectral Data"""
# TODO: All classes lack a method of dealing with uncertainties
# TODO: There are some not implemented cases left that are nice to haves.

import numpy as np
import pandas as pd

class BaseSpectrum():
    """Abstract base class for spectral data."""
    def __init__(self, intensity, baseline=None, norm=None, wavenumber=None):
        self.intensity = intensity
        self.baseline = baseline
        self.norm = norm
        self.wavenumber = wavenumber

    @property
    def intensity(self):
        """Intensity values of the spectrum. Must be a 1D array"""
        return self._intensity

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
        # I think this cant trigger
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
        # I think this cant trigger
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
    def normalized(self):
        """Normalized intensity"""
        return self.basesubed / self.norm

    @property
    def wavenumber(self):
        """Wavenumber values of the spectrum."""
        return self._wavenumber

    @property
    def df(self):
        """Return a pandas dataframe."""
        raise NotImplemented

    def to_json(self, *args, **kwargs):
        """Save spectrum to json with pd.Dataframe.to_json."""
        self.df.to_json(*args, **kwargs)


class Spectrum(BaseSpectrum):
    def __init__(self, intensity, baseline=None, norm=None, wavenumber=None):
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
        super().__init__(intensity, baseline, norm, wavenumber)

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
        return pd.DataFrame(
            np.transpose([self.intensity, self.baseline, self.norm, self.wavenumber]),
            columns = ('intensity', 'baseline', 'norm', 'wavenumber')
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
        super().__init__(intensity, baseline, norm, wavenumber)
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
            pp_delay = np.arange(np.shape[0])
        elif not len(pp_delay) == self.shape[0] or len(np.shape(pp_delay)) != 1:
            raise ValueError('Len of pp_delays must match shape of intensity.')
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
        # TODO andd pump_width, pump_pos and cc_width.
        dfs = []
        for key in ('intensity', 'baseline', 'norm', 'basesubed', 'normalized'):
            df = pd.DataFrame(
                getattr(self, key),
            )
            df.insert(0, 'pp_delay', self.pp_delay)
            df.insert(0, 'name', [key for i in range(len(self.pp_delay))])
            dfs.append(df)
        df = pd.concat(dfs)
        df.reset_index(drop=True, inplace=True)

        # Prepare wavenumber
        d = dict(zip(np.arange(len(self.wavenumber)), self.wavenumber))
        d["name"] = "wavenumber"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)
        return df

    def __sub__(self, other):
        """Returns a dictionary with all the important pump-probe data."""
        if not np.all(self.wavenumber == other.wavenumber):
            raise NotImplemented
        if not np.all(self.pp_delay == other.pp_delay):
            raise NotImplemented
        return Bleach(
            intensity=self.intensity - other.intensity,
            baseline=self.baseline - other.baseline,
            norm=self.norm - other.norm,
            wavenumber=self.wavenumber,
            pp_delay=self.pp_delay,
            basesubed=self.basesubed - other.basesubed,
            normalized=self.normalized - other.normalized,
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
    ):
        """Class to encapuslate bleach data.

        A class to handle the difference of two PumpProbe classes. It is
        basically the same as PumpProbe, but doens't check for shapes. As the
        shapes don't always need to be defined.

        It allows to export the data with `Bleach.to_json` and also generates
        DataFrames with `Bleach.df`. Data can be imported with `spectrum.json_to_bleach`

        """
        self.intensity=intensity
        self.baseline=baseline
        self.norm=norm
        self.wavenumber=wavenumber
        self.pp_delay=pp_delay
        self.basesubed=basesubed
        self.normalized=normalized
        self.pump_freq = pump_freq
        self.pump_width = pump_width
        self.cc_width = cc_width
        # Todo implement getter and setter

    @property
    def df(self):
        """Return a long form pandas dataframe."""
        # TODO andd pump_width, pump_pos and cc_width.
        dfs = []
        for key in ('intensity', 'baseline', 'norm', 'basesubed', 'normalized'):
            df = pd.DataFrame(
                getattr(self, key),
            )
            df.insert(0, 'pp_delay', self.pp_delay)
            df.insert(0, 'name', [key for i in range(len(self.pp_delay))])
            dfs.append(df)
        df = pd.concat(dfs, sort=False) # We dont need it sorted.
        df.reset_index(drop=True, inplace=True)

        # Prepare wavenumber
        d = dict(zip(np.arange(len(self.wavenumber)), self.wavenumber))
        d["name"] = "wavenumber"
        d["pp_delay"] = np.nan
        df = df.append(d, ignore_index=True)
        return df

    def to_json(self, *args, **kwargs):
        """Save spectrum to json with pd.Dataframe.to_json."""
        self.df.to_json(*args, **kwargs)

    def get_trace(
            self, pixels=slice(None), delays=slice(None),
    ):
        """Generate a Trace object form this bleach object."""
        #TODO add pump_width, pump_freq and cc_width
        trace = np.mean(self.normalized[delays, pixels], axis=1)
        pp_delay = self.pp_delay[delays]
        return Trace(pp_delay, trace, pixels=pixels, delays=delays)

class Trace():
    def __init__(
            self, pp_delay, bleach, pixels=slice(None), delays=slice(None),
            pump_freq=None, pump_width=None, cc_width=None,
    ):
        """ Class to encapuslate trace data.

        pp_delay: 1D array of pump_probe delays
        bleach: 1D array of bleach values. This is NOT a bleach object
        pixels: slice of pixels used for this trace.
        delays: slice of delays selected during creation
        pump_freq: central pump frequency as int
        pump_width: spectral width of the pump freq.
        cc_wisth: temporal width of the cross correlation.
        """
        self.pp_delay = pp_delay
        self.bleach = bleach
        self.pixels = pixels
        self.delays = delays
        self.pump_freq = pump_freq
        self.pump_width = pump_width
        self.cc_width = cc_width

    def df(self):
        # Implement a method to generate a long from dataframe from this data.
        raise NotImplemented

    def to_json(self, *args, **kwargs):
        """Save spectrum to json with pd.Dataframe.to_json."""
        self.df.to_json(*args, **kwargs)



def json_to_spectrum(*args, **kwargs):
    """Read Spectrum for json file."""
    df = pd.read_json(*args, **kwargs)
    return Spectrum(df.intensity, df.baseline, df.norm, df.wavenumber)

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
    data["wavenumber"]=data["wavenumber"][0]
    return data

def json_to_pumpprobe(*args, **kwargs):
    """Read PumpProbe from json file.
    See pandas.read_json for information.
    """
    data = _json_to_dict(*args, **kwargs)
    return PumpProbe(
        intensity=data["intensity"],
        baseline=data["baseline"],
        norm=data["norm"],
        wavenumber=data["wavenumber"],
        pp_delay=data["pp_delay"]
    )

def json_to_bleach(*args, **kwargs):
    """Read PumpProbe from json file
    See pandas.read_json for information.
    """
    data = _json_to_dict(*args, **kwargs)
    return Bleach(**data)

def json_to_trace(*args, **kwargs):
    # implement a method to read df to trace
    raise NotImplementedError
