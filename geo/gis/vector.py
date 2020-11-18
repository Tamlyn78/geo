"""Process vector data. Note that many methods are essentially example wrappers for reminder purposes. This is for non-cartopy objects"""
from os.path import splitext
import geopandas as gpd
import shapely.wkt
from shapely.geometry import mapping, Point, LineString, Polygon
from shapely.wkt import loads


class Clip:

    def clip_to_bounds(self, w, s, e, n):
        """Clip to a boundary."""
        p = Polygon([(e,s), (e,n), (w,n), (w,s), (e,s)])
        mask = gpd.GeoDataFrame({'geometry':p, 'id':[1]})
        self.clip = gpd.overlay(self.gdf, mask, how='intersection')

    def clip_to_axes(self, ax):
        """Clip the GeoDataFrame to an axis extent"""
        w, e = ax.get_xlim()
        s, n = ax.get_ylim()
        self.clip_to_bounds(w,s,e,n)


class Vector(Clip):
    """Import a vector from file to a geopandas GeoDataFrame and attach useful methods."""
    def __init__(self, path):
        """Import vector into a GeoDataFrame."""
        self.path = path
        self.gdf = gpd.read_file(path)
    
    def to_epsg(self, epsg):
        """Reproject vector using an EPSG code."""
        self.gdf = self.gdf.to_crs({'init': 'epsg:' + str(epsg)})

    def to_shp(self):
        """Output a GeoDataFrame to a shapefile"""

    def to_geojson(self, path):
        """Save GeoDataFrame as a geojson file"""
        

    def bounds(self):
        """Return a pandas series showing the four bounding coordinates"""
        gdf = self.to_gpd()
        bounds = gdf.total_bounds
        return(bounds)




# cartopy methods

def clip_to_extent(gdf, ax):
    """Clip a geodataframe to an axis extent"""
    w, e, s, n = ax.get_extent()
    p = Polygon([(e,s), (e,n), (w,n), (w,s), (e,s)])
    mask = gpd.GeoDataFrame({'geometry':p, 'id':[1]})
    clip = gpd.overlay(gdf, mask, how='intersection')
    return(clip)

class Clipbak:
    def __init__(self, path):
        """Initialise the class with the full path to a vector file."""
        self.path = path
        self.gdf = Vector(path).gdf

    def clip_to_bounds(self, w, s, e, n):
        """Clip to a boundary."""
        p = Polygon([(e,s), (e,n), (w,n), (w,s), (e,s)])
        mask = gpd.GeoDataFrame({'geometry':p, 'id':[1]})
        self.clip = gpd.overlay(self.gdf, mask, how='intersection')
        #return(clip)

    def clip_to_axis(self, ax):
        """Clip the GeoDataFrame to an axis extent"""
        w, e, s, n = ax.get_extent()
        print(w,e,s,n)
        self.clip_to_bounds(w,s,e,n)
        #return(clip)



class VectorOld:
    def _path(self, path, ext):
        p, e = splitext(path)
        return(path + ext)

    def to_gpd(self):    
        """Return a geopandas GeoDataFrame."""
        gdf = gpd.read_file(self.path)
        return(gdf)

    def to_shp(self):
        """Output a GeoDataFrame to a shapefile"""

    def bounds(self):
        """Return a pandas series showing the four bounding coordinates"""
        gdf = self.to_gpd()
        bounds = gdf.total_bounds
        return(bounds)

class ShapeFile(Vector):
    def __init__(self, path):
        self.path = self._path(path, '.shp')

class GeoJson(Vector):
    def __init__(self, path):
        self.path = self._path(path, '.geojson')

def geoseries_to_centroid(gs):
    """Return the centroid of a geopandas geoseries of shapely geometry. You can obtain a geoseries by selecting the geometry column of a geodataframe. 
    E.g. gdf['geometry']
    """
    c = gs.centroid 
    x = c.x.mean()
    y = c.y.mean()
    p = Point(x,y)
    return(p) 
 
def geometric_centre(gs):
    """Return the spatial centre of a geopandas geoseries of shapely geometry. The spatial centre is different from a centroid in that it is the central point between the maximum and minimum x and y values. This is useful for centring a vactor within a cartographic bounding box.
    You can obtain a geoseries by selecting the geometry column of a geodataframe. 
    E.g. gdf['geometry']
    """
    c = gs.centroid 
    minx, miny, maxx, maxy = [gs.bounds[i] for i in gs.bounds.columns]
    minx, miny, maxx, maxy = min(minx), min(miny), max(maxx), max(maxy)
    x = (maxx-minx)/2 + minx
    y = (maxy-miny)/2 + miny
    p = Point(x,y)
    return(p)

   
 
def spatial_overlays(df1, df2, how='intersection'):
    """Overlay tools of Geopandas are currently (20180425) very slow; 
    this function was found on the interweb to substantially increase speed (needs referencing).
    Compute overlay intersection of two 
        GeoPandasDataFrames df1 and df2
    """
    df1 = df1.copy()
    df2 = df2.copy()
    df1['geometry'] = df1.geometry.buffer(0)
    df2['geometry'] = df2.geometry.buffer(0)
    if how=='intersection':
        # Spatial Index to create intersections
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['histreg']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        pairs = df1['histreg'].to_dict()
        nei = []
        for i,j in pairs.items():
            for k in j:
                nei.append([i,k])
        
        pairs = gpd.GeoDataFrame(nei, columns=['idx1','idx2'], crs=df1.crs)
        pairs = pairs.merge(df1, left_on='idx1', right_index=True)
        pairs = pairs.merge(df2, left_on='idx2', right_index=True, suffixes=['_1','_2'])
        pairs['Intersection'] = pairs.apply(lambda x: (x['geometry_1'].intersection(x['geometry_2'])).buffer(0), axis=1)
        pairs = gpd.GeoDataFrame(pairs, columns=pairs.columns, crs=df1.crs)
        cols = pairs.columns.tolist()
        cols.remove('geometry_1')
        cols.remove('geometry_2')
        cols.remove('histreg')
        cols.remove('bbox')
        cols.remove('Intersection')
        dfinter = pairs[cols+['Intersection']].copy()
        dfinter.rename(columns={'Intersection':'geometry'}, inplace=True)
        dfinter = gpd.GeoDataFrame(dfinter, columns=dfinter.columns, crs=pairs.crs)
        dfinter = dfinter.loc[dfinter.geometry.is_empty==False]
        return(dfinter)
    elif how=='difference':
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['histreg']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0), [x.geometry]+list(df2.iloc[x.histreg].geometry)) , axis=1)
        df1.geometry = df1.new_g
        df1 = df1.loc[df1.geometry.is_empty==False].copy()
        df1.drop(['bbox', 'histreg', new_g], axis=1, inplace=True)
        return(df1)

    
