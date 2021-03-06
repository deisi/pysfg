import setuptools

requirements = [
    'numpy',
    'matplotlib',
    'scipy',
    'pandas',
    'ipython',
    'iminuit',
    'pyaml',
    'xmltodict',
]

setuptools.setup(
     name='pysfg',
     version='0.2',
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
            "fit_trace = scripts.fit_trace:main",
            "psshg = scripts.psshg:main",
        ]
    },
    install_requires=requirements,
 )
