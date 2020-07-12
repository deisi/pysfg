"""Test fitting function"""
import pysfg
import IPython.display as ipd

bleach = pysfg.spectrum.json_to_bleach('./data/bleach.json')
# TODO have a method to export and import traces.
trace = bleach.get_trace(pixel=slice(600, 800))


# In general fitting algorithms work better
# if model values are ~1. Very smal and very big
# numbers can be troublesome.
fit = pysfg.fit.TraceFourLevel(
    x=trace.pp_delay/1000, # makes it ps instead of fs
    y=trace.bleach*10, # Get values closer to 1
    yerr=trace.bleachE*10, # Pass uncertainty to fit algorithim
    # Kwargs are passed to Minuit.
    # Thus start parameters can be passed like this
    pedantic=False, # Makes iminuit complain less
    Amp=0.1, # The amplitude, translates into population fraction
    t1=0.5, # lifetime of the first excited state
    t2=0.7, # lifetime of the second excited state
    c=1, # the heat factor
    mu=0, # The position of the bleach
    sigma=0.2, # This is the width of the instrument response function
    offset=-0.9, # If this is not -1 this means pumped and probed have a static difference.
)
# Run the fit. See https://github.com/scikit-hep/iminuit for the use of minuit.
# The ipd.display can be omitted, but it helps on jupyter lab and notebooks, as it nicely
# prints sime information about the fit.
ipd.display(
    fit.minuit.migrad() # This is the important call for making the fit.
)
