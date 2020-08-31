#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import argparse
import pysfg
import logging
import yaml
from scipy.stats import sem

def run(config):
    logging.debug(config)
    # Read config
    intensity_data = Path(config['intensity_data'])
    intensity_selector = pysfg.SelectorPP(**config.get('intensity_selector', {}))
    intensity_filter = config.get('intensity_filter', None)
    background_data = Path(config['background_data'])
    background_selector = pysfg.SelectorPP(**config.get('background_selector', {}))
    background_selector.pixel = intensity_selector.pixel
    norm_data = config.get('norm_data')
    calibration_config = config.get('calibration', {})
    out = Path(config['out'])
    drift_correction_params = config.get('drift_correction_params')
    pump_freq=config.get('pump_freq')
    pump_width=config.get('pump_width')
    cc_width=config.get('cc_width')

    # Import Data
    logging.info('Importing: {}'.format(intensity_data))
    intensity_data = pysfg.read.victor.data_file(intensity_data)
    background_data = pysfg.read.victor.data_file(background_data)

    # Get calibration. Not passed vales are read from datafile.
    calibration = pysfg.Calibration(
        calibration_config.get('central_wl', intensity_data['central_wl']),
        calibration_config.get('vis_wl', intensity_data['vis_wl']),
        calibration_config.get('calib_central_wl', intensity_data['calib_central_wl']),
        calibration_config.get('calib_coeff', intensity_data['calib_coeff'])
    )
    
    # Setup filter.
    if intensity_filter:
        from scipy.ndimage import gaussian_filter1d
        gf_keywords = intensity_filter.get('gaussian_filter1d')
        if gf_keywords:
            logging.info('Use gaussian_filter1d with kwargs:{}'.format(gf_keywords))
            filter_function = lambda x: gaussian_filter1d(x, **gf_keywords)

    logging.info('Using data_select is:\n{}'.format(intensity_selector))
    logging.info('Using Calibration with:\n{}'.format(calibration))

    intensity = np.median(
        intensity_data['data'][intensity_selector.tselect],
        axis=(1) # Takes the median of the scans
    )
    if intensity_filter:
        intensity = filter_function(intensity)

    intensityE = sem(
        intensity_data['data'][intensity_selector.tselect],
        axis=(1) # Estimate uncertainties from scans
    )

    baseline = np.median(
        background_data['data'][background_selector.tselect],
        axis=(1)
    )
    if intensity_filter:
        baseline = filter_function(baseline)

    norm = None
    if norm_data:
        norm = pysfg.spectrum.json_to_spectrum(Path(norm_data)).basesubed
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

    logging.info('Saving to: {}'.format(out))
    #TODO: This currently doesnt save pump_width, pump_freq and cc_width
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

    with open(args.config) as file:
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
        run(data_config)


if __name__ == "__main__":
    main()