#!/usr/bin/env python
"""Runn all unittests in this folder"""

import os
import unittest
from pathlib import Path

path = os.path.abspath(__file__)
dir_path = Path(os.path.dirname(path))

loader = unittest.TestLoader()
tests = loader.discover(dir_path)
testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
