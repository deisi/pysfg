#!/usr/bin/env python3
"""Deal with the Phaseresolved SHG setup data."""


from pathlib import Path
import numpy as np
import pysfg
import yaml
import logging
import argparse
from scipy.stats import sem

def run(config, config_path):
    """The run loop"""
    logging.debug(config)

    pixel_slice = slice(*config.get('pixel_slice'))
    background_data = config_path / Path(config.get('background_data'))
    interference_data = config_path / Path(config['interference_data'])
    local_oszillator_data = config_path / Path(config['local_oszillator_data'])
    sample_shg_data = config_path / Path(config['sample_shg_data'])
    background_offset = config.get('background_offset', {})
    mask = config.get('mask')
    out = config_path / Path(config['out'])

    if mask:
        mask = slice(*mask)

    background_data = pysfg.read.spe.data_file(background_data)
    wavelength = background_data['wavelength'][pixel_slice]
    background_data = np.median(background_data['raw_data'], [0, 1])[pixel_slice]
    interference_data = pysfg.read.spe.data_file(interference_data)
    interference_data = np.median(interference_data['raw_data'], [0, 1])[pixel_slice] - background_data + background_offset.get('interference', 0)
    local_oszillator_data = pysfg.read.spe.data_file(local_oszillator_data)
    local_oszillator_data = np.median(local_oszillator_data['raw_data'], [0, 1])[pixel_slice] - background_data + background_offset.get('local_oszillator', 0)
    sample_shg_data = pysfg.read.spe.data_file(sample_shg_data)
    sample_shg_data = np.median(sample_shg_data['raw_data'], [0, 1])[pixel_slice] - background_data + background_offset.get('sample_shg', 0)

    # correct for LO and Sample SHG contributions
    spectrum = pysfg.spectrum.PSSHG(
        interference_data, local_oszillator_data, sample_shg_data, wavelength, mask=mask
    )
    spectrum.to_json(out)


def main():
    """main function taking care of user input and running main loop."""
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
