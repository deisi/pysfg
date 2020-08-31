#!/usr/bin/env python3

import argparse
import logging
import yaml
import pysfg
import numpy as np


def run(config):
    logging.debug(config)
    # Read config
    pumped_data = pysfg.spectrum.json_to_pumpprobe(config["pumped_data"])
    probed_data = pysfg.spectrum.json_to_pumpprobe(config["probed_data"])
    mode = config.get('mode', 'difference')
    static_difference_correction = config.get('static_difference_correction', False)
    heat_correction = config.get('heat_correction', False)
    name = config['name']

    # This generates a `pysfg.Bleach` object.
    if mode == "difference":
        logging.info('Run difference mode')
        bleach = probed_data - pumped_data
    elif mode == "ratio":
        logging.info('Run ratio mode')
        # By removing 1 here, the subsequent heat and static_difference_corrections work
        # correctly. At the end. we add the 1 again.
        bleach = probed_data / pumped_data 
        bleach.normalized -= 1
    else:
        raise ValueError('Cant understand given mode')

    if static_difference_correction:
        logging.info('Running static difference correction')
        # This corrects for static differences between pumped and unpumped
        bleach.normalized = bleach.normalized-bleach.normalized[0]


    if heat_correction:
        kwargs = heat_correction
        logging.info('Running heat correction with: {}'.format(kwargs))
        # Heat correction
        bleach.normalized = pysfg.filter.heat_filter(bleach.normalized, bleach.pp_delay, **kwargs)

    if mode == "ratio":
        bleach.normalized += 1
    # Save bleach in cache folder
    logging.info('Saving to: {}'.format(name))
    bleach.to_json(name)


def main():
    parser = argparse.ArgumentParser(description='Make Bleach.')
    parser.add_argument(
        'config',
        help='Path to a config.yaml configuration file.'
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

    for data_config in config['data']:
        run(data_config)


if __name__ == "__main__":
    main()
