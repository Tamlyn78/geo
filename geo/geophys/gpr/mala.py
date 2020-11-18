
"""Extract data from MALA file types and output into useful formats."""

#from os.path import splitext
from numpy import fromstring
import numpy as np

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
    import numpy as np
    a = np.concatenate([i for i in array.T])
    with open(path, 'wb') as f:
        for i in a:
            f.write(i)

class MetaData:
    """A metadata class creating attributes of a GPR segment."""
    class metadata:
        brand = None
        traces = None
        samples = None
        step = None

        class x:
            values = None
            precision = None

        class y:
            values = None
            precision = None

    def _get_trace_x(self):
        """Calculate the trace x coordinates from the metadata."""
        m = self.metadata
        x = distance(m.step, m.traces)
        return(x)

    def _get_trace_y(self):
        """Calculate the trace y coordinates from the metadata."""
        m = self.metadata
        y = time(m.frequency, m.samples, precision=5)
        return(y)

    def metadata_to_dict(self, dic=None):
        """"""
        m = self.metadata
        d = dict([(i, getattr(m, i)) for i in dir(m) if not i.startswith('_')])
        if dic:
            d = {**d, **dic}
        d['x_precision'] = d['x'].precision
        d['y_precision'] = d['y'].precision
        d.pop('x', None)
        d.pop('y', None)
        return(d)


class RADBak(MetaData):
    """From MALA RD3 header data, create an object with custom metadata of a GPR segment."""

    def __init__(self, path, meta=None):
        """Read a RAD FILE and set attributes using the file content."""
        self.rad_path = self._get_rad_path(path)
        self._rad_to_metadata(path)

    def _get_rad_path(self, path):
        """Return the path to the RAD file."""
        p = get_file_path(path, ext='.rad')
        return(p)

    def _rad_to_metadata(self, path):
        """Set attributes using the dictionary of proprietary metadata."""
        d = self._rad_to_dict()
        m = self.metadata
        m.brand = 'MALA'
        m.traces =d['LAST TRACE']
        m.samples = d['SAMPLES']
        m.step = d['DISTANCE INTERVAL']
        m.frequency = d['FREQUENCY']
        m.start_position = d['START POSITION']
        m.system_calibration = d['SYSTEM CALIBRATION']

        m.x.values = self._get_trace_x()
        m.x.precision = 4
        m.y.values = self._get_trace_y()
        m.y.precision = 7

    def _rad_to_dict(self):
        """Convert header information to a dictionary of raw proprietary information."""
        d = rad2dict(self.rad_path)
        return(d)

    def write_rad(self):
        """"""
        d = self._rad_to_dict()
        print(d)


class RAD(MetaData):
    """From MALA RD3 header data, create an object with custom metadata of a GPR segment."""

    def __init__(self, path, meta=None):
        """Read a RAD FILE and set attributes using the file content."""
        self.rad_path = self._get_rad_path(path)
        self._rad_to_metadata(path)

    def _get_rad_path(self, path):
        """Return the path to the RAD file."""
        p = get_file_path(path, ext='.rad')
        return(p)

    def _rad_to_metadata(self, path):
        """Set attributes using the dictionary of proprietary metadata."""
        d = self._rad_to_dict()
        m = self.metadata
        m.brand = 'MALA'
        m.traces =d['LAST TRACE']
        m.samples = d['SAMPLES']
        m.step = d['DISTANCE INTERVAL']
        m.frequency = d['FREQUENCY']
        m.start_position = d['START POSITION']
        m.system_calibration = d['SYSTEM CALIBRATION']

        m.x.values = self._get_trace_x()
        m.x.precision = 4
        m.y.values = self._get_trace_y()
        m.y.precision = 7

    def _rad_to_dict(self):
        """Convert header information to a dictionary of raw proprietary information."""
        d = rad2dict(self.rad_path)
        return(d)

    def write_rad(self):
        """"""
        d = self._rad_to_dict()
        print(d)



class RD3(RAD):
    """Create a MALA object for use in general GPR methods. Note that slight variations in frequency between lines require rounding of the time interval to force equality of time-values between adjacent lines. Reading of separate files should be independent of one another so that the class does not fail if one is missing, or if an isolated file needs to be inspected."""

    def __init__(self, path, rad_path=None):
        self.basepath = path
        rad_path = rad_path if rad_path else path
        #RAD.__init__(self, rad_path)
        self.rd3_path = self._rd3_path(path)
        self.array = self._rd3_to_array()
        self._update_trace_number()

    def _rd3_path(self, path):
        """Return the path to the RAD file."""
        p = get_file_path(path, ext='.rd3')
        return(p)

    def _rd3_to_array(self):
        """Read RD3 file into a numpy array."""
        m = self.metadata
        a = rd32arr(self.rd3_path, m.samples)
        return(a)

    def _update_trace_number(self):
        """The trace number recorded in some DAT files has been found to occasionally be in error. The returned array is used here to update the metadata"""
        self.metadata.traces = self.array.shape[1]

    def arr2rd3(array, path):
        """Write an array """
        arr2rd3(array, path)

    def write(self, path):
        """Write rd3 to file"""
        b, e = splitext(path)
        arr2rd3(b + '.rd3', self.traces, self.samples)



class Line(MetaData, RadarGram):
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


