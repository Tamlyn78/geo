"""Tools to preprocess GPR lines before processing in third-party software such as ReflexW"""

from os.path import isfile, join
import numpy as np
import pandas as pd
import math
from collections import Counter

from .gpr import MetaData, x_flip, empty_array
from .mala import rad2dict, RD3, arr2rd3, Line
from .filesystem import list_gpr_data, get_folder_and_filename
from .calculations import ns2mm


class Coordinates(MetaData):
    """Append coordinate data to a loaded collection of parallel segments. It may be sensible to put the loaded data through a grouping class to enable filtering of non-parallel segments."""

    def __init__(self, segments, filename='segment_coordinates.csv', columns=[]):
        """
            Attributes:
                dat <object>: A LoadDAT object from the gpr module containing a list of GPR data files;
                filename <str>: Name of a CSV file containing, or to contain, segment coordinate data;
                columns <list>: List of filed names for the CSV file containing, or to contain, segment coordinate data.
        """
        segs = segments
        self.data_directory = segs.data_directory
        self.filename = filename

        self.segment_coordinates_csv = self._outfile()

        MetaData.__init__(self, self.segment_coordinates_csv, self._columns(columns))

        if self.metadata_is_empty():
            print('WARNING: No segment coordinates exist.')

        self.segments = [self._segment(i) for i in segs.segments]
        
    def _outfile(self):
        d = self.data_directory
        f = self.filename
        o = join(d, f)
        return(o)

    def _columns(self, columns):
        """Return a list of column names."""
        column_names = [
            'id', # unique integer identifier
            'x0', # x-coordinate at start of segment measurement
            'y0', # y-coordinate at end of segment measurement
            'x1', # x-coordinate at end of segment measurement
            'y1', # y-coordinate at end of segment measurement
            'coord_note'
        ]
        columns = columns if columns else column_names
        return(columns)

    def _segment(self, seg):
        """Return a Line object and append data from segment metadata."""
        uid = seg.id
        m = self.metadata
        meta = m.loc[m['id']==uid,].iloc[0]
        seg.x0 = meta.x0
        seg.y0 = meta.y0
        seg.x1 = meta.x1
        seg.y1 = meta.y1
        seg.coord_note = meta.coord_note
        return(seg)

    def _attr_to_dict(self, seg):
        """Return a dictionary of segment attributes"""
        m = seg
        d = {
            'id': m.id,
            'traces': m.traces,
            'samples': m.samples,
            'step': m.step,
            'frequency': m.frequency,
            'start_position': m.start_position,
            'x0': m.x0,
            'y0': m.y0,
            'x1': m.x1,
            'y1': m.y1,
            'coord_note': m.coord_note,
        }
        return(d)

from copy import copy

class ParallelGrid(MetaData):
    """Merge a collection of parallel segments into lines for processing as a grid. It is expected that the segments were measured from a single sub-grid."""

    def __init__(self, data, xd, yd, velocity=None):
        """
            Attributes:
                dat <object>: A LoadDAT object from the gpr module containing a list of GPR data files;
        """
        #self.data = segments
        self.segments = data.segments
        print(dir(self.segments[0].metadata))
        a = self.segments[0].metadata
        a.transect_coordinate = 6
        print(self.segments[5].metadata.transect_coordinate)
        exit()

        # define grid metadata
        self.axis = self._parallel_axis(s)
        self.distance_datum = xd if self.axis=='x' else yd
        self.transect_datum = xd if self.axis=='y' else yd
        self.step = self._grid_step(s)
        self.samples = self._grid_samples(s)
        self.frequency = self._grid_frequency(s)
        self.system_calibration = self._grid_system_calibration(s)
        self.line_spacing = self._line_spacing(s)
        self.time = self._grid_time()

        self.line_coords = self._transect_coords(s)

        directions = [self._segment_direction(i) for i in s]
        start = [self._start_position(i, d) for i, d in zip(s, directions)]
        xvalues = [self._x_values(i, x0) for i, x0 in zip(s, start)]

        print(s[7].metadata.start_position)
        for n, i in enumerate(s):
            i.metadata.start_position = start[n]

        print(s[7].metadata.start_position)
        exit()
            

        self.traces = self._traces(xvalues)

        self.distance_coords = [round(self.distance_datum + (i * self.step), 6) for i in range(self.traces)]
        self.velocity = velocity

        # segments to lines
        lines = []
        for c in self.line_coords:
            l = self._line()
            l.transect_coord = c
            lines.append(l)
            ax = 'x0' if self.axis=='y' else 'y0'
            segs = [i for i in s if getattr(i, ax)==c]
            #print(segs)

            #for i in segs:
                #print(i.array.shape)
                #x0, a = i
                #for n, j in enumerate(a):
                    #if x0+n < self.traces: # when a line was started forward of the grid datum, innacuracy in the filed position may cause the line to have more traces than the calculated empty array. The array must therefore be cut before an overrun occurs.
        #            line.array[:,x0+n] = j
        #line.array = np.int16(line.array)
 
        #print(lines)
        #print(lines[0].transect_coord)
        #print(lines[1].transect_coord)
        #l = [self._line() for n, i in enumerate(self.line_coords)]
        #a, b = l[0:2]
        #a.transect_coord = 5
        #b.transect_coord = 6
        #print(a.transect_coord)
        #print([.transect_coord for i in l])
        exit()
        self.lines = [self._line(i) for n, i in enumerate(self.line_coords)]
        #print(dir(s[0]))
        #print(s[0].x0)
        print([i.metadata for i in self.lines])
        print(dir(self.lines[0].metadata))
        exit()
        for i in self.lines:
            t_coord = i.metadata.transect_coord
            print(t_coord)
            wee = 'x0' if self.axis=='y' else 'y0'
            #print(wee)
            segs = [copy(i) for i in s if getattr(i, wee)==t_coord]
            segs = [copy(i) for i in s if getattr(i, wee)==110.0]
            print(segs)

        #print([i.x0 for i in s])
        
        #self.set_line_filenames()

        #arrays = [self._x_flip(i, d) for i, d in zip(s, directions)]
        #self.array = self._3darray()

    def _parallel_axis(self, segment_list):
        """Determine the parallel grid axis."""
        ax = list(set([self._segment_axis(i) for i in segment_list]))
        if len(ax)>1:
            raise Exception('ERROR: segments must be parallel. Please check segment metadata.')
            print(self.get_metadata())
        return(ax.pop())

    def _segment_axis(self, seg):
        """Determine the axis each segment is parallel to."""
        try:
            float(seg.x1)
            axis = 'y'
        except:
            axis = 'x'
            try:
                float(seg.y1)
            except:
                print('Line is not parallel. Please check segment geometry.')
        return(axis)

    def _grid_step(self, segment_list):
        step = list(set([i.metadata.step for i in segment_list]))
        if len(step)>1:
            raise Exception('ERROR: segments steps must be equal. Please check segment metadata.')
        return(step.pop())

    def _grid_samples(self, segment_list):
        """"""
        samples = list(set([i.metadata.samples for i in segment_list]))
        if len(samples)>1:
            raise Exception('ERROR: segments samples must be equal. Please check segment metadata.')
        return(samples.pop())
 
    def _grid_frequency(self, segment_list):
        """"""
        frequency = Counter([i.metadata.frequency for i in segment_list]).most_common()[0][0]
        return(frequency)

    def _grid_system_calibration(self, segment_list):
        """"""
        calib = Counter([i.metadata.system_calibration for i in segment_list]).most_common()[0][0]
        return(calib)

    def _line_spacing(self, segment_list):
        """Return the line spacing"""
        ax = 'x0' if self.axis=='y' else 'y0'
        t = list(set([getattr(i, ax) for i in segment_list]))
        t.sort(reverse=True)
        spacing = min(list(set([t[i]-t[i+1] for i in range(len(t)-1)])))
        return(spacing)

    def _transect_coords(self, segments):
        """Return the transect coordinates of a group of segments."""
        ax = 'x0' if self.axis=='y' else 'y0'
        t = list(set([getattr(i, ax) for i in segments]))
        t0, t1 = min(t), max(t)
        line_count = math.floor((t1-t0)/self.line_spacing)
        coordinates = [t0 + i * self.line_spacing for i in range(line_count)]
        return(coordinates)

    def _grid_time(self):
        """"""
        time = [round((i) * 1 / self.frequency * 1000, 6) for i in range(self.samples)]
        return(time)

    def _segment_direction(self, seg):
        """Return the positive or negative direction of a segment."""
        x1, y1, ax = seg.x1, seg.y1, self.axis
        d = x1 if ax=='x' else y1
        return(d)

    def _start_position(self, seg, direction):
        """Set the start position of a segment."""
        start = seg.x0 if self.axis=='x' else seg.y0
        start = start if direction=='+' else start - (seg.metadata.traces * self.step)
        x0 = self.distance_datum
        distance = round(start - x0, 6)
        traces = round(distance / self.step, 6)
        tmin = round(math.floor(traces) * self.step, 6)
        tmax = round(math.ceil(traces) * self.step, 6)
        start = tmin if abs(distance-tmin)<=abs(distance-tmax) else tmax
        start = round(start + x0, 6)
        return(start)

    def _x_values(self, seg, x0):
        """"""
        m = seg.metadata
        traces = m.traces
        dx = m.step
        x = [x0 + (i * dx) for i in range(traces)]
        return(x)
 
    def _x_flip(self, seg, direction):
        """Flip the segment array along the radargram x-axis if direction is negative."""
        a = seg.array if direction=='+' else x_flip(seg.array)
        return(a)

    def _traces(self, xvalues):
        """"""
        x0 = min([min(i) for i in xvalues])
        x1 = max([max(i) for i in xvalues])
        t = int((x1 - x0) / self.step)
        return(t)

    def _line(self):
        """Fill an empty line with associated segments and return."""
        m, n = len(self.time), self.traces
        line = Line(m, n)
        line.metadata.start_position = self.distance_datum
        line.metadata.traces = self.traces
        line.metadata.samples = self.samples
        line.metadata.time = self.time
        line.metadata.step = self.step
        line.metadata.frequency = self.frequency
        line.metadata.system_calibration = self.system_calibration
        return(line)

    def wee(self, line):
        """"""
        print(line.metadata)
        print(line.metadata.transect_coord)
        print(dir(line.metadata))
        seg = self._line_segments(line.metadata.transect_coord)
        print(seg)
        #for i in self._line_segments(coord):
            #print(i)
        #    x0, a = i
        #    for n, j in enumerate(a):
        #        if x0+n < self.traces: # when a line was started forward of the grid datum, innacuracy in the filed position may cause the line to have more traces than the calculated empty array. The array must therefore be cut before an overrun occurs.
        #            line.array[:,x0+n] = j
        #line.array = np.int16(line.array)
        return(line)

    def _line_segments(self, coord):
        """Return an iterater including the start trace and transposed array of all segments occurring at a given transect coordinate. The segment arrays are returned transposed to allow iteration through columns."""
        s = [i for i in self.data.segments if i.x0==coord]
        #if coord==108:
        #    a, b = s
        #    print(a.metadata.start_position)
        #    print(b.metadata.start_position)

        a = [i.array.T for i in s]
        t0 = [int(round((i.metadata.start_position - self.distance_datum) / self.step, 6)) for i in s]
        #print(t0)
        return(zip(t0, a))
 
    def _3darray(self):
        """Stack and rotate a 3D array so that the lines are oriented to the survey grid. Iteration should occur through the time dimension."""
        a = np.stack([i.array for i in self.lines])
        return(a)

    def set_line_filenames(self, prefix='LINE', name_list=None, suffix=''):
        """Set the output filename for each line."""
        if not name_list:
            name_list = [prefix + str(int(i*100)) + suffix for i in self.line_coords]
        for l, n in zip(self.lines, name_list):
            l.filename = n

    def radargrams(self, directory, time=True, distance=True, depth=True):
        """Output jpg radargrams."""
        d = directory
        for i in self.lines:
            i.plot()
            if distance:
                i.x_axis(self.distance_coords)
            if time:
                i.y_axis(self.time)
            if depth:
                i.y2_axis([round(ns2mm(i, 0.1) / 1000, 3) for i in self.time])
            path = join(d, i.filename + '.jpg')
            if not isfile(path):
                i.jpg(path)
            i.close()
 
    def export_line_arrays(self, directory):
        """"""
        d = directory
        for i in self.lines:
            path = join(directory, i.filename + '.rd3')
            rd3 = join(directory, i.filename + '.rd3')
            if not isfile(rd3):
                arr2rd3(i.array, rd3)
            rad = join(directory, i.filename + '.rad')
            if not isfile(rad):
                with open(rad, 'w') as f:
                    f.write('SAMPLES:' + str(self.samples) + '\r\n')
                    f.write('FREQUENCY:' + str(self.frequency) + '\r\n')
                    f.write('FREQUENCY STEPS: 1' + '\r\n')
                    f.write('SIGNAL POSITION: 0' + '\r\n')
                    f.write('RAW SIGNAL POSITION: 0' + '\r\n')
                    f.write('DISTANCE FLAG: 1' + '\r\n')
                    f.write('TIME FLAG: 0' + '\r\n')
                    f.write('PROGRAM FLAG: 0' + '\r\n')
                    f.write('EXTERNAL FLAG: 0' + '\r\n')
                    f.write('TIME INTERVAL: 0' + '\r\n')
                    f.write('DISTANCE INTERVAL:' + ' ' + str(self.step) + '\r\n')
                    f.write('OPERATOR:' + '\r\n')
                    f.write('CUSTOMER:' + '\r\n')
                    f.write('SITE:' + '\r\n')
                    f.write('ANTENNAS:   500' + '\r\n')
                    f.write('ANTENNA ORIENTATION:' + '\r\n')
                    f.write('ANTENNA SEPARATION:    0.1800' + '\r\n')
                    f.write('COMMENT:Unknown=6' + '\r\n')
                    f.write('TIMEWINDOW:   29.1982' + '\r\n')
                    f.write('STACKS: 1' + '\r\n')
                    f.write('STACK EXPONENT: 1' + '\r\n')
                    f.write('STACKING TIME: 0' + '\r\n')
                    f.write('LAST TRACE:' + str(self.traces) + '\r\n')
                    f.write('STOP POSITION:' + ' ' + str.format('{0:.6f}', max(self.distance_coords)) + '\r\n')
                    f.write('SYSTEM CALIBRATION:' + str.format('{0:.10f}', self.system_calibration) + '\r\n')
                    f.write('START POSITION:' + str.format('{0:.6f}', min(self.distance_coords)) + '\r\n')
 

class Segment:
    """A line object. This class should be in the 'gpr' module but I can't seem to work out how to import it. It may be a circular import problem because gpr also imports from 'mala'"""

    def get_empty_array(self, m, n):
        """Return an empty array"""
        arr = np.zeros([m, n])
        return(arr)


