"""Tools for dealing with XYZ data, including:

    Reading XYZ data and converting to useful objects and formats
    Reorientation of array data such as flip/rotation
    Filtering array data such as high and low pass filters

    This is branch 133
"""

import numpy as np
import pandas as pd
from scipy import ndimage
import matplotlib.pyplot as plt 
from matplotlib import rc
from mpl_toolkits.axes_grid1 import make_axes_locatable

class ReadXYZ:
    """Read an XYZ file and convert to useful objects"""
    def __init__(self, path_to_xyz):
        """Read file into a pandas dataframe ready for use or conversion"""
        self.path_to_xyz = path_to_xyz
        self.df = pd.read_csv(path_to_xyz)
        
    def to_array(self, x_len, x_int):
        """Convert data to a numpy array by specifying the correct shape"""
        df = self.df
        a = df.iloc[:,2].to_numpy()
        a = np.reshape(a, (-1, int(x_len / x_int)))
        return(a)

def dummies_to_nan(array, nan=np.nan):
    """Convert dummy values to numpy nan"""
    array[array==2047.5] = nan
    return(array)

def rotate_array(array, rotation):
    """Rotate array in XGD orientation so that transects oriented up page; then rotate according to metadata"""
    a = np.rot90(array, rotation)
    return(a)


def clip_to_border(array):
    """"""
    z = array
    rows = [n for n, i in enumerate(z) if np.nansum(i) == 0]
    cols = [n for n, i in enumerate(z.T) if np.nansum(i) == 0]
    a = np.delete(array, rows, axis=0)
    a = np.delete(a, cols, axis=1)
    return(a) 

def zero_array(array, zero=0):
    """Move distribution so that the minimum value is zero"""
    a = array
    mn = np.nanmin(a)
    a = a - mn + zero
    return(a)

def smooth_array(array, zoom=20, mn=None):
    """"""
    a = array
    mn = np.nanmin(a) if not mn else mn
    print(mn)
    #a[np.isnan(a)] = 0 - mn * 10
    a = ndimage.zoom(a, zoom, mode='constant', cval=np.nan)
    print(np.nanmin(a))
    #a[a<mn] = np.nan
    #a[a<-10] = np.nan
    return(a)
 
def moving_average(array, radius=3):
    """"""
    k = np.zeros((radius, radius))
    k[k==0] = 1/(radius**2)
    a = ndimage.convolve(array, k, mode='reflect', cval=0.0)
    return(a)

def high_pass_filter(array):
    """"""
    from scipy import ndimage
    m, n = -.25, 1
    kernel = np.array([[m, m, m],
                       [m, n, m],
                       [m, m, m]])
    a = ndimage.convolve(array, kernel)
    a = a - np.nanmin(a)
    return(a)

def get_mean(array):
    """Return the mean of an array, excluding nan's"""
    mean = np.nanmean(array)
    return(mean)


def clip_array(array, std=1):
    """Clip an array to remove very high or low values"""
    a = array.copy()
    std = np.nanstd(a) * std
    mean = np.nanmean(a)
    nan = np.isnan(a)
    a[nan] = 0
    a[a < mean-std] = mean - std
    a[a > mean+std] = mean + std
    a[nan] = np.nan
    return(a)

class Stats:
    """Useful statistics for a spatial array"""
    def __init__(self, array):
        """Initiate class with a numpy array"""
        self.a = array
        self.plot()

    def plot(self):
        """Plot a histogram"""
        plt.hist(self.a)
        plt.show()
        plt.close()

def plot(array, outpath=None, xint=1, yint=1, vmin=None, vmax=None, cmap='rainbow', dpi=300, format='png', axes=True, interpolation=None, grid=False):
    """Plot an input 2D numpy array with adjustable levels and colour map"""

    font = {
        'family':'DejaVu Sans',
        'size':8,
    }
    rc('font', **font)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    m,n = array.shape
    extent = [
        0, n*xint,
        0, m*yint,
    ]
    plt.imshow(np.flip(array, axis=0), origin='lower', aspect='equal', vmin=vmin, vmax=vmax, cmap=cmap, interpolation=interpolation, extent=extent)
    
    #ax.gca()

    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Distance (m)')

    if grid:
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        sep = int(round(max([xticks[-1]-xticks[-2], yticks[-1]-yticks[-2]])))

        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()

        #xgrid = [[(x0,x1),(i,i)] for i in yticks]
        #ygrid = [[(i,i),(y0,y1)] for i in xticks]

        xthings = [i for i in range(int(round(min(yticks))), int(round(max(yticks))), sep)]
        ythings = [i for i in range(int(round(min(xticks))), int(round(max(xticks))), sep)]
        xgrid = [[(x0,x1),(i,i)] for i in xthings]
        ygrid = [[(i,i),(y0,y1)] for i in ythings]

        [plt.plot(i,j, color='grey', linewidth=0.5) for i,j in xgrid if j[0] <= ax.get_ylim()[1]]
        [plt.plot(i,j, color='grey', linewidth=0.5) for i,j in ygrid if i[0] <= ax.get_xlim()[1]]

    if not axes:
        plt.axis('off')
        pass
    else:
        
        plt.gca().set_aspect('equal')
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)

        cbar = plt.colorbar(cax=cax)
        cbar.set_label('Ohms')

    if outpath:
        if not axes:
            #plt.axis('off')
            plt.savefig(outpath + '.png', dpi=dpi, format=format, transparent=True, bbox_inches='tight', pad_inches=0)
        else:
            plt.savefig(outpath + '.png', dpi=dpi, format=format, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

