
"""Extract data from MALA file types and output into useful formats."""

from os.path import splitext
from numpy import fromstring
from glob import glob

#from .gpr import get_file_path
#from .filesystem import get_file_path
from .calculations import distance, time

def file_extensions():
    """Return a list of file extensions associated with MALA equipment output"""
    extension_list = ['.cor', '.mrk', '.rad', '.rd3']
    return(extension_list)

def rad2dict(path):
    """Return line header information as a dictionary.
           Attributes:
                rad <string>: Full path to MALA '.rad' or '.RAD' file;
    """
    p = get_file_path(path, ext='.rad')
    try:
        f = open(p, 'r')
        d = {}
        for line in f.readlines():
            text = line.split(':')
            key = text[0]
            value = text[1].strip()
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except:
                pass
            d[key] = value
        f.close()
        return(d)

    except Exception as e:
        print(e)
 
def rd32arr(path, traces, samples):
    with open(path, 'rb') as f:
        s = fromstring(f.read(), dtype = 'int16')
    arr = s.reshape(traces, samples).T
    return(arr)

def arr2rd3(array, path):
    """"""
    import numpy as np
    a = np.concatenate([i for i in array.T])
    with open(path, 'wb') as f:
        for i in a:
            f.write(i)


class RD3:
    """Create a MALA object for use in general GPR methods. Note that slight variations in frequency between lines require rounding of the time interval to force equality of time-values between adjacent lines. Reading of separate files should be independent of one another so that the class does not fail if one is missing, or if an isolated file needs to be inspected."""

    def __init__(self, path):

        p, e = get_file_path, file_extensions
        cor, mrk, rad, rd3 = [p(path, i) for i in e()]
        m = rad2dict(rad)
        t = m['LAST TRACE']
        s = m['SAMPLES']
        d = m['DISTANCE INTERVAL']
        f = m['FREQUENCY']

        a = rd32arr(rd3, t, s)

        x = distance(d, t)
        y = time(f, s, precision=5)

        self.array = a
        self.x = x
        self.y = y

        self.x_precision = 4
        self.y_precision = 7

        self.traces = t
        self.samples = s
        self.step = d
        self.frequency = f

        self.path = path

    def write(self, path):
        """Write rd3 to file"""
        b, e = splitext(path)
        arr2rd3(b + '.rd3', self.traces, self.samples)



class RD3WorkInProgress:
    """Create a MALA object for use in GPR methods. Note that slight variations in frequency between lines require rounding of the time interval to force equality of time-values between adjacent lines. Reading of separate files should be independent of one another so that the class does not fail if one is missing, or if an isolated file needs to be inspected."""

    def __init__(self, path, traces, samples):
        """"""
        p, e = get_file_path, file_extensions
        self.array = rd32arr(p, traces, samples)

    def write(self, path):
        """Write rd3 to file"""
        b, e = splitext(path)
        arr2rd3(b + '.rd3', self.traces, self.samples)




class RADWorkInProgress:
    """Read and write MALA RAD files."""

    def __init__(self, path):
        self.p = path

    def to_dict(self):
        d = rad2dict(self.p)
        return(d)

    def to_file(self, path):
        lst = [
            'SAMPLES', 
            'FREQUENCY',
            'FREQUENCY STEPS',
            'SIGNAL POSITION',
            'RAW SIGNAL POSITION',
            'DISTANCE FLAG',
            'TIME FLAG', 
            'PROGRAM FLAG',
            'EXTERNAL FLAG',
            'TIME INTERVAL',
            'DISTANCE INTERVAL',
            'OPERATOR',
            'CUSTOMER',
            'SITE',
            'ANTENNAS',
            'ANTENNA ORIENTATION',
            'ANTENNA SEPARATION',
            'COMMENT',
            'TIMEWINDOW',
            'STACKS',
            'STACK EXPONENT',
            'STACKING TIME',
            'LAST TRACE',
            'STOP POSITION',
            'SYSTEM CALIBRATION',
            'START POSITION',
            'SHORT FLAG',
            'INTERMEDIATE FLAG',
            'LONG FLAG',
            'PREPROCESSING',
            'HIGH',
            'LOW',
            'FIXED INCREMENT',
            'FIXED MOVES UP',
            'FIXED MOVES DOWN',
            'FIXED POSITION',
            'WHEEL CALIBRATION',
            'POSITIVE DIRECTION',
        ]

def combine_rads(lst):
    # this method likely does not work because of modifications elsewhere; it should probably work with gpr objects as input and return some sort of useful dataframe highlighting problem gpr lines; maybe should be a class
    """Combine a list of rad files into a dictionary of lists. The method is useful for comparing the metadata of a group of GPR lines to check for compatability in creating a 3D grid. A property can be checked by calling set(d['key']); the property for all lines is equal if the length of the result is equal to 1."""
    d = {}
    for i in lst:
        p = ramacpath(i, '.rad')
        r = rad2dict(p)
        for key in r.keys():
            try:
                d[key] += [r[key]]
            except:
                d[key] = [r[key]]
    return(d)
