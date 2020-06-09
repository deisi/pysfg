import numpy as np

def heat_time(t, H0, tau=1000, c=0):
    """Function to model the time dependecy of the heat
    ----------------
    Parameters
    t:        array type
        t time points

    H0:        number
        Amlitude or max heat of the model

    tau:     number
        time constant of the heat model

    c:        number
        time offset of the model
    for_ratio: bool
        makes negative values 1 so it works with ratio and not diff

    ----------------
    return
        array of resulting values
    """
    HM = lambda x: H0*(1-np.e**(-1*x/tau))+c
    if hasattr(t, '__iter__'):
        ret = np.array([HM(time) for time in t])
        # need to remove negative times, because
        # model is unphysical in this region
        mask = np.where(t <= 0)
        ret[mask] = 0
        return ret
    if t <= 0:
        return 0
    return HM(t)

def heat_filter(input, times, tau=700, c=0):
    """Filter input by substracting the last spectrum assuming exponential ingroth of heat."""
    H0 = input[-1]
    h = heat_time(times, H0, tau, c)
    return input - h
