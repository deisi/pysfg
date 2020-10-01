#!/usr/bin/env python3
"""
A script to analyse phaseresovled data.

One needs to pass a propper configuration.yaml file describing the properties
of the analysis to this script.
"""

# TODO: Nothing done yet

from pathlib import Path
import numpy as np
import pysfg
import yaml
import logging
import argparse
from scipy.stats import sem


def run(config, config_path):
    logging.debug(config)

    # Read config
    intensity_data = config_path / Path(config['intensity_data'])
    intensity_selector = pysfg.SelectorPP(**config.get('intensity_selector', {}))
    background_data = config.get('background_data')
    background_selector = pysfg.SelectorPP(**config.get('background_selector', {}))
    norm_data =  config.get('norm_data')
    calibration_config = config.get('calibration', {})
    out = config_path / Path(config['out'])

    # Shape is unexpected if no spectrum is selected
    if intensity_selector.spectra == slice(None):
        intensity_selector.spectra = 0
    if background_selector.spectra == slice(None):
        background_selector.spectra = 0

    # Import Data
    logging.info('Importing: %s' % intensity_data)
    if intensity_data.suffix == ".dat":
        intensity_data = pysfg.read.victor.data_file(intensity_data)
    elif intensity_data.suffix == ".spe":
        intensity_data = pysfg.read.spe.data_file(intensity_data)
    else:
        raise ValueError("Can't import %s with suffix %s" % (intensity_data, intensity_data.suffix))
    intensity_data_selected = intensity_data['data'][intensity_selector.tselect]
    logging.info('Using data_select is: \n%s' % intensity_selector)

    # This allows to pass norm as path to a norm spectrum in json format,
    # to leave it empty or to pass an array.
    if not isinstance(norm_data, type(None)):
        if isinstance(norm_data, str):
            norm_data = config_path / Path(norm_data)
            norm_data = pysfg.spectrum.json_to_spectrum(norm_data)
            norm_data = norm_data.basesubed
        try:
            norm_data * np.ones_like(intensity_data_selected)
        except ValueError:
            norm_data = norm_data[intensity_selector.pixel]
        norm_data = norm_data * np.ones_like(intensity_data_selected)
        norm_data = np.median(norm_data, axis=(0, 1))

    # This allows to pass background data as number or as path to data file, or to leave it empty
    if not isinstance(background_data, type(None)):
        if isinstance(background_data, str):
            background_data = config_path / Path(background_data)
            background_data = pysfg.read.victor.data_file(background_data)
            background_selector.pixel = intensity_selector.pixel
            background_data = background_data['data'][background_selector.tselect]
        else:
            background_data = background_data * np.ones_like(intensity_data_selected)
        background_data = np.median(background_data, axis=(0, 1))

    # For spe files use build in calibration
    wavelength = intensity_data.get('wavelength')
    if not isinstance(wavelength, type(None)):
        logging.info('Use wavelength of data file to calculate wavenumber.')
        wavenumber = pysfg.calibration.Calibration2(
            vis_wl=calibration_config['vis_wl'],
            wavelength=wavelength
        ).wavenumber[intensity_selector.pixel]
        if calibration_config.get('central_wl') or calibration_config.get('calib_central_wl') or calibration_config.get('calib_coeff'):
            raise NotImplementedError('Calibration not fully implemented for .spe files')
    else:
        calibration = pysfg.Calibration(
            calibration_config.get('central_wl', intensity_data['central_wl']),
            calibration_config.get('vis_wl', intensity_data['vis_wl']),
            calibration_config.get('calib_central_wl', intensity_data['calib_central_wl']),
            calibration_config.get('calib_coeff', intensity_data['calib_coeff'])
        )
        wavenumber = calibration.wavenumber[intensity_selector.pixel]
        logging.info('Using Calibration with: \n%s' % calibration)


    intensity = np.median(
        intensity_data_selected,
        axis=(0, 1)  # Median over pp_delay and scans
    )

    intensityE = sem(
        np.median(intensity_data_selected, axis=0),
        axis=(0)  # Median over pp_delay standard error of the mean over scans.
    )

    spectrum = pysfg.Spectrum(
        intensity=intensity,
        baseline=background_data,
        norm=norm_data,
        wavenumber=wavenumber,
        intensityE=intensityE,
        pixel=intensity_selector.pixel,
    )

    # Save results
    spectrum.to_json(out)


def main():
    parser = argparse.ArgumentParser(description='Analyse static sfg data.')
    parser.add_argument(
        'config',
        help='Path to a yaml configuration file.'
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

    fname = Path(args.config)
    config_path = fname.parent
    with open(fname) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        config = yaml.load(file, Loader=yaml.FullLoader)

    calibration_config = config.get(
        'calibration', {}
    )
    for data_config in config['data']:
        # Combine local and global calibration parameters.
        data_config_calibration = dict(data_config.get('calibration', {}))
        data_config['calibration'] = {**calibration_config, **data_config_calibration}
        run(data_config, config_path)


if __name__ == "__main__":
    main()
