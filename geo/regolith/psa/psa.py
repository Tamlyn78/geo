#! python3

"""Process various particle-size data"""

from os import makedirs
from os.path import dirname, isdir
import math
from scipy.stats import norm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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


class FreqPlot:
    """Plot a distribution as a histogram, cumulative frequency distribution on an arithmetic scale, or a cumulative frequency distribution on a probability frequency scale.

    ### NOTE: I'm happy with the outputs of histograms and cumulative frequency distributions; I'm not completely sure whether the probability frequency distribution plots are correct (they are likely mirrored to some degree).

    """
    def __init__(self, mm, frequency, base=10):
        """Initialise with a single distribution. """

        self.mm, self.frequency = mm, frequency
        self.base = base
        self.cumulative = False
        self.probability = False
        self.reverse = False
        self.replicates = None
        
    def set_cumulative(self, cumulative=False):
        """Set y-axis as cumulative."""
        self.cumulative = cumulative

    def set_probability(self, probability=False):
        """Set y-axis as probability."""
        self.probability = probability

    def reverse_x(self, reverse=False):
        """Set x-axis orientation."""
        self.reverse = reverse

    def add_replicates(self, reps=None):
        """"""
        self.replicates = reps

    def xy(self, x, y):
        x, y = self.ascend(x, y)
        if self.base:
            x = x.apply(self.log)
        if self.cumulative:
            if self.reverse:
                x = x[::-1]
            y = y[::-1].cumsum()
        if self.probability:
            x, y = self.cumulative_prob(x, y)
            if not self.reverse:
                x = x[::-1]
        return(x, y)

    def ascend(self, x, y):
        """Change the order of values such that the x-values are ascending"""
        if x.iloc[0] > x[::-1].iloc[0]:
            x = x[::-1]
            y = y[::-1]
        return(x, y)

    def log(self, val):
        """Return a logarithm to initialised base or return value unchanged."""
        b = self.base
        if b:
            val = np.log(val) / np.log(b)
        return(val)

    def exp(self, val):
        """Return an exponant of initialised base or return value unchanged."""
        b = self.base
        if b:
            val = math.pow(b, val)
        return(val)

    def plot(self, title="", col='0', linewidth=0.5, marker='o', markerfacecolor=(0,0,0,0), markeredgecolor='0', markeredgewidth=0.5):
        """"""
        x, y = self.xy(self.mm, self.frequency)
        plt.plot(x, y, color=col, linewidth=linewidth, marker=marker, markerfacecolor=markerfacecolor, markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth)

        if self.replicates:
            c = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'] # this needs expansion by using a third-party class
            for n, i in enumerate(self.replicates):
                self.add_dist(i.mm, i.frequency, col=c[n])

        self.x_axis()
        self.y_axis()

    def x_axis(self, xlab='Particle diameter (mm)', xlim=None):
        """Draw the x-axis"""
        plt.xlabel(xlab)
        x, y = self.xy(self.mm, self.frequency)
        x = x.round().astype(int)
        lst = x.unique().tolist()
        xticks = [min(lst)] + lst + [max(lst)]
        xticklabs = [self.exp(i) for i in xticks]
        if xlim:
            plt.xlim(xlim[0], xlim[1])
        else:
            plt.xlim(x.min(), x.max())
        if self.reverse:
            xlim = plt.xlim()
            plt.xlim(xlim[1], xlim[0])
        plt.xticks(xticks, xticklabs)

    def y_axis(self, ylab=None, ylim=None):
        """"""
        if ylab:
            ylab=ylab
        elif self.cumulative:
            ylab = '% coarser by mass'
        else:
            ylab = '% mass'
        plt.ylabel(ylab)
        locs, labs = plt.yticks()
        if self.probability:
            self.prob_scale()
        elif self.cumulative:
            self.cum_scale()
        else:
            x, y = self.xy(self.mm, self.frequency)
            plt.ylim(math.floor(y.min()), math.ceil(y.max()))

    def cum_scale(self):
        """"""
        labs = [0, 20, 40, 60, 80, 100]
        plt.yticks(labs, labs)
        
    def prob_scale(self):
        """Plot a probability scale on the y-axis"""
        yticklabs = [0.0001, 0.001, 0.1, 0.5, 0.9, 0.99, 0.9999]
        yticks = [-norm.ppf(i) * 100 for i in yticklabs]
        yticks.reverse()
        plt.yticks(yticks, [i *100 for i in yticklabs])

    def cumulative_prob(self, x, y): 
        """"""
        include = y.loc[y.round(4)!=100].index
        y = y.loc[include]
        y = y / 100
        prob = y.apply(norm.ppf)
        y = prob * 100
        idx = y[~y.isin([np.inf, -np.inf])].index 
        y = y.loc[idx]
        x = x.loc[idx]
        return(x,y)        

    def add_dist(self, mm, frequency, col='0', linewidth=0.5):
        """Add another series to the current plot"""
        x, y = self.xy(mm, frequency)
        plt.plot(x, y, color=col, linewidth=linewidth)

    def legend(self, lst, loc='upper left'):
        """Add a legend from a list"""
        plt.legend(lst, loc=loc, fontsize=8, frameon=False)
 
    def show(self):
        """Show the plot"""
        plt.show()
 
    def save(self, path):
        """Save the plot to file"""
        plt.savefig(path)

    def close(self):
        plt.close()


class FreqReport(FreqPlot):

    def __init__(self, mm, frequency, base=10, reverse=False, precision=2, reps=None):
        """Initialise with a single distribution."""
        self.mm = mm
        self.frequency = frequency
        self.base = base
        self.reverse = reverse
        self.cum = False
        self.prob = False
        self.precision = precision
        self.reps = reps
        self.x, self.y = mm, frequency

    def plot(self, w=None, h=None, xlim=None, ylim=None):

        inches = lambda x: x / 2.56
        w, h = inches(21), inches(29.7)

        fig = plt.figure(figsize=(w,h))
        mm, frequency, base, reverse, reps = self.mm, self.frequency, self.base, self.reverse, self.reps
        cum, prob = self.cum, self.prob

        plt.subplot(3, 2, 1)
        h = FreqPlot(mm, frequency)
        h.reverse_x(self.reverse)
        h.add_replicates(reps=reps)
        h.plot()

        plt.subplot(3, 2, 2)
        c = FreqPlot(mm, frequency)
        c.reverse_x(self.reverse)
        c.add_replicates(reps=reps)
        c.set_cumulative(True)
        c.plot()

        plt.subplot(3, 2, 3)
        p = FreqPlot(mm, frequency)
        p.reverse_x(self.reverse)
        p.add_replicates(reps=reps)
        p.set_cumulative(True)
        p.set_probability(True)
        p.plot()

        plt.subplot(3, 2, 4)
        plt.axis('off')

        plt.subplot(3, 1, 3)
        plt.axis('off')
        d = {'size':8}

        df = pd.DataFrame([mm, frequency]).T
        n = 20
        rows = int(len(df) / n)
        frames = [df.iloc[i*n:(i+1)*n].copy() for i in range(rows+1) ]

        dx = 0
        for i in frames:
            c = 1
            plt.text(dx, c, '% mass', fontdict=d)
            plt.text(dx-0.1, c, 'Size (mm)', fontdict=d)
            for n, j in i.iterrows():
                dy = 1 - c * 0.05
                f = str(round(j.frequency, 2))
                mm = str(round(j.mm, self.precision))
                plt.text(dx, dy, f, fontdict=d)
                plt.text(dx-0.1, dy, mm, fontdict=d)

                c += 1
            dx += 0.2
 
        fig.tight_layout()


class FolkAndWard:
    """Retrieve Folk and Ward statistics from a particle-size distribution.
        Attributes:
            distribution <pandas.DataFram>: See Graphical class
            precision <int>: required precision

        Further work:
            All the calculated attributes should be returnable as a dictionary. This should also include useful analytical regressions between various statistics that can be presented later as biplots with density ellipses, for example.
    """
    def __init__(self, mm, frequency, precision=2, replicates=None):
        """"""
        self.mm, self.frequency = self._sort(mm, frequency)
        self.precision = precision
        self.replicates = replicates
        self.phi = self.mm.apply(mm_to_phi)

        self._D()
        self._M_z()
        self._Rho_1()
        self._Sk_1()
        self._K_G()
        
        xlim = (mm.min(), mm.max())

        a = (self.mm, self.frequency, xlim, replicates)
        self.histogram = self.Plot(*a)
        self.cumulative = self.Plot(*a, cumulative=True)
        self.probability = self.Plot(*a, cumulative=True, probability=True)
        self.report = self.Report(*a, precision)

    class Plot(FreqPlot):
        def __init__(self, mm, frequency, xlim, replicates, cumulative=False, probability=False):
            FreqPlot.__init__(self, mm, frequency)
            self.reverse_x(True)
            self.set_cumulative(cumulative)
            self.set_probability(probability)
            self.add_replicates(reps=replicates)
            
    class Report(FreqReport):
        """"""
        def __init__(self, mm, frequency, xlim, replicates, precision=2):
            FreqReport.__init__(self, mm, frequency, base=10, reverse=True, precision=precision, reps=replicates)

    def _sort(self, mm, freq):
        """Sort the distribution such that the size values decrease from top to bottom."""
        df = pd.DataFrame({'mm':mm, 'frequency':freq,})
        df = df.sort_values('mm', ascending=False)
        df = df.reset_index(drop=True)
        return(df.mm, df.frequency)

    def get_cumulative(self):
        """Return the cumulative frequency distribution"""
        c = self.frequency.cumsum().round(self.precision)
        return(c)
 
    def get_percentile(self, percentile):
        """Return the index of the input percentile.
            Attributes:
                cumulative <pandas.Series>: A cumulative series of a particle-size distribution.
                percentile <int>: An integer representing the percentile required.
        """
        perc = percentile
        cum = self.get_cumulative()
        phi = self.phi
        i0 = cum[cum>perc].index[0]
        i1 = cum[cum<=perc].index[-1]
        x2, x1 = phi[i0], phi[i1]
        y2, y1 = cum[i0], cum[i1]
        m = (y2 - y1) / (x2 - x1)
        b = (y1 - m * x1)
        x = (perc - b) / m
        return(x)

    def _D(self):
        """"""
        for i in [5,16,25,50,75,84,95,99]:
            p = self.get_percentile(i)
            setattr(self, 'D' + str(i), p)

    def _M_z(self):
        """Return the graphic mean."""
        D16, D50, D84 = self.D16, self.D50, self.D84
        self.M_z = (D16 + D50 + D84) / 3

    def _Rho_1(self):
        """Return the graphic standard deviation."""
        D5, D16, D84, D95 = self.D5, self.D16, self.D84, self.D95
        self.Rho_1 = (D84 - D16) / 4 + (D95 - D5) / 6.6
        
    def _Sk_1(self):
        """Return the graphic skewness."""
        D5, D16, D50, D84, D95 = self.D5, self.D16, self.D50, self.D84, self.D95
        self.Sk_1 = (D16 + D84 - (2 * D50)) / (2 * (D84 - D16)) + (D5 + D95 - (2 * D50)) / (2 * (D95 - D5))
        
    def _K_G(self):
        """Return the graphic kurtosis."""
        p = [self.get_percentile(i) for i in [5,25,75,95]]
        D5, D25, D75, D95 = self.D5, self.D25, self.D75, self.D95
        self.K_G = (D95 - D5) / (2.44 * (D75 - D25))

    def get_size_limits(self):
        """Return the minimum and maximum phi values for graphing purposes."""
        mm, freq = self.mm, self.frequency
        phi = mm.apply(mm_to_phi)
        lim = (phi.max(), phi.min())
        return(lim)

    def get_max_freq(self):
        """"""
        f = self.frequency
        return(f.max())

    def stats_to_dict(self, mm=False):
        """"""
        unit = 'mm' if mm else 'phi' 
        phi_range = self.get_size_limits()
        d = {
            'unit': unit,
            'size_min': phi_range[0],
            'size_max': phi_range[1],
            'freq_max': self.get_max_freq(),
            'M_z': self.M_z,
            'Rho_1': self.Rho_1,
            'Sk_1': self.Sk_1,
            'K_G': self.K_G,
            'D5': self.D5,
            'D16': self.D16,
            'D25': self.D25,
            'D50': self.D50,
            'D75': self.D75,
            'D84': self.D84,
            'D95': self.D95,
            'D99': self.D99,
            'D75-D25': self.D75-self.D25,
        }
        if mm:
            d['unit'] = 'mm'
            for i in d.keys():
                if i!='unit':
                    d[i] = phi_to_mm(d[i])
        return(d)
 
    def stats_to_series(self):
        """Return graphical statistics as a pandas series."""
        d = self.to_dict()
        s = pd.Series(d)
        return(s)

    def stat_descriptions(self):
        """Returns a dictionary with stats as keys and human-readable description as values."""
        d = {
            'M_z':'mean',
            'Rho_1':'standard deviation',
            'Sk_1':'skewness',
            'K_G':'kurtosis',
        }
        return(d)

    def stat_to_text(self, stat):
        """Return a human-readable phrase describing a statistic."""
        d = self.stat_descriptions()
        return(d[stat])

    def biplot_combinations(self):
        """Return a list of field headings for input into biplots."""
        lst = [
            ('M_z', 'Rho_1', 'Mean', 'Standard deviation'),
            ('M_z', 'Sk_1', 'Mean', 'Skewness'),
            ('M_z', 'K_G', 'Mean', 'Kurtosis'),
            ('Rho_1', 'Sk_1', 'Standard deviation', 'Skewness'),
            ('Rho_1', 'K_G', 'Standard deviation', 'Kurtosis'),
            ('Rho_1', 'D75-D25', 'Standard deviation', 'Quartile deviation')
            ('D50', 'D99', 'Median', 'One percentile')
        ]
        return(lst)



class PSD:
    """A particle-size distribution object. This should form the core of all particle-size analysis classes by formalising essential attributes."""
    def __init__(self, mm, frequency, precision=2, replicates=None):
        """The essential core attributes include the input requirements.
            Attributes: 
                mm <pandas.Series>: A series of size values representing size boundaries;
                frequency <pandas.Series>: A series of frequencies of same length as 'mm';
                precision <int>: An integer representing the numeric precision;
                replicates <list>: A list of PSD replicate objects. These can be added where needed. 
        """
        self.name = None
        self.mm = mm
        self.frequency = frequency
        self.precision = precision
        self.replicates = replicates

        mm, freq = self.clip()
        self.folk_and_ward = FolkAndWard(mm, freq, precision=precision, replicates=replicates)

    def clip(self):
        """Return size and frequency clipped to remove leading and trailing zero-data."""
        f, sz = self.frequency, self.mm
        idx = f[f!=0].index
        rn = range(idx.min()-1, idx.max()+2) # a zero should exist on either side for calculation of percentiles
        mm = sz.loc[rn]
        freq = f.loc[rn]
        return(mm,freq)

        
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
        d = dirname(path)
        if not isdir(d):
            makedirs(d)
        plt.savefig(path)
        plt.close()

def wentworth_udden():
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
    
    
