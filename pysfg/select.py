"""The select mdule. Used for slicing of 4D data."""

class SelectorPP:
    def __init__(
            self, pp_delays=slice(None), scans=slice(None), spectra=slice(None), pixel=slice(None)
    ):
        """Selector object to slice in 4D pump-probe data files.

        use data[SelectorPP.select] to select a subset of data.
        """
        self.select = (pp_delays, scans, spectra, pixel)

    def _test(self, value):
        if not isinstance(value, int) or not isinstance(value, type(slice)) or not hasattr(value, __iter__):
            raise ValueError("Must pass int or slice or iterable")

    @property
    def pp_delays(self):
        return self.select[0]

    @pp_delays.setter
    def pp_delays(self, value):
        self._test(value)
        self.select[0] = value

    @property
    def scans(self):
        return self.select[1]

    @scans.setter
    def scans(self, value):
        self._test(value)
        self.select[1] = value

    @property
    def spectra(self):
        return self.select[2]

    @spectra.setter
    def spectra(self, value):
        self._test(value)
        self.select[2] = value

    @property
    def pixel(self):
        return self.select[3]

    @pixel.setter
    def pixel(selv, value):
        self._test(value)
        self.select[3] = value

    def __repr__(self):
        return str(self.select)

    def __str__(self):
        return str(self.select)

    def __getitem__(self, key):
        return self.select[key]

    def __iter__(self):
        return self.select

    def __len__(self):
        return len(self.select)
