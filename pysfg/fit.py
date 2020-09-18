"""A Module to help fitting some distributions.

Fitting is based in iminnuit. Make yourself famialiar with
https://github.com/scikit-hep/iminuit
"""
import numpy as np
import json
import logging
import sys
from scipy.special import erf, erfc
from scipy.stats import norm
from iminuit import Minuit, describe
from iminuit.util import make_func_code
from pathlib import Path


def from_json(fname):
    """Import from json serialized version. fname is a string with a path
    to where to read the file from.
    """
    with open(Path(fname)) as json_file:
        d = json.load(json_file)

    thismodule = sys.modules[__name__]
    FitClass = getattr(thismodule, d.pop('class'))
    d.pop('errors')

    fit = FitClass(
            **d, errordef=1
        )
    fit.minuit.migrad()
    return fit


class LeastSquares:
    def __init__(self, model, x, y, yerr):
        self.model = model  # model predicts y for given x
        self.x = np.array(x)
        self.y = np.array(y)
        self.yerr = np.array(yerr)
        self.func_code = make_func_code(describe(self.model)[1:])

    def __call__(self, *par):  # par is a variable number of model parameters
        ym = self.model(self.x, *par)
        chi2 = sum(((self.y - ym)/self.yerr)**2)
        return chi2


class FitBase():
    def __init__(self, x, y, yerr=None, **kwargs):
        """kwargs are passed to minuit"""
        # TODO add shape chekers
        self.x = np.array(x)
        self.y = np.array(y)
        if isinstance(yerr, type(None)):
            yerr = np.ones_like(self.x)
        self.yerr = np.array(yerr)

        # TODO errorbars
        self.lsq = LeastSquares(self.model, self.x, self.y, self.yerr)
        # get the args from line and strip 'x'
        self.minuit = Minuit(self.lsq, **kwargs)

    def model(self, *args, **kwargs):
        """This must be implemented by the subcalsses."""
        raise NotImplementedError

    @property
    def dict(self):
        """A serialized representation of this fit class"""
        return {
                "class": self.__class__.__name__,
                "x": list(self.x),
                "y": list(self.y),
                "yerr": list(self.yerr),
                **dict(self.minuit.values),
                **{"fix_" + key: value for key, value in self.minuit.fixed.items()},
                "errors": dict(self.minuit.errors),
                }


    def fit(self, x):
        """Fit function at value x."""
        return self.model(x, *self.minuit.args)

    def to_json(self, fname):
        """Export json serialized version. fname is a string with a path to
        where to save the serialized json object.
        """
        logging.info('Saving to: %s' % fname)
        with open(Path(fname), 'w') as outfile:
            json.dump(self.dict, outfile, indent=2)


class Gaussian(FitBase):
    def __init__(self, x, y, yerr=None, **kwargs):
        """Gaussian data model"""
        super().__init__(x, y, yerr, **kwargs)

    def model(self, x, A, mu, sigma, c):
        if sigma < 0:
            return 0
        return A * norm.pdf(x, mu, sigma) + c

class TraceFourLevel(FitBase):
    def __init__(self, x, y, yerr=None,  **kwargs):
        """4 Level model trace

        An offset of -1 is correct for traces based on the difference
        of pumped and probed. An offset of 0 is correct for traces based
        on the ratio of pumped and probed. See my thesis for explanation.
        """
        super().__init__(x, y, yerr, **kwargs)

    def model(self, t, Amp, t1, t2, c, mu, sigma, offset):

        """Function for the time dependency of pump-probe sfg data.

        Function is derived by analytically solving the 4 level system and
        subsequent convolution with a gaussian excitation function of the
        model. Initial state is N0=1. All other states are empty.

        This exact implementation has a problem when t1==t2 exactly. Due to
        numerical constrains this must be avoided.

        If difference instead of ratio is used. The function keeps the same
        due to the distributivity of the convolution and the fact that gaussian
        convolved with -1 gives -1. Therefore only -1 needs to be subtract.

        **Arguments**:
        - **t**:  Array of Time values. Usually given by experiment.
        - **Amp**: Amplitude of the excitation pulse. Determines the fraction
                 of oscillators excited by the excitation pulse.
        - **t1**: Lifetime of the first excited vibrational state in units of
                  **t**
        - **t2**: Lifetime of the second excited vibrational state in units of
                  **t**
        - **c**: Scaling factor of final (heated) state. Used to account for
                 spectral differences induced by residual heat.
        - **mu**: Tempoaral position of pump pulse in units of **t**.
        - **sigma**: Temporal width of pump pulse in units of **t**.
        - **offset**: 0 for difference based traces and -1 for ration based traces
            The offset should be fixed to any of these two. However, if no zero line
            correction is performed, this number can be in between 0 and -1.

        **Returns**
        Modeled result as deduced from the 4 level system for the given array
        of **t** time values.

        """
        pi=np.pi;
        #a0 = erf((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/sigma))
        def mysqrt(x): return np.sqrt(x)
        aux0=sigma*((t1**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux1=sigma*((t1**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux2=sigma*((t1**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux3=(((t1-t2)**2))*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma)))));
        aux4=sigma*(t1*(t2*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma)))))));
        aux5=sigma*(t1*(t2*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma)))))));
        aux6=sigma*(t1*(t2*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma)))))));
        aux7=sigma*((t2**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux8=sigma*((t2**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux9=sigma*((t2**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)/\
        sigma))))));
        aux10=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux11=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*((t1**2)*(-1.+(erf(aux10))))));
        aux12=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux13=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux12)))))));
        aux14=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux15=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux14)))))));
        aux16=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux17=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux16))))));
        aux18=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux19=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux18))))));
        aux20=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux21=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux20)))))));
        aux22=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux23=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux22)))))));
        aux24=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux25=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux24))))));
        aux26=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux27=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux26)))))));
        aux28=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux29=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux28))))));
        aux30=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux31=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux30))))));
        aux32=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux33=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux32))))));
        aux34=(0.5*((sigma**2)*(t1**-2.)))+((mu/t1)+((0.5*((sigma**2)*(t2**-2.\
           )))+((mu/t2)+(((sigma**2)/t2)/t1))));
        aux35=(((2.**-0.5)*mu)/sigma)+((((2.**-0.5)*sigma)/t1)+(((2.**-0.5)*\
        sigma)/t2));
        aux36=(mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf((aux35-(((2.**-0.5)*t)/sigma))))))));
        aux37=(0.5*((sigma**2)*(t1**-2.)))+((mu/t1)+((0.5*((sigma**2)*(t2**-2.\
           )))+((mu/t2)+(((sigma**2)/t2)/t1))));
        aux38=(((2.**-0.5)*mu)/sigma)+((((2.**-0.5)*sigma)/t1)+(((2.**-0.5)*\
        sigma)/t2));
        aux39=(mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf((aux38-(((2.**-0.5)*t)/sigma)))))));
        aux40=(0.5*((sigma**2)*(t1**-2.)))+((mu/t1)+((0.5*((sigma**2)*(t2**-2.\
           )))+((mu/t2)+(((sigma**2)/t2)/t1))));
        aux41=(((2.**-0.5)*mu)/sigma)+((((2.**-0.5)*sigma)/t1)+(((2.**-0.5)*\
        sigma)/t2));
        aux42=(mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf((aux41-(((2.**-0.5)*t)/sigma)))))));
        aux43=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t2))-(((2.**-0.5)\
        *t)/sigma);
        aux44=(np.exp(((2.*((sigma**2)*(t2**-2.)))+(((2.*mu)/t2)+((-2.*t)/t2))\
           )))*((mysqrt((2.*pi)))*(sigma*((t2**2)*(-1.+(erf(aux43))))));
        aux45=t1*(t2*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t1))-(t*t1)))/t1)/\
        sigma))));
        aux46=(np.exp((0.5*((t1**-2.)*((sigma**2)+((2.*(mu*t1))+(-2.*(t*t1))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux45));
        aux47=t1*(t2*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t1))-(t*t1)))/t1)/\
        sigma))));
        aux48=(np.exp((0.5*((t1**-2.)*((sigma**2)+((2.*(mu*t1))+(-2.*(t*t1))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux47));
        aux49=(t2**2)*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t1))-(t*t1)))/t1)/\
        sigma)));
        aux50=(np.exp((0.5*((t1**-2.)*((sigma**2)+((2.*(mu*t1))+(-2.*(t*t1))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux49));
        aux51=t1*(t2*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t2))-(t*t2)))/t2)/\
        sigma))));
        aux52=(np.exp((0.5*((t2**-2.)*((sigma**2)+((2.*(mu*t2))+(-2.*(t*t2))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux51));
        aux53=(t2**2)*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t2))-(t*t2)))/t2)/\
        sigma)));
        aux54=(np.exp((0.5*((t2**-2.)*((sigma**2)+((2.*(mu*t2))+(-2.*(t*t2))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux53));
        aux55=(3.*(Amp*aux46))+((Amp*(c*aux48))+((-2.*(Amp*aux50))+((Amp*(c*\
        aux52))+(Amp*aux54))));
        aux56=(-2.*((Amp**2)*(c*((np.exp(((aux40-(t/t2))-(t/t1))))*aux42))))+(\
        ((Amp**2)*(c*aux44))+aux55);
        aux57=((Amp**2)*((c**2)*((np.exp(((aux34-(t/t2))-(t/t1))))*aux36)))+((\
        2.*((Amp**2)*((np.exp(((aux37-(t/t2))-(t/t1))))*aux39)))+aux56);
        aux58=((Amp**2)*aux29)+((-2.*((Amp**2)*(c*aux31)))+(((Amp**2)*((c**2)*\
        aux33))+aux57));
        aux59=(2.*((Amp**2)*(c*aux23)))+((-2.*((Amp**2)*aux25))+((2.*((Amp**2)\
        *(c*aux27)))+aux58));
        aux60=(-2.*((Amp**2)*aux17))+((2.*((Amp**2)*(c*aux19)))+((2.*((Amp**2)\
        *aux21))+aux59));
        aux61=((Amp**2)*((c**2)*aux11))+((3.*((Amp**2)*aux13))+((-2.*((Amp**2)\
        *(c*aux15)))+aux60));
        aux62=((Amp**2)*((c**2)*((mysqrt((0.5*pi)))*aux8)))+((Amp*(c*((\
        mysqrt((2.*pi)))*aux9)))+aux61);
        aux63=(2.*((Amp**2)*(c*((mysqrt((2.*pi)))*aux6))))+(((Amp**2)*((\
        mysqrt((0.5*pi)))*aux7))+aux62);
        aux64=(2.*(Amp*((mysqrt((2.*pi)))*aux4)))+((-2.*(Amp*(c*((mysqrt((\
        2.*pi)))*aux5))))+aux63);
        aux65=(Amp*(c*((mysqrt((2.*pi)))*aux2)))+(((mysqrt((0.5*pi)))*(\
        sigma*aux3))+aux64);
        aux66=((Amp**2)*((mysqrt((0.5*pi)))*aux0))+(((Amp**2)*((c**2)*((\
        mysqrt((0.5*pi)))*aux1)))+aux65);
        aux67=(t2**2)*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t2))-(t*t2)))/t2)/\
        sigma)));
        aux68=(np.exp((0.5*((t2**-2.)*((sigma**2)+((2.*(mu*t2))+(-2.*(t*t2))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux67));
        aux69=t1*(t2*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t2))-(t*t2)))/t2)/\
        sigma))));
        aux70=(np.exp((0.5*((t2**-2.)*((sigma**2)+((2.*(mu*t2))+(-2.*(t*t2))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux69));
        aux71=(t1**2)*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t1))-(t*t1)))/t1)/\
        sigma)));
        aux72=(np.exp((0.5*((t1**-2.)*((sigma**2)+((2.*(mu*t1))+(-2.*(t*t1))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux71));
        aux73=(t1**2)*(erfc(((((2.**-0.5)*(((sigma**2)+(mu*t1))-(t*t1)))/t1)/\
        sigma)));
        aux74=(np.exp((0.5*((t1**-2.)*((sigma**2)+((2.*(mu*t1))+(-2.*(t*t1))))\
           ))))*((mysqrt((2.*pi)))*(sigma*aux73));
        aux75=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t2))-(((2.**-0.5)\
        *t)/sigma);
        aux76=(np.exp(((2.*((sigma**2)*(t2**-2.)))+(((2.*mu)/t2)+((-2.*t)/t2))\
           )))*((mysqrt((0.5*pi)))*(sigma*((t2**2)*(-1.+(erf(aux75))))));
        aux77=((((aux66-(Amp*(c*aux68)))-(Amp*aux70))-(Amp*(c*aux72)))-(Amp*\
        aux74))-((Amp**2)*((c**2)*aux76));
        aux78=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t2))-(((2.**-0.5)\
        *t)/sigma);
        aux79=(np.exp(((2.*((sigma**2)*(t2**-2.)))+(((2.*mu)/t2)+((-2.*t)/t2))\
           )))*((mysqrt((0.5*pi)))*(sigma*((t2**2)*(-1.+(erf(aux78))))));
        aux80=(0.5*((sigma**2)*(t1**-2.)))+((mu/t1)+((0.5*((sigma**2)*(t2**-2.)))+((mu/t2)+(((sigma**2)/t2)/t1))));
        aux81=(((2.**-0.5)*mu)/sigma)+((((2.**-0.5)*sigma)/t1)+(((2.**-0.5)*\
        sigma)/t2));
        aux82=(mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf((aux81-(((2.**-0.5)*t)/sigma))))))));
        aux83=(aux77-((Amp**2)*aux79))-((Amp**2)*((np.exp(((aux80-(t/t2))-(t/\
        t1))))*aux82));
        aux84=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux85=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux84)))))));
        aux86=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t2))-(((2.**-0.5)*\
        t)/sigma);
        aux87=(np.exp((((0.5*((sigma**2)*(t2**-2.)))+(mu/t2))-(t/t2))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux86)))))));
        aux88=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux89=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((2.*pi)))*(sigma*((t1**2)*(-1.+(erf(aux88))))));
        aux90=((aux83-((Amp**2)*((c**2)*aux85)))-((Amp**2)*aux87))-((Amp**2)*(\
        c*aux89));
        aux91=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux92=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((0.5*pi)))*(sigma*((t1**2)*(-1.+(erf(aux91))))));
        aux93=((((2.**-0.5)*mu)/sigma)+(((mysqrt(2.))*sigma)/t1))-(((2.**-0.5)\
        *t)/sigma);
        aux94=(np.exp(((2.*((sigma**2)*(t1**-2.)))+(((2.*mu)/t1)+((-2.*t)/t1))\
           )))*((mysqrt((0.5*pi)))*(sigma*((t1**2)*(-1.+(erf(aux93))))));
        aux95=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux96=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*(t1*(t2*(-1.+(erf(aux95)))))));
        aux97=((aux90-((Amp**2)*((c**2)*aux92)))-((Amp**2)*aux94))-((Amp**2)*(\
        (c**2)*aux96));
        aux98=((((2.**-0.5)*mu)/sigma)+(((2.**-0.5)*sigma)/t1))-(((2.**-0.5)*\
        t)/sigma);
        aux99=(np.exp((((0.5*((sigma**2)*(t1**-2.)))+(mu/t1))-(t/t1))))*((\
        mysqrt((2.*pi)))*(sigma*((t1**2)*(-1.+(erf(aux98))))));
        aux100=sigma*((t2**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*\
        t)/sigma))))));
        aux101=sigma*((t2**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*\
        t)/sigma))))));
        aux102=((aux97-((Amp**2)*aux99))-((Amp**2)*(c*((mysqrt((2.*pi)))*\
        aux100))))-(Amp*((mysqrt((2.*pi)))*aux101));
        aux103=sigma*(t1*(t2*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)\
        /sigma)))))));
        aux104=sigma*(t1*(t2*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*t)\
        /sigma)))))));
        aux105=(aux102-((Amp**2)*((c**2)*((mysqrt((2.*pi)))*aux103))))-((\
        Amp**2)*((mysqrt((2.*pi)))*aux104));
        aux106=sigma*((t1**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*\
        t)/sigma))))));
        aux107=sigma*((t1**2)*(1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*\
        t)/sigma))))));
        aux108=(aux105-((Amp**2)*(c*((mysqrt((2.*pi)))*aux106))))-(Amp*((\
        mysqrt((2.*pi)))*aux107));
        aux109=(((t1-t2)**2))*(-1.-(erf(((((2.**-0.5)*mu)/sigma)-(((2.**-0.5)*\
        t)/sigma)))));
        aux110=((2.*pi)**-0.5)*(((t1-t2)**-2.)*(aux108-((mysqrt((0.5*pi)\
           ))*(sigma*aux109))));
        output=aux110/sigma + offset
        return output


class TraceExponential(FitBase):
    def __init__(self, x, y, yerr=None, **kwargs):
        """Single exponential trace model."""
        super().__init__(x, y, yerr, **kwargs)


    def model(self, t, A, t1, c, mu, ofs, sigma):
        """Result of a convolution of Gausian an exponential recovery.

        This function is the Analytically solution to the convolution of:
        f = (- A*exp(-t/tau) + c)*UnitStep(t)
        g = Gausian(t, mu, sigma)
        result = Convolve(f, g)

        **Arguments:**
          - **t**: array of times
          - **A**: Amplitude of the recovery
          - **t1**: Livetime of the recovery
          - **c**: Convergence of the recovery
          - **mu**: Tempoaral Position of the Pulse
          - **ofs**: Global offset factor
          - **sigma**: Width of the gaussian
        """

        ## This dtype hack is needed because the exp cant get very large.
        return 1/2 * (
            c + c * erf((t - mu)/(np.sqrt(2) * sigma)) -
            A * np.exp(((sigma**2 - 2 * t * t1 + 2 * mu * t1)/(2 * t1**2))) *
            erfc((sigma**2 - t * t1 + mu * t1)/(np.sqrt(2) * sigma * t1))
        ) + ofs
