"""The select mdule. Used for slicing of 4D data."""

class SelectorPP:
    def __init__(
            self, pp_delays=None, scans=None, spectra=None, pixel=None
    ):
        """Selector object to slice in 4D pump-probe data files.

        Helps to deal with the correct slicing of the 4D PumpProbe data read of
        by `pysfg.read.victor.data_file`. The advantage of this class is, that
        one doesn't need to pass all axis selections in the correct order each
        time. Instead the class returns them always in the correct order. Not that only integers or
        slices are allowed. Index indexing like [1 ,2, 4, 7] would fail.

        Example:
        ```
        data = pysfg.read.victor.data_file('some_path')
        # Traditional slicing:
        data['data'][:, :, 0, 400: 1200]
        # The same with this class:
        data['data'][SelectorPP(spectra=0, pixel=slice(400, 1200)).select]
        # While this method is more verbose, it makes clear, and easier to
        # understand that we want spectrum 0 and pixel 400 to 1200. While
        # we want all pp_delays and scans.

        ```

        use data[SelectorPP.tselect] to select a subset of data.

        """
        self.select = [slice(None), slice(None), slice(None), slice(None)]
        self.pp_delays = pp_delays
        self.scans = scans
        self.spectra = spectra
        self.pixel = pixel

    def _cast(self, value):
        if isinstance(value, int) or isinstance(value, slice):
            return value
        elif isinstance(value, type(None)):
            return slice(value)
        return slice(*value)

    @property
    def tselect(self):
        """Use this to select."""
        return tuple(self.select)

    @property
    def pp_delays(self):
        """The slice of pp_delays to use"""
        return self.select[0]

    @pp_delays.setter
    def pp_delays(self, value):
        self.select[0] = self._cast(value)

    @property
    def scans(self):
        """The slice of scans to use."""
        return self.select[1]

    @scans.setter
    def scans(self, value):
        self.select[1] = self._cast(value)

    @property
    def spectra(self):
        """The slice of spectra to use."""
        return self.select[2]

    @spectra.setter
    def spectra(self, value):
        self.select[2] = self._cast(value)

    @property
    def pixel(self):
        """The slice of pixel to use."""
        return self.select[3]

    @pixel.setter
    def pixel(self, value):
        self.select[3] = self._cast(value)

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
