#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import argparse
import pysfg
import logging
import yaml
from scipy.stats import sem


def run(config, config_path):
    logging.debug(config)
    # Read config
    intensity_data = config_path / Path(config['intensity_data'])
    intensity_selector = pysfg.SelectorPP(**config.get('intensity_selector', {}))
    intensity_filter = config.get('intensity_filter', None)
    drift_correction_params = config.get("drift_correction_params")
    background_data = config.get('background_data')
    background_selector = pysfg.SelectorPP(**config.get('background_selector', {}))
    background_selector.pixel = intensity_selector.pixel
    norm_data = config.get('norm_data')
    calibration_config = config.get('calibration', {})
    out = config_path / Path(config['out'])
    pump_freq = config.get('pump_freq')
    pump_width = config.get('pump_width')
    cc_width = config.get('cc_width')


    # Shape is unexpected if no spectrum is selected
    if intensity_selector.spectra == slice(None):
        intensity_selector.spectra = 0
    if background_selector.spectra == slice(None):
        background_selector.spectra = 0
    # Import Data and get its structure
    logging.info('****New Config****')
    logging.info('Importing: %s', intensity_data)
    logging.info('Using data_select is: %s', intensity_selector)
    intensity_data = pysfg.read.victor.data_file(intensity_data)
    intensity_data_selected = intensity_data['data'][intensity_selector.tselect]

    # background can be a path, number or None.
    if isinstance(background_data, str):
        background_data = pysfg.read.victor.data_file(config_path / Path(background_data))
        background_data_selected = background_data['data'][background_selector.tselect]
    elif background_data:
        background_data_selected = background_data * np.ones_like(intensity_data_selected)
    else:
        background_data_selected = np.zeros_like(intensity_data_selected)
    baseline = np.median(
        background_data_selected,
        axis=(1)
    )

    # Get calibration. Not passed vales are read from datafile.
    calibration = pysfg.Calibration(
        calibration_config.get('central_wl', intensity_data['central_wl']),
        calibration_config.get('vis_wl', intensity_data['vis_wl']),
        calibration_config.get('calib_central_wl', intensity_data['calib_central_wl']),
        calibration_config.get('calib_coeff', intensity_data['calib_coeff'])
    )
    logging.debug('Using Calibration with: %s', calibration)

    # Init filter_function to apply after median of data is calculated
    if intensity_filter:
        from scipy.ndimage import gaussian_filter1d
        gf_keywords = intensity_filter.get('gaussian_filter1d')
        if gf_keywords:
            logging.info('Use gaussian_filter1d with kwargs: %s', gf_keywords)
            filter_function = lambda x: gaussian_filter1d(x, **gf_keywords)

    # Apply drift correction must be applied to the scan axis. Thus before the
    # calculation if intensity from intensity_data_selected
    if not isinstance(drift_correction_params, type(None)):
        logging.info("Applying drift correction %s", drift_correction_params)
        intensity_data_selected = pysfg.filter.drift_correction(
            drift_correction_params, intensity_data_selected,
            np.mean(background_data_selected, axis=1, keepdims=True) * np.ones_like(intensity_data_selected)
        )

    intensity = np.median(
        intensity_data_selected,
        axis=(1)  # Takes the median of the scans
    )
    if intensity_filter:
        intensity = filter_function(intensity)

    intensityE = sem(
        intensity_data_selected,
        axis=(1)  # Estimate uncertainties from scans
    )

    if intensity_filter:
        baseline = filter_function(baseline)

    norm = None
    if norm_data:
        norm = pysfg.spectrum.json_to_spectrum(config_path / Path(norm_data)).basesubed
        if len(norm) != np.shape(intensity)[-1]:
            norm = norm[intensity_selector.pixel]

    spectrum = pysfg.spectrum.PumpProbe(
        intensity=intensity,
        baseline=baseline,
        norm=norm,
        wavenumber=calibration.wavenumber[intensity_selector.pixel],
        pp_delay=intensity_data['timedelay'],
        intensityE=intensityE,
        pixel=intensity_selector.pixel,
        pump_freq=pump_freq,
        pump_width=pump_width,
        cc_width=cc_width,
    )

    spectrum.to_json(out)


def main():
    parser = argparse.ArgumentParser(description='Compile normalization data.')
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
    pump_freq = config.get('pump_freq')
    pump_width = config.get('pump_width')
    cc_width = config.get('cc_width')
    for data_config in config['data']:
        # Combine local and global calibration parameters.
        data_config_calibration = dict(data_config.get('calibration', {}))
        data_config['calibration'] =  {**calibration_config, **data_config_calibration}
        data_config['pump_freq'] =  data_config.get('pump_freq', pump_freq)
        data_config['pump_width'] = data_config.get('pump_width', pump_width)
        data_config['cc_width'] =  data_config.get('cc_width', cc_width)
        run(data_config, config_path)


if __name__ == "__main__":
    main()
