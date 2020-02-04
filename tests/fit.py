"""Test fitting function"""
import pysfg

bleach = pysfg.spectrum.json_to_bleach('./data/bleach.json')
# TODO have a method to export and import traces.
trace = bleach.get_trace(pixels=slice(600, 800))


# In general fitting algorithms work better
# if model values are ~1. Very smal and very big
# numbers can be troublesome.
fit = pysfg.fit.TraceFourLevel(
    trace.pp_delay/1000, # makes it ps instead of fs
    trace.bleach*10, # Get values closer to 1
    # Kwargs are passed to Minuit.
    # Thus start parameters can be passed like this
    pedantic=False,
    Amp=0.1,
    t1=0.5,
    t2=0.7,
    c=1,
    mu=0,
    sigma=0.2,
    offset=-0.9, # If this is not -1 this means pumped and probed have a static difference.
)
# Run the fit. See https://github.com/scikit-hep/iminuit for the use of minuit.
fit.minuit.migrad()
