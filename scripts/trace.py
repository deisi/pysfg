#!/usr/bin/env python3

from pathlib import Path
import argparse
import logging
import yaml
import pysfg
import numpy as np


def run(config):
    logging.debug(config)
    bleach_data = pysfg.spectrum.json_to_bleach(Path(config["bleach_data"]))
    traces_config = config.get('traces')
    for trace_config_block in traces_config:
        out = Path(trace_config_block['out'])
        pixel = slice(*trace_config_block.get('pixel', [None]))
        wavenumber = trace_config_block.get('wavenumber')
        if wavenumber:
            wavenumber = slice(*wavenumber)
            index = np.where((bleach_data.wavenumber>wavenumber.start)&(bleach_data.wavenumber<wavenumber.stop))[0]
            _p = bleach_data.pixel[index]
            pixel = slice(_p.min(), _p.max())
        trace = bleach_data.get_trace(pixel=pixel)
        logging.info('Saving to: {}'.format(out))
        trace.to_json(out)


def main():
    parser = argparse.ArgumentParser(description='Make Traces.')
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
