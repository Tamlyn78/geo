#! python3

"""Process data acquired from the Malvern Mastersizer 2000. The csv output contains lots of factor information with the numeric data towards the end. A common feature of the classes and modules is to split thse datasets into associate 'head' and 'data' subsets so that the numerical data can be processed independantly."""

import os
from os.path import join
import sys
import numpy as np
import pandas as pd

from ..database.csv import MetaData
from .psa import Test as PSA


def csv_to_df(path):
    """Load an exported Mastersizer 2000 csv into a pandas dataframe. Two headers exist and dates should be parsed."""
    df = pd.read_csv(path, header = [0,1], parse_dates = [5,6])
    return(df)


class MS2000(PSA):
    """Create an object from a row of Mastersizer 2000 CSV."""
    def __init__(self, row):
        """"""
        m, d = self._split_row(row)
        self._meta_to_self(m)
        self.dist = self._get_distribution(d)
        self.precision = 6

    def _split_row(self, row):
        """Return the metadata from a row."""
        h2 = row.index.get_level_values(1)
        hix, dix = [], []
        
        for n, i in enumerate(h2):
            try:
                float(i)
                dix += [n]
            except:
                hix += [n]
        
        h = row[row.index[(hix)]]
        d = row[row.index[(dix)]]
        h.index = h.index.droplevel(1)
        d.index = d.index.droplevel(0)
        return(h, d)

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

    def _get_distribution(self, dat):
        """Return data as a dataframe of size limits and frequency"""
        df = dat.reset_index()
        df['index'] = df['index'].astype('float') / 1000
        df.columns = ['mm', 'frequency']
        df['frequency'] = [round(i,6) for i in df['frequency']]
        df.dropna(inplace=True)
        return(df)
        



class CSV(MS2000):
    """"""
    def __init__(self, path):
        """Import a Mastersizer 2000 exported CSV and split into data and metadata."""
        df = self._load_csv(path)
        self.df = df

    def _load_csv(self, path):
        """"""
        df = csv_to_df(path)
        return(df)

    def _splitdf(self, df):
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

    def idx_from_sample_name(self, name):
        """Return a row from """

    def idx_to_object(self, idx):
        """Return an MS2000 object from an idx"""
        ms2 = MS2000(self.df.iloc[idx])
        return(ms2)







class Wee:

    def row_to_object(self, idx):
        """Convert a row of Mastersizer 2000 metadata to an object."""
        ms2 = type('MS2000', (PSA,), {})()
        row = self.metadata.iloc[idx]
        for i in row.keys():
            v = getattr(row, i)
            k = i.replace('[4, 3] - ','').replace('[3, 2] - ','')
            k = k.replace('(0.1)','10').replace('(0.5)','50').replace('(0.9)','90')
            k = k.rstrip()
            k = k.replace(' ','_')
            k = k.lower()
            setattr(ms2, k, v)
        df = pd.DataFrame(self.data.iloc[idx]).reset_index()
        df.columns = ['um', 'frequency']
        df.dropna(inplace=True)
        setattr(ms2, 'distribution', df)
        return(ms2)





    def sample_names(self):
        """Return unique sample names."""
        names = self.meta['Sample Name'].unique().tolist()
        return(names)

    def subset_metadata(self, df):
        """Define the metadata to process by a subsetted pandas dataframe. The pandas dataframe should be subsetted externally as required."""
        self.metadata = df.copy()
        print(df)



class MasterSizer2000(PSA):
    def __init__(self, df):
        """Useful operations for mastersizer 2000 data"""
        self.original_metadata, self.data = self._splitdf(df)
        self.metadata = self.original_metadata.copy()
        self.psa = [self.row_to_object(i) for i in self.metadata.index]
        
    def _splitdf(self, df):
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

    def row_to_object(self, idx):
        """Convert a row of Mastersizer 2000 metadata to an object."""
        ms2 = type('MS2000', (PSA,), {})()
        row = self.metadata.iloc[idx]
        for i in row.keys():
            v = getattr(row, i)
            k = i.replace('[4, 3] - ','').replace('[3, 2] - ','')
            k = k.replace('(0.1)','10').replace('(0.5)','50').replace('(0.9)','90')
            k = k.rstrip()
            k = k.replace(' ','_')
            k = k.lower()
            setattr(ms2, k, v)
        df = pd.DataFrame(self.data.iloc[idx]).reset_index()
        df.columns = ['um', 'frequency']
        df.dropna(inplace=True)
        setattr(ms2, 'distribution', df)
        return(ms2)





    def sample_names(self):
        """Return unique sample names."""
        names = self.meta['Sample Name'].unique().tolist()
        return(names)

    def subset_metadata(self, df):
        """Define the metadata to process by a subsetted pandas dataframe. The pandas dataframe should be subsetted externally as required."""
        self.metadata = df.copy()
        print(df)




        
    def pkeys(self):
        """Return primary keys as a list of tuples"""
        m = self.meta
        df = pd.concat([m['Sample Name'], pd.to_datetime(m['Measurement date and time'].dt.strftime('%Y-%m-%d'))], axis=1).drop_duplicates()
        tuples = [tuple(i) for i in df.values]
        return(tuples)
        
    def idx(self, pkey):
        """Return indices for a given primary key"""
        m = self.meta
        idx = m[m['Sample Name']==pkey[0]].index
        return(idx)
   
    def replicates(self, indices):
        """Return a list of replicate series from given dataframe indices"""
        d = self.data
        lst = [self.row2series(i) for i in indices]
        return(lst)
        
    def row2series(self, idx):
        """Return a pandas series of a given replicate"""
        # retrieve dataframe row
        d = self.data
        # drop first column of NaN values
        d = d.drop('0.010000', axis=1)
        s = d.iloc[idx]
        # convert index from microns to mm and drop maximum size; this converts the size boundaries to lower limits to conform with traditional numerical methods
        s.index = self.sizes_mm()[0:100]
        return(s)
        
    def sizes_mm(self):
        """Return a list of floats of the sizes in mm"""
        d = self.data
        mm = [round(float(i) * 10**-3, 9) for i in d.columns]
        return(mm)
        

   
    
class SampleMetaData(MetaData):
    """Create a csv to establish groups of samples."""

    def __init__(self, folder, filename='metadata.csv', columns=[], lab_id=[], groups=['group']):
        """
            Attributes:
                datdir <str>: A filesystem path to the folder to place the output csv;
                filename <str>: Name of a CSV file containing, or to contain, segment coordinate data;
                columns <list>: List of field names to override the default.
        """

        self.csv_path = join(folder, filename)

        MetaData.__init__(self, self.csv_path, self._columns(columns, groups))

        if self.metadata_is_empty():
            if lab_id:
                self.append(lab_id)
            print('WARNING: No metadata exists.')

    def _columns(self, columns, groups):
        """Return a list of column names."""
        lst = [
            'id', # unique integer identifier
            'sample_name', # unique name of sample
        ] + groups + [
            'note'
        ]
        c = columns if columns else lst
        return(c)

   
    
    
    
#######################################################################   
    
    
    
    
    
    
#########################################    

def splitdf(df):
    """Split the raw dataframe into seperate data and metadata dataframes"""
    h2 = df.columns.get_level_values(1)
    hix, dix = [], []
    for n, i in enumerate(h2):
        try:
            float(i)
            dix += [n]
        except:
            hix += [n]
    
    h = df[df.columns[[hix]]]
    d = df[df.columns[[dix]]]
    h.columns = h.columns.droplevel(level = 1)
    d.columns = d.columns.droplevel(level = 0)
    return(h, d)
    
def replicatesafvafvafv(df, pkeys = None):
    """Return a dictionary of data frame indices corresponding to unique sample names and measurement dates; unique groups of replicates are assumed here to be represented by a unique sample name and a unique date.
        Attributes:
            df <pd.DataFrame>: A pandas data frame including the columns 'Sample Name' and 'Measurement date and time'
    """
    # convert dataframe timestamp to date
    if not pkeys:
        dfk = pd.concat([df['Sample Name'], pd.to_datetime(df['Measurement date and time'].dt.strftime('%Y-%m-%d'))], axis=1).drop_duplicates() 
        pkeys = [tuple(i) for i in dfk.values]
    else:
        pkeys = [(i[0], pd.to_datetime(i[1])) for i in pkeys]
        print(df2pkeys(df))
        
        
    #df = df.drop_duplicates()
    #if not pkeys:
    #    pkeys = df
    #print(df[['Sample Name','Measurement date and time']])
    #print(df['Sample Name', 'Measurement date and time'])
    
    #g = df.groupby(['Sample Name', 'Measurement date and time'])
    #return(g.groups)
    
def keycols():
    """Return a list of column names defining the primary keys of Mastersizer 2000 data"""
    lst = ['Sample Name', 'Measurement date and time']
    return(lst)
    
def df2pkeys(df, cols = keycols()):
    """Return a list of tuples of primary keys for Mastersizer data"""
    subset = pd.concat([df[cols[0]], pd.to_datetime(cols[1].dt.strftime('%Y-%m-%d'))], axis=1).drop_duplicates() 
    pkeys = [tuple(i) for i in dfk.values]
   
    
################# REVISE ALL BELOW ###########################
    
def create_index(df):
    """Create dataframe index"""
   
class data(object):
    """A class to handleMastersizer 2000 data
        Attributes:
            paths <string or list>: a single string or list of strings
        
    """
    def __init__(self, csvpath):
        """Load a mastersizer 2000 csv"""
        try:
            
            raw = csv2df(csvpath)
            print(raw)
            
            df = formatIndices(raw)   
            
            h, d = splitdf(df)
            d = cols2lower(d)
            self.head = h
            self.data = d
            
        except Exception as e:
            print(e)
        
          

    
def formatIndices(df):
    """Set the indices of a Mastersizer dataset to primary keys"""
    fmt = pkeys2MultiIndex(df)
    fmt.columns = df.columns
    fmt.index.set_names(pkcols(), inplace = True)
    return(fmt)
    
def pkeys2MultiIndex(df):
    """Return a Mastersizer 2000 dataframe with primary keys set as indices"""
    pk = get_pkeys(df)
    pknames = ['pk1', 'pk2']
    pk.columns = pknames
    df = pd.concat([df, pk], axis = 1)
    df = df.set_index(pknames, drop = True)
    return(df)
    
def pkcols():
    """Return the names of the primary key columns"""
    lst = ['Sample Name', 'Measurement date and time']
    return(lst)
    
def get_pkeys(df):
    """Return formatted primary key columns from head dataset"""
    colnames = pkcols()
    tmp = df[colnames]
    tmp.columns = colnames
    col1 = tmp[colnames[0]]
    col2 = timestamp2day(tmp[colnames[1]])
    pk = pd.concat([col1, col2], axis=1)
    return(pk)
    
def timestamp2day(Series):
    """Convert a timestamp type pandas series to YY-mm-dd format"""
    s = Series
    fmt = pd.to_datetime(s.dt.strftime('%Y-%m-%d'))
    return(fmt)
    

    
def cols2lower(df):
    """Convert column names in numerical particle-size data to reflect the lower size limits (they represent the upper limits by default).
        Attributes:
            df <DataFrame>: numerical dataframe of particle-size frequencies.
    """
    c = df.columns[:-1]
    del df[df.columns[0]]
    df.columns = c
    return(df)
    
def folk_and_ward(Series):
    """Convert a raw series of mastersiser data for processing using Folk and Ward methods"""
    from pyreglib.psa import mm2phi, flip
    s = Series
    s.index = pd.to_numeric(nm2mm(s.index))
    s = flip(s)
    s.index = [mm2phi(i) for i in s.index]
    return(s)

def graphical_statistics(df):
    """Return graphical statistics for a dataset of replicates. Input dataframe must have row indices set as 'Sample Name' and 'Measurement data and time'."""
    from pyreglib.psa import graphical_statistics as gs
    m = reps2mean(df)
    for i in m.index:
        s = m.loc[i]
        s = folk_and_ward(s)
        s = gs(s)
        try:
            stats = stats.append(s)
        except:
            stats = s
    stats.index.set_names(m.index.names, inplace = True)
    return(stats)
    
def percentiles(df):
    """Return percentiles for a dataset of replicates. Input dataframe must have row indices set as 'Sample Name' and 'Measurement data and time'."""
    from pyreglib.psa import percentile as prc
    
    m = reps2mean(df)
    for i in m.index:
        s = m.loc[i]
        s = folk_and_ward(s)
        p = [1,5,16,50,84,95,99]
        lst = [prc(s, j) for j in p]
        row = pd.DataFrame([lst], columns = ['D' + str(i) for i in p])
        row.index = pd.MultiIndex.from_tuples([s.name])
        
        try:
            perc = perc.append(row)
        except:
            perc = row
    perc.index.set_names(m.index.names, inplace = True)
    return(perc)

    
def reps2mean(df):
    """Return a dataframe of means for an input dataframe of replicates.
        Attributes:
            df <pandas.DataFrame>: Dataframe must consist of rows of replicate measurements. Indices must be labeled as a MultiIndex of samples and analysis day"""
    df = df.groupby(level = [0,1]).mean()
    return(df)
    
def nm2mm(iterable):
    """Convert iterable from nm to mm"""
    idx = [str(float(i) / 1000) for i in iterable]
    return(idx)
        
        
class graphical_statisticsbak(object):
    """Return a dataframe of graphical statistics for a given dataset"""
    def __init__(self, head, data):
        """"""
        self.h, self.d = head, data
        self.h['Measurement date and time'] = timestamp2day(self.h['Measurement date and time'])
        from pyreglib.psa import graphicalStatistics
        samples = self.samples()
        
        #m = self.mean()
        #print(m)
        
    def samples(self):
        """Return a list of tuples of samples and measurement day"""
        s = self.h['Sample Name']
        #d = timestamp2day(self.h['Measurement date and time'])
        d = self.h['Measurement date and time']
        #print(d)
        #print(self.h[['Sample Name', 'Measurement date and time']])
        
    def mean(self):
        """Create a dataframe of averages for replicates"""
        h, d = self.h, self.d
        g = h.groupby(['Sample Name', 'Measurement day'])
        for i in g:
            idx = i[1].index
            m = d.loc[idx].mean()
            try:
                out = pd.concat([out, m], axis = 1)
            except:
                out = m.to_frame()
        return(out)
        
    def df(self):
        """Return pandas dataframe"""
        return('weeeee')
        
        
        
    

        
        
        
        
        
        
        
        
        
        

    

            
def replicate_idx(head):
    """Return a list of indices representing replicate groups"""
    h = head
    g = h.groupby(['Sample Name', 'Measurement day'])
    idx = [i[1].index for i in g]
    return(idx)
    
    
    



def subset_indices(head, sample_names, dates):
    """Return the indices of a header dataframe that correspond with input keys"""
    h = head
    s = sample_names
    d = pd.to_datetime(dates)
    h['Measurement day'] = pd.to_datetime(h['Measurement date and time'].dt.strftime('%Y-%m-%d'))
    s_test = h['Sample Name'].isin(s)
    d_test = h['Measurement day'].isin(d)
    df = h[s_test & d_test]
    idx = df.index
    return(idx)
    
    

    

    
            

            
            
            
            
class mastersizer_2000bak(object):

    """A class to read, write, and process Mastersizer 2000 data
    
        Attributes:
            paths <string or list>: a single string or list of strings
        
    """
    def __init__(self, path, samples = None):
        """Process the input csv <path> if it exists, or, make the processing methods available for external use.
            Attributes:
                path <string>: filesystem path to the exported Mastersizer 2000 csv.
                samples <list>: Optional list of sample names to process.
        """
        if os.path.isfile(path):
            df = self.readCsv(path)
            self.fct = fct = self.splitcsv(df, 0)
            self.sample_names = fct['Sample Name']
            self.timestamps = fct['Measurement date and time']
            num = self.splitcsv(df, 1)
            self.mm = pd.Series([float(i) / 1000 for i in num.columns], index = None)
            self.num = self.cols2lower(num)
            self.reps, self.means = self.transform(self.fct, self.num)
        else:
            pass

    def readCsv(self, path, sep = ","):
        """Read an exported Mastersizer 2000 csv into a pandas dataframe.
            Attributes:
                path <string>: Filesystem path to exported Mastersizer 2000 csv."""
        df = pd.read_csv(path, sep = sep, header = [0,1], parse_dates = [5,6])
        return(df)
        
    def splitcsv(self, df, level):
        """Split an exported Mastersizer 2000 csv into a factorial dataframe and a numerical particle-size frequency dataframe).
            Attributes:
                df <DataFrame>: The raw input dataframe.
                level <int>: The header; 0 for first header and 1 for second
        """
        colidx = [n for n,x in enumerate(df.columns) if 'Unnamed' not in x[level]]
        outdf = df[df.columns[[colidx]]]
        droplvl = 0 if level == 1 else 1
        outdf.columns = outdf.columns.droplevel(droplvl)
        return(outdf)
        
    def cols2lower(self, df):
        """Convert column names in numerical particle-size data to reflect the lower size limits (they represent the upper limits by default).
            Attributes:
                df <DataFrame>: numerical dataframe of particle-size frequencies.
        """
        c = df.columns[:-1]
        del df[df.columns[0]]
        df.columns = c
        return(df)

    def transform(self, fct, num):
        """Return dictionaries of replicate measurements and means of replicates extracted from exported Mastersizer 2000 data.
            Attributes:
                fct <DataFrame>: Factorial data extracted from exported Mastersizer 2000 csv using the splitcsv method.
                numdf <DataFrame>: Particle-size frequencies extracted from exported Mastersizer 2000 csv using the splitcsv method.
        """
        reps, means = {}, {}
        for i in list(set(fct['Sample Name'])):
            idx = self.sampleRowIdx(fct, i)
            reps[i] = self.reps(num, idx)
            means[i] = self.means(reps[i])
        return(reps, means)

    def sampleRowIdx(self, df, sample_name):
        """Return row indices matching a sample name"""
        lst = df[(df['Sample Name'] == sample_name)].index
        return(lst)
        
    def reps(self, df, rowidx):
        """Return replicate numeric data from row indices"""
        outdf = df.ix[rowidx].T
        return(outdf)
        
    def means(self, reps):
        """Return replicate numeric data from row indices. reps <dataframe>"""
        df = reps.mean(axis = 1)
        return(df)
        
    def sample_names(self, df):
        """Return a list of sample names"""
        output = list(set(df['Sample Name']))
        return(output)

