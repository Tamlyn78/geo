#!/usr/bin/env python

"""Process pXRF data"""

import os
import csv
import datetime
import numpy as np
import pandas as pd

class olympusDelta(object):

    """Process data for an Olympus Delta model pXRF
        
    Attributes:
        
        paths <tuple>: A tuple containing all input paths to csv files exported from the Olympus Delta software;
        pkeys <list of tuples(date, int)>: A list of tuples (date [YYMMDD] and analysis id) used as primary keys used to specify data to extract from the csv's
        elements <tuple>: A tuple containing strings of elements required to be used in the analysis
                
    """

    def __init__(self, paths, pkeys = None, elements = None):
        """Assign arguments to objects and read csv's to a dictionary"""
        
        # check if the input path is a tuple
        if type(paths) != tuple:
            raise TypeError("""Variable "paths" is """ + str(type(paths)) + """. It must be a tuple!!!""")
            
        # check is the paths exist
        
        if not elements:
            elements = ["P","S","Cl","K","Ca","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","As","Se","Rb","Sr","Y","Zr","Nb","Mo","Rh","Pd","Ag","Cd",
                        "Sn","Sb","Ba","La","Ce","Pr","Nd","Ta","W","Pt","Au","Hg","Pb","Bi","Th","U","LE","Al","Si","Sc","Hf"]
        
        # assign the csv header to an object
        with open(paths[0], 'r') as f:
            reader = csv.reader(f, delimiter = ',')
            self.columns = next(reader)
        
        # append the data of all csv's in input paths to a list of tuples
        for counter, path in enumerate(paths):
            with open(path, 'r') as f:
                reader = csv.reader(f, delimiter = ',')
                reader.next()
                lst = []
                for line in reader:
                    lst.append(tuple(line))

        # filter the data list to include only records matching the input primary keys
        rows = self.rowIndices(lst, pkeys)
        filtered = self.filterRows(lst, rows)
        names = [i[self.colIndex("Sample name")] for i in filtered]
        dates = [i[self.colIndex("Date")] for i in filtered]
        self.arr, self.colNames = self.getArr(filtered, elements)

    def rowIndices(self, lst, pkeys):
        """Return a list of row indices that match the input primary keys"""
        if not pkeys:
            idx = range(0, len(lst))
            return(idx)
        dates = [self.formatDate(i[self.colIndex("Date")]) for i in lst]
        names = [i[self.colIndex("Sample name")] for i in lst]
        datKeys = zip(dates, names)
        idx = [i for i, pkey in enumerate(datKeys) if pkey in pkeys]
        return(idx)
        
    def formatDate(self, dateString):
        """Modify the date format supplied by the input csv to YYYYMMDD"""
        return(datetime.datetime.strptime(dateString, '%d/%m/%Y').strftime('%Y%m%d'))
        
    def filterRows(self, lst, indices):
        """Return the rows of a list corresponding to a list of indices"""
        return([vals for row, vals in enumerate(lst) if row in indices])
        
    def colIndex(self, name):
        """Return a column index from the column name"""
        index = self.columns.index(name)
        return(index)
        
    def getArr(self, lst, elements, LOD = 5):
        """Convert data list to a numpy array, excluding data with null values (usually whole columns) and where samples are below limit of detection exceed a givenpercentage"""        
        colIndices = [self.colIndex(i) for i in elements] # find column indices corresponding with selected elements
        transpose = map(list, zip(*lst)) # transpose list to enable iteration through columns
        elementCols = [vals for field, vals in enumerate(transpose) if field in [i for i in colIndices]]
        head = []
        dat = []
        for counter, row in enumerate(elementCols): # remove null columns and below detection threshold
            if not "" in row and float(row.count("<LOD")) < float(len(row)) * LOD / 100:
                head.append(elements[counter])
                dat.append([float(i.replace("<LOD", "0")) for i in row])
        dat = map(list, zip(*dat)) # transpose back
        dtype = [(i, 'float') for i in head]
        arr = np.array(dat)
        return(arr, head)
        
def read_bruker(data_directory):
    """
    Read a tab-separated value (tsv) file outputted by Bruker. The method searches a root directory containing subdirectories created for separate analyses (the Bruker may seperate analyses based on different days) and walks through all subdirectories to find files named "GeoChem.tsv". The method currently does not account for variations in Bruker export and/or filenaming convensions that may be programmable.
    
    The tab-delimited files are read instead of the comma-delimited files (csv) as the csv files contain unaligned blocks of datarows and therefore much more complicated to read and align. This method superceeds a previously written class that attempted to read the csv files.
    
        Attributes:
            data_directory <str> - the path to the top-level directory containing Bruker tsv data.
            
    """
        
    # create a list of paths to tsv files
    datfiles = []
    for root, dirs, files in os.walk(data_directory):
        if not os.path.basename(root).startswith('Backup'): # exclude searching the 'Backup' folder
            for f in files:
                if f.endswith("GeoChem.tsv"):
                    datfiles.append(os.path.join(root, f))
                    
    # validate the tsv files somehow ... to be implemented.
                     
    # read and concatenate tsv files
    for n, path in enumerate(datfiles):
        tsv = pd.read_csv(path, sep = '\t', encoding = 'utf-8-sig')
        if n == 0:
            pxrf = tsv
        else:
            pxrf = pd.concat([pxrf, tsv])
            
    pxrf = pxrf.set_index('File #') # set the index as the file idenifier to allow joining to other datasets

    # determine the analyte columns based on the consistent use of ' Err' to define error columns of the analytes
    errcols = [i for i in pxrf.columns if i.endswith(' Err')]
    analytes = [i.replace(' Err','') for i in errcols]
    return(pxrf, analytes)
    
class brukerBak(object): # this was initial work to deal with Bruker data but superceeded by a simple read method

    """Process data for a Bruker S1 Titan 800
        
    Attributes:
        
        paths <tuple>: A tuple containing all input paths to csv files exported from the Olympus Delta software;
        pkeys <list of tuples(date, int)>: A list of tuples (date [YYMMDD] and analysis id) used as primary keys used to specify data to extract from the csv's
        elements <tuple>: A tuple containing strings of elements required to be used in the analysis
                
    """

    def __init__(self, paths, pkeys = None, elements = None):
        """Assign arguments to objects and read csv's to a dictionary"""
        
        # check if the input path is a tuple
        if type(paths) != tuple:
            raise TypeError("""Variable "paths" is """ + str(type(paths)) + """. It must be a tuple!!!""")
            
        # check is the paths exist
        
        if not elements:
            elements = ["P","S","Cl","K","Ca","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","As","Se","Rb","Sr","Y","Zr","Nb","Mo","Rh","Pd","Ag","Cd",
                        "Sn","Sb","Ba","La","Ce","Pr","Nd","Ta","W","Pt","Au","Hg","Pb","Bi","Th","U","LE","Al","Si","Sc","Hf"]
        
        # assign the csv header to an object
        with open(paths[0], 'r') as f:
            reader = csv.reader(f, delimiter = ',')
            self.columns = next(reader)
        
        # append the data of all csv's in input paths to a list of tuples
        for counter, path in enumerate(paths):
            with open(path, 'r') as f:
                reader = csv.reader(f, delimiter = ',')
                reader.next()
                lst = []
                for line in reader:
                    lst.append(tuple(line))

        # filter the data list to include only records matching the input primary keys
        rows = self.rowIndices(lst, pkeys)
        filtered = self.filterRows(lst, rows)
        names = [i[self.colIndex("Sample name")] for i in filtered]
        dates = [i[self.colIndex("Date")] for i in filtered]
        self.arr, self.colNames = self.getArr(filtered, elements)

    def rowIndices(self, lst, pkeys):
        """Return a list of row indices that match the input primary keys"""
        if not pkeys:
            idx = range(0, len(lst))
            return(idx)
        dates = [self.formatDate(i[self.colIndex("Date")]) for i in lst]
        names = [i[self.colIndex("Sample name")] for i in lst]
        datKeys = zip(dates, names)
        idx = [i for i, pkey in enumerate(datKeys) if pkey in pkeys]
        return(idx)
        
    def formatDate(self, dateString):
        """Modify the date format supplied by the input csv to YYYYMMDD"""
        return(datetime.datetime.strptime(dateString, '%d/%m/%Y').strftime('%Y%m%d'))
        
    def filterRows(self, lst, indices):
        """Return the rows of a list corresponding to a list of indices"""
        return([vals for row, vals in enumerate(lst) if row in indices])
        
    def colIndex(self, name):
        """Return a column index from the column name"""
        index = self.columns.index(name)
        return(index)
        
    def getArr(self, lst, elements, LOD = 5):
        """Convert data list to a numpy array, excluding data with null values (usually whole columns) and where samples are below limit of detection exceed a givenpercentage"""        
        colIndices = [self.colIndex(i) for i in elements] # find column indices corresponding with selected elements
        transpose = map(list, zip(*lst)) # transpose list to enable iteration through columns
        elementCols = [vals for field, vals in enumerate(transpose) if field in [i for i in colIndices]]
        head = []
        dat = []
        for counter, row in enumerate(elementCols): # remove null columns and below detection threshold
            if not "" in row and float(row.count("<LOD")) < float(len(row)) * LOD / 100:
                head.append(elements[counter])
                dat.append([float(i.replace("<LOD", "0")) for i in row])
        dat = map(list, zip(*dat)) # transpose back
        dtype = [(i, 'float') for i in head]
        arr = np.array(dat)
        return(arr, head)
