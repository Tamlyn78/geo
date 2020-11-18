
from os.path import isfile, join
from collections import OrderedDict
import pandas as pd


class MetaData:
    """A base class to create a csv for metadata logging and loading. The attributes of the metadata are defined by the child class.
        Attributes:
            path <str>: A filesystem path to the required csv location;
            cols <list>: A list of strings representing the header columns of 
                the csv.
    """
    def __init__(self, name='metadata'):
        """Create a metadata attribute."""
        setattr(self, name, OrderedDict())

    def meta_to_csv(self, path, cols):
        """Create a dataframe and export to csv."""
        df = pd.DataFrame(columns=cols)
        if not isfile(path):
            df.to_csv(path, index=False)
        
    def columns_to_meta(self, cols, path):
        """Append columns of an input dataframe to the metadata and export to csv.
            Attributes:
                df <pandas.DataFrame>: A dataframe to append.
                filename <str>: A filesystem path to the target CSV.
        """
        m = pd.read_csv(path)
        if m.empty:
            try:
                for i in cols.columns:
                    m[i] = cols[i]
            except:
                m[cols.name] = cols
            m.to_csv(path, index=False)

    def meta_to_df(self, path):
        """Return a pandas dataframe. Improvements might include specification of data type."""
        df = pd.read_csv(path)
        return(df)



