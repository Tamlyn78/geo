#! python3

"""Process data acquired from the Malvern Mastersizer 2000. The csv output contains lots of factor information with the numeric data towards the end. A common feature of the classes and modules is to split thse datasets into associate 'head' and 'data' subsets so that the numerical data can be processed independantly."""

from os.path import join
import datetime
import pandas as pd

from ...database.csv import MetaData
from .psa import PSD


def csv_to_df(*paths):
    """Load an exported Mastersizer 2000 csv into a pandas dataframe. Two headers exist and dates should be parsed. Multiple paths to csv files can be entered with the results being concatenated together."""
    get_df = lambda p: pd.read_csv(p, header = [0,1], parse_dates = [5,6])
    df = pd.concat([get_df(i) for i in paths])
    df.reset_index(drop=True, inplace=True)
    return(df)

def timestamp_to_day(Series):
    """Convert a timestamp type pandas series to YY-mm-dd format"""
    s = Series
    fmt = pd.to_datetime(s.dt.strftime('%Y-%m-%d'))
    return(fmt)


class MS2000(PSD):
    """Create an object from a row of Mastersizer 2000 CSV."""

    def __init__(self, data, metadata=pd.Series(dtype='float64'), replicates=None):
        """"""
        m, d = metadata, data
        if not m.empty:
            self._meta_to_self(m)
        self.ms2000 = data
        self.precision = 6
        self.ms2000_replicates = replicates
        self.replicates = [i.psd for i in replicates] if replicates else replicates

        mm, frequency = self._get_psd()
        self.psd = PSD(mm, frequency, self.precision, self.replicates)

    def _meta_to_self(self, meta):
        """Add metadata as attributes of the current object."""
        row = meta
        for i in meta.keys():
            v = getattr(row, i)
            k = i.replace('[4, 3] - ','').replace('[3, 2] - ','')
            k = k.replace('(0.1)','10').replace('(0.5)','50').replace('(0.9)','90')
            k = k.rstrip()
            k = k.replace(' ','_')
            k = k.lower()
            setattr(self, k, v)

    def _get_psd(self):
        """Return data as a dataframe of size limits and frequency"""
        df = self.ms2000.copy().reset_index()
        df['index'] = df['index'].astype('float') / 1000
        df.columns = ['mm', 'frequency']
        df['frequency'] = [round(i,6) for i in df['frequency']]
        df.dropna(inplace=True)
        return(df.mm, df.frequency)

    def clip_psd(self):
        """"""

    def get_date(self):
        """Return the analysis timestamp in a useful format."""
        print(self.analysis_date_and_time)


class MS2000CSV(MS2000):
    """"""
    def __init__(self, *paths):
        """Import a Mastersizer 2000 exported CSV and split into data and metadata."""
        df = self._load_csv(*paths)
        self.meta, self.data = self._split_df(df)
        self.idx = self.active = df.index

    def _load_csv(self, *paths):
        """"""
        df = csv_to_df(*paths)
        return(df)

    def _split_df(self, df):
        """Split the raw dataframe into separate data and metadata dataframes"""
        h2 = df.columns.get_level_values(1)
        hix, dix = [], []
        
        for n, i in enumerate(h2):
            try:
                float(i)
                dix += [n]
            except:
                hix += [n]
        
        h = df[df.columns[(hix)]]
        d = df[df.columns[(dix)]]
        h.columns = h.columns.droplevel(level = 1)
        d.columns = d.columns.droplevel(level = 0)
        return(h, d)

    def name_to_idx(self, name):
        """Return indices of a given sample name from the complete dataset."""
        sample_names = self.meta['Sample Name'].astype('str')
        idx = sample_names[sample_names==str(name)].index
        return(idx)

    def date_to_idx(self, date):
        """Return indices of given sample date from the complete dataset."""
        m = self.meta['Measurement date and time']
        df = pd.to_datetime(m).dt.date
        date = pd.to_datetime(date)
        idx = df[df==date].index
        return(idx)

    def uid_to_idx(self, name, date):
        """Return indices of given sample name and date from the complete dataset."""
        names = self.name_to_idx(name)
        dates = self.date_to_idx(date)
        idx = names[names.isin(dates)]
        return(idx)

    def set_active(self, indices):
        """Set the active indices."""
        a = self.idx
        a = a[a.isin(indices)]
        self.active = a

    def idx_to_ms2(self, idx):
        """Return an MS2000 object from a single index name."""
        m, d = self.meta.loc[idx], self.data.loc[idx]
        tp = pd.Series
        if type(m)!=tp or type(d)!=tp:
            raise TypeError('Input must be a single value.')
        ms2 = MS2000(d, m)
        return(ms2)

    def replicates(self, name, date=None):
        """Return a set of replicate ms2 objects."""
        if date:
            idx = self.uid_to_idx(name, date)
        else:
            idx = self.name_to_idx(name)
        reps = [self.idx_to_ms2(i) for i in idx]
        return(reps)

    def mean(self, name, date=None):
        """Return the mean and replicates as an MS2000 object."""
        reps = self.replicates(name, date=date)
        data = [i.ms2000 for i in reps]
        mean = sum(data) / len(data)
        ms2 = MS2000(mean, replicates=reps)
        return(ms2)






    def get_size_limits(self, idx=None):
        """Return the maximum and minimum size values for the entire dataset, for standardised plotting purposes."""
        dt = self.data.loc[self.active]
        d = dt.loc[idx].copy() if idx else dt.copy()
        mean = d.sum() / d.shape[0]
        cumsum = mean.cumsum()
        c = cumsum
        lead = c[c==0].index.to_list()
        if len(lead) > 0:
            lead = lead[:-1]
        trail = c[c==c.loc[c.index[-1]]].index.to_list() 
        if len(trail) > 1:
            trail = trail[1:]
        idx = [i for i in c.index if i not in lead + trail]
        return(idx[0], idx[-1])

    def get_freq_limits(self):
        """Return the maximum frequency of the dataset."""
        d = self.data.loc[self.active].copy()
        d.dropna(axis=1, inplace=True)
        flat = d.values.flatten()
        mn = flat.min().round(6)
        mx = flat.max().round(6)
        lim = (mn, mx)
        return(lim)

    def active_from_date(self, date):
        """Set active idxs' from a date.
            Attributes:
                date <datetime.datetime>: A date in datetime format.        
        """
        idx = self.date_to_idx(date, active=False)
        self.active = idx

    def get_datetimes(self, fmt=None):
        """Return the 'Analysis date and time' field. Format if needed using standard format syntax (e.g. '%Y%m%d')"""
        dt = self.meta['Analysis date and time'].dt.strftime(fmt)
        return(dt)

    def get_dates(self):
        """Return a list of datetimes representing the Mastersizer 2000 'Analysis date and time' field."""
        dt = self.get_datetimes('%Y%m%d')
        dates = [pd.to_datetime(i) for i in dt.unique()]
        return(dates)

    def dt_to_date(self, dt):
        """Convert a datetime to '%Y%m%d' format."""
        date = dt.date()
        return(date)

    def get_uid(self, dataframe=False):
        """Return a dateframe of replicate group unique identifiers. The returned dataframe includes the fields 'Sample Name', and 'Analysis date and time' in '%Y%m%d' format. The returned dataframe can be converted to a list of tuples for input into the 'SampleMetaData' class."""
        df = self.meta[['Sample Name', 'Analysis date and time']].loc[self.active].copy()
        df['Analysis date and time'] = df['Analysis date and time'].apply(self.dt_to_date)
        df.sort_values(by=['Analysis date and time', 'Sample Name'], inplace=True)
        df.drop_duplicates(inplace=True, ignore_index=True)
        if dataframe:
            return(df)
        else:
            lst = df.to_records(index=False).tolist()
            return(lst)


class MS2000Collection(MetaData, MS2000CSV):
    """Load Mastersizer2000 CSV files and create a metadata file for custom analyses. """

    def __init__(self, folder, *paths, filename='metadata.csv', groups=None):
        """
            Attributes:
                datdir <str>: A filesystem path to the folder to place the output csv;
                filename <str>: Name of a CSV file containing, or to contain, segment coordinate data;
                uid <list of tuples>: A list of tuples representing the unique identifiers of sample names and dates, corresponding to Mastersizer 2000 data.
                columns <list>: List of field names to override the default.
        """

        self.metadata_csv = join(folder, filename)

        MetaData.__init__(self, self.metadata_csv, self._columns(groups))
        self.metadata['date'] = pd.to_datetime(self.metadata['date'])

        ms2000 = MS2000CSV.__init__(self, *paths)

        if self.metadata_is_empty():
            uid = self.get_uid()
            self.append(uid)
            print('WARNING: No metadata exists.')

    def _columns(self, groups):
        """Return a list of column names."""
        lst = [
            'id', # unique integer identifier
            'sample_name', # unique name of sample
            'date', # date of sample analysis ('%Y%m%d')
        ]
        lst = lst + groups if groups else lst
        lst += ['note']
        return(lst)

    def get_psd(self, metarow):
        """Get a mean PSD object from metadata, and add metadata as attributes."""
        m = metarow
        name = m.sample_name
        dt = pd.to_datetime(m.date)
        mean = self.mean(name, date=dt)
        for i in m.keys():
            setattr(mean, i, getattr(m, i))
        return(mean)

    def to_dict(self):
        """Load each distribution and assign to a dictionary of Mastersizer 2000 objects with the metadata ids' as keys."""
        d = dict([(i.id, self.get_psd(i)) for n, i in self.metadata.iterrows()])
        self.dict = d

    def folk_and_ward(self, mm=True, meta=True):
        """Return a dictionary of folk and ward statistics. Disable appending metadata if required."""
        try:
            d = self.dict
        except:
            d = self.to_dict()
        keys = [i for i in d.keys()]
        keys.sort()
        fw = [d[i].psd.folk_and_ward for i in keys]
        stats = [i.stats_to_dict(mm=mm) for i in fw]
        dicts = [{**{'id':k},**s} for k, s in zip(keys, stats)]
        df = pd.DataFrame(dicts)
        if meta:
            df = self.metadata.merge(df, on='id')
        stat_to_text = fw[0].stat_to_text
        dic = {
            'stats':df,
            'stat_to_text':stat_to_text,
        }
        return(dic) 
        
        
class SampleMetaData(MetaData):
    """Create a csv to establish groups of samples."""

    def __init__(self, folder, filename='metadata.csv', uid=None, columns=None, groups=None):
        """
            Attributes:
                datdir <str>: A filesystem path to the folder to place the output csv;
                filename <str>: Name of a CSV file containing, or to contain, segment coordinate data;
                uid <list of tuples>: A list of tuples representing the unique identifiers of sample names and dates, corresponding to Mastersizer 2000 data.
                columns <list>: List of field names to override the default.
        """

        self.csv_path = join(folder, filename)

        MetaData.__init__(self, self.csv_path, self._columns(columns, groups))
        self.metadata['date'] = pd.to_datetime(self.metadata['date'])

        if self.metadata_is_empty():
            if type(uid) != None:
                self.append(uid)
            print('WARNING: No metadata exists.')

    def _columns(self, columns, groups):
        """Return a list of column names."""
        lst = [
            'id', # unique integer identifier
            'sample_name', # unique name of sample
            'date', # date of sample analysis ('%Y%m%d')
        ]
        lst = lst + groups if groups else lst
        lst += ['note']
        c = columns if columns else lst
        return(c)

   
