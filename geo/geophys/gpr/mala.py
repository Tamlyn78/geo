
"""Extract data from MALA file types and output into useful formats."""

#from os.path import splitext
from numpy import fromstring
import numpy as np
from collections import namedtuple

from .filesystem import get_file_path
from .calculations import distance, time
from .graph import RadarGram


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
 
def rd32arr(path, samples):
    """Read a MALA RD3 file into a numpy array.
        Attributes:
            path <str>: filesystem path to a MALA RD3 file;
            samples <int>: The number of samples per trace read from a MALA RAD file.
        Note:
            Errors have previously been found in the trace number in the DAT files, therefore it is calculated here from the sample number. Metadata would therefore need to be updated for a returned array.
    """
    with open(path, 'rb') as f:
        s = fromstring(f.read(), dtype = 'int16')
        length = s.shape[0]
        traces = round(length / samples)
    try:
        arr = s.reshape(traces, samples).T
        return(arr)
    except Exception as e:
        print(e)
        print(path)

def arr2rd3(array, path):
    """"""
    a = np.concatenate([i for i in array.T])
    with open(path, 'wb') as f:
        for i in a:
            f.write(i)


class RAD:
    """From MALA RD3 header data, create an object with custom metadata of a GPR segment."""

    def __init__(self, path):
        """Read a RAD FILE and set attributes using the file content."""
        p = get_file_path(path, ext='.rad')
        d = rad2dict(p)

        s = self
        s.format = 'MALA'
        s.traces = d['LAST TRACE']
        s.samples = d['SAMPLES']
        s.step = d['DISTANCE INTERVAL']
        s.frequency = d['FREQUENCY']
        s.start_position = d['START POSITION']
        s.system_calibration = d['SYSTEM CALIBRATION']

        values = self._x_values()
        precision = 4
        X = namedtuple('x', ['values', 'precision'])
        s.x = X(values, precision)

        values = self._y_values()
        precision = 7
        Y = namedtuple('y', ['values', 'precision'])
        s.y = Y(values, precision)

        s.rad_path = p

    def _x_values(self):
        """Calculate the trace x coordinates from the metadata."""
        x = distance(self.step, self.traces)
        return(x)

    def _y_values(self):
        """Calculate the trace y coordinates from the metadata."""
        y = time(self.frequency, self.samples, precision=5)
        return(y)


class RD3(RAD):
    """Create a MALA object for use in general GPR methods. Note that slight variations in frequency between lines require rounding of the time interval to force equality of time-values between adjacent lines. Reading of separate files should be independent of one another so that the class does not fail if one is missing, or if an isolated file needs to be inspected."""

    ext = 'rd3'

    def __init__(self, path, rad_path=None):
        rad_path = rad_path if rad_path else path
        RAD.__init__(self, rad_path)
        p = get_file_path(path, ext='.rd3')
        self.array = rd32arr(p, self.samples)
        self._update_traces()
        self.rd3_path = p

    def _update_traces(self):
        """The trace number recorded in some DAT files has been found to occasionally be in error. The returned array is used here to update the metadata"""
        self.traces = self.array.shape[1]

    def write_array(self, path):
        """Write rd3 to file"""
        #b, e = splitext(path)
        #arr2rd3(b + '.rd3', self.traces, self.samples)


class Line(RadarGram):
    """A line object"""
    def __init__(self, m, n):
        """"""
        self.array = self._empty_array(m, n)
        self.x = n
        self.y = m

    def _empty_array(self, m, n):
        """Return an empty array"""
        arr = np.zeros([m, n])
        return(arr)


