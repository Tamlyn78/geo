"""Map field coordinates"""


class MetaData:
    """A parent class to create a csv for metadata logging and loading. The attributes of the metadata are defined by the child class.
        Attributes:
            path <str>: A filesystem path to the required csv location;
            cols <list>: A list of strings representing the header columns of 
                the csv.
    """
    def __init__(self, path, cols):
        """Create a csv if not exists and load a dataframe"""
        self._create_csv(path, cols)
        self.df = self._get_dataframe(path, cols)
        self.path = path

    def _create_csv(self, path, cols):
        """Create a CSV in the specified path."""
        try:
            with open(path, 'x', newline='') as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow([i for i in cols.keys()])
        except Exception as e:
            print(e)

    def _get_dataframe(self, path, cols):
        """Return a pandas dataframe."""
        df = pd.read_csv(path, dtype=cols)
        return(df)

class Mapping(MetaData):
    """"""
    def __init__(self, path):
        """Return a pandas dataframe of a csv containing the terminal Cartesian coordinates of each GPR line.
    CSV fields:
        id <int>: a unique row identifier for each GPR line record;
        """
        MetaData.__init__(self, path, self._columns())

    def _columns(self):
        """Return a list of attribute fields"""
        d = {
            'id':int, 
            'grid_id':str, 
            'x':float, 
            'y':float, 
            'note':str,
        }
        return(d)

    def metadata(self, rdir):
        """Return a row of metadata dataframe as a series with a path field"""
        df = self.df
        if rdir:
            d = lambda x: str(x[1].folder)
            f = lambda x: str(x[1].filename)
            df['path'] = [join(rdir, d(i), f(i)) for i in df.iterrows()]
        s = [i[1] for i in df.iterrows()]
        return(s)
 
