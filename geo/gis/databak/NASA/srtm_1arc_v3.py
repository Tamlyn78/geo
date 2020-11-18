
import os
import tempfile
import shutil
    
class grass7(object):
    """Load a list of 1arc SRTM tifs. Requirement to have an active grass session"""
    def __init__(self, lst, gisdir, output = 'srtm_1arc_v3', mapset = 'PERMANENT'):
    
        import grass.script as g

        self.g = g
        self.lst = lst
        self.gisdir = gisdir
        self.output = output
        self.mapset = mapset
                
        glist = g.read_command('g.list', type = 'raster', pattern = output, mapset = 'PERMANENT')
        
        if not glist:
            self.main()
                        
    def main(self):
    
        try:

            r = self.g.run_command

            db, l, m = self.env()
            
            # create a temporary location
            tmp = self.location(db)
            r('g.mapset', flags = 'c', mapset = 'PERMANENT', location = tmp)
            
            # import rasters to temporary location
            rasters = self.iter()
            
            # set region to the collection of rasters
            r('g.region', raster = tuple(rasters))
            
            # patch the rasters together
            self.r_patch()
            
            # save region setting of patched raster
            region = self.g_region()
            r('g.region', raster = self.output)
            r('v.in.region', overwrite = True, output = self.output)
            
            # reproject the patched vector
            r('g.mapset', flags = 'c', mapset = self.mapset, location = l)
            r('v.proj', overwrite = True, location = tmp, mapset = 'PERMANENT', input = self.output)
            
            # set region to patched raster using vector boundary
            r('g.region', vector = self.output, rows = int(region['rows']), cols = int(region['cols']))
            r('g.remove', flags = 'f', type = 'vector', name = self.output)
            
            # reproject raster
            r('r.proj', location = tmp, mapset = 'PERMANENT', input = self.output)
   
        except:
        
            pass
            
        finally:
        
            # set region to initial settings
            r('g.mapset', flags = 'c', mapset = m, location = l)
            d = os.path.join(db, tmp)
            shutil.rmtree(d)
            
    def env(self):
        """Return current environment variables"""
        try:
            db = self.g.read_command('g.gisenv', get = 'GISDBASE')
            l = self.g.read_command('g.gisenv', get = 'LOCATION_NAME')
            m = self.g.read_command('g.gisenv', get = 'MAPSET')
            return(db, l, m)
        except:
            pass
            
    def location(self, db):
        """Create temporary location to import dataset"""
        try:
            p = tempfile.mkdtemp(dir = db)
            n = os.path.basename(p)
            shutil.rmtree(p)
            self.g.run_command('g.proj', epsg = 4326, location = n)
            return(n)
        except:
            pass
            
    def iter(self):
        """"""
        outlst = []
        for i in self.lst:
            try:                
                tif = os.path.join(self.gisdir, i + '.tif')
                mapname = os.path.splitext(os.path.basename(tif))[0]
                outlst += [mapname]
                self.r_in_gdal(tif, mapname)
            except:
                pass
        return(outlst)
        
    def r_in_gdal(self, path, output):
        """Import an ASTGTM2 dataset into the current location"""
        try:
            self.g.run_command('r.in.gdal', overwrite = True, flags = 'o', input = path, output = output)
        except:
            pass
            
    def r_patch(self):
        """"""
        r = self.g.run_command
        r('r.patch', overwrite = True, input = tuple(self.lst), output = self.output)
             
    def g_region(self):
        """Return a dictionary of the current region settings"""
        r = self.g.read_command('g.region', flags = 'g')
        r = r.splitlines()
        r = [i.split('=') for i in r]
        d = {i[0]:i[1] for i in r}
        return(d)
            

