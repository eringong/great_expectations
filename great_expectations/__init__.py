import pandas as pd


from .util import *
from great_expectations import dataset

from pkg_resources import get_distribution
try:
    __version__ = get_distribution('great_expectations').version
except:
    pass

def list_sources():
    raise NotImplementedError

def connect_to_datasource():
    raise NotImplementedError

def connect_to_dataset():
    raise NotImplementedError

def read_csv(
    filename,
    dataset_class=dataset.pandas_dataset.PandasDataSet,
    expectations_config=None,
    *args, **kwargs
):
    df = pd.read_csv(filename, *args, **kwargs)
    df.__class__ = dataset_class
    df.initialize_expectations(expectations_config)

    return df

def df(df, dataset_config=None, *args, **kwargs):
    df.__class__ = dataset.pandas_dataset.PandasDataSet
    df.initialize_expectations(dataset_config)

    return df

def expect(data_source_str, expectation):
    raise NotImplementedError
