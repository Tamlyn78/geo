"""A module for processing of text files outputted from geophysical equipment"""

from os import getcwd, walk
from os.path import join, relpath
import numpy as np
import pandas as pd
import tempfile
import csv
import string
import re

control_characters = ''.join(map(chr, [i for i in range(0,32)] + [i for i in range(127,160)]))

class LineErrors:
    """"""
    line_errors = []

    def check_line(self, line):
        """"""
        n, t = line
        try:
            t = self._decode(t)
            t = self._control_characters(t.strip(), n)
            self._check_empty(t)
            return(n, t)
        except Exception as e:
            print("Line " + str(n) + ': ' + str(e))
            self.add_line_error(n, t, str(e))

    def _decode(self, line):
        """"""
        l = line.decode('utf-8').strip()
        return(l)
  
    def _check_empty(self, line):
        """Check if line is empty and otherwise discard"""
        assert line, "line returned 'None'"

    def _control_characters(self, line, n):
        """Check that line does not contain unprintable characters"""
        l = re.compile('[%s]'  % re.escape(control_characters)).sub('', line)
        return(l)

    def add_line_error(self, line_number, line, note=None):
        """"""    
        self.line_errors += [(line_number, line, note)]

class TextFile(LineErrors):
    """"""
    def __init__(self, path, ncols=1, sep=",", header=[0]):
        """Initialise useful metadata of a text file."""
        self.path = path
        print("Reading '" + str(path) + "'")
        t = self._to_binary(path)
        n = [i[0] for i in enumerate(t, start=1)]
        lines = [(self.check_line(i)) for i in zip(n, t)]
        self.lines = [i for i in lines if i]
        self.ncols = ncols
        self.header = header
        if ncols > 1:
            self.lines = [self.check_columns(i, sep) for i in self.lines if i]
 
    def linecount(self):
        """Return the current line count."""
        count = len(self.lines)
        return(count)

    def line_numbers(self):
        """Return a list of line numbers"""
        n = [i[0] for i in self.lines]
        return(n)

    def to_file(self, lines=None, ext='.txt', root=None):
        """"""
        tmp = tempfile.NamedTemporaryFile(mode='w+t', newline='', 
            suffix=ext, dir=root, delete=False)
        for i in self.lines:
            tmp.write(i[1] + '\n')
        tmp.seek(0)
        return(tmp.name)

    def concat_line_numbers(self, sep=","):
        """Add line numbers to the start of each line"""
        l = self.lines
        l = [''.join([str(n), sep, i]) for n, i in l if i]
        return(l)

    def _to_binary(self, path):
        """Read a text file to binary to avoid decoding errors. Strip newline"""
        with open(path, 'rb') as f:
            #lines = [i.strip() for i in f.readlines()]
            lines = f.readlines()
        return(lines)
      
    def __str__(self):
        """Set path as the string method."""
        return(self.path)

    def check_columns(self, line, sep):
        """Split the line into a list of csv fields and check the length"""
        n, t = line
        try:
            s = t.split(sep)
            e = "Line " + str(n) + ": returned incorrect number of csv fields"
            assert len(s) == self.ncols, e
            return(line)
        except Exception as e:
            print(e)
            self.add_line_error(n, t, e)
        

class HyperTerminal(TextFile):
    """"""

    def __init__(self, path, ncols=1, sep=",", header=[0]):
        """Read a file exported from HyperTerminal and prepare it for further processing"""
        TextFile.__init__(self, path, ncols, sep, header)
        l = self.lines
        l = [self._get_checksum(i) for i in l if i]
        self.lines = [i for i in l if i]

    def _get_checksum(self, line):
        """Extract the Hyperterminal added checksum and test. Return line if checksum OK."""
        n, t = line
        error = lambda x: "Cannot find checksum of line " + str(n) + ": " + str(x)
        try:
            split = t[::-1].split('*', 1) 
            checksum = split[0]
            # call methods for further checks here
            line = (n, split[1][::-1])
            return(line)
        except Exception as e:
            e = "Cannot find checksum of line " + str(n) + ": " + str(e)
            print(e)
            self.add_line_error(n, t, e)


class DataType:
    """"""
    def __init__(self, df, dtypes):
        """Read a csv file object to a dataframe"""
        c = []
        for i in range(len(df.columns)):
            s = df[df.columns[i]]
            s.name = i
            c += [self._column(s, dtypes[i])]
        self.df = pd.concat(c, axis=1, join='inner')

    def _column(self, s, dtype):
        """"""
        fn = self._column_to_type(s, dtype)
        try:
            s = fn(dtype)
            return(s)
        except Exception as e:
            s = self._cell(s, dtype)
            return(s)
 
    def _column_to_type(self, s, dtype):
        """Return a custom function for data type conversion"""
        if dtype.startswith('int'):
            fn = lambda x: s.astype('float', errors='raise').astype(x, errors='raise')
        else:
            fn = lambda x: s.astype(x, errors='raise')
        return(fn)
     
    def _cell(self, s, dtype):
        """"""
        fn = self._cell_to_type(s, dtype)
        error = []
        for i in s.index:
            try:
                s.at[i] = fn(i)
            except Exception as e:
                print('Column ' + str(s.name) + ' index ' + str(i) + ' ' + str(e))
                error += [i]

        s.drop(error, inplace=True)
        s = self._column(s, dtype)
        return(s)

    def _cell_to_type(self, s, dtype):
        """Return a custom function for data type conversion"""
        convert = getattr(np, dtype)
        if dtype.startswith('int'):
            fn = lambda x: convert(float(s.at[x]))
        else:
            fn = lambda x: convert(s.at[x])
        return(fn)

     
def get_paths(root, ext='', relative=False):
    """Create a list of paths to multiple files in a directory"""
    p = lambda x, y: join(x, y)
    lst = [[p(i[0], j) for j in i[2]] for i in walk(root)]
    lst = sum(lst, [])
    paths = [i for i in lst if i.endswith(ext)]
    paths = [relpath(i, getcwd()) for i in paths] if relative else paths
    return(paths)

