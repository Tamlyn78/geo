"""Process raster data"""

from os import sep
from os.path import join
import gdal
import osr
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from tempfile import NamedTemporaryFile


# read and write
def read_tif(path):
    """Read a geotif file."""
    ds = gdal.Open(path)
    return(ds)
    
def subset_raster(ds, outfile, ulx, uly, lrx, lry):
    """Create a subset of raster tif"""
    gdal.Translate(outfile, ds, projWin=[ulx,uly,lrx,lry])
    ds = None

def read_zip(path):
    """Read a dataset from a zipfile without decompressing"""
    tic = time.clock()
    p = join(sep, 'vsizip', path, path.replace('zip','tif'))
    ds = gdal.Open(p)
    return(ds)


    
# mapping tools
def colorbar(fig, left, bottom, width, height, labelsize, tcolor='black'):
    import matplotlib.pyplot as plt
    ax = fig.add_axes([left, bottom, width, height])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_frame_on(False)
    cbar = plt.colorbar(fraction=1)
    cbar.outline.set_linewidth(0.5)
    cbar.ax.tick_params(labelsize=labelsize, color=tcolor, labelcolor=tcolor, width=0.5)
    return(fig)


# online datasets
class OpenStreetMap:
    """Plot Open Street Map tiles on a matplotlib axis"""
    def __init__(self, zoom=14):
        from cartopy.io.img_tiles import OSM
        self.zoom = zoom
        self.tiles = OSM()

    def plot(self, ax):
        ax.add_image(self.tiles, self.zoom)


class GoogleEarth:
    """Plot current Google Earth imagery on a matplotlib axis. Styles also include 'street' (useful for when OSM doesn't work)"""
    def __init__(self, style='satellite'):
        from cartopy.io.img_tiles import GoogleTiles
        self.tiles = GoogleTiles(style=style)

    def plot(self, ax):
        """Last time this was used it threw an error when saving the file. A workaround was to code the command in the main script."""
        ax.add_image(self.tiles)


def Wee(filename='location', zoom=14):
    from cartopy.io.img_tiles import GoogleTiles as T
    m = cart()
    wee = T(style='street')
    m.ax.add_image(wee, zoom)
    #r.GoogleEarth(style='street').plot(m.ax)
    outfile = mkjoin(mapdir, filename)
    m.save(outfile)



class SixMaps:
    """Plot NSW SixMaps imagery on a matplotlib axis"""
    def __init__(self):
        self.url = 'http://maps.six.nsw.gov.au/arcgis/services/public/NSW_Imagery/MapServer/WMSServer?request=GetCapabilities&service=WMS'

    def plot(self, ax):
        ax.add_wms(wms=self.url, layers=['0'])


# georeferencing tools
def reproject_tif(inpath, outpath, crs='EPSG:4326'):
    """Reproject a geotif dataset. This code is sourced from the rasterio documentation <https://rasterio.readthedocs.io/en/latest/topics/reproject.html>."""
    
    dst_crs = crs
    
    with rasterio.open(inpath) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
    
        with rasterio.open(outpath, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
 
class RectifyTif:
    """Rectify a tif image using the known coordinates of the image corners. Useful for rectifying rectangular geophysical maps."""

    def rectify(self, path, corners, epsg):

        ds = gdal.Open(path, gdal.GA_Update)
        gt = ds.GetGeoTransform()
    
        w, h = ds.RasterXSize, ds.RasterYSize
        x0 = int(gt[0])
        y1 = int(gt[3] + w*gt[4] + h*gt[5])
        x1 = int(gt[0] + w*gt[1] + h*gt[2])
        y0 = int(gt[3])
    
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(epsg)
        
        c = corners
        gcps = [
    
            gdal.GCP(c[0][0], c[0][1], 0, x0, y1), # ll
            gdal.GCP(c[1][0], c[1][1], 0, x0, y0), # ul
            gdal.GCP(c[2][0], c[2][1], 0, x1, y0), # ur
            gdal.GCP(c[3][0], c[3][1], 0, x1, y1), # lr
    
        ]    
    
        ds.SetGCPs(gcps, sr.ExportToWkt())
        ds.SetProjection(sr.ExportToWkt())
        ds.SetGeoTransform(gdal.GCPsToGeoTransform(gcps))
    
        tmp = NamedTemporaryFile(delete=False, suffix='.tif')
    
        gdal.Warp(tmp.name, ds)
        ds = None
    
        return(tmp.name)
    

