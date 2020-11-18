"""Produce maps for PhD"""

import os
from os.path import dirname, isdir, join

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiLineString
from cartopy import crs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from palettable.colorbrewer import qualitative as cb

# custom modules
import sys
sys.path.append(join('python', 'pygislib'))
#from .. import data
from pygislib.geopandas import spatial_overlays



outdir = join(dirname(__file__), 'maps')
if not isdir(outdir):
    os.makedirs(outdir)

epsg = 32648

class decorations:

    def __init__(self, n, s, w, e):
        self.n = n
        self.s = s
        self.w = w
        self.e = e
        self.ns1 = (n - s) / 100
        self.ew1 = (e - w) / 100
        
    def scalebar(self, x, y, d, color = 'black'):
        x0 = self.ew1 * x + self.w
        y0 = self.ns1 * y + self.s
        plt.plot([x0, x0 + d], [y0, y0], color = color)
        plt.text(x0 + d + self.ew1 * x / 2, y0, str(round(d / 1000)) + ' km', ha = 'left', va = 'center')
        
    def northarrow(self, x, y):
        x0 = self.ew1 * x + self.w
        y0 = self.ns1 * y + self.s
        wee = (self.ns1 * 1000 / self.ns1)
        plt.arrow(x0, y0, 0, wee, width = wee / 2, head_width = wee, color = 'k')
        plt.text(x0, y0 + wee + self.ns1 * 3, 'N', ha = 'center', va = 'bottom', size = 14, weight = 'bold') 

            
class color:

    def greys(length):
        """Return a list of sequential greys with a given length between 3 and 9"""
        from palettable.colorbrewer import sequential as cb
        length = 3 if length < 3 else length
        length = 9 if length > 9 else length
        method = getattr(cb, 'Greys_' + str(length))
        greys = method.colors
        gy = []
        for i in greys:
            rgb = []
            for j in i:
                rgb += [j / 255]
            gy += [rgb]
        return(gy)

        
class datasets:
    """A compilation of methods to load commonly used datasets in a standard view"""
    
    def gdf(self, path):
        """Load a gis file to a geodataframe"""
        gdf = gpd.read_file(path)
        return(gdf)
    
    def angkor_schematic(self):
        """Plot schematic of angkor"""
        from .player.SCHEMATIC_LINEARS import SCHEMATIC_LINEARS_2450 as ds
        gdf = self.gdf(ds.path)
        return(gdf)

    def angkor_geology(self):
        """Plot schematic of angkor"""
        from .jica import Geology_Cambodia_JICA_50K as ds
        gdf = self.gdf(ds.path)
        return(gdf)
        
    def angkor_catchment(self):
        """Plot schematic of angkor"""
        from .player import catchment as ds
        gdf = self.gdf(ds.path)
        return(gdf)

    def angkor_subcatchments(self):
        """Plot schematic of angkor"""
        from .player import subcatchments as ds
        gdf = self.gdf(ds.path)
        return(gdf)  

    def tonlesap(self):
        """Plot Tonle Sap"""
        from .jica import Hydrology_Areas_JICA_50K as ds
        gdf = self.gdf(ds.path)
        gdf = gdf[gdf['DN_POL_ID'] == 159]
        return(gdf)  

    def roluos_river(self):
        """Plot Tonle Sap"""
        #from .mrc import Hydrology_MRC_50K as ds
        from .player import roluos_river as ds
        gdf = self.gdf(ds.path)
        #gdf = gdf.iloc[24311]
        return(gdf) 

    def puok_river(self):
        """Plot Tonle Sap"""
        #from .mrc import Hydrology_MRC_50K as ds
        from .player import puok_river as ds
        gdf = self.gdf(ds.path)
        #gdf = gdf[gdf['DN_POL_ID'] == 159]
        return(gdf) 

    def siem_reap_river(self):
        """Plot Tonle Sap"""
        #from .mrc import Hydrology_MRC_50K as ds
        from .player import siem_reap_river as ds
        gdf = self.gdf(ds.path)
        #gdf = gdf[gdf['DN_POL_ID'] == 159]
        return(gdf)    

    def gradients(self):
        """"""
        from .player import gradient_analysis as ds
        df = ds.df
        return(df)

class utm(datasets):
    """Make a map on UTM projection"""
    def __init__(self):
        """"""
    
    def proj(self):
        """Set projection parameters"""
        proj = crs.epsg(epsg)
        return(proj)
        
    def axes(self, n, s, w, e):
        """Set standard axes parameters"""
        ax = plt.axes(projection = self.proj())
        ax.set_extent([e, w, s, n], self.proj())
        return(ax)
        
    def point(self, e, n, label = None):
        """Plot a point"""
        plt.plot(e, n, color = 'white', marker = 'o', markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = label)
        if label:
            plt.annotate(label, xy = (e, n), xytext = (e, n), ha = 'right', va = 'top', fontsize = 8, weight = 'bold')
            
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
        
    def plot(self, geometry, facecolor = 'none', edgecolor = 'black'):
        """Plot dataset using cartopy"""
        self.ax.add_geometries(geometry, crs = self.proj(), facecolor = facecolor, edgecolor = edgecolor)
        
        
class annotation(utm):
    def kulen(self, size = 12, ha = 'center', weight = 'bold', rotation = 0):
        e, n = 404000, 1503000
        plt.text(e, n, 'Kulen Hills', size = size, ha = ha, weight = weight, rotation = rotation, transform = self.proj())
        
    def tonlesap(self, size = 12, ha = 'center', weight = 'bold', rotation = 0, color = 'white'):
        e, n = 370000, 1457000
        plt.text(e, n, 'Tonle Sap', size = size, ha = ha, weight = weight, rotation = rotation, color = color, transform = self.proj())
        
    def phnom_krom(self, size = 12, ha = 'center', weight = 'regular', rotation = 0, color = 'black'):
        e, n = 366500, 1469500
        plt.text(e, n, 'Phnom Krom', size = size, ha = ha, weight = weight, rotation = rotation, color = color, transform = self.proj())
        
    def phnom_bakheng(self, size = 12, ha = 'center', weight = 'regular', rotation = 0, color = 'black'):
        e, n = 370200, 1483000
        plt.text(e, n, 'Phnom Bakheng', size = size, ha = ha, weight = weight, rotation = rotation, color = color, transform = self.proj())
        
    def phnom_bok(self, size = 12, ha = 'center', weight = 'regular', rotation = 0, color = 'black'):
        #e, n = 394000, 1491000
        e, n = 394200, 1489500
        plt.text(e, n, 'Phnom Bok', size = size, ha = ha, weight = weight, rotation = rotation, color = color, transform = self.proj())
        
    def roluos_river(self, size = 8, ha = 'left', va = 'center', weight = 'bold', rotation = 0, color = 'black'):
        e, n = 389500, 1477000
        plt.text(e, n, 'Roluos River', size = size, ha = ha, weight = weight, rotation = 95, color = color, transform = self.proj())
        
    def puok_river(self, size = 8, ha = 'left', va = 'center', weight = 'bold', rotation = 0, color = 'black'):
        e, n = 358500, 1484800
        plt.text(e, n, 'Puok River', size = size, ha = ha, weight = weight, rotation = 22, color = color, transform = self.proj())
        
    def siem_reap_river(self, size = 8, ha = 'left', va = 'center', weight = 'bold', rotation = 0, color = 'black'):
        e, n = 376000, 1481000
        plt.text(e, n, 'Siem Reap River', size = size, ha = ha, weight = weight, rotation = 68, color = color, transform = self.proj())
        
        
class geology(utm):
    """Plot a map of geology around the Angkor catchment area"""
    
    def __init__(self):

        fig = plt.figure(figsize = (16,19.2))
        n, s, e, w = data.region('catchment')
        self.ax = self.axes(n, s, w, e)
        g = color.greys(9)

        # geological features
        gdf = self.angkor_geology()
        
        phnom_kulen = gdf[(gdf['SYMBOL'] == 'JCcg') | (gdf['SYMBOL'] == 'JCg') | (gdf['SYMBOL'] == 'J1-2') | (gdf['SYMBOL'] == 'Co')]
        self.plot(phnom_kulen['geometry'], facecolor = g[0], edgecolor = g[0])
        
        floodplain = gdf[gdf['SYMBOL'] == 'Fp']
        self.plot(floodplain['geometry'], facecolor = g[1], edgecolor = g[1])
        
        pediments = gdf[(gdf['SYMBOL'] == 'Pd') | (gdf['SYMBOL'] == 'PL') | (gdf['SYMBOL'] == 'NC') | (gdf['SYMBOL'] == 'p2') | (gdf['SYMBOL'] == 'Csq') | (gdf['SYMBOL'] == 'a') | (gdf['SYMBOL'] == 'di') | (gdf['SYMBOL'] == 'Ta')]
        self.plot(pediments['geometry'], facecolor = g[2], edgecolor = g[2])
        
        alluvial_fans = gdf[gdf['SYMBOL'] == 'Af']
        self.plot(alluvial_fans['geometry'], facecolor = g[3], edgecolor = g[3])
        
        lake_bed_deposits = gdf[gdf['SYMBOL'] == 'Lb']
        self.plot(lake_bed_deposits['geometry'], facecolor = g[4], edgecolor = g[4])
        
        organic_deposits = gdf[(gdf['SYMBOL'] == 'Sw') | (gdf['SYMBOL'] == 'Br')]
        self.plot(organic_deposits['geometry'], facecolor = g[5], edgecolor = g[5])
        
        water = gdf[gdf['SYMBOL'] == 'W']
        self.plot(water['geometry'], facecolor = g[6], edgecolor = g[6])
        
        intrusions = gdf[gdf['SYMBOL'] == 'r2t']
        self.plot(intrusions['geometry'], facecolor = g[7], edgecolor = g[7])
        
        deltaic_deposits = gdf[gdf['SYMBOL'] == 'Dd']
        self.plot(deltaic_deposits['geometry'], facecolor = g[3], edgecolor = 'k')
        alluvial_terrace = gdf[gdf['SYMBOL'] == 'Ta']
        self.plot(deltaic_deposits['geometry'], facecolor = g[3], edgecolor = g[3])  
        
        
        # angkor schematic
        gdf = self.angkor_schematic()
        self.plot(gdf['geometry'], edgecolor = g[0])
        
        
        # annotations
        a = annotation()
        a.kulen()
        a.tonlesap()
        a.phnom_krom()
        a.phnom_bakheng()
        a.phnom_bok()

        # decorations
        s = decorations(n, s, w, e)
        s.scalebar(2, 2, 10000)
        s.northarrow(2, 91)
        
        # save to file
        self.ax.outline_patch.set_edgecolor('white')
        outpath = join(outdir, 'geology.png')
        plt.savefig(outpath, format = 'png', dpi = 600, bbox_inches = 'tight', pad_inches = 0)
        
        
class hydrology(utm):
    """Plot a map of geology around the Angkor catchment area"""
    
    def __init__(self):

        fig = plt.figure(figsize = (16,19.2))
        n, s, e, w = data.region('catchment')
        self.ax = self.axes(n, s, w, e)
        gry = color.greys(9)


        # hydrological features
        gdf = self.angkor_subcatchments()
        self.plot(gdf['geometry'], facecolor = 'white', edgecolor = 'black')
        gdf['area'] = gdf['geometry'].area
        
        gdf = gdf.sort_values('area')
        gdf['color'] = [i/255 for i in range(50, 255, 5)][1:28]

        for i in gdf.index:
            geom = gdf['geometry'].iloc[i]
            clr = gdf['color'].iloc[i]
            self.plot([geom], facecolor = [clr,clr,clr], edgecolor = [clr+0.1,clr+0.1,clr+0.1])
        
        # tonle sap
        gdf = self.tonlesap()
        self.plot(gdf['geometry'], facecolor = gry[5], edgecolor = gry[5])
        
        # angkor schematic
        gdf = self.angkor_schematic()
        self.plot(gdf['geometry'], edgecolor = 'black')
        
        # rivers
        gdf = self.roluos_river()
        for i in gdf['geometry']:
            self.line(i, edgecolor = 'white')
        gdf = self.puok_river()
        for i in gdf['geometry']:
            self.line(i, edgecolor = 'white')
        gdf = self.siem_reap_river()
        for i in gdf['geometry']:
            self.line(i, edgecolor = 'white')
            
        # annotations
        a = annotation()
        a.kulen()
        a.tonlesap()
        a.roluos_river()
        a.puok_river()
        a.siem_reap_river()

        # decorations
        s = decorations(n, s, w, e)
        s.scalebar(2, 2, 10000)
        s.northarrow(2, 91)
        
        # save to file
        self.ax.outline_patch.set_edgecolor('white')
        outpath = join(outdir, 'hydrology.png')
        plt.savefig(outpath, format = 'png', dpi = 600, bbox_inches = 'tight', pad_inches = 0)
        
        
class lineaments(utm):
    """"""    
    
    def __init__(self):
        
        fig = plt.figure(figsize = (16,19.2))
        n, s, e, w = data.region('catchment')
        self.ax = self.axes(n, s, w, e)
        gry = color.greys(9)
        
        # angkor schematic
        #gdf = self.angkor_schematic()
        #self.plot(gdf['geometry'], edgecolor = 'black')
        
        # gradient analyses
        df = self.gradients()
        lst = []
        for i in df.index:
            #print(i)
            try:
                row = df.iloc[i]
                a1 = df['label1'].iloc[i]
                a2 = df['label2'].iloc[i]
                e0 = df['easting'].iloc[i]
                e1 = df['easting'].iloc[i+1]
                n0 = df['northing'].iloc[i]
                n1 = df['northing'].iloc[i+1]
                #wth = df['elevation'].iloc[i] / 20
                ls = LineString([Point(e0, n0), Point(e1, n1)])
                lst += [ls]

            except:
                pass
                
        iter = [i[1] for i in df.groupby('label1')]
                
        for i in iter:
            lab1 = i['label1'].unique()
            lab2 = i['label2'].unique()
            for j in i.index:
                try:
                    print(j, lab1)
                    row = i.loc[j]
                    e0 = df['easting'].loc[j]
                    e1 = df['easting'].loc[j+1]
                    n0 = df['northing'].loc[j]
                    n1 = df['northing'].loc[j+1]
                    wth = df['elevation'].loc[j] / 20
                    ls = LineString([Point(e0, n0), Point(e1, n1)])
                    self.ax.add_geometries([ls], crs = self.proj(), edgecolor = 'black', linewidth = wth)
                except:
                    pass 

            
        # annotations
        a = annotation()

        # decorations
        s = decorations(n, s, w, e)
        s.scalebar(2, 2, 10000)
        s.northarrow(2, 91)
        
        # save to file
        self.ax.outline_patch.set_edgecolor('white')
        outpath = join(outdir, 'lineaments.png')
        plt.savefig(outpath, format = 'png', dpi = 600, bbox_inches = 'tight', pad_inches = 0)
        
        
        
# import data from main project directory
from .. import data

import os
from os.path import dirname, isdir, join
import sys
sys.path.append(join('python', 'pygislib'))

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from shapely.geometry import Point, Polygon, MultiLineString
from cartopy import crs as crs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from palettable.colorbrewer import qualitative as cb

from pygislib.geopandas import spatial_overlays

from .pottier.Features_Pottier_1999 import Features_Pottier_1999 as pottier
from .evans import Features_Evans_2006 as evans

outdir = join(dirname(__file__), 'maps')
if not isdir(outdir):
    os.makedirs(outdir)

epsg = 32648

def greys():
    """Return a matplotlib compatible list of grey rgb values"""
    from palettable.colorbrewer import sequential as cb
    lst1 = []
    for i in cb.Greys_9.colors:
        lst2 = []
        for j in i:
            lst2 += [j / 255]
        lst1 += [lst2]
    return(lst1)
 
def proj():
    """Return the cartopy projection"""
    proj = crs.epsg(epsg)
    return(proj)
    
def region_proj():
    """Define longlat projection for the regional view"""
    #gl = crs.Globe(datum = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    #gl = crs.Globe(datum = '+proj=longlat +datum=WGS84 +no_defs')
    proj = crs.Mercator()
    return(proj)
    
def region_extents():
    """Return the extents for a standard regional view of southeast asia"""
    n = 30
    s = 0
    e = 115
    w = 90
    return([n,s,e,w])
    
def site():
    """Return point location for the study site"""
    e, n = 377018.078, 1489918.093
    return(e, n)
    
def study_area(path = '/media/sam/qs/projects/_45/gis/StudyArea/StudyArea.shp'):
    """Import study area polygon"""
    gdf = gpd.read_file(path).to_crs({'init': 'epsg:' + str(epsg)})
    return(gdf)
    
def test_areas(path = '/media/sam/qs/projects/_45/gis/TestAreas/TestAreas.shp'):
    """Import test area points"""
    gdf = gpd.read_file(path).to_crs({'init': 'epsg:' + str(epsg)})
    return(gdf)
    #points = list(Reader(path).geometries())
    #return(points)
    
def poly2centroid():
    """Return the centroid of a polygon"""
    
def cards2bbox(n, s, e, w):
    """Cardinal boundaries to bounding box"""
    ll = Point(w, s)
    ul = Point(w, n)
    ur = Point(e, n)
    lr = Point(e, s)
    
    lst = [ll, ul, ur, lr]
    bbox = Polygon([[i.x, i.y] for i in lst])
    return(bbox)
    
def point2bbox(x, y, width = 4000):
    """Convert a point to a bounding box with A4 paper proportions"""

    w = width
    x0 = x - w / 2
    x1 = x + w / 2
    
    h = height = width * 21 / 29.7
    y0 = y - h / 2
    y1 = y + h / 2
    
    ll = Point(x0, y0)
    ul = Point(x0, y1)
    ur = Point(x1, y1)
    lr = Point(x1, y0)
    
    lst = [ll, ul, ur, lr]
    bbox = Polygon([[i.x, i.y] for i in lst])

    return(bbox)
    
def vect2gdf(path):
    """Read vector to a dataframe"""
    gdf = gpd.read_file(path).to_crs({'init': 'epsg:' + str(epsg)})
    #gdf.to_file('/home/sam/wee.json', driver = "GeoJSON")
    return(gdf)
    
def clipdf(gdf, bbox):
    """Clip dataframe to a bounding box"""
    clip = gpd.GeoDataFrame(gpd.GeoSeries(bbox), columns = ['geometry'])
    #gdfc = gpd.overlay(gdf, clip, how = 'intersection')
    gdfc = spatial_overlays(gdf, clip)
    return(gdfc)
    
def cats2colours(cats, reverse = False):
    """Return a dictionary of category colours"""
    if reverse == False:
        pallete = cb.Pastel1_9.colors
    else:
        pallete = reversed(cb.Pastel1_9.colors)
    colours = []
    for i in pallete:
        rgb = ','.join([str(j / 255) for j in i])
        colours += [rgb]
    d = dict(zip(cats, colours))
    return(d)
    
def format_axes(ax, bbox):
    """"""

    ax.set_aspect('equal')
    ax = plt.axes(projection = proj())
    extent = [bbox.bounds[i] for i in [0, 2, 1, 3]]
    ax.set_extent(extent, crs = proj())
    
    # set ticks
    x1 = extent[0]
    x2 = extent[1]
    y1 = extent[2]
    y2 = extent[3]
    
    xticks = list(range(round(x1), round(x2), 1000))
    yticks = list(range(round(y1), round(y2), 1000))
    
    #ax.tick_params(axis = 'both', which = 'major', labelsize = 5, direction = 'in')
    ax.tick_params(axis = 'both', which = 'major', labelsize = 6)
    #ax.tick_params(axis = 'x', which = 'major', pad = -10)
    #ax.tick_params(axis = 'y', which = 'major', pad = -10)
    #ax.xaxis.set_tick_params(labeltop = 'on', labelbottom = 'off')
    ax.set_xticklabels(xticks, ha = 'left')
    ax.set_yticklabels(yticks, rotation = 90, va = 'bottom')
    
    ax.set_xticks(xticks, crs = proj())
    ax.set_yticks(yticks, crs = proj())
    #return(ax)
    
    
def test(dic):
    """"""
    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    
    # create plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax = plt.axes(projection = proj())
    extent = [bbox.bounds[i] for i in [0, 2, 1, 3]]
    ax.set_extent(extent, crs = proj())
    #ax = format_axes(ax, bbox)
    
    # add study area
    sa = study_area()
    ax.add_geometries(sa['geometry'], crs = proj(), color = 'red', facecolor = "None")
    
    wee = sa['geometry'].centroid
    print(wee)
    ax.add_geometries(wee, crs = proj())
    
    # add test areas
    ta = test_areas()
    for i in ta['id']:
        p = ta.loc[ta['id'] == i]['geometry'].item()
        plt.text(p.x, p.y, str(i), fontsize = 8)
    
    plt.show()
    
    
def geologybak(dic, catcol = 'Lett_Sym_1'):
    """"""

    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    
    # read shapefile to dataframe
    gdf1 = vect2gdf('/media/sam/gis/data/GSNSW/Wollongong_PortHacking_geol100k_shape/Wollongong_PortHacking100_RockUnit_MGAz56.shp')
    gdf1[catcol] = gdf1['LETT_SYMB']

    gdf2 = vect2gdf('/media/sam/gis/data/GSNSW/Penrith_geol100k_shape/Penrith100RockUnit_MGA56.shp')
    
    gdf = gdf1.append(gdf2, ignore_index = True)
    #gdf = gdf2
    
    # clip dataframe to figure extents
    gdf = clipdf(gdf, bbox)

    # export a table of data

    # assign colors to classes
    cats = sorted(gdf[catcol].dropna().unique())
    cdict = cats2colours(cats)

    # create plot
    fig, ax = plt.subplots()
    ax = format_axes(ax, bbox)

    # add shapefile
    #ax.add_geometries(gdf['geometry'], crs = proj(), facecolor = 'red')
    leglst = []
    for key in cdict.keys():
        geom = gdf.loc[gdf[catcol] == key]['geometry']
        colour = tuple([i for i in cdict[key].split(',')])
        ax.add_geometries(geom, crs = proj(), facecolor = colour)
        leg = patches.Patch(color = colour, label = key)
        leglst.append(leg)

    # add point location
    #point = plt.plot(e, n, color = 'red', marker = 'o', linewidth = 0, markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = 'Site')
    
    # add study area
    sa = study_area()
    ax.add_geometries(sa['geometry'], crs = proj(), color = 'red', facecolor = "None")
    leg = patches.Patch(edgecolor = 'red', facecolor = "None", label = 'Study Area')
    leglst = [leg] + leglst
    
    # add test areas
    ta = test_areas()
    for i in ta['id']:
        p = ta.loc[ta['id'] == i]['geometry'].item()
        plt.text(p.x, p.y, str(i), fontsize = 8)
    
    plt.legend(handles = leglst, loc = 'lower right', fontsize = 8)

    plt.tight_layout()
    plt.show()
    #plt.savefig(dic['outfile'], dpi = 600)
    
    
def soil(dic, catcol = 'NAME'):
    """"""

    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    
    # read shapefile to dataframe
    gdf1 = vect2gdf('/media/sam/gis/data/NSWOEH/Soils_SoilLandscapes_Wollongong_20170526/Data/Soils_WollongongPortHacking_GDA94.shp')
    
    gdf2 = vect2gdf('/media/sam/gis/data/NSWOEH/Soils_SoilLandscapes_Penrith_20170526/Data/Soils_Penrith_GDA94.shp')
    
    gdf = gdf1.append(gdf2, ignore_index = True)

    # clip dataframe to figure extents
    gdf = clipdf(gdf, bbox)

    # export a table of data
    
    # assign colors to classes
    cats = sorted(gdf[catcol].unique())
    #cats = ['BLACKTOWN', 'LUCAS HEIGHTS', 'LUDDENHAM', 'BIRRONG', 'DEEP CREEK', 'GYMEA', 'WATER']
    cdict = cats2colours(cats, reverse = True)

    # create plot
    fig, ax = plt.subplots()
    ax = format_axes(ax, bbox)
    
    # add shapefile
    leglst = []
    for key in cdict.keys():
        geom = gdf.loc[gdf[catcol] == key]['geometry']
        colour = tuple([i for i in cdict[key].split(',')])
        ax.add_geometries(geom, crs = proj(), facecolor = colour)
        leg = patches.Patch(color = colour, label = key.title())
        leglst.append(leg)

    # add point location
    #point = plt.plot(e, n, color = 'red', marker = 'o', linewidth = 0, markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = 'Site')
    
    # add study area
    sa = study_area()
    ax.add_geometries(sa['geometry'], crs = proj(), color = 'red', facecolor = "None")
    leg = patches.Patch(edgecolor = 'red', facecolor = "None", label = 'Study Area')
    leglst = [leg] + leglst
    
    # add test areas
    ta = test_areas()
    for i in ta['id']:
        p = ta.loc[ta['id'] == i]['geometry'].item()
        plt.text(p.x, p.y, str(i), fontsize = 8)

    plt.legend(handles = leglst, loc = 'lower right', fontsize = 8)

    plt.tight_layout()
    plt.savefig(dic['outfile'], dpi = 600)
    
    
            
            
def elevation(dic):
    """"""
    import rasterio
    
    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    

    
    lid = rasterio.open('/media/sam/qs/projects/_45/gis/LiDar2.tif')
    #print(lid.driver)
    #print(lid.height, lid.width)
    #print(lid.shape)
    #print(lid.count)
    #print(lid.crs)
    #print(lid.affine)
    
    arr = lid.read(1)
    
    xmin = lid.transform[0]
    xmax = lid.transform[0] + lid.transform[1] * lid.width
    ymin = lid.transform[3] + lid.transform[5] * lid.height
    ymax = lid.transform[3]
    
    crs = crs.epsg(epsg)
    
    # create plot
    fig, ax = plt.subplots()
    ax = format_axes(ax, bbox)
    
    #plt.imshow(arr, origin = 'upper', extent = [xmin, xmax, ymin, ymax], transform = crs, interpolation = 'nearest', cmap = 'terrain')
    plt.imshow(arr, origin = 'upper', extent = [xmin, xmax, ymin, ymax], transform = crs, interpolation = 'nearest', cmap = 'terrain', vmin = 50, vmax = 160)

    
    # add point location
    #point = plt.plot(e, n, color = 'red', marker = 'o', linewidth = 0, markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = 'Site')
    
    # add study area
    sa = study_area()
    ax.add_geometries(sa['geometry'], crs = proj(), color = 'red', facecolor = "None")
    leg = patches.Patch(edgecolor = 'red', facecolor = "None", label = 'Study Area')

    plt.legend(handles = [leg], loc = 'lower right', fontsize = 8)
    #plt.legend(handles = point, loc = (0.85, 0.25), fontsize = 8)
    
    # add test areas
    ta = test_areas()
    for i in ta['id']:
        p = ta.loc[ta['id'] == i]['geometry'].item()
        plt.text(p.x, p.y, str(i), fontsize = 8)
    
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    
    # raster legend
    cbaxes = inset_axes(ax, width = "5%", height = "20%", loc = 3)
    cbaxes.tick_params(axis = 'both', which = 'major', labelsize = 6)
    rleg = plt.colorbar(cax = cbaxes)
    plt.text(0.18, 1.1, 'm a.s.l')

    
    #plt.show()
    plt.tight_layout()
    plt.savefig(dic['outfile'], dpi = 600)
    
import itertools
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return([i for i in zip(a, b)])


def location(dic):
    """"""
    from cartopy.io.img_tiles import OSM
    
    from pyproj import Proj, transform
    
    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    #bounds = [bbox.bounds[i] for i in [0, 2, 1, 3]]
    bounds = bbox.bounds
    

    osm_tiles = OSM()

    fig, ax = plt.subplots()
    ax = format_axes(ax, bbox)

    ax = plt.axes(projection = proj())

    ax.set_extent([bounds[i] for i in [0,2,1,3]], proj())
    
    # Add the tiles at zoom level 12.
    ax.add_image(osm_tiles, 15)
    
    # add point location
    #point = plt.plot(e, n, color = 'red', marker = 'o', linewidth = 0, markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = 'Site')
    
    # add study area
    sa = study_area()
    ax.add_geometries(sa['geometry'], crs = proj(), color = 'red', facecolor = "None")
    leg = patches.Patch(edgecolor = 'red', facecolor = "None", label = 'Study Area')
    
    # add test areas
    ta = test_areas()
    for i in ta['id']:
        p = ta.loc[ta['id'] == i]['geometry'].item()
        plt.text(p.x, p.y, str(i), fontsize = 8)

    plt.legend(handles = [leg], loc = 'lower right', fontsize = 8)
    
    #plt.show()
    plt.tight_layout()
    plt.savefig(dic['outfile'], dpi = 600)
    
    

def google_earth(outfile = None):
    """Create a google map"""
    from cartopy.io.img_tiles import GoogleTiles
    
    from pyproj import Proj, transform
    
    # return coordinates of site location
    e, n = site()
    
    # calculate figure extents
    bbox = point2bbox(e, n)
    bounds = bbox.bounds

    google_tiles = GoogleTiles(style = 'satellite')

    fig, ax = plt.subplots()
    ax = format_axes(ax, bbox)

    ax = plt.axes(projection = proj())

    ax.set_extent([bounds[i] for i in [0,2,1,3]], proj())
    
    # Add the tiles at zoom level 15.
    ax.add_image(google_tiles, 15)
    
    plt.tight_layout()
    plt.show()
    if outfile:
        plt.savefig(outfile, dpi = 600)
    
    

    


    
    
############## EVERYTHING BELOW HERE IS GREAT ##########################




    
    
class regional:
    def __init__(self):
        """Make a regional map with standard view of extents"""
        
    def proj(self):
        """"""
        proj = crs.Mercator()
        #proj = crs.PlateCarree()
        return(proj)
        
    def extents(self):
        """"""
        n = 30
        s = 0
        e = 115
        w = 90
        return([n,s,e,w])
        
    def axes(self):
        """"""
        cardinals = self.extents()
        extent = [cardinals[i] for i in [3,2,1,0]]
        
        ax = plt.axes(projection = self.proj())
        ax.set_extent(extent, self.proj())

        x1 = extent[0]
        x2 = extent[1]
        y1 = extent[2]
        y2 = extent[3]

        xticks = [i for i in range(round(x1), round(x2), round((x2 - x1) / 5))]
        yticks = [i for i in range(round(y1), round(y2), round((y2 - y1) / 5))]
        
        ax.tick_params(axis = 'both', which = 'major', length = 5, labelsize = 10, direction = 'in', pad = 0)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)
        return(ax)
        
    def greys(self):
        """"""
        from palettable.colorbrewer import sequential as cb
        lst1 = []
        for i in cb.Greys_3.colors:
            lst2 = []
            for j in i:
                lst2 += [j / 255]
            lst1 += [lst2]
        return(lst1)

    def point(self, e, n, label = None):
        """Plot a point"""
        plt.plot(e, n, color = 'white', marker = 'o', markeredgecolor = 'black', markeredgewidth = 0.2, markersize = 5, label = label)
        if label:
            plt.annotate(label, xy = (e, n), xytext = (e, n), ha = 'right', va = 'top', fontsize = 8, weight = 'bold')
        
    def plot(self, gdf, facecolor = 'none', edgecolor = 'black'):
        """"""
        self.ax.add_geometries(gdf['geometry'], crs = region_proj(), facecolor = facecolor, edgecolor = edgecolor)
        
    def coastline(self, dict, andaman_sea = True, south_china_sea = True):
        """"""
        from .naturalearth import ne_50m_coastline as coast
        gdf = gpd.read_file(coast.path)
        dict['gdf'] = gdf
        self.plot(**dict)
            
        if andaman_sea:
            plt.text(95.5, 11, 'Andaman\nSea', size = 18, ha = 'center',weight = 'bold', transform = self.proj())
            
        if south_china_sea:
            plt.text(112, 15, 'South\nChina\nSea', size = 18, ha = 'center', weight = 'bold', transform = self.proj())

    def empire(self, dict):
        """"""
        from .thematic.archaeology import SCHEMATIC_empire_extent as empire
        gdf = gpd.read_file(empire.path)
        dict['gdf'] = gdf
        self.plot(**dict)
    
    def rivers(self, dict, song_hong = True, irrawaddy = True, salween = True, mekong = True):
        """"""
        from .naturalearth import ne_10m_rivers_lake_centerlines as rivers
        gdf = gpd.read_file(rivers.path)
        gdf = gdf[
            (gdf['name'] == 'Hong (Red)') | 
            (gdf['name'] == 'Ayeyarwady (Irrawaddy)') |
            (gdf['name'] == 'Salween') |
            (gdf['name'] == 'Mekong') |
            (gdf['name'] == 'Tonle Sap')
            ]
            
        # the following needs simplification; it's required because of an apparent bug/design that linestrings are filled with colour and must be broken down into individual line segments for display
        for i in gdf['geometry']:
            if i.type == 'MultiLineString':
                line_good = []
                for l in i:
                    start_pt = list(l.coords)[0]
                    for i in range(1,len(l.coords)):
                        end_pt = list(l.coords)[i]
                        simple_line = (start_pt, end_pt)
                        line_good.append(simple_line)
                        start_pt = end_pt
                lines = MultiLineString(line_good)
                self.ax.add_geometries(lines, crs = region_proj(), edgecolor = 'black', linewidth = 2)
            elif i.type == 'LineString':
                line_good = []
                start_pt = list(i.coords)[0]
                for j in range(1,len(i.coords)):
                    end_pt = list(i.coords)[j]
                    simple_line = (start_pt, end_pt)
                    line_good.append(simple_line)
                    start_pt = end_pt
            lines = MultiLineString(line_good)
            self.ax.add_geometries(lines, crs = region_proj(), edgecolor = 'black', linewidth = 2)
            
        if song_hong:
            plt.text(104.75, 23, 'Song Hong', size = 12, ha = 'center', weight = 'bold', rotation =  -40, transform = self.proj())
            
        if irrawaddy:
            plt.text(94.75, 22.25, 'Irrawaddy', size = 12, ha = 'center', weight = 'bold', rotation =  40, transform = self.proj())
            
        if salween:
            plt.text(97.25, 20.25, 'Salween', size = 12, ha = 'center', weight = 'bold', rotation =  70, transform = self.proj())
            
        if mekong:
            plt.text(105.75, 16.5, 'Mekong', size = 12, ha = 'center', weight = 'bold', rotation =  -45, transform = self.proj())
                
            
    def tonle_sap(self, dict, annotation = True):
        """"""
        from .naturalearth import ne_10m_lakes as lakes
        gdf = gpd.read_file(lakes.path)
        gdf = gdf[gdf['name'] == 'Tonle Sap']
        dict['gdf'] = gdf
        self.plot(**dict)
        
        if annotation:
            plt.text(103.5, 12, 'Tonle\nSap', size = 10, ha = 'center', weight = 'bold', transform = self.proj())

    def cambodia(self, dict):
        """"""
        from .borders import Cambodia
        gdf = gpd.read_file(Cambodia.path).to_crs(epsg = 4326)
        dict['gdf'] = gdf
        self.plot(**dict)
        
    def tai(self):
        """"""
        e, n = 102.5, 19
        plt.text(e, n, 'Tai', size = 12, ha = 'center', weight = 'bold', transform = self.proj())
        b = 0.2
        plt.arrow(e - b, n - b, -(e - 100.58803) + b*2, -(n - 14.369559) + b*2, width = 0.01, length_includes_head = True, head_width = 0.1, color = 'black')

        #style="Simple,tail_width=0.5,head_width=4,head_length=8"
        #kw = dict(arrowstyle=style, color="k")
        #patches.FancyArrowPatch((95, 12), (100, 6), **kw)

        #plt.plot([e, n], [100.58803, 14.369559], color = 'red', linewidth = 5, marker = 'o', transform = self.proj())
        
    def dai_viet(self):
        """"""
        e, n = 106.75, 17.5
        plt.text(e, n, 'Dai Viet', size = 12, ha = 'center', weight = 'bold', rotation = -45, transform = self.proj())
        b = 0.2
        plt.arrow(e - b, n - b*2, -(e - 109) - b, -(n - 13.25) - b*2, width = 0.01, length_includes_head = True, head_width = 0.1, color = 'black')
        
    def champa(self):
        """"""
        plt.text(109, 13.25, 'Champa', size = 12, ha = 'center', weight = 'bold', rotation = -90, transform = self.proj())

class khmer_empire(regional):
    """Make a map of the extent of the Khmer empire with relevant locations"""
    
    def __init__(self):

        fig = plt.figure(figsize = (16,19.2))

        self.ax = self.axes()
        c = self.greys()
        self.coastline({'edgecolor':c[2]})
        self.empire({'facecolor':c[0]})
        self.cambodia({'facecolor':c[1]})
        self.tonle_sap({'facecolor':'black'})
        self.rivers({'edgecolor':c[2]})
        
        self.dai_viet()
        self.champa()

        from pyproj import Proj, transform
        inProj = Proj(init = 'epsg:' + str(epsg))
        outProj = Proj(init = 'epsg:4326')

        p = data.point_location('phnom_penh', 'cambodia')
        e, n = transform(inProj, outProj, p[0], p[1])
        self.point(e, n, 'Phnom Penh')
        
        p = data.point_location('oc_eo', 'cambodia')
        e, n = transform(inProj, outProj, p[0], p[1])
        self.point(e, n, 'Oc Eo')

        p = data.point_location('angkor_borei', 'cambodia')
        e, n = transform(inProj, outProj, p[0], p[1])
        self.point(e, n, 'Angkor Borei')

        p = data.point_location('ayutthaya', 'cambodia')
        e, n = p[0], p[1]
        self.point(e, n, 'Ayutthaya')

        self.tai()


        self.ax.outline_patch.set_edgecolor('white')
        plt.savefig('test.pdf', format = 'pdf', dpi = 600, bbox_inches = 'tight', pad_inches = 0)



    
def tpcz():
    """Make a test map of the tpcz"""
    df = data.regions
    cardinals = data.region('tpcz')
    extent = [cardinals[i] for i in [3,2,1,0]]
    
    ax = plt.axes(projection = proj())
    ax.set_extent(extent, proj())
    
    gdf = gpd.read_file(evans.path).to_crs({'init': 'epsg:' + str(epsg)})
    bbox = cards2bbox(*cardinals)
    gdf = clipdf(gdf, bbox)
    
    fill = evans.fcolors
    edge = evans.colors
    for i in fill.keys():
        g = gdf.loc[gdf['type'] == int(i)]['geometry']
        f = [i / 255 for i in fill[i]]
        e = [i / 255 for i in edge[i]]
        ax.add_geometries(g, crs = proj(), facecolor = f, edgecolor = e)
    
    plt.show()
