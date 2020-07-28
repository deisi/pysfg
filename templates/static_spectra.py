#!/usr/bin/env python3

import numpy as np
import pysfg
import os
import matplotlib.pyplot as plt
import yaml
import logging
import argparse
from scipy.stats import sem

def make_spectrum(
        data,
        background_data=None,
        norm=None,
        data_select=pysfg.SelectorPP(spectra=0),
        background_select=pysfg.SelectorPP(spectra=0),
        calibration=None
):
    """Make Spectrum object from static SFG measurment.

    data: data dict. A 4D numpy array with the keyword 'data' is expected.
    background: data dict with background data. Same format as above.
    norm: pysfg.Spectrum, for normalization or array or integer
    data_select: pysfg.SelctorPP object.
    background_select: pysfg.SelectorPP object
    calibration: `pysfg.Calibration` object. if none given, the calibration
      is infered from the data. However this only works for victor data, as that
      is the only setup as of right now, that correctly exports all required information.

    Returns `pysfg.Spectrum` objecth
    """

    if not isinstance(data, dict):
        raise TypeError('data must be of type dict')
    try:
        data['data']
    except:
        raise ValueError("data dict must contain keyword 'data'")

    if not isinstance(norm, type(None)) and not isinstance(norm, pysfg.spectrum.Spectrum):
        raise TypeError('Cant use norm type of {}, {}'.format(type(norm), norm))

    # Handle various background data inputs
    if isinstance(background_data, dict):
        baseline = np.median(
            background_data['data'][background_select.select],
            axis=(0, 1)
        )
    elif isinstance(background_data, pysfg.Spectrum):
        baseline = background_data.intensity
    # Spectrum can handle the input or will fail
    else:
        baseline = background_data

    intensity = np.median(
        data['data'][data_select.select],
        axis=(0, 1) # Median over pp_delay and scans
    )

    intensityE = sem(
        np.median(data['data'][data_select.select], axis=0),
        axis=(0) # Median over pp_delay sem over scans.
    )

    if isinstance(calibration, type(None)):
        calibration = pysfg.Calibration(
            data['central_wl'], data['vis_wl'], data['calib_central_wl'], data['calib_coeff']
        )
    wavenumber = calibration.wavenumber[data_select.pixel]

    if isinstance(norm, pysfg.spectrum.Spectrum):
        if len(norm.basesubed) != len(intensity):
            norm = norm.basesubed[data_select.pixel]

    return pysfg.Spectrum(
        intensity=intensity,
        baseline=baseline,
        norm=norm,
        wavenumber=wavenumber,
        intensityE=intensityE,
        pixel=data_select.pixel,
    )

def run(config):
    """This is run per top level element of the config.yaml file."""
    logging.debug(config)
    intensity_data = config['intensity_data']
    fpath = os.path.split(intensity_data)[0]
    intensity_selector = pysfg.SelectorPP(**config.get('intensity_selector', {}))

    background_data = config['background_data']
    background_selector = pysfg.SelectorPP(**config.get('background_selector', {}))
    # Background and intensity must have same pixel count. Thus background is overwritten by intensity
    background_selector.pixel = intensity_selector.pixel

    norm_data = config.get('norm_data')
    if norm_data:
        norm_data = pysfg.spectrum.json_to_spectrum(norm_data)

    name = config['name']
    #TODO: Add pp_delay and scan selection

    # Import Data
    logging.info('Importing: '+ intensity_data)
    intensity_data = pysfg.read.victor.data_file(intensity_data)
    background_data = pysfg.read.victor.data_file(background_data)

    # Get calibration. Not passed vales are read from datafile.
    calibration_config = config.get('calibration', {})
    calibration = pysfg.Calibration(
        calibration_config.get('central_wl', intensity_data['central_wl']),
        calibration_config.get('vis_wl', intensity_data['vis_wl']),
        calibration_config.get('calib_central_wl', intensity_data['calib_central_wl']),
        calibration_config.get('calib_coeff', intensity_data['calib_coeff'])
    )

    logging.info('Using data_select is:\n{}'.format(intensity_selector))
    logging.info('Using Calibration with:\n{}'.format(calibration))

    # Make a general spectrum object
    spectrum = make_spectrum(
        data=intensity_data,
        background_data=background_data,
        norm=norm_data,
        data_select=intensity_selector,
        background_select=background_selector,
        calibration=calibration,
       )

    # Save results
    logging.info('Save as: ' + name)
    spectrum.to_json(name)


def main():
    parser = argparse.ArgumentParser(description='Compile normalization data.')
    parser.add_argument(
        'config',
        help='Path to a normalization.yaml configuration file.'
    )
    parser.add_argument(
        '--debug', default="INFO",
        help="Debug Level. Default INFO, Possible: DEBUG, INFO, WARN, ERROR, CRITICAL ",
    )
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=getattr(logging, args.debug))
    else:
        logging.basicConfig(level=logging.INFO)

    with open(args.config) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        config = yaml.load(file, Loader=yaml.FullLoader)

    calibration_config = config.get(
        'calibration', {}
    )
    for data_config in config['data']:
        # Combine local and global calibration parameters.
        data_config_calibration = dict(data_config.get('calibration', {}))
        data_config['calibration'] =  {**calibration_config, **data_config_calibration}
        run(data_config)


if __name__ == "__main__":
    main()
