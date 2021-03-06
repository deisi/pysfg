"""Functions related to figures."""

import matplotlib.pyplot as plt
from pathlib import Path
import logging


def figures2pdf(fname, figures, close=False):
    """Save list of figures into a multipage pdf.

    **Arguments:**
      - **fname**: Name of the file to save to
      - ++figures**: List of figures to use
      - **close**: Close the figures after using
    """
    fname = Path(fname)
    figures = list(figures)
    close = bool(close)

    from matplotlib.backends.backend_pdf import PdfPages
    if fname.suffix != ".pdf":
        fname = fname.with_suffix(".pdf")

    logging.info('Saving to: %s' % fname)

    with PdfPages(fname) as pdf:
        for fig in figures:
            pdf.savefig(fig)
            if close:
                plt.close(fig)

def errorline(xdata, ydata, yerr, kwargs_plot=None, kwargs_filllines=None):
    """Function to  plot lines with surrounding error lines.

    **Arguments**
    - **xdata**: array of x data
    - **ydata**: array of ydata
    - **yerr**: array of yerr. Used as line boundaries

    **kwargs**:
    - **kwargs_plot**: keywords passed to plot of the data
    - **kwargs_fillines**: keywords passed to fillines plot that makes up
      the boundaries lines of the error plot.
    """
    if not kwargs_plot:
        kwargs_plot = {}
    if not kwargs_filllines:
        kwargs_filllines = {}
    lines = plt.plot(xdata, ydata, **kwargs_plot)
    ymin, ymax = ydata - yerr, ydata + yerr
    kwargs_filllines.setdefault('color', [line.get_color() for line in lines])
    kwargs_filllines.setdefault('alpha', 0.3)
    lines.append(plt.fill_between(xdata, ymin, ymax, **kwargs_filllines))
    return lines


