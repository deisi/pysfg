import os
import pysfg


data_path = os.path.dirname(__file__) + '/data/'
all_data = pysfg.read.victor.folder(data_path)
