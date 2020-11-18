#!/usr/bin/env python

"""Methods for csv database management."""

from os import makedirs
from os.path import isdir, isfile, join
import pandas as pd
import csv

def rbind(lst, header = None):
    """Combine multiple csv files by row"""
    for i in lst:
        print(i)


class MetaData:
    """A parent class to create a csv for metadata logging and loading. The attributes of the metadata are defined by the child class.
        Attributes:
            path <str>: A filesystem path to the required csv location;
            cols <list>: A list of strings representing the header columns of 
                the csv.
    """
    def __init__(self, path, cols):
        """Create a csv if not exists and load a dataframe"""
        self.path, self.cols = path, cols
        self._to_csv()
        self.metadata = self._to_df()

    def _to_csv(self):
        """Create a CSV in the specified path."""
        try:
            with open(self.path, 'x', newline='') as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow([i for i in self.cols])
        except Exception as e:
            print(e)

    def _to_df(self):
        """Return a pandas dataframe. Improvements might include specification of data type."""
        df = pd.read_csv(self.path)
        return(df)

    def metadata_is_empty(self):
        """Return True if the CSV has no data."""
        m = self.metadata
        return(m.empty)
        
    def append(self, list_of_tuples):
        """Append data to the CSV.
            Attributes:
                list_of_data <list of tuples>: A list of tuples containing the field data for each line."""
        with open(self.path, 'a', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for n, i in enumerate(list_of_tuples, start=1):
                row = [n] + [j for j in i]
                w.writerow(row)


class factors(object):
    """Create a collection of csv files to manage factors related to elements of a study.
        Attributes:
            groups <str>: name of a csv to be created or read containing a heirarchical table of factors relating to an element.
    
    """
    def __init__(self, directory, elements = "elements", groups = "groups", factors = "factors"):
        """Create csv files if they do not exist"""
        d = directory
        if not isdir(d):
            makedirs(d)
        epath = join(d, elements + '.csv')
        gpath = join(d, groups + '.csv')
        fpath = join(d, factors + '.csv')
        self.create_csv(epath, self.elements())
        self.create_csv(gpath, self.elements())
        self.create_csv(fpath, self.elements())
        self.e = self.csv2df(epath)
        self.g = self.csv2df(gpath)
        self.f = self.csv2df(fpath)
        f2g = self.f2g()
        self.dic = self.e2f(f2g)
        
    def create_csv(self, path, header):
        """"""
        if not isfile(path):
            f = open(path, 'w')
            f.write(','.join(header))
            f.close()
            
    def csv2df(self, path):
        """Convert a csv to a pandas dataframe"""
        df = pd.read_csv(path, index_col = None)
        return(df)
        
    def elements(self):
        """Return a list of fields for the elements csv"""
        lst = ['id', 'element']
        return(lst)
        
    def groups(self):
        """Return a list of fields for the groups csv"""
        lst = ['group', 'level', 'factor', 'group_note']
        return(lst)
        
    def factors(self):
        """Return a list of fields for the factors csv"""
        lst = ['element_id', 'group', 'level', 'value', 'factor_note']
        return(lst)
        
    def f2g(self):
        """Join factors to groups"""
        g = self.g
        f = self.f
        df = f.merge(g, how = 'inner', on = ['group', 'level'], suffixes = ('', '.a'))
        return(df)
        
    def e2f(self, df):
        """Return a dictionary of pivoted factor tables joined to elements"""
        dic = {}
        e = self.e
        f = self.f
        for g in list(set(f['group'])):
            group = df[df['group'] == g].pivot(index = 'element', columns = 'factor', values = 'value')
            join = e.merge(group, how = 'inner', left_on = 'id', right_index = True, suffixes = ('', '.a'))
            dic[g] = join
        return(dic)


