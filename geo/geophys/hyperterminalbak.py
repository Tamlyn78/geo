# process dualem data acquired through geoscout

import os
from os.path import join as jn
import csv
import numpy as np
import pandas as pd
import tempfile
import matplotlib.pyplot as plt
import math


# assign global variables
rdir = os.path.dirname(os.getcwd())
datdir = os.path.join(rdir, "data")
header = ['Longitude', 'Latitude', 'Elevation', 'Fix_Type', 'UTC_Time', 'Speed', 'Course', 'Array', 'Timestamp', 'HCP_cond', 'HCP_inphase', 'PRP_cond', 'PRP_inphase']

#######################################

# methods for reading data
def surveydirs():
    """Return a list of directories containing survey data"""
    surveys = [
        "20170726", 
        "20170727", 
        "20170728", 
        "20170731", 
        "20170801", 
        "20170802",
        "20170803",
        "20170804"
        ]
    return(surveys)

def csv_fnames(path):
    """Return csv filenames in a directory"""
    filenames = os.listdir(path)
    return(filenames)
    
def csvPaths():
    lst = []
    for i in surveydirs():
        d = os.path.join(datdir, i)
        f = csv_fnames(d)
        paths = [os.path.join(d, i) for i in f]
        lst += paths
    return(lst)

# methods for checking data lines

def lst2df(lst, h = header):
    """Convert a list to a single-line dataframe"""
    df = pd.DataFrame([lst], columns = h)
    try:
        df[['Longitude', 'Latitude', 'Elevation', 'Speed', 'Course', 'HCP_cond', 'HCP_inphase' , 'PRP_cond', 'PRP_inphase']] = df[['Longitude', 'Latitude', 'Elevation', 'Speed', 'Course', 'HCP_cond', 'HCP_inphase' , 'PRP_cond', 'PRP_inphase']].apply(pd.to_numeric)
        df[['Fix_Type', 'UTC_Time', 'Timestamp']] = df[['Fix_Type', 'UTC_Time', 'Timestamp']].apply(pd.to_numeric)

        val = df['Array'].iloc[0]
        if val.startswith('$PDLM') and len(val) == 6:
            return(df)
    except:
        pass

def trim_list(line, header):
    """Trim the number of fields in an input csv line to math the header"""
    t = line[:len(header)]
    return(t)
        
def line2lst(line):
    """Return a list of fields from an input csv line"""
    lst = line.split(',')
    return(lst)
        
def line2df(line, h = header):
    """Convert line of csv to pandas"""
    try:
        l = line.decode('utf-8')
        lst = line2lst(l)
        t = trim_list(lst, h)
        if len(t) == len(h):
            df = lst2df(t)
            return(df)
    except:
        pass
        
def csv2df(path):
    """Convert a csv to a pandas dataframe"""
    try:
        with open(path, 'rb') as f:
            next(f)
            for line in f.readlines():
                print(line)
        #        tmp = line2df(line, header)
        #        try:
        #            df = df.append(tmp, ignore_index = True)
        #        except:
        #            df = tmp
        #return(df)
    except:
        pass
    
def concat_data(infile):
    """Concatenate all datafiles into a csv"""
    for path in csvPaths():
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
        

    
def empty_file(path):
    """Return False for an empty file"""
    bool = os.stat(path).st_size == 0
    return(bool)
    
def non_ascii(path):
    """Clean a csv file of non-ascii characters and return as a temporary file object"""
    tmp = tempfile.TemporaryFile()
    with open(path, 'rb') as f:
        for n, line in enumerate(f.readlines()):
            try:
                line.decode('utf-8')
                tmp.write(line)
            except Exception as e:
                print('Line ' + str(n) + ':', e)   
    return(tmp)
    
def malformed(file_object):
    tmp = tempfile.TemporaryFile()
    f = file_object
    f.seek(0)
    lst = []
    for line in f.readlines():
        l = line.decode('utf8')
        if l.startswith('$'):
            tmp.write(line)
        #poo = l[0:5]
        #lst += [poo]
        #if not l.startswith('$GNGGA'):
        #    print(l)
        #    print('wee')
        #if line.startswith(b'$GNGGA') and line.endswith(b'\r\n'):
        #    tmp.write(line)
    #print(lst)
    #for i in lst:
    #    if not i.startswith('$'):
    #        print(i)
    return(tmp)
    
def TrimbleR10bak():
    """"""
    d = jn(datdir, 'TrimbleR10')
    lst = os.listdir(d)
    columns = {
                'id':str,
                'utc':np.float64, 
                'latitude':np.float64, 
                'latitude_direction':str, 
                'longitude':np.float64, 
                'longitude_direction':str, 
                'quality':np.int8, 
                'sv_count':np.int8, 
                'hdop':np.float16, 
                'height':np.float64, 
                'height_units':str, 
                'geoid_separation':np.float16, 
                'geoid_separation_units':str, 
                'age_of_record':np.float16, 
                'reference_id_and_checksum':str, 
                }
    header = [i for i in columns.keys()]
    
    print(lst)
    lst = [lst[1]]
    print(lst)
    for i in lst:
        path = jn(d, i)
        if empty_file(path):
            continue
        tmp = non_ascii(path)
        tmp = malformed(tmp)
        tmp.seek(0)
        df = pd.read_csv(tmp, names = header, error_bad_lines = False)
        #for i in df['id']:
        #    wee = str(i)
        
        #    if not wee.startswith('$'):
        #        print(i)
           #print(type(i))
        #df.to_csv(jn(r'C:\Users\Field\Dropbox\QS\_47\test', str(count) + '.csv'))
        #count = count + 1
        try:
            outdf = outdf.append(df, ignore_index = True)
        except:
            outdf = df
        
    #for i in pd.to_numeric(outdf['latitude'], errors = 'coerse'):
    #    if i > 3445:
    #        print(i)
        
    #print(outdf['latitude'])
            
    #wee = gps[['longitude', 'latitude']]
    #wee.to_csv(r'C:\Users\Field\Dropbox\QS\_47\moo.csv')
            
    outdf['longitude'] = pd.to_numeric(outdf['longitude'], errors = 'coerse')
    outdf['latitude'] = pd.to_numeric(outdf['latitude'], errors = 'coerse')
    outdf = outdf.dropna(subset = ['longitude', 'latitude'])
    #print(outdf)

    return(outdf)
                    
                    #tmp = line2df(line, header)        
            
        #with open(path, 'r') as f:
        #    next(f)
        #    for line in f.readlines():
        #        print(line)
        #        tmp = line2df(line, header)
        #        try:
        #            df = df.append(tmp, ignore_index = True)
        #        except:
        #            df = tmp

        #exit()
        
        
        
def TrimbleR10bak2():
    """"""
    d = jn(datdir, 'TrimbleR10')
    lst = os.listdir(d)
    columns = {
                'id':str,
                'utc':np.float64, 
                'latitude':np.float64, 
                'latitude_direction':str, 
                'longitude':np.float64, 
                'longitude_direction':str, 
                'quality':np.int8, 
                'sv_count':np.int8, 
                'hdop':np.float16, 
                'height':np.float64, 
                'height_units':str, 
                'geoid_separation':np.float16, 
                'geoid_separation_units':str, 
                'age_of_record':np.float16, 
                'reference_id_and_checksum':str, 
                }
    header = [i for i in columns.keys()]
    
    tmp = tempfile.TemporaryFile()
    #lst = [lst[0]]
    for i in lst:
        path = jn(d, i)
        if empty_file(path):
            continue
        with open(path, 'r') as f: 
            for line in f.readlines():
                if line.startswith('$'):
                    tmp.write(line.encode('utf8'))
        #tmp = non_ascii(path)
        tmp.seek(0)
    df = pd.read_csv(tmp, names = header, error_bad_lines = False)
    return(df)
    
def ddm2dg(s):
    """"""
    # ll = df
    # ll[['decimal','integer']] = ll['longitude'].apply(math.modf).apply(pd.Series)
    # ll['dd'] = ll['integer'].astype(str).str[:-4].astype(np.int64) + (ll['integer'] - (ll['integer'].astype(str).str[:-4].astype(np.int64) * 100) + ll['decimal']) / 60
    # return(ll['dd'])
    ll = s.to_frame(name = 'coords')
    ll[['decimal','integer']] = ll['coords'].apply(math.modf).apply(pd.Series)
    ll['dd'] = ll['integer'].astype(str).str[:-4].astype(np.int64) + (ll['integer'] - (ll['integer'].astype(str).str[:-4].astype(np.int64) * 100) + ll['decimal']) / 60
    return(ll['dd'])

    

def hyperterminal():
    """"""
    gps = TrimbleR10()
    gps['longitude'] = ddm2dg(gps['longitude'])
    gps['latitude'] = -ddm2dg(gps['latitude'])
    print(gps)
    #ddm2dg(gps)
    gps.to_csv(r'C:\Users\Field\Dropbox\QS\_47\moo.csv')
    
    x = gps['longitude']
    y = gps['latitude']
    plt.plot(x, y)
    plt.show()
    
    
    
def TrimbleR10(datdir):
    """"""
    date = os.path.basename(datdir)
    datfiles = os.listdir(datdir)
    tmp = tempfile.TemporaryFile()
    
    columns = {
                'id':str,
                'utc':np.float64, 
                'latitude':np.float64, 
                'latitude_direction':str, 
                'longitude':np.float64, 
                'longitude_direction':str, 
                'quality':np.int8, 
                'sv_count':np.int8, 
                'hdop':np.float16, 
                'height':np.float64, 
                'height_units':str, 
                'geoid_separation':np.float16, 
                'geoid_separation_units':str, 
                'age_of_record':np.float16, 
                'reference_id_and_checksum':str, 
                }
    header = [i for i in columns.keys()]
    
    for i in datfiles:
        path = jn(datdir, i)
        # ignore file if empty
        if empty_file(path):
            continue
        with open(path, 'r') as f: 
            for line in f.readlines():
                if line.startswith('$'):
                    tmp.write(line.encode('utf8'))
    tmp.seek(0)
    df = pd.read_csv(tmp, names = header, error_bad_lines = False)
    df['date'] = date
    print(df['utc'].dtype)
    df['datetime'] = df['date'].astype(str) + df['utc'].astype(str)
    return(df)        
            
if __name__ == '__main__':
    """"""
    #hyperterminal()
    
    # concatenate and clean gps data
    gpsdir = jn(datdir, 'TrimbleR10')
    gpsdates = os.listdir(gpsdir)
    for i in gpsdates:
        path = jn(gpsdir, i)
        try:
            df = df.append(TrimbleR10(path), ignore_index = True)
        except:
            df = TrimbleR10(path)
            
    print(df)
        
    #gps = TrimbleR10(gpsdir)
    #print(gps)
    
    #datfile = os.path.join(datdir, 'SurveyConcat.CSV')
    
    #try:
    #    df = pd.read_csv(datfile)
    #except:
    #    df = concat_data(datfile)
