# pysfg
Second attempt in getting a useful python library for our SFG setups.

## Install
- Install Anaconda for python3 64Bit
- Setup a conda environment with:
  `conda env create -f environment.yml`
- Activate the environment with:
  `conda activate sfg`
- Install this library in editable mode.
  `pip install --editable .`
- Add a kernel to the default jupyterlab environment
  `ipython kernel install --user --name=sfg`
  
# Usage
## Read Data
``` python
import numpy as np
import pysfg

fpath = '00_sc_quartz_ssp_e10s_gal0.dat'
data = pysfg.read_victor(fpath)
# A dictionary with metadata and file data
data

# The raw file data
data['raw_data']

# Structured version of the data
data['data']

# The shape of the strcutured data is:
np.shape(data['data'])
(number_of_ppdelays, number_of_frames/scans, number_of_spectra, number_of_pixel)

# Import all data from a folder
data = pysfg.read_folder('./')

# Data is a dict of dicts.
# Keys are the data file paths.
# Values is a data return dict
data.keys()

```

