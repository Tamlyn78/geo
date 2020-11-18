
from cartopy import crs
import matplotlib.pyplot as plt
from . import vector
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches

def epsg_to_proj(epsg):
    """Return a cartopy projection from an EPSG code.
        Attributes:
            epsg <int>: An EPSG code.
    """
    proj = crs.epsg(epsg)
    return(proj)
    

class CentreToPage:
    """Return coordinates of page dimensions from a central point. A4 size and landscape is default. Need to expand by allowing orientation to be set"""
    def __init__(self, point, orientation='landscape'):
        p = point
        self.x = p.x
        self.y = p.y
        if orientation=='landscape':
            self.a4 = 210 / 297
        elif orientation=='portrait':
            self.a4 = 297 / 210

    def set_width(self, width):
        w = width / 2
        h = w * self.a4
        return(self._coords(w,h))

    def set_height(self, height):
        h = height / 2
        w = h / self.a4
        return(self._coords(w,h))

    def _coords(self, w, h):
        x, y = self.x, self.y
        w,s,e,n = x-w, y-h, x+w, y+h
        return(w,s,e,n) 

    
class Page:
    """Useful methods for page formatting from a geometry"""
    def __init__(self, geom):
        self.g = geom

    def centroid(self):    
        p = vector.geoseries_to_centroid(self.g)
        return(p)

    def width_to_page(self, width):
        c = self.centroid()
        w,s,e,n = CentroidToPage(c).set_width(width)
        return(w,s,e,n)

class AxesOld:
    """"""
    def __init__(self, proj):
        """Attributes:
            proj <cartopy.crs>: crs projection from cartopy
        """
        self.proj = proj

    def axes(self, ticks=1000):
        """If class is not initialised then self.proj should derive from an inheriting class"""
        proj = self.proj
        ax = plt.axes(projection=proj)
        return(ax)

    def axis_ticks(self, ticks):
        """"""
        ax = self.ax
        w, e, s, n = ax.get_extent()
        xticks = list(range(int(round(w)), int(round(e)), ticks))
        yticks = list(range(int(round(s)), int(round(n)), ticks))
        ax.tick_params(axis = 'both', which = 'major', labelsize = 4)
        ax.set_xticklabels(xticks, ha = 'left')
        ax.set_yticklabels(yticks, rotation = 90, va = 'bottom')
        
        ax.set_xticks(xticks, crs = self.proj)
        ax.set_yticks(yticks, crs = self.proj)


#class MapOld: 
#     """This was written to include a cartopy projection but that's actually unnescessary unless working with geographical projections (UTM is already a Cartesian projection and can readily be plotted in matplotlib)"""
#    def __init__(self, proj, ticks=1000):
#        """
#        Attributes:
#            proj <cartopy.crs>: A cartopy projection.    
#        """
#        self.proj = proj
#        self.fig, ax = plt.subplots()
#        self.ax = plt.axes(projection=proj)
#        self.color = 'black'
#
#    def _color(self, c):
#        color = c if c else self.color
#        return(color)
#
#    def decorations(self, color=None):
#        self.north(color=color)
#        self.scale(color=color)
#
#    def north(self, x=5, y=90, color=None):
#        color = self._color(color)
#        decorations(self.ax).northarrow(x, y, color)
#
#    def scale(self, x=5, y=5, width=10000, color=None):
#        color = self._color(color)
#        decorations(self.ax).scalebar(x, y, width, color)
#
#    def legend(self, handles):
#        plt.legend(handles=handles, loc='lower right', fontsize=4, title='Legend', title_fontsize=6)
#
#    def colorbar(self, label='Raster'):
#        """Plot a colorbar to show raster values"""
#        divider = make_axes_locatable(self.ax)
#        cax = divider.append_axes("right", size="5%", pad=0.1)
#        #cbar = plt.colorbar(cax=cax)
#        #cbar.set_label(label)
#
#    def save(self, outfile, dpi=300):
#        """"""
#        plt.savefig(outfile + '.jpg', format='jpg', dpi=dpi, bbox_inches='tight')


class decorationsbak:
    """"""
    def __init__(self, ax):
        self.w, self.e, self.s, self.n = ax.get_extent()

        self.ns1 = (self.n - self.s) / 100
        self.ew1 = (self.e - self.w) / 100
        
    def scalebar(self, x, y, d, color = 'k', linewidth = 0.5):
        x0 = self.ew1 * x + self.w
        y0 = self.ns1 * y + self.s
        plt.plot([x0, x0 + d], [y0, y0], color = color, linewidth = linewidth)
        units = 'm' if d < 1000 else 'km'
        label = str(round(d)) if d < 1000 else str(round(d/1000))
        plt.text(x0 + d + self.ew1 * x / 2, y0, label + ' ' + units, ha = 'left', va = 'center', size = 6, color = color)
        
    def northarrow(self, x, y, color='k'):
        x0 = self.ew1 * x + self.w
        y0 = self.ns1 * y + self.s
        ns1 = self.ns1
        plt.arrow(x0, y0, 0, ns1, width = ns1 / 2, head_width = ns1, color = color)
        plt.text(x0, y0 + ns1 * 3, 'N', ha = 'center', va = 'bottom', size = 8, weight = 'bold', color = color) 


class Decorations:
    """"""
    def __init__(self, ax):
        self.w, self.e, self.s, self.n = ax.get_extent()

        self.ns1 = (self.n - self.s) / 100
        self.ew1 = (self.e - self.w) / 100

    def _get_wesn(self):
        """Return the coordinates of the axis boundary."""
        x0, x1 = self.ax.get_xlim()
        y0, y1 = self.ax.get_ylim()
        w, e, s, n = x0, x1, y0, y1
        return(w, e, s, n)

    def _frame_percent(self):
        """Return the magnitude of length representing 1% of the frame x and y axes."""
        w, e, s, n = self._get_wesn()
        ns1 = (n-s)/100
        ew1 = (e-w)/100
        return(ew1, ns1)

    def scalebar(self, x, y, d, color = 'k', linewidth = 0.5):
        w, e, s, n = self._get_wesn()
        ew1, ns1 = self._frame_percent()
        x0 = ew1 * x + w
        y0 = ns1 * y + s
        plt.plot([x0, x0 + d], [y0, y0], color=color, linewidth=linewidth)
        units = 'm' if d < 1000 else 'km'
        label = str(round(d)) if d < 1000 else str(round(d/1000))
        plt.text(x0+d+ew1*x/2, y0, label+' '+units, ha='left', va='center', size=6, color=color)
        
    def northarrow(self, x, y, color='k'):
        w, e, s, n = self._get_wesn()
        ew1, ns1 = self._frame_percent()
        x0 = ew1 * x + w
        y0 = ns1 * y + s
        plt.arrow(x0, y0, 0, ns1, width=ns1/2, head_width=ns1, color=color)
        plt.text(x0, y0+ns1*3, 'N', ha='center', va='bottom', size=8, weight='bold', color=color) 


class Map(Decorations):
    """Plot a map using matplotlib. Note that this class assumes that the data exists in a Cartesian coordinate system (e.g. UTM); do not use with cartopy projection objects."""
    def __init__(self, proj=None, xlim=(None,None), ylim=(None,None), ticks=1000):
        """
        Attributes:
            proj <cartopy.crs>: A cartopy projection.    
        """
        self.fig, self.ax = plt.subplots()
        if proj:
            self.ax = plt.axes(projection=proj)
        #self._plot_extent(xlim, ylim)
        self.color = 'black'

    def _plot_extent(self, xlim, ylim):
        """Use the matplotlib axes methods 'set_xlim' and 'set_ylim' to define the plot window."""
        if xlim:
            self.ax.set_xlim(xlim)
        if ylim:
            self.ax.set_ylim(ylim)

    def _color(self, c):
        color = c if c else self.color
        return(color)

    def decorations(self, color=None):
        self.north(color=color)
        self.scale(color=color)

    def north(self, x=5, y=90, color=None):
        color = self._color(color)
        self.northarrow(x, y, color)

    def scale(self, x=5, y=5, width=10000, color=None):
        color = self._color(color)
        self.scalebar(x, y, width, color)

    def legend(self, handles):
        plt.legend(handles=handles, loc='lower right', fontsize=4, title='Legend', title_fontsize=6)

    def colorbar(self, label='Raster'):
        """Plot a colorbar to show raster values"""
        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        #cbar = plt.colorbar(cax=cax)
        #cbar.set_label(label)

    def save(self, outfile, dpi=300):
        """"""
        plt.savefig(outfile+'.jpg', format='jpg', dpi=dpi, bbox_inches='tight', pad_inches=0)

def gdf_to_patches(gdf):
    """Convert a GeoDataFrame of classes and rgb colors to legend patches.
        Attributes:
            gdf <geopandas.GeoDataFrame>: A 2-column geodataframe with clases in first column and colors in second"""
    handles = [mpatches.Patch(color=i[1], label=i[0]) for n, i in gdf.iterrows()]
    return(handles)

class MplPalettes:
    """Return the full lists of colour palettes provided by the palettable package by name and returned as matplotlib compatable"""
    import palettable as p

    def pastel1(self):
        """Colorbrewer2 Pastel1 palette"""
        p = self.p.colorbrewer.qualitative.Pastel1_9.mpl_colors
        return(p)
 



#####################################################

def extent_from_vectorbak(x, y, ew = 5000):
    """Return extents of a map from the centre point. Return coordinates in format of matplotlib 'get_extent'"""
    width = ew / 2
    height = ew / 2 * 210 / 297
    w = x - width
    e = x + width
    s = y - height
    n = y + height
    return(w,e,s,n)

def geodataframe_to_centroid(gdf):
    c = gdf.centroid 
    x = c.x.mean()
    y = c.y.mean()
    p = Point(x,y)
    return(p) 
    
        
       
        

def extent_from_vector(geometry, ew = 5000):
    """Return extents of a map from the centre point. Return coordinates in format of matplotlib 'get_extent'"""
    print('wee')
    c = geometry.centroid 
    x = c.x.mean()
    y = c.y.mean()
    wee = point_to_page(Point(x, y), 100)
    print(wee)

    exit()
 
    g = geometry.total_bounds
    print(g)
    print(mean(g[2]-g[0]), g[3]-g[1])

    
    exit()


    print(type(geometry))
    print(dir(geometry))
    print(dir(geometry.total_bounds))
    print(geometry.total_bounds.centroid)
    g = GeometryToPage(geometry)
        
    exit()

    c = geodataframe_to_centroid(geometry)
    print(c)
    exit()

    c = geometry.centroid 
    x = c.x.mean()
    y = c.y.mean()
    print(x, y) 
    
    #print(c)
    #print(type(c.centroid))
    #print(dir(c.centroid))
    #print(min(c.centroid))
    exit()
    x, y = c.x, c.y
    width = ew / 2
    height = ew / 2 * 210 / 297
    w = x - width
    e = x + width
    s = y - height
    n = y + height
    return(w,e,s,n)




def save_plot(outfile, dpi=600, format='png'):    
    plt.savefig(outfile, format = format, dpi = dpi, bbox_inches = 'tight')
    plt.close()

from os.path import dirname, join
import numpy as np
import geopandas as gpd
from .vector import spatial_overlays
from matplotlib.patches import Patch
import tempfile
from matplotlib import cm

from shapely.geometry import Point, LineString, Polygon, MultiLineString

rdir = dirname(__file__)

            
def colorwee(length, pallete = 'Pastel1'):
    """Return a list of sequential greys with a given length between 3 and 9"""
    from palettable.colorbrewer import qualitative as cb
    length = 3 if length < 3 else length
    length = 9 if length > 9 else length
    method = getattr(cb, pallete + '_' + str(length))
    cols = method.colors
    c = []
    for i in cols:
        rgb = []
        for j in i:
            rgb += [j / 255]
        c += [rgb]
    return(c)

  
  
    

class cartography:
    """"""

    def axes(self, n, s, w, e, epsg, ticks=1000):
        """Set standard axes parameters"""
        self.epsg = epsg
        ax = plt.axes(projection = self.proj())
        ax.set_extent([e, w, s, n], self.proj())
        
        # set ticks
        xticks = list(range(round(w), round(e), ticks))
        yticks = list(range(round(s), round(n), ticks))
        ax.tick_params(axis = 'both', which = 'major', labelsize = 6)
        ax.set_xticklabels(xticks, ha = 'left')
        ax.set_yticklabels(yticks, rotation = 90, va = 'bottom')
        
        ax.set_xticks(xticks, crs = self.proj())
        ax.set_yticks(yticks, crs = self.proj())
        return(ax)
    
    def proj(self):
        """Set projection parameters"""
        proj = crs.epsg(self.epsg)
        return(proj)
        
    def point(self, e, n, label = None, color = 'k', markersize=5, linewidth=0):
        """Plot a point"""
        p = plt.plot(e, n, color = color, marker = 'o', markeredgecolor = 'black', markeredgewidth = 0.2, markersize = markersize, label = label, linewidth=linewidth)
        if label:
            plt.annotate(label, xy = (e, n), xytext = (e, n), ha = 'right', va = 'top', fontsize = 8, weight = 'bold')
        return(p)
            
    def line(self, linestring, edgecolor = 'black', linewidth = 2):
        """"""
        ls = linestring
        line_good = []
        start_pt = list(ls.coords)[0]
        for i in range(1,len(ls.coords)):
            end_pt = list(ls.coords)[i]
            simple_line = (start_pt, end_pt)
            line_good.append(simple_line)
            start_pt = end_pt
        lines = MultiLineString(line_good)
        self.ax.add_geometries(lines, crs = self.proj(), edgecolor = edgecolor, linewidth = linewidth)
        
    def plot(self, geometry, facecolor = 'none', edgecolor = 'black', linewidth = 0.5):
        """Plot dataset using cartopy"""
        self.ax.add_geometries(geometry, crs = self.proj(), facecolor = facecolor, edgecolor = edgecolor, linewidth = linewidth)
        
    def save(self, outfile, dpi=600, format='png'):    
        plt.savefig(outfile, format = format, dpi = dpi, bbox_inches = 'tight')
        plt.close()
        
    
def cards2bbox(n, s, w, e):
    """Cardinal boundaries to bounding box"""
    ll = Point(w, s)
    ul = Point(w, n)
    ur = Point(e, n)
    lr = Point(e, s)
    
    lst = [ll, ul, ur, lr]
    bbox = Polygon([[i.x, i.y] for i in lst])
    return(bbox)
    
def clipdf(gdf, bbox):
    """Clip dataframe to a bounding box"""
    clip = gpd.GeoDataFrame(gpd.GeoSeries(bbox), columns = ['geometry'])
    #gdfc = gpd.overlay(gdf, clip, how = 'intersection')
    gdfc = spatial_overlays(gdf, clip)
    return(gdfc)
    


       
