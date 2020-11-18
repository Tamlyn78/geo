
"""Process GPR data and produce radargrams and timeslices.

This module performs general tasks for processing GPR data non-specific to a commercial brand of file formats. Input data is typically read as numpy arrays produced from separate modules in this package specific to commercial file formats.
"""

from os.path import join
import numpy as np

from .gpr import MetaData, list_an_attribute, equal_list_elements as eqlst, RadarGram, TimeSlice, ns2mm

class Geometry(MetaData):
    def __init__(self, path):
        """Return a pandas dataframe of a csv containing the terminal Cartesian coordinates of each GPR line.
    CSV fields:
        id <int>: a unique row identifier for each GPR line record;
        folder <str>: the subfolder name relative to a parent directory containing GPR data;
        group: a unique group identifier for each GPR line (e.g. a survey number);
        filename <str>: the base filename (excluding extension) of a GPR line;
        x0 <float>: the cartesian starting x-coordinate;
        y0 <float>: the cartesian starting y-coordinate;
        x1 <float or str>: the cartesian ending x-coordinate ("+" or "-" may be used to indicate direction);
        y1 <float or str>: the cartesian ending y-coordinate ("+" or "-" may be used to indicate direction);
        notes <str>: line field notes.

        NB: x1 and y1 may be notated with "+" or "-" to indicate direction from the 
        """
        MetaData.__init__(self, path, self._columns())

    def _columns(self):
        """Return a list of attribute fields"""
        d = {
            'id':int, 
            'folder':str, 
            'group':str, 
            'filename':str, 
            'x0':float, 
            'y0':float, 
            'x1':str, 
            'y1':str, 
            'note':str,
        }
        return(d)

    def metadata(self, rdir):
        """Return a row of metadata dataframe as a series with a path field"""
        df = self.df
        if rdir:
            d = lambda x: str(x[1].folder)
            f = lambda x: str(x[1].filename)
            df['path'] = [join(rdir, d(i), f(i)) for i in df.iterrows()]
        s = [i[1] for i in df.iterrows()]
        return(s)
 
class Grid(MetaData):
    def __init__(self, path):
        """Return a pandas dataframe of a csv containing the terminal Cartesian coordinates of each GPR line.
    CSV fields:
        id <int>: a unique row identifier for each GPR line record;
        folder <str>: the subfolder name relative to a parent directory containing GPR data;
        group: a unique group identifier for each GPR line (e.g. a survey number);
        filename <str>: the base filename (excluding extension) of a GPR line;
        x0 <float>: the cartesian starting x-coordinate;
        y0 <float>: the cartesian starting y-coordinate;
        x1 <float or str>: the cartesian ending x-coordinate ("+" or "-" may be used to indicate direction);
        y1 <float or str>: the cartesian ending y-coordinate ("+" or "-" may be used to indicate direction);
        notes <str>: line field notes.

        NB: x1 and y1 may be notated with "+" or "-" to indicate direction from the 
        """
        MetaData.__init__(self, path, self._columns())

    def _columns(self):
        """Return a list of attribute fields"""
        d = {
            'id':int, 
            'x0':float, 
            'y0':float, 
            'easting0':float, 
            'northing0':float, 
            'bearing':float, 
            'note':str,
        }
        return(d)

    def metadata(self):
        """Return a row of metadata dataframe as a series with a path field"""
        df = self.df
        s = [i[1] for i in df.iterrows()]
        return(s)
   

class AdjustGrid:
    """Adjust the grid coordinates for each line so that the grid x-axis aligns with the radargram x-axis."""
    def __init__(self):
        self.wee()

    def wee(self):
        """"""
        attr = ['x0', 'y0', 'x1', 'y1']
        x0, y0, x1, y1 = [self._get_axis(i) for i in attr]
        try:
            [float(i) for i in x0] == [float(i) for i in x1]
            # swap axes and flip y-axis
            wee = zip(y0, x0[::-1], y1, x1[::-1])
            [self._update_line(i, *j) for i, j in zip(self.lines, wee)]
        except:
            pass # do nothing everything is already aligned

    def _get_axis(self, attribute):
        """"""
        lst = [getattr(i, attribute) for i in self.lines]
        return(lst)

    def _update_line(self, line, x0, y0, x1, y1):
        """"""
        wee = zip(('x0','y0','x1','y1'), (x0,y0,x1,y1))
        [setattr(line, i[0], i[1]) for i in wee]


class AlignRadarGrams:
    """Align the x-values of parallel GPR objects relative to a grid datum.
        Attributes:
            gpr <list>: a list of gpr objects;
            x <float>: the x-value of the survey grid datum;
            y <float>: the y-value of the survey grid datum.
    """
    def __init__(self, x, y):
        """Initialise and update gpr object x-values."""
        self.x = x
        [setattr(i, 'x', self._align_x(i)) for i in self.lines]

    def _align_x(self, line):
        """Return gpr x-values adjusted to align with the input datum."""
        p = line.x_precision
        x0 = line.x0
        try:
            traces = round(abs((self.x - x0) / line.step))
            lst = [round((self.x + i * line.step - x0), p) for i in range(int(traces*2))]
            a = [abs(i) for i in lst]
            idx = a.index(min(a))
            dx = round(lst[idx], p)
            x = [round(i + x0 + dx, p) for i in line.x]
        except:
            x = [round(i + x0, 4) for i in line.x]
        return(x)


class FillRadarGrams:
    def __init__(self, clip=None):
        """Fill radargrams with zeros to maximum and minimum x"""
        self.x = self._x()
        [self.update_x(i) for i in self.lines]

    def update_x(self, line):
        """Update the x-values for each listed line object"""
        x = self.x
        idx0 = x.index(min(line.x))
        idx1 = x.index(max(line.x)) + 1

        m, n = len(line.y), len(x)
        arr = np.zeros((m, n))
        arr[:,idx0:idx1] = line.array
        line.array = arr
       
    def _x(self):
        """Get the minimum and maximum x-values"""
        x0 = min([min(i.x) for i in self.lines])
        x1 = max([max(i.x) for i in self.lines])
        step = eqlst([i.step for i in self.lines])
        traces = round((x1 - x0) / step + 1)
        x = [round(x0 + i * step, 4) for i in range(traces)]
        return(x)


class StackLinesNew(AdjustGrid, AlignRadarGrams, FillRadarGrams):
    def __init__(self, list_of_lines, x0, y0):
        """"""
        self.lines = list_of_lines
        print([i.x0 for i in self.lines])
        #AdjustStep

class StackLines(AdjustGrid, AlignRadarGrams, FillRadarGrams, TimeSlice):
    def __init__(self, list_of_lines, x, y, grid=None):

        self.lines = list_of_lines
        AdjustGrid.__init__(self)
        AlignRadarGrams.__init__(self, x, y)
        FillRadarGrams.__init__(self)

        self.y = self._y()
        self.z = self._z()

        self.velocity = eqlst([i.velocity for i in self.lines])
        self.depth = [round(ns2mm(i/2, self.velocity)) for i in self.z]
        self.array = self._stack()

        TimeSlice.__init__(self)

    def _y(self):
        """"""
        y = [i.y0 for i in self.lines]
        return(y)

    def _z(self):
        """Clip to minimum z."""
        y0 = min([min(i.y) for i in self.lines])
        y1 = max([max(i.y) for i in self.lines])
        samples = max([i.samples for i in self.lines])
        time_interval = round(y1 / samples, 5)
        z = [round(y0 + i * time_interval, 5) for i in range(samples)]
        return(z)

    def _stack(self):
        """Stack the radargram arrays and rotate so that the first dimension returns the ground-surface slice"""
        a = np.stack([i.array for i in self.lines])
        a = np.rot90(a, axes = (1,0))
        a = np.flip(a, axis = 1)
        #a = np.rot90(a, axes = (1,2))
        return(a)

    def geometry(self):
        """Return a list of coordinate tuples representing the nodes of each line."""
        from shapely.geometry import LineString, MultiLineString, Point
        x0 = [min(i.x) for i in self.lines]
        x1 = [max(i.x) for i in self.lines]
        y = [i.y0 for i in self.lines]
        start = [i for i in zip(x0, y)]
        end = [i for i in zip(x1, y)]
        line = lambda x, y: LineString([Point(x), Point(y)])
        geom = [line(*i) for i in zip(start, end)]
        geom = MultiLineString(geom)
        return(geom)


