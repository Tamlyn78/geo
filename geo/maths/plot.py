"""Useful plotting methods. Please take care here as methods and classes are likely to be imported by other modules."""


import os
#from scipy.interpolate import spline
#from scipy import interpolate
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def confidence_ellipse(x, y, stdev=2):
    """Fit a confidence ellipse of a given standard deviation around a set of Cartesian data points. Returns an 'Artist' object that can be drawn on an axis as follows:
        ax.add_artist(e)        
    The returned artist can be modified as needed.
    """
    cv = np.cov(x, y)
    lambda_, v = np.linalg.eig(cv)
    lambda_ = np.sqrt(lambda_)

    xy = (np.mean(x), np.mean(y))
    w = lambda_[0]*stdev*2
    h = lambda_[1]*stdev*2
    theta = np.rad2deg(np.arccos(v[0, 0]))

    e = Ellipse(xy=xy, width=w, height=h, angle=theta)
    return(e)




################### Review below and scrap if need be ######################

class depthplot(object):
    """"""
    def __init__(self, title = "", xlab = "", ylab = "Depth (m)", fontsize = 10):
        """"""

        fig = plt.figure(figsize = (210 / 2 * 0.0393701, 297 / 2 * 0.0393701), dpi = 150) # quarter of a portrait A4 page
        plt.gca().invert_yaxis()
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.xticks(fontsize = fontsize * 0.8)
        plt.yticks(fontsize = fontsize * 0.8)
        self.plt = plt
        
    def addseries(self, x, y, col = 'k', linestyle = 'solid', marker = '.', linewidth = 1):
        plt.plot(x, y, color = col, linestyle = linestyle, marker = marker, linewidth = linewidth)
        #return(plt)
        
    def splinebak(self, x, y, k = 5, col = 'r'):
        """Add spline to series"""
        s = spline(y, x, k = k)
        xs = s(y)
        plt.plot(xs, y, color = col, linestyle = '--')

    def spline(self, x, y, wee=5, col = 'r'):
        """Add spline to series"""
        new = [0.7,0.9,1.1,1.3,1.5,1.7]
        mn = min(y)
        mx = max(y)
        print(mn, mx)
        rn = mx - mn
        new = [mn + rn / (wee-1) * i for i in range(0,wee)]
        #new = [0.7 + 0.025 * i for i in range(0,wee-1)]
        #print(new)
        #s = spline(y, x, xnew = new)
        #x1 = np.array(x)
        #y1 = np.array(y)
        #print(x1.shape)
        #print(y1.shape)
        
        print(x, y)
        s = interpolate.CubicSpline(y, x)
        
        #x = np.arange(10)
        #y = np.sin(x)
        #cs = interpolate.CubicSpline(x, y)
        #print(x, y)
        #exit()

        #s = interpolate.CubicSpline(y1, x1)
        print(s)
        #plt.plot(s, new, color = col, linestyle = '--')
        #plt.plot(s, new, color = col)
        
        xs = np.arange(mn, mx, (mx-mn)/(wee-1))
        print(xs)
        plt.plot(s(xs), xs, color=col)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.tight_layout()
        plt.savefig(path)
        
    def close(self):
        plt.close()
        
        
class biplot(object):
    """"""
    def __init__(self, x, y, path = None, title = "", xlab = "", ylab = ""):
        """"""
        self.x = x
        self.y = y
        fig = plt.figure(figsize = (10, 14.14), dpi = 30)
        xbuff = (max(x) - min(x)) * 0.1
        ybuff = (max(y) - min(y)) * 0.1
        plt.xlim(min(x) + xbuff, max(x) - xbuff)
        plt.ylim(min(y) + ybuff, max(y) - ybuff)
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        
    def plot(self, col = 'k'):
        plt.scatter(self.x, self.y, color = col)
        
    def show(self):
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        d = os.path.dirname(path)
        if not os.path.isdir(d):
            os.makedirs(d)
        plt.savefig(path)
        plt.close()



def matrix_scatterplot(df, alpha = 0.5, figsize = None, ax = None, grid = False, diagonal = "kde", marker = '.', density_kwds = None, hist_kwds = None):
    """Plot a matrix of bi-plots from a dataframe for quick view of multiple regressions."""
    pd.tools.plotting.scatter_matrix(df, alpha = alpha, figsize = figsize, ax = ax, grid = grid, diagonal = diagonal, marker = marker, density_kwds = density_kwds, hist_kwds = hist_kwds)
    plt.tight_layout()
    return(plt)

