"""An example module to demonstrate the use of the raster module"""

import matplotlib.pyplot as plt
from cartopy import crs
import rasterio
from rasterio.plot import show
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling





def plot_srtm():
    """Plot an srtm geotif on a map and include a colorbar"""
    fig, ax = plt.subplots()

    src = rasterio.open('srtm.tif')
    arr = src.read()

    # note that images are defined from their top-left corner, so if you have defined a Cartesian-like coordinate system before plotting a raster, it will appear upside-down; the following can be used to flip it if necessary
    #arr = np.flip(arr, axis=1) # it would be good to know why rasterio reads rasters upsidedown, requiring us to flip it

    show(arr, ax=ax, transform=src.transform, cmap='terrain', vmin=0, vmax=250, interpolation='bilinear') 
    #plt.colorbar()
    plt.show()

def plot_srtm_warped():
    """Warp a geotiff and plot"""

    inpath = 'srtm.tif'
    epsg = 28356
    outpath = 'tmp.tif'

    dst_crs = 'EPSG:' + str(epsg)
    with rasterio.open(inpath) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({'crs': dst_crs, 'transform': transform, 'width':width, 'height':height})
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

    fig, ax = plt.subplots()
    
    src = rasterio.open('tmp.tif')
    arr = src.read()
    
    show(arr, ax=ax, transform=src.transform, cmap='terrain', vmin=0, vmax=250, interpolation='bilinear') 
    #plt.colorbar()
    plt.show()

    

#plot_srtm()
plot_srtm_warped()    


