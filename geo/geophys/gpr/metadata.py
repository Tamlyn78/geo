
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
    def __init__(self, rdir, name, columns):
        self.csv = csv = join(rdir, name + '.csv')
        self.name = name
        cols = self._columns(columns)
        if not isfile(csv):
            df = pd.DataFrame(columns=cols)
            self.write(df)

    def _columns(self, columns):
        """Add an 'id' and 'note' field as standard to the list of column names."""
        c = ['id'] + columns + [self.name + '_note']
        return(c)        

    def write(self, df):
        """"""
        df.to_csv(self.csv, index=False)

    def read(self):
        """"""
        df = pd.read_csv(self.csv)
        return(df)

    def if_empty(self, bf=None):
        df = self.read()
        if df.empty:
            df['id'] = bf['id']
            self.write(df)


