# pysfg

A toolkit to help analysing pump probe sfg data.

## Install

- Install Anaconda for python3 64Bit

- Setup automatic kernel generation
  example: `conda install nb_conda_kernels`

- Download code
  
  example: `git clone https://github.com/deisi/pysfg.git`

- Navigate to the folder where this `reademe.md` file is located
  
  example: `cd pysfg`

- Setup a conda environment
  example: `conda env create -f environment.yml`

- If you haven't set up the automatic kernel generation above you now need to do it manually with:
  
  - Activate the environment with:
    exmple: `conda activate sfg`
  - Add a kernel to the default jupyterlab environment
    example: `ipython kernel install --user --name=sfg`

## Folders

- `pysfg`
  
  Tha place of the backend code. This is where data classes, there input and output is defined.

- `scripts`
  
  A collection of user ready scripts. The scripts is what you as the user want to work with. Each script takes a specific `configuration.yaml` file as input and generates time results in the form of `.json` files. These `.json` files can then be used to further data processing.
  - `static_spectra.py`
    Script to help analyse static SFG data. I can be used to automatically averade frames, subtract the background and normalize to a reference.
  - `timescan.py`
    Script that deals with time stability of data. It basically looks at the integrated Intensity vs measurement time.
  - `bleach.py`
    Script to calculate the bleach of a pump-probe sfg measurement.
  - `trace.py`
    Uses the result of bleach to generate pump-probe traces.
  - `fit_trace.py`
    Uses the result of trace, to fit the trace with e.g. the nummerical solutioin of the four-level-model
  - `psshg.py`
    Script to analyse phase-resolve second harmonic data as produced by e.g. Merlin
- `tests`
  
  A folder with a bunch of unittests. Before codechanges are commited. One has to run: `python -m unittests discover -s tests` and pass all tests.

- `tutorial`
  
  This folder contains a tutorial in the form of a  [jupyter lab notebook](https://jupyterlab.readthedocs.io/en/stable/). The [tutorial/Tutorial.ipynb](https://github.com/deisi/pysfg/blob/master/tutorial/Tutorial.ipynb) notebook explains how to run and configure the scripts The `.yaml` files in tutorial can be seen as a reference implementation.

# Usage

Have a look at [./tutorial/Tutorial.ipynb](https://github.com/deisi/pysfg/blob/master/tutorial/Tutorial.ipynb), the configuration files in `tutorial` and maybe even browse through the `scripts`. This should give you an idear of how this should be used.
