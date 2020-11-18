
"""Graphical procedures for GPR data."""

import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import cm

from ...gis.raster import RectifyTif

class PLT:
    def show(self):
        """Display the current plot."""
        plt.show()

    def save(self, outpath):
        """Save the current plot to file."""

    def jpg(self, path, levels=50, cmap=cm.Spectral, axis=True, dpi=150, format='jpg', bbox_inches='tight', pad_inches=0):
        """Remove the axes of a timeslice for spatial recification"""
        plt = self.plot(array, levels, cmap) 
        if axis == False:
            plt.axis('off')
        plt.savefig(path, dpi=dpi, format=format, bbox_inches=bbox_inches, pad_inches=pad_inches)
        plt.close()
 

class RadarGram(PLT):
    """Plot a radargram using a GPR object"""

    def __init__(self, array, x=None, y=None):
        self.array = array
        #self.x = x
        #self.y = y

    def imshow(self, cmap='Greys_r', aspect='auto', interpolation='bicubic', vmin=None, vmax=None):
        """"""
        fig = plt.figure(figsize=(29.7/2.54, 21/2/2.54))
        ax = plt.axes()
        a = self.array
        ax.imshow(a, cmap=cmap, aspect=aspect, interpolation=interpolation, vmin=vmin, vmax=vmax)
        ax.set_xlabel('Traces')
        ax.set_ylabel('Samples')
        ax.set_title(self.path)

       
 
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
 






