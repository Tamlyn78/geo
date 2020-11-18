
import os
import tempfile
import zipfile
import shutil
import ogr

#dbpath = os.path.normpath([i for i in dbases if i.endswith('sqlite.db')][0])
#con = sqlite3.connect(dbpath)

#from pygislib.data.NSWOEH import Soils_SoilLandscapes as soil

epsg = 28356

def list_datasets():
    """List available datasets"""
    lst = os.listdir(os.path.dirname(__file__))
    return(lst)

def zippath(name):
    path = os.path.join(os.path.dirname(__file__), name + '.zip')
    return(path)
    
def sydney():
    """Import most recent Sydney dataset"""
    d = {
        'zip':'Sydney_geol_100k_shape',
        'snap':-1,
    }
    return(d)
    
def penrith():
    """Import most recent Sydney dataset"""
    zip = 'Penrith_geol100k_shape'
    snap = 0.00001
    name = grass7(zip, snap = snap).name
    return(name)
    

        
 
class shp2grass7(object):
    """Load shapefile into current grass mapset"""
    def __init__(self, path, name = None, snap = -1):
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        self.create_location()
        self.v_in_ogr(path, name, snap)
        
    def create_location(self):
        """Create a temporary location to import the dataset"""
        try:
            dbase = g.run_command('g.gisenv', get = 'GISDBASE')
            name = os.path.basename(tempfile.mktemp(dir = dbase))
            self.g.run_command('g.proj', epsg = epsg, location = name)
            self.g.run_command('g.mapset', flags = 'c', mapset = 'PERMANENT', location = name)
            return(name)
        except Exception as e:
            print(e)
            
    def v_in_ogr(self, path, name, snap):
        try:
            self.g.run_command('v.in.ogr', flags = 'o', overwrite = True, input = path, output = name, snap = snap)
        except Exception as e:
            print(e)

    def v_proj(self, location, mapset, input, name):
        """"""
        try:
            self.g.run_command('v.proj', location = location, mapset = mapset, input = name, output = name)
        except Exception as e:
            print(e)

    
class shp2grass7bak(object):

    #def __init__(self, zip, mapset = 'PERMANENT', snap = -1):
    def __init__(self, shp, snap = -1):

        try:
            import grass.script as grass
            self.g = grass
            name = os.path.splitext(os.path.basename(shp))[0]
            print(name)
            
            #if name not in self.g_list('vector', mapset = mapset):
                #print('wee')
                #location = self.create_location(env['db'])
                #shpdir = self.unzip(zpath)
                #self.update_table(shpdir)
                #print(shpdir, snap, name)
                #print(os.path.join(shpdir))
                #path = 
                #mapname = self.v_in_ogr(shpdir, snap, name)
                #self.g.run_command('g.mapset', mapset = mapset, location = env['lc'])
                #self.v_proj(location, 'PERMANENT', mapname, name)
            #shutil.rmtree(os.path.join(env['db'], location))
            #self.name = name
        except Exception as e:
            print(e)
        finally:
            #self.g.run_command('g.mapset', mapset = env['ms'], location = env['lc'])
            pass
        
    def gisenv(self):
        """Return a dictionary of environment variables"""
        try:
            dbase = self.g.read_command('g.gisenv', get = 'GISDBASE')
            location = self.g.read_command('g.gisenv', get = 'LOCATION_NAME')
            mapset = self.g.read_command('g.gisenv', get = 'MAPSET')
            d = {
                'db':dbase,
                'lc':location,
                'ms':mapset
            }
            return(d)
        except Exception as e:
            print(e)
            
    def readzip(self, zippath):
        try:
            z = zipfile.ZipFile(zippath)
            shp = self.find_rock_unit([i for i in z.namelist() if i.endswith('.shp')])
            return(os.path.splitext(shp)[0])
        except Exception as e:
            print(e)
              
    def find_rock_unit(self, lst):
        """Return the 'RockUnit' file from a given list of single file-types (e.g. '.shp' only)"""
        return([i for i in lst if 'RockUnit' in i][0])
        
    def g_list(self, type, mapset = '.'):
        lst = self.g.read_command('g.list', type = type, mapset = mapset).splitlines()
        return(lst)
            
    def create_location(self, gisdbase):
        """Create a temporary location to import the dataset"""
        try:
            name = os.path.basename(tempfile.mktemp(dir = gisdbase))
            self.g.run_command('g.proj', epsg = epsg, location = name)
            self.g.run_command('g.mapset', flags = 'c', mapset = 'PERMANENT', location = name)
            return(name)
        except Exception as e:
            print(e)
            
    def unzip(self, path):
        """Unzip dataset to a temporary directory"""
        try:
            d = tempfile.mkdtemp()
            z = zipfile.ZipFile(path, 'r')
            z.extractall(d)
            z.close()
            return(d)
        except Exception as e:
            print(e)

    def update_table(self, path):
        """Change column names that are sqlite keywords"""
        try:
            lst = [i for i in os.listdir(path) if i.endswith('.dbf')]
            dbf = os.path.join(path, self.find_rock_unit(lst))
            source = ogr.Open(dbf, update = True)
            lyr = source.GetLayer()
            i = lyr.GetLayerDefn().GetFieldIndex('GROUP')
            fld_defn = ogr.FieldDefn('GROUP_', ogr.OFTString)
            lyr.AlterFieldDefn(i, fld_defn, ogr.ALTER_NAME_FLAG)
        except Exception as e:
            print(e)

    def v_in_ogr(self, shpdir, snap, name):
        try:
            shp = [os.path.join(shpdir, i) for i in os.listdir(shpdir) if i.endswith('.shp') and 'RockUnit' in i][0]
            self.g.run_command('v.in.ogr', flags = 'o', overwrite = True, input = shp, output = name, snap = snap)
        except Exception as e:
            print(e)

    def v_proj(self, location, mapset, input, name):
        """"""
        try:
            self.g.run_command('v.proj', location = location, mapset = mapset, input = name, output = name)
        except Exception as e:
            print(e)
           
           
           
def old_stuff():
    import tempfile

    from pygislib import grass7 as gs
    from pygislib import decorations
    #from terrain import srtm_1arc_v3 as elevation
    from studyarea.studyarea import grass7 as studyarea
    import Regions as rg
    import Cartography as cart

    import brewer2mpl
    
    
    
def zip2tmp(path):
    """Unzip dataset into a temporary directory"""
    #def __init__(self, zip, mapset = 'PERMANENT', snap = -1):
    try:
        d = tempfile.mkdtemp()
        z = zipfile.ZipFile(path, 'r')
        z.extractall(d)
        z.close()
        return(d)
    except Exception as e:
        print(e)

def shp2grass7(zippath, shpname):
    """Load required gis imported from gis package"""
    try:
        import grass.script as g
        from pygislib.grass7 import load_environment as le, shp2grass7 as s2g, g_list, temporary_location as tloc
        
        # unzip dataset to temporary directory
        d = zip2tmp(zippath)
        
        # create a temporary location
        current_environment = le()
        tmp = tloc(28356)
        
        # import shapefile to temporary location
        g.run_command('g.mapset', flags = 'c', mapset = 'PERMANENT', location = tmp)
        path = os.path.join(d, 'Sydney100RockUnit_MGAz56.shp')
        s2g(path)
        
        # reload previous mapset
        current_environment.g_mapset()
        print(g.read_command('g.gisenv', get = 'MAPSET'))
        
        # project dataset to current environment
            
    except Exception as e:
        print(e)
        
        