
"""Process GPR data and produce radargrams and timeslices.

This module performs general tasks for processing GPR data non-specific to a commercial brand of file formats. Input data is typically read as numpy arrays produced from separate modules in this package specific to commercial file formats.

Workflow:

    2D Survey:
        Tasks:
        1 - from a user-defined storage, process the lines using a third-party software, then output images to any user-defined directory


        Solution:
        1 - methods to read data in outputted format
        2 - methods to generate a consistent but flexible radargram image

    3D Survey:
        Tasks:
        1 - from a user-defined storage, process the lines using a third-party software, then output images to any user-defined directory
        


    When processing MALA data the first thing to do is process the lines for production to radargrams and timeslices


New workflow in progress:

    1 - create a spreadsheet for each survey group; a survey group would normally represent a rectangle of lines measured to produce timeslices, but can be any form of data-splitting; a group should include a grid id   

    2 - create a spreadsheet describing the coordinate system of the grids used on the ground; for most surveys only 1 grid might be necessary (e.g. all x-y coordinates are relative to eachother for all survey groups), but multiple might be necessary for logistical reasons; a grid should include an x-origin y-origin and optionally an easting and northing and angle it should be rectified to.

    1 - create a spreadsheet of processing data (reflexw); for each survey group the name of the reflexw plf file should be given and a note describing the aim of processing (e.g. a procedure for radargram production vs another for timeslices).
    2 - create a spreadsheet of segment data; each row describes a line of GPR data and should include the folder name containing the data, the survey group it belongs to, the filename (without extension), the x0 y0 x1 y1 coordinate data, and a note.

    3 - script should 

"""

from os import listdir, makedirs, walk
from os.path import basename, isdir, join, splitext
import csv
from glob import glob
import itertools
import tempfile
import numpy as np
import pandas as pd
import math
import statistics
import matplotlib.pyplot as plt
from matplotlib import cm

from ...gis.raster import RectifyTif
from .mala import RD3
#from .calculations import *
from .filesystem import list_gpr_data, get_folder_and_filename

def x_flip(a):
    """Flip the x-axis of a radargram numpy array"""
    a = np.flip(a, axis=1)
    return(a)

def empty_array(rows, columns):
    """"""
    rg = np.zeros(m, n)
    arr = np.stack([rg for i in range(len(self.x))])
    return(arr)

def line_to_ascii4(line, path):
    """Convert a line object to ASCII 3-columns"""
    x = line.start_position
    y = line.transect_coord
    print(line.array.shape)
    with open(path, 'w') as f:
        for array in line.array.T:
            for amp, time in zip(array, line.time):
                s = lambda x: str.format('{0:.6f}', x)[::-1]
                d = s(x)
                l = s(y)
                t = s(time)
                a = s(amp)
                
                wee = str(a.ljust(15) + t.ljust(15) + l.ljust(15) + d.ljust(14))[::-1] + '\r\n'
                f.write(wee)
                
                #print(a)
                #f.write(str.format('{0:.6f}', x) + '\t' + str.format('{0:.6f}', time) + '\t' + str.format('{0:.6f}', amp) + '\r\n')
            x = round(x + line.step, 6)


def line_to_ascii3(line, path):
    """Convert a line object to ASCII 3-columns"""
    x = line.start_position
    print(line.array.shape)
    with open(path, 'w') as f:
        for array in line.array.T:
            for amp, time in zip(array, line.time):
                s = lambda x: str.format('{0:.6f}', x)[::-1]
                d = s(x)
                t = s(time)
                a = s(amp)
                
                wee = str(a.ljust(15) + t.ljust(15) + d.ljust(14))[::-1] + '\r\n'
                f.write(wee)
                
                #print(a)
                #f.write(str.format('{0:.6f}', x) + '\t' + str.format('{0:.6f}', time) + '\t' + str.format('{0:.6f}', amp) + '\r\n')
            x = round(x + line.step, 6)

def line_to_ascii1(line, path):
    """Convert a line object to ASCII 1-column"""
    with open(path, 'w') as f:
        for array in line.array.T:
            for amp, time in zip(array, line.time):
                s = lambda x: str.format('{0:.6f}', x)[::-1]
                a = s(amp)
                
                wee = str(a.ljust(15))[::-1] + '\r\n'
                f.write(wee)
                

class MetaData:
    """A parent class to create a csv for metadata logging and loading. The attributes of the metadata are defined by the child class.
        Attributes:
            path <str>: A filesystem path to the required csv location;
            cols <list>: A list of strings representing the header columns of 
                the csv.
    """
    def __init__(self, path, cols):
        """Create a csv if not exists and load a dataframe"""
        self.path, self.cols = path, cols
        self._to_csv()
        self.metadata = self._to_df()

    def _to_csv(self):
        """Create a CSV in the specified path."""
        try:
            with open(self.path, 'x', newline='') as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow([i for i in self.cols])
        except Exception as e:
            print(e)

    def _to_df(self):
        """Return a pandas dataframe. Improvements might include specification of data type."""
        df = pd.read_csv(self.path)
        return(df)

    def metadata_is_empty(self):
        """Return True if the CSV has no data."""
        m = self.metadata
        return(m.empty)
        
    def prepopulate_csv(self, list_of_tuples):
        """Append data to the CSV.
            Attributes:
                list_of_data <list of tuples>: A list of tuples containing the field data for each line."""
        with open(self.path, 'a', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for n, i in enumerate(list_of_tuples, start=1):
                w.writerow([n] + [j for j in i])


class GroupData(MetaData):
    """Group GPR data for further processing. Loaded data can be passed through as many times as necessary for where multiple groups are necessary."""
    def __init__(self, dat, filename='groups.csv', columns=[]):
        self.data_directory = dat.data_directory
        self.filename = filename

        self.groups_csv = self._outfile()

        MetaData.__init__(self, self.groups_csv, self._columns(columns))

        if self.metadata_is_empty():
            print('WARNING: No group data exists.')

        try:
            self.metadata = pd.concat([dat.metadata, self.metadata.drop('id', axis=1)], axis=1)
        except Exception as e:
            print(e)

        self.segments = dat.segments

    def _outfile(self):
        d = self.data_directory
        f = self.filename
        o = join(d, f)
        return(o)

    def _columns(self, columns):
        """Return a list of column names."""
        column_names = [
            'id',
            'group',
            'group_note'
        ]
        columns = columns if columns else column_names
        return(columns)


class Segments(MetaData):
    """Load GPR data contained in a given folder. Create a CSV file within the given folder listing the subdirectory and filename of the GPR data."""

    def __init__(self, data_directory, filename='segment_files.csv', extension='rd3', columns=[]):
        """Attributes:
            data_directory <str>: A filesystem path to a folder containing GPR data. The data should be kept in subfolders of the path.)"""

        self.data_directory = data_directory
        self.filename = filename
        self.extension = extension

        csv = self.segment_files_csv = self._outfile()
        cols = self._columns(columns)

        MetaData.__init__(self, csv, cols)
        if self.metadata.empty:
            lst = self._listdir()
            lst = [i + [''] for i in lst]
            self.prepopulate_csv(lst)

        fmt = self._get_format(extension)
        m = self.metadata
        self.segments = [self._segment(i, fmt) for n, i in m.iterrows()]

    def _outfile(self):
        d = self.data_directory
        f = self.filename
        o = join(d, f)
        return(o)

    def _columns(self, columns):
        """Return a list of column names."""
        column_names = [
            'id',
            'folder',
            'filename',
            'dat_note'
        ]
        columns = columns if columns else column_names
        return(columns)

    def _listdir(self):
        """"""
        d = self.data_directory
        e = self.extension
        lst = list_gpr_data(d, e)
        meta = [get_folder_and_filename(i) for i in lst]
        return(meta)    

    def _segment(self, metadata, fmt):
        """Return a Line object and append data from segment metadata."""
        m = metadata
        path = self._basepath(m)
        seg = fmt(path)
        seg.id = m.id
        seg.dat_note = m.dat_note
        return(seg)

    def _basepath(self, row):
        """Return the path to a GPR line from a row of metadata."""
        d = self.data_directory
        fd = str(row['folder'])
        fn = str(row['filename'])
        path = join(d, fd, fn)
        return(path)

    def _get_format(self, ext):
        """"""
        if ext=='rd3':
            return(RD3)

    def to_df(self):
        """"""
        s = self.segments
        df = pd.DataFrame([{**{'id':i.id}, **i.metadata_to_dict()} for i in s])
        return(df)


    def groups(self):
        """Create categorical groups and append metadata"""
        


class RadarGram:
    """Plot a radargram using a GPR object"""

    def __init__(self, array):
        self.array = array

    def plot(self, xlab='Traces', ylab='Samples', cmap='Greys_r', aspect='auto', interpolation='bicubic', vmin=None, vmax=None):
        fig = plt.figure(figsize=(29.7/2.54, 21/2/2.54))
        self.ax = plt.axes()
        a = self.array
        self.ax.imshow(a, cmap=cmap, aspect=aspect, interpolation=interpolation, vmin=vmin, vmax=vmax)
        self.ax.set_xlabel(xlab)
        self.ax.set_ylabel(ylab)

    def x_axis(self, x, zero=False, axis_label='Distance (m)'):
        """"""
        self.ax.set_xlabel(axis_label)
        labs = [i for i in range(round(min(x)), round(max(x)) + 1, 2)]
        ticks = [(i-labs[0]) / (x[1]-x[0]) for i in labs]
        plt.xticks(ticks, labs)
 
    def y_axis(self, y, zero=False, axis_label='Time (ns)'):
        """"""
        self.ax.set_ylabel(axis_label)
        labs = [i for i in range(0, round(max(y)) + 1, 10)]
        ticks = [i/(y[1]-y[0]) for i in labs]
        plt.yticks(ticks, labs)

    def y2_axis(self, y, axis_label='Depth (m)'):
        """"""
        ax = self.ax.twinx()
        ax.set_ylabel(axis_label)
        labs = list(set([math.floor(i) for i in y]))
        ticks = [1 - (1/max(y) * i) for i in labs]
        plt.yticks(ticks, labs)

    def show(self):
        """Display current radargram plot."""
        plt.show()

    def jpg(self, path, dpi=150, bbox_inches='tight', pad_inches=0):
        """Save radargram plot to file."""
        if not path.lower().endswith('.jpg'):
            path += 'jpg'
        print(path)
        plt.savefig(path, dpi=dpi, format='jpg', bbox_inches=bbox_inches, pad_inches=pad_inches)

    def close(self):
        """Close the plot."""
        plt.close()















#######################
class MetaDataBak:
    """A parent class to create a csv for metadata logging and loading. The attributes of the metadata are defined by the child class.
        Attributes:
            path <str>: A filesystem path to the required csv location;
            cols <list>: A list of strings representing the header columns of 
                the csv.
    """
    def __init__(self, path, cols):
        """Create a csv if not exists and load a dataframe"""
        self.path, self.cols = path, cols
        self._create_csv()

    def _create_csv(self):
        """Create a CSV in the specified path."""
        try:
            with open(self.path, 'x', newline='') as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow([i for i in self.cols])
        except Exception as e:
            print(e)

    def get_df(self):
        """Return a pandas dataframe. Improvements might include specification of data type."""
        df = pd.read_csv(self.path)
        return(df)

    def metadata_is_empty(self):
        """Return True if the CSV has no data."""
        df = self.get_df()
        return(df.empty)
        
    def add_metadata(self, list_of_data):
        """Append data to the CSV.
            Attributes:
                list_of_data <list of tuples>: A list of tuples containing the field data for each line."""
        with open(self.path, 'a', newline='') as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL)
            for n, i in enumerate(list_of_data, start=1):
                w.writerow([n] + [j for j in i])
        










##############################################################################










        

class SurveyDat:
    """Load all raw survey data into an object for further processing."""
    def __init__(self, rdir, datdir='data', procdir='processing', outdir='output', imdir='imagery'):
        """Create filesystem; gpr survey data into the folder named 'data'."""

        lst = [datdir, procdir, outdir, imdir]
        d, p, o, i = [self.mkdir(join(rdir, i)) for i in lst]
        self.rdir = rdir
        self.datdir = d
        self.procdir = p
        self.outdir = o
        self.imdir = i

    def mkdir(self, d):
        if not isdir(d):
            makedirs(d)
        return(d)
 
    def segments(self, datdir, outname='segments'):
        """Create a csv of GPR data files located in subdirectories of datdir."""
        d = sorted([i for i in listdir(datdir) if isdir(join(datdir, i))])
        if not d:
            raise ValueError("\n\n   There are no GPR files located in subdirectories of '" + datdir + "'. Please add them and re-run program.\n")
            
        t = []
        for i in d:
            flst = listdir(join(datdir, i))
            fnames = sorted(list(set([splitext(j)[0] for j in flst])))
            t += [(n, i, j) for n, j in enumerate(fnames, start=1)]
            
        outpath = join(datdir, outname + '.csv')
        try:
            with open(outpath, 'x') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['id', 'folder', 'filename', 'note'])
                for i, d, f in t:
                    writer.writerow([i,d,f])
        except Exception as e:
            print(e)




           


#
class ParrallelLines:
    """An object of parallel lines"""
    def __init__(self):
        """"""


class AlignX:
    """Align the x-axes of a parallel line."""

    def __init__(self, line):
        """Attributes:
            line <Line>: An initialised  Line object from the current module.
        """
        self.y0 = line.y0
        self.x0 = line.x0
        self.step = line.step
        self.traces = line.traces
        self.get_x0 = line.get.x0
        self.get_dx = line.get_dx
        self._round_x = line._round_x

    def align_x(self, datum=0):
        """Align the x-values to a given datum value"""
        x0 = self.get_x0()
        dx = self.get_dx(datum, x0)

        if self.x1 == '+' or self.y1 == '+':
            sign = 1
        else:
            sign = -1
 
        self.x = [self._round_x(x0 + dx + sign * i * self.step) for i in range(self.traces)]


class LineBak(AlignX):
    """Create an object of GPR data and metadata sourced from a pandas series."""
    def __init__(self, metadata, gpr_type, velocity=None):
        """
        Use a pandas series of metadata to create an object of GPR data.
            Attributes:
                gpr_format <class>: A class specific to a GPR type (e.g. MALA)
                    that include a 'path' input.
                metadata <pandas.Series>: A series of metadata that includes a field named 'path'. The path is used in 'gpr_format'. 
        """
        self._add_meta(metadata)
        self._add_gpr(gpr_type)
        self._add_velocity(velocity)

    def _add_meta(self, s):
        for k, v in zip(s.index, s.values):
            setattr(self, k, v)

    def _add_gpr(self, gpr_type):
        obj = gpr_type(self.path)
        self.__dict__.update(obj.__dict__)

    def _add_velocity(self, velocity):
        """"""
        self.velocity = velocity

    def _round_x(self, x):
        """Round a value to the line x-axis precision."""
        a = round(x, self.x_precision)
        return(a)

    def _round_y(self, y):
        """Round a value to the line x-axis precision."""
        a = round(y, self.y_precision)
        return(a)

    def get_line_increment(self):
        """Return the origin of the line x-axis."""
        try:
            if float(self.x0) == float(self.x0):
                y0 = self.x0
        except:
            if float(self.y0) == float(self.y1):
                y0 = self.y0
        return(y0)

    def get_x0(self):
        """Return the origin of the line x-axis."""
        try:
            if float(self.x0) == float(self.x0):
                x0 = self.y0
        except:
            if float(self.y0) == float(self.y1):
                x0 = self.x0
        return(x0)

    def get_dx(self, datum, x0):
        """Find the displacement required to align x-values with datum"""
        traces = math.ceil(abs(datum - x0) / self.step)
        if traces == 0:
            dx = 0
        else:
            x = [self._round_x(x0 - self.step * i) for i in range(traces)]
            dx = self._round_x(datum - x[-1])
        return(dx)


class RadarGram:
    """Plot a radargram using a GPR object"""

    def __init__(self, array, x, y):
        self.array = array
        self.x = x
        self.y = y

    def plot(self, xlab='Distance (m)', ylab='Time (ns)', y2lab='Depth (m)', velocity=None, vmin=None, vmax=None):
        fig = plt.figure(figsize=(29.7/2.54, 21/2/2.54))
        ax1 = plt.axes()
        a = self.array
        #ax1.imshow(a, cmap = 'Greys_r', aspect = 'auto', interpolation = 'bicubic')
        ax1.imshow(a, cmap = 'Greys_r', aspect = 'auto', interpolation = 'bicubic', vmin=vmin, vmax=vmax)
        self.x_labels(ax1, xlab)
        self.y_labels(ax1, ylab)
        self.y2_labels(ax1, y2lab, velocity)
        return(plt)

    def x_labels(self, ax, label):
        
        ax.set_xlabel(label)
        x = [i - self.x[0] for i in self.x]
        labs = [i for i in range(round(min(x)), round(max(x)) + 1, 3)]
        ticks = [(i-labs[0]) / (x[1]-x[0]) for i in labs]
        plt.xticks(ticks, labs)
    
    def y_labels(self, ax, label):
        ax.set_ylabel(label)
        y = self.y
        labs = [i for i in range(0, round(max(y)) + 1, 10)]
        ticks = [i/(y[1]-y[0]) for i in labs]
        plt.yticks(ticks, labs)

    def y2_labels(self, ax, label, velocity):
        """"""
        try:
            ax2 = ax.twinx()
            ax2.set_ylabel(label)
            y, v = self.y, velocity
            d = [ns2mm(i/2, v) / 1000 for i in y]
            mn, mx = math.floor(min(d)), math.ceil(max(d))
            labs = [i for i in range(mn, mx)]
            near = lambda x: abs(min([i-x for i in d]))
            locs = [1-(near(i)/max(d)) for i in labs]
            plt.yticks(locs, labs)
        except Exception as e:
            print(e)


class Stack:
    def __init__(self, list_of_lines, x0=0, length=None, width=None, velocity=None):
        """"""
        #[i.align_x(x0) for i in list_of_lines]
        for i in list_of_lines:
            i.align_x(x0)
                

        self.lines = list_of_lines

        self.step = self._get_attr('step')
        self.precision = self._get_attr('x_precision')

        self.x = self._get_x()
        self.y = self._get_y(x0, length)
        self.z = self._get_z()
        self.times = self._get_times()
        self.velocity = velocity
        self.depths = self._get_depths()

        line = self._empty_line()

        # this array is oriented to plot radargrams from the origin
        self.array = np.stack([self.wee(i) for i in self.x])

    def _get_x(self):
        x = list(set([i.get_line_increment() for i in self.lines]))
        x.sort()
        spacing = self._get_line_spacing(x)
        total_lines = int((max(x) - min(x)) / spacing)
        x = [min(x) + spacing * i for i in range(total_lines)]
        return(x)

    def _get_y(self, x0, length):
        x1 = x0 + length if length else max([max(i.x) for i in self.lines])
        traces = math.ceil((x1 - x0) / self.step)
        x = [round(x0 + self.step * i, self.precision) for i in range(traces)]
        return(x)

    def _get_z(self):
        samples = [i for i in range(self._get_attr('samples'))]
        return(samples)

    def _get_times(self):
        frequency = self._get_attr('frequency', mode=True)
        samples = len(self.z)
        ns = time(frequency, samples)
        return(ns)

    def _get_depths(self):
        """"""
        v = self.velocity
        if v:
            times = self.times
            m = [round(ns2mm(i, v) / 2 / 1000, 4) for i in times]
            return(m)
        else:
            return(None)

    def _get_line_spacing(self, y):
        lst = [j - i for i, j in zip(y[:-1], y[1:])]
        mode = statistics.mode(lst)
        return(mode)

    def _get_attr(self, attribute, mode=False):
        lst = [getattr(i, attribute) for i in self.lines]
        if mode:
            m = statistics.mode(lst)
            return(m)
        unique_values = list(set(lst))
        # need to raise error when list length is greater than 1
        return(unique_values.pop())

    def _empty_line(self):
        """Return a line of zeros"""
        m = len(self.z)
        n = len(self.y)
        arr = np.zeros((m, n)) 
        return(arr)

    def wee(self, x):
        """"""
        arr = self._empty_line()
        lines = [i for i in self.lines if i.get_line_increment() == x]
        for i in lines:
            arr = self._update_array(arr, i)
        return(arr)
        
    def _update_array(self, arr, line):
        """"""
        for n, i in enumerate(line.x):
            if i in self.y: # lines may exceed length of the empty array
                col = line.array[:,n]
                idx = [n for n, j in enumerate(self.y) if j == i].pop()
                arr[:,idx] = col
        return(arr)
       

    def poo(self, stack, top, bottom):
        """"""
        mm = stack.depths
        idx = [n for n, i in enumerate(mm) if i > top and i <= bottom]
        lst = [stack.array[i] for i in idx]
        arr_sum = sum([abs(i) for i in lst])
        arr_norm = arr_sum / arr_sum.max()
        return(arr_norm)

    def bum(self, thickness):
        """"""
        # rotate stack to be in order of timeslices
        array = np.rot90(self.array, axes=(0,1))
        # reverse array to make ground surface the top
        array = np.flip(array, axis=[0])
        mm = [i for i in self.depths]
        poo = self.chunks(mm, 50 / 1000) 
        wee = []
        for i in poo:
            idx = [n for n, j in enumerate(self.depths) if j in i]
            lst = [array[j] for j in idx]
            arr_sum = sum([abs(j) for j in lst])
            arr_norm = arr_sum / arr_sum.max()
            wee += [arr_norm]

        return(wee)


    def chunks(self, l, n):
        """Yield successive n-sized chunks from l."""
        pee = n
        lst = []
        while (n < max(l)):
            lst += [[i for i in l if i >= n-pee and i <= n]]
            n = n+pee
        return(lst)



class TimeSlice(RectifyTif):
    """"""
    def __init__(self):
        """"""


    def plot(self, array, x, y, levels=5, cmap='rainbow'):
        """Name of method changed to avoid conflict with radargram plot method; other plot method should be deleted in time."""

        

        #x = [i - xwee.x[0] for i in xwee]
        #y = [i - ywee.y[0] for i in ywee]
    
        line_spacing = abs(round(y[1] - y[0], 4))
        distance_interval = abs(x[1] - x[0])

        # create a 21 x 21 vertex mesh
        X, Y = np.meshgrid(np.linspace(min(x), max(x), len(x)), np.linspace(min(y), max(y), len(y)))

        x_ratio = len(x) * distance_interval
        y_ratio = len(y) * line_spacing

        fig, ax1 = plt.subplots(figsize = (21 / 2.54 / 2, 21 / 2 / 2.54 * y_ratio / x_ratio))
        
        levels=5
        import matplotlib as mpl
        #cset = ax1.contourf(X, -Y, array, levels, norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        #cset = ax1.contourf(X, -Y, array, levels, cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        cset = ax1.contourf(X, -Y, array, levels, cmap=cmap)

        y_min = min([abs(i) for i in y])
        y_max = max([abs(i) for i in y])
        yticks = [i for i in ax1.get_yticks() if abs(i) <= y_max and abs(i) >= y_min]
        plt.yticks(yticks, [abs(i) for i in yticks])

        # set axis labels
        #ax1.set_xlabel('Distance (m)')
        #ax1.set_ylabel('Distance (m)')
        plt.axis('off')

        return(plt)

    def jpg(self, path, array, levels=50, cmap=cm.Spectral, axis=True, dpi=150, format='jpg', bbox_inches='tight', pad_inches=0):
        """Remove the axes of a timeslice for spatial recification"""
        plt = self.plot(array, levels, cmap) 
        if axis == False:
            plt.axis('off')
        plt.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close()
        
    def tif(self, path, array, levels=50, cmap=cm.Spectral, axis=False, dpi=150, format='tif', bbox_inches='tight', pad_inches=0):
        """Remove the axes of a timeslice for spatial recification"""
        plt = self.plot(array, levels, cmap) 
        if axis == False:
            plt.axis('off')
        plt.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close()
 







#####################################################################




class LineNodes(MetaData):
    """This class contains a fixed set of fields for creation of a CSV file used for logging the terminal Cartesian coordinates of a set of GPR lines."""

    def __init__(self, path):
        """Initiate the MetaData class for creating the CSV file if it does not exist."""
        MetaData.__init__(self, path, self._columns())

    def _columns(self):
        """
        Return a list of fields required for the CSV file:
            id <int>: unique row identifier for each GPR line record;
            folder <str>: a subfolder name relative to a parent directory containing all the project GPR data;
            group <str>: a unique group identifier for each GPR line (e.g. a survey number or date);
            filename <str>: the base filename (excluding extension) of a GPR line;
            x0 <float>: the cartesian starting x-coordinate;
            y0 <float>: the cartesian starting y-coordinate;
            x1 <float or str>: the cartesian ending x-coordinate ("+" or "-" may be used to indicate direction);
            y1 <float or str>: the cartesian ending y-coordinate ("+" or "-" may be used to indicate direction);
        notes <str>: line field notes.
        
        NB: x1 and y1 may be notated with "+" or "-" to indicate direction from the 
"""

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
    

class RadarGramNew:
    """Plot a radargram using a GPR object; this is for standalone use rather than import"""

    def __init__(self, array, x, y, velocity=None):
        self.array = array
        self.x = x
        self.y = y
        self.v = velocity

    def plot(self, xlab='Distance (m)', ylab='Time (ns)', y2lab='Depth (m)', velocity=None):
        fig = plt.figure(figsize=(29.7/2.54, 21/2/2.54))
        ax1 = plt.axes()
        a = self.array
        ax1.imshow(a, cmap = 'Greys_r', aspect = 'auto', interpolation = 'bicubic')
        self.x_labels(ax1, xlab)
        self.y_labels(ax1, ylab)
        if self.v:
            self.y2_labels(ax1, y2lab)
        return(plt)

    def x_labels(self, ax, label):
        ax.set_xlabel(label)
        x = [i - self.x[0] for i in self.x]
        labs = [i for i in range(round(min(x)), round(max(x)) + 1, 3)]
        ticks = [(i-labs[0]) / (x[1]-x[0]) for i in labs]
        plt.xticks(ticks, labs)
    
    def y_labels(self, ax, label):
        ax.set_ylabel(label)
        y = self.y
        labs = [i for i in range(0, round(max(y)) + 1, 10)]
        ticks = [i/(y[1]-y[0]) for i in labs]
        plt.yticks(ticks, labs)

    def y2_labels(self, ax, label):
        """"""
        try:
            ax2 = ax.twinx()
            ax2.set_ylabel(label)
            y, v = self.y, self.v
            d = [ns2mm(i/2, v) / 1000 for i in y]
            mn, mx = math.floor(min(d)), math.ceil(max(d))
            labs = [i for i in range(mn, mx)]
            near = lambda x: abs(min([i-x for i in d]))
            locs = [1-(near(i)/max(d)) for i in labs]
            plt.yticks(locs, labs)
        except Exception as e:
            pass


class RadarGramBak:
    """Plot a radargram using a GPR object"""

    def plot(self, xlab='Distance (m)', ylab='Time (ns)', y2lab='Depth (m)', velocity=None):
        fig = plt.figure(figsize=(29.7/2.54, 21/2/2.54))
        ax1 = plt.axes()
        a = self.array
        ax1.imshow(a, cmap = 'Greys_r', aspect = 'auto', interpolation = 'bicubic')
        self.x_labels(ax1, xlab)
        self.y_labels(ax1, ylab)
        self.y2_labels(ax1, y2lab)
        return(plt)

    def x_labels(self, ax, label):
        ax.set_xlabel(label)
        x = [i - self.x[0] for i in self.x]
        labs = [i for i in range(round(min(x)), round(max(x)) + 1, 3)]
        ticks = [(i-labs[0]) / (x[1]-x[0]) for i in labs]
        plt.xticks(ticks, labs)
    
    def y_labels(self, ax, label):
        ax.set_ylabel(label)
        y = self.y
        labs = [i for i in range(0, round(max(y)) + 1, 10)]
        ticks = [i/(y[1]-y[0]) for i in labs]
        plt.yticks(ticks, labs)

    def y2_labels(self, ax, label):
        """"""
        try:
            ax2 = ax.twinx()
            ax2.set_ylabel(label)
            y, v = self.y, self.velocity
            d = [ns2mm(i/2, v) / 1000 for i in y]
            mn, mx = math.floor(min(d)), math.ceil(max(d))
            labs = [i for i in range(mn, mx)]
            near = lambda x: abs(min([i-x for i in d]))
            locs = [1-(near(i)/max(d)) for i in labs]
            plt.yticks(locs, labs)
        except Exception as e:
            pass


class LineBak(RadarGram):
    """Create an object of GPR data and metadata sourced from a pandas series."""
    def __init__(self, metadata, gpr_type, velocity=None):
        """
        Use a pandas series of metadata to create an object of GPR data.
            Attributes:
                gpr_format <class>: A class specific to a GPR type (e.g. MALA)
                    that include a 'path' input.
                metadata <pandas.Series>: A series of metadata that includes a field named 'path'. The path is used in 'gpr_format'. 
        """
        self._add_meta(metadata)
        self._add_gpr(gpr_type)
        self._add_velocity(velocity)

    def _add_meta(self, s):
        for k, v in zip(s.index, s.values):
            setattr(self, k, v)

    def _add_gpr(self, gpr_type):
        obj = gpr_type(self.path)
        self.__dict__.update(obj.__dict__)

    def _add_velocity(self, velocity):
        """"""
        self.velocity = velocity


def list_an_attribute(list_of_lines, attribute):
    """"""
    lst = [getattr(i, attribute) for i in list_of_lines]
    return(lst)
       


def flip_radargram(a):
    """Flip the x-axis of a radargram numpy array"""
    a = np.flip(a, axis=1)
    return(a)
 
def equal_list_elements(lst):    
    """Check all items in a list are equal. This is useful to check the equality of gpr object attributes prior to stacking."""
    i = iter(lst)
    i0 = next(i)
    try:
        assert all([i0 == j for j in i]) == True
        return(i0)
    except AssertionError:
        print('List elements are not equal.')
        exit(1)

def max_shape(list_of_arrays):
    """Return the maximum m and n of a list of arrays. This is useful when reshaping arrays to a standard shape before combining to a 3D array."""
    m = max([i.shape[0] for i in list_of_arrays])
    n = max([i.shape[1] for i in list_of_arrays])
    return(m, n)


class TimeSliceBak(RectifyTif):
    """"""
    def plot_timeslice(self, array, levels=50, cmap='rainbow_r'):
        """Name of method changed to avoid conflict with radargram plot method; other plot method should be deleted in time."""

        x = [i - self.x[0] for i in self.x]
        y = [i - self.y[0] for i in self.y]
    
        line_spacing = abs(round(y[1] - y[0], 4))
        distance_interval = abs(x[1] - x[0])

        # create a 21 x 21 vertex mesh
        X, Y = np.meshgrid(np.linspace(min(x), max(x), len(x)), np.linspace(min(y), max(y), len(y)))

        x_ratio = len(x) * distance_interval
        y_ratio = len(y) * line_spacing

        fig, ax1 = plt.subplots(figsize = (21 / 2.54 / 2, 21 / 2 / 2.54 * y_ratio / x_ratio))
        
        #cset = ax1.contourf(X, -Y, array, levels, cmap=cmap) # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        levels=5
        import matplotlib as mpl
        cset = ax1.contourf(X, -Y, array, levels, norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        #cset = ax1.contourf(X, -Y, array, levels, cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances

        # set axis labels
        ax1.set_xlabel('Distance (m)')
        ax1.set_ylabel('Distance (m)')

        return(plt)

   #def plot(self, array, levels=50, cmap=cm.Spectral_r):
    def plot(self, array, levels=50, cmap='rainbow_r'):
        """Plot a timeslice"""

        x = [i - self.x[0] for i in self.x]
        y = [i - self.y[0] for i in self.y]
    
        line_spacing = abs(round(y[1] - y[0], 4))
        distance_interval = abs(x[1] - x[0])

        # create a 21 x 21 vertex mesh
        X, Y = np.meshgrid(np.linspace(min(x), max(x), len(x)), np.linspace(min(y), max(y), len(y)))

        x_ratio = len(x) * distance_interval
        y_ratio = len(y) * line_spacing

        fig, ax1 = plt.subplots(figsize = (21 / 2.54 / 2, 21 / 2 / 2.54 * y_ratio / x_ratio))
        
        #cset = ax1.contourf(X, -Y, array, levels, cmap=cmap) # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        levels=5
        import matplotlib as mpl
        cset = ax1.contourf(X, -Y, array, levels, norm=mpl.colors.Normalize(vmin=0, vmax=1), cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances
        #cset = ax1.contourf(X, -Y, array, levels, cmap='rainbow') # the sign of y will flip the y-axis; there is some indication that this needs manually changing in some instances

        # set axis labels
        ax1.set_xlabel('Distance (m)')
        ax1.set_ylabel('Distance (m)')

        return(plt)

    def jpg(self, path, array, levels=50, cmap=cm.Spectral, axis=True, dpi=150, format='jpg', bbox_inches='tight', pad_inches=0):
        """Remove the axes of a timeslice for spatial recification"""
        plt = self.plot(array, levels, cmap) 
        if axis == False:
            plt.axis('off')
        plt.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close()
        
    def tif(self, path, array, levels=50, cmap=cm.Spectral, axis=False, dpi=150, format='tif', bbox_inches='tight', pad_inches=0):
        """Remove the axes of a timeslice for spatial recification"""
        plt = self.plot(array, levels, cmap) 
        if axis == False:
            plt.axis('off')
        plt.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close()
 
 
def wee(stack, top, bottom):
    """"""
    mm = stack.depths
    #for n, i in enumerate(depths):
    #    try:
            #a = depths[n]
            #b = depths[n+1]
    idx = [n for n, i in enumerate(mm) if i > top and i <= bottom]
    lst = [stack.array[i] for i in idx]
    arr_sum = sum([abs(i) for i in lst])
    arr_norm = arr_sum / arr_sum.max()
    return(arr_norm)

    #    except Exception as e:
    #        print(e)
    #        break
    


#######################################################################

 

   
def expand_array(arr, m, n):
    """Add rows and columns to a radargram array and fill with null values. This is only able to expand an array but could be written to also clip. 
        Attributes:
            arr <np.array?: a 2D array of radargram data;
            m <int>: the number of rows that the new array should have (must be greater than arr.shape[0]);
            n <int>: the number of columns that the new array should have (must be greater than arr.shape[1]);
    """
    a = np.zeros((m, n))
    a[:] = np.nan
    m1, n1 = arr.shape
    rows = m1 - m if m1 - m != 0 else m1
    cols = n1 - n if n1 - n != 0 else n1
    a[:rows,:cols] = arr
    return(a)

   
   
   

def plot_timeslice(arr, x, y, velocity = None, levels = 50, cmap=cm.Spectral):
    """Plot a timeslice"""
    
    line_spacing = x[1] - x[0]
    distance_interval = y[1] - y[0]

    # create a 21 x 21 vertex mesh
    X, Y = np.meshgrid(np.linspace(0,max(x),len(x)), np.linspace(0,max(y),len(y)))

    m, n = arr.shape
    fig, ax1 = plt.subplots(figsize = (21 / 2.54 / 2, 21 / 2 / 2.54 * (len(y) * distance_interval) / (len(x) * line_spacing)))

    # plot timeslice 
    cset = ax1.contourf(X, Y, np.flip(arr, axis=0), levels, cmap=cmap)

    # set axis labels
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Distance (m)')

    # the following was previously required when using the imshow method; kept here in case needed for future bugs
    #labs = [0, 5, 10]
    #labs = [i for i in range(0, round(max(x)) + 1, 2)]
    #ticks = [i/line_spacing for i in labs]
    #plt.xticks(ticks, labs)
    #labs = [0, 5, 10]
    #labs = [i for i in range(0, round(max(y)) + 1, 2)]
    #ticks = [len(y) - i/distance_interval for i in labs]
    #plt.yticks(ticks, labs)

    return(plt)
    #return(cset)
 

class segments2array(object):
    """Convert line segments from a parrallel or zig-zag GPR survey into a numpy array for further processing."""

    def __init__(self, segments, dimensions, rads = None):
        """
        A list of tuples is unpacked to individual lists. The input lists are used to create a list of objects for each line segments with attributes particular to the MALA 'rd3' file format. A list of numpy arrays and file headers are extracted from the list of objects.

        Attributes:

            segments <list>: A list of tuples representing essential input for each line segment. A tuple is required to prevent the input of unnequal lists rather than needing to provide an internal check.
            Each tuple must include:
                <str>: A filesystem path to an 'rd3' file (the inclusion of the file extension is optional).
                <float>: The unique x-coordinate of the line.
                <float>: The starting y-coordinate of the line segment. End coordinates are claculated from the distance-interval recorded in the file header.
                <boolean>: The direction of measurement for each line segment. Positive y-direction is represented by '1' and negative by '0'

    """

        self.segments = segments
        self.length = dimensions[0]
        self.width = dimensions[1]
        spath, self.sx, self.sy, self.sdir = zip(*segments)
        ramac = [rd3(i) for i in spath]

        self.arr = [i.arr for i in ramac]
        self.headers = [i.info for i in ramac]

        self.x = list(set(self.sx))
        self.x.sort()
        self.y = self.distance()
        self.z = self.time()
        self.t0 = [x2trace(i, self.distance_interval()) for i in self.sy]
        self.rg_array = self.build_array()
        self.ts_array = self.rotate_array()

    def rotate_array(self):
        """Rotate radargram-iterable array to a timeslice-iterable array"""
        a = self.rg_array
        a = np.rot90(a, axes = (1,0))
        a = np.flip(a, axis = 1)
        a = np.rot90(a, axes = (1,2))
        #a = np.flip(a, axis = 1)
        return(a)

    def depth_interval(self, velocity):
        """Return the depth (mm) represented by each sample (e.g. the depth-equivalent of the time_interval"""
        v = velocity
        t = self.time_interval()
        s = ns2mm(t, v) / 2
        return(s)

    def depths(self, velocity):
        """Return list of depths"""
        v = velocity
        t = self.time()
        s = [ns2mm(i, v) / 2 for i in t]
        return(s)

    def samples(self):
        """Return the average number of samples of the input line segments"""
        s = int(round(pd.Series([i['SAMPLES'] for i in self.headers]).mean()))
        return(s)

    def time_interval(self):
        """Return the average two-way time interval between samples of the input line segments. TThis method needs some way of checking whether the values are significantly different for cases where the input segments were measured using different measurement parameters."""
        i = round(pd.Series([1 / i['FREQUENCY'] * 1000 for i in self.headers]).mean(), 5)
        return(i)

    def time(self):
        """Return a list of two-way travel times (ns) of length equal to the average number of samples of the input line segments"""
        dz = self.time_interval()
        s = self.samples()
        labs = [round(i * dz, 6) for i in range(1, s + 1)]
        return(labs)

    def distance_interval(self):
        """Return the average distance interval between traces of the input line segments. This method needs some way of checking whether the values are significantly different for cases where the input segments were measured using different measurement parameters"""
        i = float(round(pd.Series([i['DISTANCE INTERVAL'] for i in self.headers]).mean(), 6))
        return(i)

    def distance(self):
        """Return a list of distances with intervals of equal magnitude to the average distance intervals of all line segments. The maximum distance must not exceed the length of the grid square."""
        dx = self.distance_interval()
        lst = []
        x = 0
        while x <= self.length:
            lst += [x]
            x += dx
        labs = [round(i, 6) for i in lst]
        return(labs)

    def lineidx(self, x):
        """Return the incides of line segments equal to the given x-coordinate"""
        idx = [n for n, i in enumerate(self.sx) if i == x]
        return(idx)

    def build_array(self):
        idx = [self.lineidx(i) for i in self.x]
        lines = []
        for i in idx:
            x = set([self.sx[j] for j in i]).pop()
            print('Line x = ' + str(x))
            a = [self.arr[j] for j in i]
            t =  [x2trace(self.sy[j], self.distance_interval()) for j in i]
            d = [self.sdir[j] for j in i]
            s = [i for i in zip(a, t, d)]
            line = segments2line(s)

            line = line[0:self.samples(),:len(self.distance())] # clip to maximum sample and trace of grid length

            dt = len(self.distance()) - line.shape[1]
            z = np.array([int(0) for i in range(line.shape[0] * dt)]).reshape(line.shape[0], dt)
            line = np.append(line, z, axis = 1) # add columns if line is short

            # add rows if samples are short (not needed to implement as yet)
            ds = self.samples() - line.shape[0]
            if ds > 0:
                z = np.array([[int(0) for j in range(line.shape[1])] for i in range(ds)])
                line = np.append(line, z, axis = 0) # add rows if line is short

            line = line.astype(int)
            lines += [line]

        stack = np.stack(lines)
        return(stack)


def analyse_timeslice(a, velocity):
    """Scroll through timeslices; this is an effort to enable plotting timeslices and radargrams together and scroll through"""
    import matplotlib.pyplot as plt
    from matplotlib import cm

    # plot timeslices
    ts = a.stack.timeslices
    x = a.x
    y = a.y
    z = a.z
    d = [ns2mm(i / 2 / 1000, velocity) for i in z]

    line_spacing = x[1] - x[0]
    distance_interval = y[1] - y[0]
    
    # create a 21 x 21 vertex mesh
    X, Y = np.meshgrid(np.linspace(0,max(x),len(x)), np.linspace(0,max(y),len(y)))

    global curr_pos
    curr_pos = 0

    def key_event(e):
        global curr_pos

        if e.key == "right":
            curr_pos = curr_pos + 1
        elif e.key == "left":
            curr_pos = curr_pos - 1
        else:
            return
        curr_pos = curr_pos % len(ts)

        ax1.cla()
        
        arr = np.flip(ts[curr_pos], axis=0)
        cset = ax1.contourf(X, Y, arr, 30, cmap=cm.RdYlBu)

        plt.title('Depth = ' + str(round(ns2mm(z[curr_pos] / 2, velocity))) + ' mm')

        # set axis labels
        ax1.set_xlabel('Distance (m)')
        ax1.set_ylabel('Distance (m)')

        fig.canvas.draw()

    fig, ax1 = plt.subplots(figsize = (21 / 2.54 / 2, 21 / 2 / 2.54 * (len(y) * distance_interval) / (len(x) * line_spacing)))

    fig.canvas.mpl_connect('key_press_event', key_event)

    plt.show()


def plot_3d(a, depth, velocity):
    """Plot a timeslice in 3d; this is part of an effort to enable plotting of timeslices and radargrams together and also scroll through the plots"""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    from matplotlib import cm

    # plot timeslices
    ts = a.stack.timeslices
    x = a.x
    y = a.y
    z = a.z
    d = [ns2mm(i / 2 / 1000, velocity) for i in z]

    line_spacing = x[1] - x[0]
    distance_interval = y[1] - y[0]

    # create a 21 x 21 vertex mesh
    X, Y = np.meshgrid(np.linspace(0,max(x),len(x)), np.linspace(0,max(y),len(y)))
    Z =  10*np.ones(len(z))

    # create the figure
    fig = plt.figure()

    curr_pos = 100
    depth_to_show = depth 
    nearest_depth = min(d, key=lambda x:abs(x - depth_to_show))
    idx = d.index(nearest_depth)

    ax = fig.add_subplot(111, projection='3d')
    cset = ax.contourf(X, Y, ts[idx], 10, zdir='z', offset=nearest_depth, cmap=cm.RdYlBu)

    plt.title('Depth = ' + str(round(ns2mm(z[idx] / 2, velocity))) + ' mm')

    # set axis labels
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Distance (m)')
    ax.set_zlabel('Depth (m)')

    ax.set_zlim((max(d), min(d)))

    plt.show() 


def ts2gis(square, line_spacing, velocity = None, outdir = None):
    """Plot timeslice contours to polygons and rectify; the resulting plot contains holes"""
    import tempfile
    from PIL import Image, ImageChops
    import gdal, osr
    import geopandas as gpd
    import matplotlib.pyplot as plt

    # load metadata
    rd3 = join(output, 'timeslices')
    ramac = GridRAMAC(square, rd3, line_spacing, velocity = None)

    # plot timeslices
    ts = ramac.stack.timeslices
    x = ramac.x
    y = ramac.y
    z = ramac.z

    ts = np.nan_to_num(ts)

    import matplotlib.pyplot as plt
    cs = plot_timeslice_contour(ts[0], x, y)
    #print(len(cs.collections))
    print('\n'.join(dir(cs)))
    #print(cs.collections)
    #plt.show()

    from shapely.geometry import LinearRing, MultiPolygon, Polygon
    lst = []
    for i in cs.collections:
        p = i.get_paths()
        if len(p) > 0:
            v = p[0].vertices
            x = v[:,0]
            y = v[:,1]
            poly = Polygon([(j[0], j[1]) for j in zip(x,y)])
            lst += [poly]

    c = cs.collections
    p = [i.get_paths() for i in c]
    v = [[j.vertices for j in i] for i in p if len(p) > 0]
    x = [[j[:,0] for j in i] for i in v]
    y = [[j[:,1] for j in i] for i in v]
    zipped = [[(j[0], j[1]) for j in zip(i[0], i[1])] for i in zip(x, y)] 
    polys = [[Polygon([j for j in zip(i[0], i[1])]) for i in k] for k in zipped]
    print(len(polys))
    print([len(i) for i in polys])

    labs1 = [[cs.layers[n] for j in i] for n, i in enumerate(polys)]
    labs2 = [i for j in labs1 for i in j]
    polys2 = [i for j in polys for i in j]
    print(len(polys2))

    #mpoly = MultiPolygon([i for i in lst])
    df = gpd.GeoDataFrame({'geometry':polys2})
    print(df)
    #print(moo)
    #plt.close()
    df.plot()
    plt.show()
    exit()
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    


























    
# the following might be discarded but need to be checked for any use    
    

def test_array():
    """Return a simple numpy array for testing functions"""
    a = [[1,1,2,3,4], [1,5,6,7,8], [1,9,10,11,12]]
    b = [[2,1,2,3,4], [2,5,6,7,8], [2,9,10,11,12]]
    c = [[3,1,2,3,4], [3,5,6,7,8], [3,9,10,11,12]]
    ndarray = np.array([a, b, c])
    return(ndarray)



def x2trace(distance, interval):
    """Return the trace number closest to a given distance. The input distance is effectively dimesionless given that the interval is proportional to it. NB: Not sure if the returned trace is a python index or gpr trace but that needs to be specified here.
    Attributes:
        distance <float>: the distance along a GPR line that a trace must be identified;
        interval <float>: the distance interval in meters between adjacent traces.
    Alternative names:
	line_trace
    """
    trace = round(distance / interval)
    return(trace)

def traceidx(ndarray, start_trace, positive = True):
    """Return a list of trace indices for an array.
    Attributes:
        arr <numpy.array>: An array of a GPR line segment;
        start_trace <int>: The index of the trace of the GPR line that the first trace of the input line segment corresponds to;
        positive <bool>: The direction of the line segment, positive (True) or negative (False).
    """
    a, t, pos = ndarray, start_trace, positive
    n = lambda a: a.shape[1]
    if pos:
        idx = [i for i in range(t, t + n(a))]
    else:
        a = np.flip(a, 1)
        idx = [i for i in range(t, t - n(a), -1)]
    return(idx)

def segments2line(segments):
    """Combine GPR line segments input as numpy arrays into a single GPR line.
        Attributes:
            segments <list>: A list of tuples containing the input data.
                tuple[0] <numpy.array>: An nd array of a GPR line segment.
                tuple[1] <int>: The trace number of the output GPR line that the line segment begins.
                tuple[2] <bool>: The measurement direction (positive = 1, negative = 0) of the line segment.
    """
    s = segments
    a = [i[0] for i in s]
    idx = [traceidx(i[0], i[1], i[2]) for i in s]

    # create empty array
    y = min([i.shape[0] for i in a])
    x = max(itertools.chain.from_iterable(idx)) + 1
    ar = (np.zeros((y, x)))

    # populate array with segment values
    for i in [i for i in zip(a, idx)]:
        for m, row in enumerate(i[0]):
            if m < ar.shape[0]:
                for n, col in enumerate(i[1]):
                    if n < ar.shape[1]:
                        ar[m][col] = i[0][m][n]

    return(ar)

def subarraymean(ndarray, idx):
    """Return the mean of a 3-dimensional array as a 2-dimensional array
    Attributes:
        ndarray <numpy.array>: a three-dimensional numpy array;
        idx <list>: a list of integers representing the indices of axis = 0 to subset

    """
    subset = ndarray[idx]
    mean = np.average(subset, axis = 0)
    return(mean)
    
    
def x2trace2(distance, interval):
    """Return the trace number closest to and less than a given distance. 
    Attributes:
        distance <float>: the distance along a GPR line that a trace must be identified;
        interval <float>: the distance interval in meters between adjacent traces.
    Alternative names:
	line_trace
    """
    trace = round(distance / interval)
    return(trace)

    
def array2rg(ndarray, distances, times, velocity = None):
    """Plot a 2-dimensional radargram from a numpy array. Standar output dimensions should be the long half of an A4 page"""
    dim = ndarray.shape
    x = ndarray.shape[1]
    y = ndarray.shape[0]
    
    fig, ax1 = plt.subplots(figsize = (277 * 0.0393701, 190 / 2 * 0.0393701))
    ax1.set_xlabel('Distance (m)')
    ax1.set_ylabel('Time (ns)')
    ax1.imshow(ndarray, cmap = 'Greys_r', aspect = (190 / 2) / 277 * x / y, interpolation = 'bicubic')
    
    lst = [i for i in zip(range(dim[1]), distances)]
    tr = round(len(range(dim[1])) / 5)
    labs = lst[0::tr]
    plt.xticks([i[0] for i in labs], [round(i[1]) for i in labs])
    lst = [i for i in zip(range(dim[0]), times)]
    tr = round(len(range(dim[0])) / 5)
    labs = lst[0::tr]
    plt.yticks([i[0] for i in labs], [round(i[1]) for i in labs])
    
    if velocity:
        ax2 = ax1.twinx()
        ax2.set_ylabel('Depth (m)')
        depths = [ns2mm(i / 2, velocity) / 1000 for i in times]

        labs = [round(i * max(depths) / len(ax2.get_yticks()), 2) for i in range(len(ax2.get_yticks()))][::-1]

        ax2.set_yticklabels(labs)
    fig.tight_layout()
    
    return(plt)

def depth_breaks(increment_mm, max_mm):
    """Return a list of tuples representing depth ranges from a given depth increament (mm) and the maximum depth required"""
    dd, dmax = increment_mm, max_mm
    a = [i for i in range(0, dmax, dd)]
    b = [(a[n], a[n+1]) for n, i in enumerate(a) if i != max(a)]
    return(b)

def slice_indices(depths, breaks):
    """Return a list of tuples"""
    d, b = depths, breaks
    lst = [[n for n, j in enumerate(d) if j >= i[0] and j < i[1]] for i in b]
    return(lst)

def array2ts(a, x, y, colormap = 'Greys_r', interp = 'gaussian'):
    """Plot a 2-dimensional timeslice from a numpy array."""
    rows, cols = a.shape[0], a.shape[1]
    asp = cols / rows * max(y) / max(x)
    asp = 0.0625
    print(asp, max(y), max(x))
    fig = plt.figure()
    plt.imshow(a, cmap = colormap, aspect = asp, interpolation = interp)
    plt.xlabel('Distance (m)')
    lst = [i for i in zip(range(cols), x)]
    tr = round(len(range(cols)) / 5)
    labs = lst[0::tr]
    plt.xticks([i[0] for i in labs], [round(i[1]) for i in labs])
    plt.ylabel('Distance (m)')
    lst = [i for i in zip(range(rows), y)]
    
    tr = round(len(range(rows)) / 5)
    labs = lst[0::tr]
    plt.yticks([i[0] for i in labs[1:]], [round(i[1]) for i in labs[::-1]])
    plt.tight_layout()
    return(plt)


    

########################################################################
# Code below here is rejected from MALA module

class Rd32Grid3d:
    """Return filesystem and geometrical information for a square"""
    def __init__(self, rd3_paths, line_spacing, velocity = None):
    
        # combine radargram arrays into a list
        arr = [rd32arr(i) for i in rd3_paths]

        # create a 3D stack from the list of arrays
        m, n = max_shape(arr)
        expanded = [expand_array(i, m, n) for i in arr]
        self.stack = gpr.StackArrays(expanded)
        
        # get info from rad files
        rad_paths = [ramacpath(i, ext = '.rad') for i in rd3_paths]
        rad_dicts = [rad2dict(i) for i in rad_paths]
        
        # retrieve distance interval and timewindow from the rad data
        self.distance_interval = set([i['DISTANCE INTERVAL'] for i in rad_dicts]).pop()
        samples = set([i['SAMPLES'] for i in rad_dicts]).pop()
        frequency = set([i['FREQUENCY'] for i in rad_dicts]).pop()
        time_interval = 1 / frequency * 1000
        self.time_window = samples * time_interval
        self.line_spacing = line_spacing
        self.velocity = velocity

        m, n, o = self.stack.radargrams.shape
        self.x = [i * self.line_spacing for i in range(m)]
        self.y = [round(i * self.distance_interval, 6) for i in range(o)]
        time_interval = self.time_window / n
        self.z = [round(i * time_interval, 6) for i in range(1, n + 1)] # a reflection time can never be zero therefore the sequence is shifted forward

    def stack(self, rdir, subdirectory = None):
        """"""
        rd3_paths = self.ramac_paths(rdir, 'enhanced')
        arr = [mala.rd32arr(i) for i in rd3_paths]
        m, n = max_shape(arr)
        expanded = [expand_array(i, m, n) for i in arr]
        stack = StackArrays(expanded)
        return(stack)











####################################################################
# The code below needs to be checked for anything useful and then discarded if not


class segments2array(object):
    """Convert line segments from a parrallel or zig-zag GPR survey into a numpy array for further processing."""

    def __init__(self, segments, dimensions, rads = None):
        """
        A list of tuples is unpacked to individual lists. The input lists are used to create a list of objects for each line segments with attributes particular to the MALA 'rd3' file format. A list of numpy arrays and file headers are extracted from the list of objects.

        Attributes:

            segments <list>: A list of tuples representing essential input for each line segment. A tuple is required to prevent the input of unnequal lists rather than needing to provide an internal check.
            Each tuple must include:
                <str>: A filesystem path to an 'rd3' file (the inclusion of the file extension is optional).
                <float>: The unique x-coordinate of the line.
                <float>: The starting y-coordinate of the line segment. End coordinates are claculated from the distance-interval recorded in the file header.
                <boolean>: The direction of measurement for each line segment. Positive y-direction is represented by '1' and negative by '0'

    """

        self.segments = segments
        self.length = dimensions[0]
        self.width = dimensions[1]
        spath, self.sx, self.sy, self.sdir = zip(*segments)
        ramac = [rd3(i) for i in spath]

        self.arr = [i.arr for i in ramac]
        self.headers = [i.info for i in ramac]

        self.x = list(set(self.sx))
        self.x.sort()
        self.y = self.distance()
        self.z = self.time()
        self.t0 = [x2trace(i, self.distance_interval()) for i in self.sy]
        self.rg_array = self.build_array()
        self.ts_array = self.rotate_array()

    def rotate_array(self):
        """Rotate radargram-iterable array to a timeslice-iterable array"""
        a = self.rg_array
        a = np.rot90(a, axes = (1,0))
        a = np.flip(a, axis = 1)
        a = np.rot90(a, axes = (1,2))
        #a = np.flip(a, axis = 1)
        return(a)

    def depth_interval(self, velocity):
        """Return the depth (mm) represented by each sample (e.g. the depth-equivalent of the time_interval"""
        v = velocity
        t = self.time_interval()
        s = ns2mm(t, v) / 2
        return(s)

    def depths(self, velocity):
        """Return list of depths"""
        v = velocity
        t = self.time()
        s = [ns2mm(i, v) / 2 for i in t]
        return(s)

    def samples(self):
        """Return the average number of samples of the input line segments"""
        s = int(round(pd.Series([i['SAMPLES'] for i in self.headers]).mean()))
        return(s)

    def time_interval(self):
        """Return the average two-way time interval between samples of the input line segments. TThis method needs some way of checking whether the values are significantly different for cases where the input segments were measured using different measurement parameters."""
        i = round(pd.Series([1 / i['FREQUENCY'] * 1000 for i in self.headers]).mean(), 5)
        return(i)

    def time(self):
        """Return a list of two-way travel times (ns) of length equal to the average number of samples of the input line segments"""
        dz = self.time_interval()
        s = self.samples()
        labs = [round(i * dz, 6) for i in range(1, s + 1)]
        return(labs)

    def distance_interval(self):
        """Return the average distance interval between traces of the input line segments. This method needs some way of checking whether the values are significantly different for cases where the input segments were measured using different measurement parameters"""
        i = float(round(pd.Series([i['DISTANCE INTERVAL'] for i in self.headers]).mean(), 6))
        return(i)

    def distance(self):
        """Return a list of distances with intervals of equal magnitude to the average distance intervals of all line segments. The maximum distance must not exceed the length of the grid square."""
        dx = self.distance_interval()
        lst = []
        x = 0
        while x <= self.length:
            lst += [x]
            x += dx
        labs = [round(i, 6) for i in lst]
        return(labs)

    def lineidx(self, x):
        """Return the incides of line segments equal to the given x-coordinate"""
        idx = [n for n, i in enumerate(self.sx) if i == x]
        return(idx)

    def build_array(self):
        idx = [self.lineidx(i) for i in self.x]
        lines = []
        for i in idx:
            x = set([self.sx[j] for j in i]).pop()
            print('Line x = ' + str(x))
            a = [self.arr[j] for j in i]
            t =  [x2trace(self.sy[j], self.distance_interval()) for j in i]
            d = [self.sdir[j] for j in i]
            s = [i for i in zip(a, t, d)]
            line = segments2line(s)

            line = line[0:self.samples(),:len(self.distance())] # clip to maximum sample and trace of grid length

            dt = len(self.distance()) - line.shape[1]
            z = np.array([int(0) for i in range(line.shape[0] * dt)]).reshape(line.shape[0], dt)
            line = np.append(line, z, axis = 1) # add columns if line is short

            # add rows if samples are short (not needed to implement as yet)
            ds = self.samples() - line.shape[0]
            if ds > 0:
                z = np.array([[int(0) for j in range(line.shape[1])] for i in range(ds)])
                line = np.append(line, z, axis = 0) # add rows if line is short

            line = line.astype(int)
            lines += [line]

        stack = np.stack(lines)
        return(stack)


