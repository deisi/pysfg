# pysfg

A toolkit to help analysing pump probe sfg data.

## Install

- Install Anaconda for python3 64Bit

- Setup automatic kernel generation
  `conda install nb_conda_kernels`

- Download code
  
   `git clone https://github.com/deisi/pysfg.git`

- Navigate to the folder where this `reademe.md` file is located
  
   `cd pysfg`

- Setup a conda environment with:
  `conda env create -f environment.yml`

- If you haven't set up the automatic kernel generation above you now need to do it manually with:
  
  - Activate the environment with:
    `conda activate sfg`
  - Add a kernel to the default jupyterlab environment
    `ipython kernel install --user --name=sfg`

## Structure

The package has two parts. Within the `./pysfg` folder you find the under the hood code of the module. If you want it is the backend of the whole thing. Within the `./tests` folder you find some test functions but they need to be rewritten, so don't bother about this right now. The `./scripts` folder contains a few set of stand alone scripts, that use the code of `pysfg` to automate common analysis steps we do after a pump probe experiment.  Within the`./tutorial` folder, there are some example configurations for the scripts of the `./scripts` folder and specifically the the `Tutorial.ipynb` tries to show how to use the scripts and how to configure them.

# Usage

Have a look at [./tutorial/Tutorial.ipynb](https://github.com/deisi/pysfg/blob/master/tutorial/Tutorial.ipynb).
