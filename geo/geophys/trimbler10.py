""""""

from os.path import basename, dirname
import tempfile
import numpy as np
import pandas as pd
import math

def ddm2dg(ddm):
    """Convert a float in decimal degree minutes to decimal degrees"""
    decimal, integer = math.modf(ddm / 100)
    decimal = decimal / 60 * 100
    dg = integer + decimal
    return(dg)
    
def check_line(line, f, n):
    """"""
    s = line.split(',')
    
    a = s[0] if s[0] == '$GNGGA' else 'NaN'
    b = np.datetime64('1900-01-01T' + str(s[1][:2] + ':' + s[1][2:4] + ':' + s[1][4:6]))
    c = ddm2dg(float(s[2]))
    d = 'N' if s[3] == 'N' else 'S' if s[3] == 'S' else 'NaN'
    c = -c if d == 'S' else c
    e = ddm2dg(float(s[4]))
    f = 'W' if s[5] == 'W' else 'E' if s[5] == 'E' else 'NaN'
    g = np.int64(s[6]) if np.int64(s[6]) in [0,1,2,4,5] else 'NaN'
    h = np.int64(s[7])
    i = float(s[8])
    j = float(s[9])
    k = 'M' if s[10] == 'M' else 'NaN'
    l = float(s[11])
    m = 'M' if s[12] == 'M' else 'NaN'
    n = str(s[13])
    o, checksum = s[14].split('*')
    o = str(o)

    line = ','.join([str(i) for i in [a,b,c,d,e,f,g,h,i,j,k,l,m,n,o]]) + '\n'
    return(line)
    
    
def hyperterminal(path_to_file, date = None, timedelta = None):
    """
        Process a text file exported from Hyperterminal that captured a data strem from a TrimbleR10. The Trimble apparatus for which this module is coded only outputed time; if the survey was undertaken over multiple days then the date must be manually input if the data is to be merged with another dataset, such as a geophysical device.
        
        Attributes:
            path_to_file <str>: Path to the hyperterminal output file (usually '.TXT' extension).
            date <str>: Date that file was generated formatted as %H%M%S.
            timedelta <dict>: Time to alter the raw time data aquired from the TrimbleR10 for synchronisation with a seperate dataset, such as geophysics apparatus. EG. {'hours':9, 'minutes':32, 'seconds':51}.
    
    """
    
    # create temporary file to capture processed output
    tmp = tempfile.TemporaryFile()
    
    # open data file for reading
    p = path_to_file

    with open(p, 'rb') as f:
    
        # iterate through each line and discard those with errors; this command will not fail for an empty file
        for n, l in enumerate(f.readlines()):

            try:
                # decode line and remove trailing newline; command will fail if line is malformed, discarding line from output
                decoded_line = l.decode('utf-8').rstrip()
                
                # check the decoded line and discard those with formatting errors
                checked_line = check_line(decoded_line, f, n)
                
            except Exception as e:
                txt = 'File ' + p + ' Line ' + str(n) + ' ' + str(e)
                #print(txt)
                checked_line = None
                
            # if output line exists write to temporary file
            if checked_line is not None:
                tmp.write(checked_line.encode('utf-8'))
                
      
        columns = [
            'id',
            'time', 
            'latitude', 
            'latitude_direction', 
            'longitude', 
            'longitude_direction', 
            'quality', 
            'sv_count', 
            'hdop', 
            'height', 
            'height_units', 
            'geoid_separation', 
            'geoid_separation_units', 
            'age_of_record', 
            'reference_id',
        ]
        
        # read temporary file to a dataframe
        tmp.seek(0)
        df = pd.read_csv(tmp, names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'])

        
        # coerse the datetime data type of the dataframe and adjust timestamp if requested
        df['b'] = pd.to_datetime(df['b'], errors = 'coerce')
        if timedelta:
            td = pd.Timedelta(**timedelta)
            df['b'] = df['b'] + td
        date = pd.to_datetime(date)
        df['b'] = df['b'].apply(lambda x: x.replace(year = date.year, month = date.month, day = date.day))
        
        # coerse the numeric data types of the dataframe; errors to 'Nan'
        df['c'] = pd.to_numeric(df['c'], errors = 'coerce')
        df['g'] = pd.to_numeric(df['g'], errors = 'coerce')
        df['h'] = pd.to_numeric(df['h'], errors = 'coerce')
        df['i'] = pd.to_numeric(df['i'], errors = 'coerce')
        df['j'] = pd.to_numeric(df['j'], errors = 'coerce')
        df['l'] = pd.to_numeric(df['l'], errors = 'coerce')
        df['n'] = pd.to_numeric(df['n'], errors = 'coerce')
        
        # remove rows with 'Nan'
        df.dropna(inplace = True)

        # return dataframe
        return(df)
    
    
                