# process dualem data acquired through geoscout

import os
import csv
import numpy as np
import pandas as pd

# assign global variables
rdir = os.path.dirname(os.getcwd())
datdir = os.path.join(rdir, "Data")
header = ['Longitude', 'Latitude', 'Elevation', 'Fix_Type', 'UTC_Time', 'Speed', 'Course', 'Array', 'Timestamp', 'HCP_cond', 'HCP_inphase', 'PRP_cond', 'PRP_inphase']

#######################################

# methods for checking data lines

def lst2df(lst):
    """Convert a list to a single-line dataframe"""
    df = pd.DataFrame([lst], columns = header)
    try:
        df[['Longitude', 'Latitude', 'Elevation', 'Speed', 'Course', 'HCP_cond', 'HCP_inphase' , 'PRP_cond', 'PRP_inphase']] = df[['Longitude', 'Latitude', 'Elevation', 'Speed', 'Course', 'HCP_cond', 'HCP_inphase' , 'PRP_cond', 'PRP_inphase']].apply(pd.to_numeric)
        df[['Fix_Type', 'UTC_Time', 'Timestamp']] = df[['Fix_Type', 'UTC_Time', 'Timestamp']].apply(pd.to_numeric)

        val = df['Array'].iloc[0]
        if val.startswith('$PDLM') and len(val) == 6:
            return(df)
    except:
        pass

def trim_list(line):
    """Trim the number of fields in an input csv line to match the header"""
    df = line[:len(header)]
    return(df)
        
def line2lst(line):
    """Convert a row of data to a list.
        line <string>: a decoded row of data from a csv outputted from a GeoScout datalogger 
    """
    lst = line.split(',')
    return(lst)
    
def decodeline(line):
    """Decode a line of csv data and strip the trailing linebreak.
        line <string>: a row of data from a csv outputted from a GeoScout datalogger
    """
    try:
        l = line.decode('utf-8').strip()
        return(l)
    except Exception as e:
        print(e)
    
def filterline(line):
    """Convert line of csv to pandas"""
    try:
        l = decodeline(line)

        lst = line2lst(l)
        t = trim_list(lst)
        if len(t) == len(header):
            df = lst2df(t)
            return(df)
    except:
        pass
        
def opencsv(path):
    """Read csv in bytes to avoid exceptions from corrupt data and save to an object"""
    try:
        b = open(path, 'rb')
        next(b)
        return(b)
    except Exception as e:
        print(e)

def csv2df(path):
    """Convert a csv to a pandas dataframe"""
    try:
        b = opencsv(path)
        for line in b.readlines():
            tmp = filterline(line)
            try:
                df = df.append(tmp, ignore_index = True)
            except:
                df = tmp
        return(df)
    except Exception as e:
        print(e)
    
def splitarray(df, arrays = [1,2,4]):
    """Split a dataframe into its arrays"""
    print(df)       
        
    
def concat_data(infile):
    """Concatenate all datafiles into a csv"""
    for path in infile():
        print(path)
        tmp = csv2df(path)
        try:
            df = df.append(tmp)
        except:
            if tmp is not None:
                df = tmp
    try:
        df.to_csv(infile, index = False)
        return(df)
    except:
        pass
    

