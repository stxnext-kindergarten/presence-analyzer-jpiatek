"""config file"""
import os.path

MAIN_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', 'runtime', 'data', 'sample_data.csv'
)

MAIN_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', 'runtime', 'data', 'sample_data.xml'
)

DEBUG = True
DATA_CSV = MAIN_DATA_CSV
DATA_XML = MAIN_DATA_XML
