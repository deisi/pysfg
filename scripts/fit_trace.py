#!/usr/bin/env python

from pathlib import Path
import argparse
import logging
import yaml
import pysfg
import numpy as np
import IPython.display as ipd


def run(config, config_path):
    logging.debug(config)
    fpath = config_path / Path(config['trace_data'])
    roi = slice(*config.get('roi', [None]))
    roi_pp_delay = config.get('roi_pp_delay')
    pp_delay_scale = config.get('pp_delay_scale', 1)
    bleach_scale = config.get('bleach_scale', 1)
    out = config_path / Path(config['out'])
    kwargs = config.get('kwargs', {})
    tr = pysfg.json_to_trace(fpath)
    logging.info('Running %s' % fpath)

    if roi_pp_delay:
        roi_pp_delay = slice(*roi_pp_delay)
        index = np.where((tr.pp_delay>roi_pp_delay.start)&(tr.pp_delay<roi_pp_delay.stop))[0]
        _p = tr.pp_delay[index]
        roi = slice(_p.min(), _p.max())

    fit = pysfg.fit.TraceFourLevel(
        x=tr.pp_delay[roi]*pp_delay_scale, # To get from fs to ps
        y=tr.bleach[roi]*bleach_scale, # Scale by 10 to have numbers closer to 1
        yerr=tr.bleachE[roi]*bleach_scale,
        **kwargs,
    )
    ipd.display(fit.minuit.migrad())
    #ipd.display(fit.minuit.hesse())
    #print(fit.minuit.values)
    #print(fit.minuit.accurate)
    #print(fit.minuit.np_covariance())
    fit.to_json(out)
    return fit

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

    fname = Path(args.config)
    config_path = fname.parent
    with open(args.config) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python in the dictionary format
        config = yaml.load(file, Loader=yaml.FullLoader)

    for data_config in config['data']:
        run(data_config, config_path)


if __name__ == "__main__":
    main()
