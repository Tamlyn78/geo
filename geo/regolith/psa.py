#! python3

"""Process various particle-size data"""

import os
import sys
import csv
import tempfile
import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mp
from matplotlib import gridspec
from scipy.stats import norm
from scipy.stats import probplot
from scipy.interpolate import UnivariateSpline as spline
import pylab

def mm_to_phi(mm):
    """Convert a mm float to phi-scale.
        Attributes:
            mm <float64>: A float value for conversion"""
    return(-math.log2(mm))
    
def phi_to_mm(phi):
    """Convert a phi value float to mm.
        Attributes:
            mm <float64>: A float value for conversion"""
    return(math.pow(2, -phi))


class FolkAndWard:
    """"""
    def __init__(self, distribution):
        """Initialise with a pandas dataframe with columns 'mm' (lower size limits in mm) and 'frequency' (represented as a proportion of 1)."""
        dist = distribution.sort_values('mm', ascending=False)
        dist['phi'] = [mm_to_phi(i) for i in dist['mm']]
        self.dist = dist
        self.precision = 6

    def fw_dist(self):
        """Return a distribution for Folk and Ward processing"""
        d = self.dist.sort_values('mm', ascending=False)
        d['phi'] = [mm_to_phi(i) for i in d['mm']]
        return(d)

    def phi(self):
        """Return the mm sizes to phi-scale"""
        mm = self.dist['mm'].apply(mm_to_phi)
        mm = mm.reindex(index=mm.index[::-1])
        return(mm)

    def cumulative(self):
        """Return the cumulative distribution. Round to precision if defined."""
        freq = self.dist['frequency']
        freq = freq.reindex(index=freq.index[::-1])
        freq = freq.cumsum()
        return(freq)

    def percentile(self, percentile):
        """Return the index of the input percentile.
            Attributes:
                cumulative <pandas.Series>: A cumulative series of a particle-size distribution.
                percentile <int>: An integer representing the percentile required.
        """
        p = percentile
        c, phi = self.cumulative(), self.phi()
        l = c.index
        #for n, i in enumerate(c):
        #    print(100-n, i)
        #for i in c:
        #    print(i)
        mn = c[c > p].min()
        mx = c[c <= p].max()
        print(mn, mx)
        print(c)
        exit()
        y1 = mn.min()
        y2 = mx.max()
        x1 = mn.idxmin()
        x2 = mx.idxmax()
        m = (y2 - y1) / (x2 - x1)
        b = (y1 - m * x1)
        x = (p - b) / m
        return(x)
     
    def fw_M_z(self):
        """Return the graphical mean."""
        #c = self.fw_cumulative()
        a = self.percentile(16)

    def M_z(cumulative):
        """Return the graphic mean."""
        p = [percentile(cumulative, i) for i in [16, 50, 84]]
        return((p[0] + p[1] + p[2]) / 3)
 

class Testbak(FolkAndWard):
    """A base class for particle-size operations."""
    
class C:
    def Cwee(self):
        print('cwee')

class A(C):
    def __init__(self):
        print('awee init')
    
    def Awee(self):
        pass

    class Ab:
        def Abwee(self):
            print('abwee')

class _FolkAndWard:
    class FolkAndWard:
        def fw_method(self):
            print('folk and ward')

class B:
    def Bwee(self):
        pass

class Test(A, B, _FolkAndWard):
    def __init__(self, df):
        print('test init')
        self.distribution = df
        self.awee = A.__init__(self)
        





def average_dist(lst):
    """Return the average distribution from a list of distributions"""
    df = pd.DataFrame(lst)
    av = df.sum() / len(lst)
    return(av)
    
def folk_and_ward(Series):
    """Prepare a distribution for processing using methods of Folk and Ward"""
    s = Series
    idx = s.index
    if idx[0] < idx[len(idx)-1]:
        s = s.iloc[::-1]
    return(s)

# Graphical statistics of Folk and Ward
def graphical_statistics(distribution):
    """Return the graphic summary statistics of a particle-size distribution as a dataframe row.
        Attributes:
            Series <pandas.Series>: A particle-size distribution with index labels representing lower size-limits in phi-scale and ordered with higher phi-values (fining) descending. This format is used by Folk and Ward."""
    c = distribution.cumsum()
    stats = [M_z(c), Rho_1(c), Sk_1(c), K_G(c)]
    row = pd.DataFrame(data = [stats], columns = ['M_z', 'Rho_1', 'Sk_1', 'K_G'])
    return(row)
    
def graphical_percentiles(distribution, percentiles = [1,5,16,50,84,95,99]):
    """Return percentiles for graphic summary statistics of a particle-size distribution as a dataframe row.
        Attributes:
            Series <pandas.Series>: A particle-size distribution with index labels representing lower size-limits in phi-scale and ordered with higher phi-values (fining) descending. This format is used by Folk and Ward."""
    c = distribution.cumsum()
    p = [percentile(c, i) for i in percentiles]
    row = pd.DataFrame(data = [p], columns = ['D' + str(i) for i in percentiles])
    row.index = pd.MultiIndex.from_tuples([c.name])
    return(row)

def percentilebak(distribution, percentile):
    """Make sure the distribution is arranged as needed"""
    c = distribution.cumsum()
    l = c.index
    p = percentile
    mn = c[c > p]
    mx = c[c <= p]
    y1 = mn.min()
    y2 = mx.max()
    x1 = mn.idxmin()
    x2 = mx.idxmax()
    m = (y2 - y1) / (x2 - x1)
    b = (y1 - m * x1)
    x = (p - b) / m
    return(x)
    
def M_z(cumulative):
    """Return the graphic mean."""
    p = [percentile(cumulative, i) for i in [16, 50, 84]]
    return((p[0] + p[1] + p[2]) / 3)
    
def Rho_1(cumulative):
    """Return the graphic mean."""
    p = [percentile(cumulative, i) for i in [5, 16, 84, 95]]
    return((p[2] - p[1]) / 4 + (p[3] - p[0]) / 6.6)
    
def Sk_1(cumulative):
    """Return the graphic mean."""
    p = [percentile(cumulative, i) for i in [5, 16, 50, 84, 95]]
    return(p[1] + p[3] - (2 * p[2])) / (2 * (p[3] - p[1])) + (p[0] + p[4] - (2 * p[2])) / (2 * (p[4] - p[0]))
    
def K_G(cumulative):
    """Return the graphic mean."""
    p = [percentile(cumulative, i) for i in [5, 25, 75, 95]]
    return(p[3] - p[0]) / (2.44 * (p[2] - p[1]))    

def mm2phi(mm):
    """Convert a mm float to phi-scale.
        Attributes:
            mm <float64>: A float value for conversion"""
    return(-math.log2(mm))
    
def phi2mm(phi):
    """Convert a phi value float to mm.
        Attributes:
            mm <float64>: A float value for conversion"""
    return(math.pow(2, -phi))
    
def flip(Series):
    """Folk and Ward datasets must be ordered with size limits descending"""
    s = Series
    idx = Series.index
    u = idx[0]
    l = idx[-1]
    if u < l:
        s = s.iloc[::-1]
    return(s)
    
    
    


class histogram(object):

    def __init__(self, dist, title = "", xlab = "Particle diameter (mm)", ylab = "% volume", xlim = None, ylim = None):
        """Plot a histogram
            Attributes:
                dist <pandas.Series>: Particle-size distribution labelled in mm"""
        self.logx = [math.log10(float(i) / 1000) for i in list(dist.index)]
        print(self.logx)
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        xticklabs = [math.pow(10, i) for i in xticks]
        plt.xticks(xticks, xticklabs)
        if xlim:
            min = math.log10(xlim[0])
            max = math.log10(xlim[1])
            print(min, max)
            plt.xlim(min, max)
        if ylim:
            plt.ylim(ylim[0], ylim[1])

    def addseries(self, freq, col = '0', line = '', clip = False):
        """Add another series to the current plot"""
        if clip == True:
            x, y = clip_y(self.logx, freq)
        else:
            x, y = self.logx, freq
        plt.plot(x, y, color = col)
        
    def legend(self, lst, loc = 'upper left'):
        """Add a legend from a list"""
        #plt.legend(lst, loc = loc)
        plt.legend(lst, loc = loc, fontsize = 8, frameon = False)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)
    
class histogramOld(object):

    def __init__(self, x, title = "", xlab = "Particle diameter (mm)", ylab = "% volume", xlim = None, ylim = None):
        """Plot a histogram"""
        mm = x.apply(phi2mm)
        self.logx = mm.apply(math.log10)

        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        xticklabs = [math.pow(10, i) for i in xticks]
        plt.xticks(xticks, xticklabs)
        if xlim:
            plt.xlim(math.log10(xlim[0]), math.log10(xlim[1]))
        if ylim:
            plt.ylim(ylim[0], ylim[1])
        
    def addseries(self, freq, col = '0', line = '', clip = False):
        """Add another series to the current plot"""
        if clip == True:
            x, y = clip_y(self.logx, freq)
        else:
            x, y = self.logx, freq
        plt.plot(self.logx, freq, color = col)
        
    def x2(self, xloc, xlab = None):
        """Add a second x axis"""
        #print(xloc)
        plt.twiny()
        #plt.xticks([11,12,13])
        #print(mp.axes.yaxis.get_major_ticks())
        
    def legend(self, lst, loc = 'upper left'):
        """Add a legend from a list"""
        #plt.legend(lst, loc = loc)
        plt.legend(lst, loc = loc, fontsize = 8, frameon = False)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)
        
class cumulative_curve(object):
    def __init__(self, x, title = "", xlab = "Particle diameter (mm)", ylab = "% finer by volume", xlim = None, ylim = None):
        """Plot a cumulative curve using descending sizes"""
        self.logx = [math.log10(float(i)) for i in list(x.index)]
        plt.ylim((0,100))
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        xticklabs = [math.pow(10, i) for i in xticks]
        plt.xticks(xticks, xticklabs)
        if xlim:
            plt.xlim(math.log10(xlim[0]), math.log10(xlim[1]))
        if ylim:
            plt.ylim(ylim[0], ylim[1])
        
    def sum(self, freq):
        """Return the cumulative sum of a series"""
        cum = freq.cumsum()
        return(cum)        

    def addseries(self, freq, col = '0', line = '', clip = False):
        """Add another series to the current plot"""
        if clip == True:
            x, y = clip_y(self.logx, freq)
        else:
            x, y = self.logx, freq
        #cum = self.sum(y)
        plt.plot(x, freq, color = col, marker = ".", markersize = 8)
        
    def x2(self, xloc, xlab = None):
        """Add a second x axis"""
        #self.plt.twiny()
        
    def legend(self, lst, loc = 'upper left'):
        """Add a legend from a list"""
        plt.legend(lst, loc = loc, fontsize = 8, frameon = False)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)
        
class probabilityCurve(object):

    def __init__(self, x, title = "", xlab = "Particle diameter (mm)", ylab = "% finer by volume", xlim = None):
        """Plot a cumulative curve using descending sizes"""
        self.logx = [math.log10(float(i)) for i in list(x.index)]
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        xticklabs = [math.pow(10, i) for i in xticks]
        plt.xticks(xticks, xticklabs)
        yticklabs = [0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999]
        yticks = [-norm.ppf(i) for i in yticklabs]
        yticks.reverse()
        plt.yticks(yticks, yticklabs)
        self.x = x
        if xlim:
            plt.xlim(math.log10(xlim[0]), math.log10(xlim[1]))
        
    def prob(self, freq):
        """Return the cumulative sum of a series"""
        cum = freq.cumsum()
        # round the maximum value to 100
        maxidx = cum[cum == max(cum)].index[0]
        cum[maxidx] = cum[maxidx].round()
        prob = [norm.ppf(i / 100) for i in cum]
        plt.ylim(-norm.ppf(0.9999), -norm.ppf(0.0001))
        return(prob)        

    def addseries(self, freq, col = '0', line = '', clip = False):
        """Add another series to the current plot"""
        if clip == True:
            x, y = clip_y(self.logx, freq)
        else:
            x, y = self.logx, freq
        prob = self.prob(y)
        plt.plot(x, prob, color = col, marker = ".", markersize = 8)
        
    def x2(self, xlab = None):
        """Add a second x axis"""
        #print(self.logx)
        #plt.twiny()
        #xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        #xticklabs = [math.pow(10, i) for i in xticks]
        #plt.xticks(self.weex, self.weex)
        
    def legend(self, lst, loc = 'upper left'):
        """Add a legend from a list"""
        self.plt.legend(lst, loc = loc)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)
        
class probabilityCurveOld(object):

    def __init__(self, x, title = "", xlab = "Particle diameter (mm)", ylab = "% finer by volume", xlim = None):
        """Plot a cumulative curve using descending sizes"""
        mm = x.apply(phi2mm)
        self.logx = mm.apply(math.log10)
        plt.title(title)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        xticklabs = [math.pow(10, i) for i in xticks]
        plt.xticks(xticks, xticklabs)
        yticklabs = [0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999]
        yticks = [-norm.ppf(i) for i in yticklabs]
        yticks.reverse()
        plt.yticks(yticks, yticklabs)
        self.x = x
        if xlim:
            plt.xlim(math.log10(xlim[0]), math.log10(xlim[1]))
        
    def prob(self, freq):
        """Return the cumulative sum of a series"""
        cum = freq.cumsum()
        # round the maximum value to 100
        maxidx = cum[cum == max(cum)].index[0]
        cum[maxidx] = cum[maxidx].round()
        prob = [norm.ppf(i / 100) for i in cum]
        #print(prob)
        plt.ylim(-norm.ppf(0.9999), -norm.ppf(0.0001))
        return(prob)        

    def addseries(self, freq, col = '0', line = '', clip = False):
        """Add another series to the current plot"""
        if clip == True:
            x, y = clip_y(self.logx, freq)
        else:
            x, y = self.logx, freq
        prob = self.prob(y)
        plt.plot(x, prob, color = col, marker = ".", markersize = 8)
        
    def x2(self, xlab = None):
        """Add a second x axis"""
        #print(self.logx)
        #plt.twiny()
        #xticks = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        #xticklabs = [math.pow(10, i) for i in xticks]
        #plt.xticks(self.weex, self.weex)
        
    def legend(self, lst, loc = 'upper left'):
        """Add a legend from a list"""
        self.plt.legend(lst, loc = loc)
        
    def show(self):
        """Show the plot"""
        plt.show()
        
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)

        
class report(object):
    def __init__(self, key, x, hist, cum, prob, rawx, rawy, stats = pd.Series()):
        """Pass"""
        inch2cm = lambda x: x * 0.393701
        width = 8.2677
        height = 11.6929
        
        fig = plt.figure(figsize = (10, 14.14), dpi = 30)
        
        ax1 = fig.add_subplot(321)
        #input('dbg')
        hist(key)
        
        ax2 = fig.add_subplot(322)
        cum(key)
        ax3 = fig.add_subplot(323)
        prob(key)
        ax4 = fig.add_subplot(324)
        ax4.axis('off')
        
        if not stats.empty:
            ax4.text(0, 0.9, 'Graphic Mean ($\phi$): ' + str(round(stats['M_z'], 2)))
            ax4.text(0, 0.78, 'Standard deviation ($\phi$): ' + str(round(stats['Rho_1'], 2)))
            ax4.text(0, 0.66, 'Skewness ($\phi$): ' + str(round(stats['Sk_1'], 2)))
            ax4.text(0, 0.54, 'Kurtosis ($\phi$): ' + str(round(stats['K_G'], 2)))
            ax4.axis('off')
        
        ax5 = fig.add_subplot(325)
        fontdict = {'size':8}
        plt.text(0, 1, 'Volume %', fontdict = fontdict)
        plt.text(0.2, 1, 'Size (mm)', fontdict = fontdict)
        plt.text(0.4, 1, 'Volume %', fontdict = fontdict)
        plt.text(0.6, 1, 'Size (mm)', fontdict = fontdict)
        plt.text(0.8, 1, 'Volume %', fontdict = fontdict)
        plt.text(1, 1, 'Size (mm)', fontdict = fontdict)
        plt.text(1.2, 1, 'Volume %', fontdict = fontdict)
        plt.text(1.4, 1, 'Size (mm)', fontdict = fontdict)
        plt.text(1.6, 1, 'Volume %', fontdict = fontdict)
        plt.text(1.8, 1, 'Size (mm)', fontdict = fontdict)
        
        for i, val in enumerate(rawx, start = 1):
            vspace = 0.05
            if i <= 20:
                plt.text(0, 1 - i * vspace, round(rawx[i - 1], 6), fontdict = fontdict)
                plt.text(0.2, 1 - i * vspace, round(rawy[i - 1], 3), fontdict = fontdict)
            if 20 < i <= 40:
                plt.text(0.4, 1 - (i - 20) * vspace, round(rawx[i - 1], 6), fontdict = fontdict)
                plt.text(0.6, 1 - (i - 20) * vspace, round(rawy[i - 1], 3), fontdict = fontdict)
            if 40 < i <= 60:
                plt.text(0.8, 1 - (i - 40) * vspace, round(rawx[i - 1], 6), fontdict = fontdict)
                plt.text(1, 1 - (i - 40) * vspace, round(rawy[i - 1], 3), fontdict = fontdict)
            if 60 < i <= 80:
                plt.text(1.2, 1 - (i - 60) * vspace, round(rawx[i - 1], 6), fontdict = fontdict)
                plt.text(1.4, 1 - (i - 60) * vspace, round(rawy[i - 1], 3), fontdict = fontdict)
            if 80 < i <= 100:
                plt.text(1.6, 1 - (i - 80) * vspace, round(rawx[i - 1], 4), fontdict = fontdict)
                plt.text(1.8, 1 - (i - 80) * vspace, round(rawy[i - 1], 3), fontdict = fontdict)
                
        ax5.axis('off')
        
        fig.tight_layout()
        self.fig = fig
        
        
    def show(self):
        self.fig.show()
        
    def save(self, path):
        """Save the plot to file"""
        self.fig.savefig(path)

        


        
        
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

def WentworthUdden():
    """Return the size-limits and classes of the Wentworth-Udden size scale. Needs improving by allowing optional keyword indicating how to combine size classes if required"""
    lower_limit_mm = [0, 1/256, 1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 64, 256]
    upper_limit_mm = [1/256, 1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4, 64, 256, 4096]
    classes = [
                'Clay', 
                'Very fine silt', 
                'Fine silt', 
                'Medium silt', 
                'Coarse silt', 
                'Very fine sand', 
                'Fine Sand', 
                'Medium Sand',
                'Coarse Sand',
                'Very coarse sand',
                'Granule',
                'Pebble',
                'Cobble',
                'Boulder'
                ]
    df = pd.DataFrame([lower_limit_mm, upper_limit_mm, classes]).T
    df.columns = ['lower_limit_mm', 'upper_limit_mm', 'class']
    return(df)
    
def dist2class(dist, sizes, lower, upper, names):
    """Return a series of classes from a particle-size distribution.
        Attributes:
            dist <Series>: A particle-size distribution. 
    """
    lst = []
    
    for n, x in enumerate(names):
        l = lower[n]
        u = upper[n]
        lst += [sum([dist[i] for i in dist.index if l <= float(i) < u])]
    s = pd.Series(lst)
    s.index = names
    return(s)
    
def dics2df(dic, lower, upper, names):
    """Return a dataframe of size classes from a dictionary of distributions
        Attributes:
            dic <Dictionary>: Particle-size distributions as pandas series with lower size limit as index labels; dictionary keys should represent sample identifiers.
    """
    keys = list(dic.keys())
    lst = []
    for i in keys:
        dist = dic[i]
        dist.index = [float(float(i) / 1000) for i in dist.index] # this only works for mastersizer
        freq = dist2class(dist, lower, upper, names)
        lst += [freq]
    df = pd.DataFrame(lst)
    return(df)
    
def distUnits(distribution, multiplier):
    """Convert the units of a series label indices.
        Attributes:
            distribution <pandas.Series>: Particle-size frequency distribution with label indices representing the lower size-limit.
            multiplier <float>: a numerical multiplier to convert units. This does not allow for phi-scale.
    """
    d = distribution
    m = multiplier
    d.index = [float(float(i) * m) for i in d.index]
    return(d)
    
def dropZeroCols(df):
    """Drop zero columns to remove erroneaous size fractions from an analysis/graph.
        Attributes:
            df <pandas.DataFrame>: A dataframe containing numeric columns.
    """
    for i in df.columns:
        # check numeric here
        if sum(df[i]) == 0:
            del df[i]
    return(df)
    
def cumsumByRow(df):
    """Calculate the cumulative sum of frequency data accross rows of a dataframe.
        Attributes:
            df <pandas.DataFrame>: A dataframe containing numeric columns of frequency-data.
    """
    lst = []
    for i in df.index:
        j = df.ix[i].cumsum()
        lst += [j]
    output = pd.DataFrame(lst)
    return(output)
    
def frequencyDepthPlot(df, depths, path):
    """Generate a depthplot showing the cumulative frequencies of a vertical sequence of particle-size distributions.
        Attributes:
            df <DataFrame: Columns are frequency values of a size-class.
            depth <Series>: A sequence of depths (m) with the same length as df.
    """
    import matplotlib.patches as patches
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim([0, 100])
    ax.set_ylim([max(depths), min(depths)])
    grey = 1 / len(df.columns)
    shade = 0 + grey
    for n, x in enumerate(df.columns):
        if n == 0:
            x1 = pd.Series([0] * len(df.iloc[:,0]))
        else:
            x1 = df.iloc[:, n - 1]
        x2 = df.iloc[:,n]
        y = depths
        left_bound = [i for i in zip(x1,y)][::-1]
        right_bound = [i for i in zip(x2,y)]
        poly = patches.Polygon(left_bound + right_bound, color = str(shade), label = x)
        shade = shade + grey
        ax.add_patch(poly)
    plt.xlabel('Cumulative frequency (%)')
    plt.ylabel('Depth (m)')
    legend = ax.legend(bbox_to_anchor=(0.5,1), loc = 8, ncol = 3, fontsize = 6, frameon = False)
    plt.savefig(path)
    
    
