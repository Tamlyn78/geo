import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.colors as mcolors
from matplotlib.colors import TABLEAU_COLORS as tcol


class DepthPlot:
    """A standard plot for data with a variable vs depth."""
    def __init__(self, figsize=None):
        self.fig, self.ax = plt.subplots(figsize=figsize)

    def x_axis(self, xlab='', xlim=None):
        plt.xlabel(xlab)
        if xlim:
            plt.xlim(xlim[0], xlim[1])

    def y_axis(self, ylab='Depth (m)', ylim=None):
        plt.ylabel(ylab)
        if ylim:
            plt.ylim(max(ylim), min(ylim))
        else:
            ylim = plt.ylim()
        plt.ylim(max(ylim), min(ylim))

    def plot(self, x, y, y2=pd.Series(), col='0', linewidth=0.5, marker='o', markerfacecolor=(0, 0, 0, 0), markeredgecolor='0', markeredgewidth=0.5):
        """"""
        if not y2.empty:
            x = pd.Series([i for i in x for _ in (0, 1)])
            y = pd.Series([i for j in zip(y,y2) for i in j])

        ax = self.ax
        leg = ax.plot(x, y, color=col, linewidth=linewidth, marker=marker, markerfacecolor=markerfacecolor, markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth)
        self.x_axis()
        self.y_axis()
        return(leg)
       
    def show(self):
        plt.show()

    def save(self, path):
        plt.savefig(path)

    def close(self):
        plt.close()


class BiPlot:
    """A standard plot for data with 2 variables."""
    def __init__(self):   
        self.fig, self.ax = plt.subplots()

    def x_axis(self, xlab='', xlim=None):
        plt.xlabel(xlab)
        if xlim:
            plt.xlim(xlim[0], xlim[1])

    def y_axis(self, ylab='', ylim=None):
        plt.ylabel(ylab)
        if ylim:
            plt.ylim(ylim[0], ylim[1])
        
    def plot(self, x, y, s=10, color='0', marker='o', label=None, cmap=None):
        """"""
        c = list(tcol.values())
        if isinstance(color, int):
            try:
                color = c[color]
            except Exception as e:
                print(e)
        ax = self.ax
        leg = ax.scatter(x, y, s=s, color=color, marker=marker, label=label)
        #leg = ax.scatter(x, y, s=s, cmap='rainbow', marker=marker, label=label)
        #color = ['red' for i in range(10)]
        #print(color)
        #print(x)
        #print(y)
        #leg = ax.plot(x, y, colors=color, marker=marker, linewidth=0)
        return(leg)

    def show(self):
        plt.show()

    def save(self, path, tight=True):
        if tight:
            plt.tight_layout()
        plt.savefig(path, tight=tight)

    def close(self):
        plt.close()


