import setuptools
from glob import glob


requirements = [
    'numpy',
    'matplotlib',
    'scipy',
    'pandas',
    'ipython',
    'iminuit',
    'pyaml',
]

setuptools.setup(
     name='pysfg',
     version='0.1',
     author="Malte Deiseroth",
     author_email="deiseroth@mpip-mainz.mpg.de",
     description="A Package to import and analyse SFG data.",
     url="https://github.com/deisi/pysfg",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    entry_points={
        'console_scripts': [
            "static_spectra = scripts.static_spectra:main",
            "timescan = scripts.timescan:main",
            "bleach = scripts.bleach:main",
            "trace = scripts.trace:main",
            "fit_trace = scripts.fit_trace:main"
        ]
    },
    install_requires=requirements,
 )
