"""Module to encapsulate common experiments."""

class Normalization:
    def __init__(
            self,
            data,
            pp_delays=slice(None),
            scans=slice(None),
            spectra=0,
            pixel=slice(None),
    ):
        """A Normalization object. Typically a quartz or gold scan."""
        self.data = data
        self.pp_delays=pp_delays
        self.scans = scans
        self.spectra = spectra
        self.pixel = pixel
