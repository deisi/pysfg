#!/usr/bin/env python3

import numpy as np
import pysfg
import os
import matplotlib.pyplot as plt
import yaml
import logging
import argparse

def run(config):
    """This is run per top level element of the config.yaml file."""
    logging.debug(config)
    intensity_data = config['intensity_data']
    fpath = os.path.split(intensity_data)[0]
    intensity_spectrum_index = config['intensity_spectrum_index']
    background_data = config['background_data']
    background_spectrum_index = config['background_spectrum_index']
    pixel = config.get('pixel', slice(None))
    name = config['name']
    #TODO: Add pp_delay and scan selection

    # Import Data
    logging.info('Importing: '+ intensity_data)
    intensity_data = pysfg.read.victor.data_file(intensity_data)
    background_data = pysfg.read.victor.data_file(background_data)

    # Get calibration
    calibration_config = config['calibration']
    calibration = pysfg.Calibration(
        calibration_config.get('central_wl', intensity_data['central_wl']),
        calibration_config.get('vis_wl', intensity_data['vis_wl']),
        calibration_config.get('calib_central_wl', intensity_data['calib_central_wl']),
        calibration_config.get('calib_coeff', intensity_data['calib_coeff'])
    )

    # Make a general spectrum object
    spectrum = pysfg.experiments.spectrum(
        data=intensity_data,
        background_data=background_data,
        data_select=pysfg.SelectorPP(spectra=intensity_spectrum_index, pixel=pixel),
        background_select=pysfg.SelectorPP(spectra=background_spectrum_index, pixel=pixel),
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
