
import os
import sys
import tempfile
from os.path import dirname as dn
import shutil

import grass.script as g

def gisdbase7(path):
    """Use a common local directory for users of this package; named individually"""
    return(path)

def setup(dic):
    """Enter mapset and create if not exists."""
    
    d = dic
    
    gisdbase = d['gisdbase']
    location = str(d['location'])
    mapset = str(d['mapset'])
    os.environ['GRASS_RENDER_WIDTH'] = '5262'
    os.environ['GRASS_RENDER_HEIGHT'] = '3508'
    os.environ['GRASS_RENDER_LINE_WIDTH'] = '5'
    try:
        os.environ['GRASS_FONT'] = d['font']
    except Exception as e:
        print(e)
    try:
        g.run_command('g.mapset', mapset = mapset, location = location, dbase = gisdbase)
    except:

        if os.path.isdir(gisdbase) is False:
            os.makedirs(gisdbase)
        create_location(gisdbase, location, d['epsg'])
        #g.run_command('g.mapset', mapset = mapset, location = location, dbase = gisdbase) # this command has been needed for a bug in windows where the DEFAULT_WIND file cannot be copied
        g.run_command('g.mapset', flags = 'c', mapset = mapset, location = location, dbase = gisdbase)
        
def create_location(gisdbase, name, epsg):
    """Create a grass location in the current or a different location if it does not exists"""
    lst = os.listdir(gisdbase)
    if not name in lst:
        try:
            g.run_command('g.proj', 'c', epsg = epsg, location = name)
        except:
            pass
        src = os.path.join(g.read_command('g.gisenv', get = 'GISDBASE'), name)
        dst = os.path.join(gisdbase, name)
        shutil.move(src, dst)
        
def temporary_location(epsg, dbase = None):
    """Create a temporary location"""
    try:
        if not dbase:
            dbase = g.read_command('g.gisenv', get = 'GISDBASE')
        name = os.path.basename(tempfile.mktemp(dir = dbase))
        g.run_command('g.proj', epsg = epsg, location = name)
        return(name)
    except Exception as e:
        print(e)
        
class load_environment(object):
    """Save the current environment and reload after changing mapset"""
    def __init__(self):
        """Save the current environment"""
        r = g.read_command
        self.dbase = r('g.gisenv', get = 'GISDBASE')
        self.ln = r('g.gisenv', get = 'LOCATION_NAME')
        self.ms = r('g.gisenv', get = 'MAPSET')
        self.r = r
        
    def g_mapset(self):
        """Reload the environment"""
        g.run_command('g.mapset', mapset = self.ms, location = self.ln, dbase = self.dbase)
    
   
def out2dic(output):
    """Assign numeric output of a grass command to a dictionary"""
    split = output.splitlines()
    d = {}
    for i in split:
        key, value = i.split('=')
        try:
            d[key] = int(value)
        except:
            d[key] = float(value)
    return(d)

def v_out_ogr(vector):
    """Export shapefile to temporary directory"""
    tmp = tmpfile.TemporaryDirectory()
    print(tmp)
    #g.run_command('v.out.ogr', overwrite = True, input = vector, output = 'C:\Users\Sam\Desktop\poo\poo', format = 'ESRI_Shapefile', output_layer = 'Subcatchments')
    
    
def shp2grass7(path, name = None, snap = -1):
    """Load shapefile into temporary location"""
    try:
        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        g.run_command('v.in.ogr', flags = 'o', overwrite = True, input = path, output = name, snap = snap)
    except Exception as e:
        print(e)
    
    
######## HYDROLOGY ##########

   
###### REGIONS #########
def g_region(g, d, flags = None):
    """Set region from a dictionary of region settings"""
    g.run_command('g.region', flags = flags, overwrite = True, n = d['n'], s = d['s'], e = d['e'], w = d['w'], res = d['res'], save = d['name'])
    
  
def pg2region(self, dic):
    r = dic['db'].pg2dic('grass_g_region')
    idx = [n for n, i in enumerate(r['region'])]
    for i in idx:
        d = {}
        for key in r.keys():
            d[key] = r[key][i]
        self.g_region(d)
        
# def g_region2(sql2dic, name):
    # """Load a named region stored in a database"""
    # sql = """SELECT * FROM grass_g_region WHERE region = '%s'"""
    # d = sql2dic(sql % name)
    # g.run_command('g.region', overwrite = True, n = d['n'], s = d['s'], e = d['e'], w = d['w'], res = d['res'], save = name)
    # return(name)
    
def regiondic():
    r = g.read_command('g.region', flags = 'g')
    r = r.splitlines()
    r = [i.split('=') for i in r]
    d = {}
    for i in r:
        try:
            d[i[0]] = int(i[1])
        except:
            d[i[0]] = float(i[1])
    return(d)
    
def region2map(ratio = 1.5):
    """Convert current region to 1.5 or custom ratio"""
    
    r = ratio
    d = regiondic()
    
    n = d['n']
    s = d['s']
    w = d['w']
    e = d['e']
    
    if (e-w) / (n-s) > 1.5:
        print('expand ns')
    elif (e-w) / (n-s) < 1.5:
        m = (e - w) / 2 + w
        d = (n - s) * 1.5 / 2
        w1 = m - d
        e1 = m + d
        g.run_command('g.region', w = w1, e = e1)
        
def center_region(vector, x = 0, y = 0):
    """Center a region on the centroid of a vector"""
    
    d = regiondic()
    n1, s1, w1, e1 = d['n'], d['s'], d['w'], d['e']
    ewr = e1 - w1
    nsr = n1 - s1
    cre = (ewr) / 2 + w1
    crn = (nsr) / 2 + s1
    
    xshift = ewr * x / 100
    yshift = nsr * y / 100
    
    c = g.read_command('v.out.ascii', input = vector, type = 'centroid').split('|')
    cve = float(c[0]) - xshift
    cvn = float(c[1]) - yshift
    
    de = cve - cre
    dn = cvn - crn
    
    n2 = n1 + dn
    s2 = s1 + dn
    w2 = w1 + de
    e2 = e1 + de

    g.run_command('g.region', n = n2, s = s2, w = w2, e = e2)
    
def scalereg(self, percentage):
    """Scale a region by a give percentage; > 100% will increase the area; < 100% will decrease the area"""
    output = self.g.read_command('g.region', flags = 'g')

    d = self.out2dic(output)

    n = d['n']
    s = d['s']
    w = d['w']
    e = d['e']
    
    ns = n - s
    ew = e - w
    ratio = ew / ns
    
    ns_disp = ns * percentage / 100
    ew_disp = ns_disp * ratio
    
    n = n + ns_disp / 2
    s = s - ns_disp / 2
    w = w - ew_disp / 2
    e = e + ew_disp / 2
    
    self.g.run_command('g.region', n = n, s = s, e = e, w = w)
        
        
######## CARTOGRAPHY #############

def northarrow(map, arrow, resize = 1):
    """"""
    try:
        from PIL import Image
        b = Image.open(map)
        bw, bh = b.size
        pw = bw / 100
        ph = bh / 100
        
        f = Image.open(arrow)
        fw, fh = f.size
        f = f.resize((fw * resize, fh * resize), Image.ANTIALIAS)
        
        fw2, fh2 = f.size
        x = ph * 5
        y = bh - (ph * 5) - fh2
        b.paste(f, (x, y), f)
        b.save(map)
    except Exception as e:
        print('\nError' + ' at ' + __name__ + '.northarrow')
        print('\t' + e.message + '\n')

def footbox(div = 5):
    """Return the coordinate of the rectangle filling the lower fifth of the current region"""
    try:
        
        region = g.read_command('g.region', 'g')
        d = out2dic(region)
        n, s, w, e = d['n'], d['s'], d['w'], d['e']
        h = (n - s) / div
        
        up = str(s + h)
        lo = str(s)
        le = str(w)
        ri = str(e)
        
        txt = """polygon
        """ + le + """ """ + lo + """
        """ + le + """ """ + up + """
        """ + ri + """ """ + up + """
        """ + ri + """ """ + lo
        
        tmp = tempfile.NamedTemporaryFile(delete = False)
        
        tmp.write(txt)
        tmp.close()
        return(tmp.name)
    except Exception as e:
        print('\nError' + ' at ' + __name__ + '.footbox')
        print('\t' + e.message + '\n')


######## OUTPUT METHODS #########
def rast2tif(grass, name, path):
    grass.run_command('r.out.gdal', flags = 'cf', overwrite = True, input = name, output = path, format = 'GTiff', type = 'Int16')
    
def vect2shp(grass, name, path):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    grass.run_command('v.out.ogr', overwrite = True, input = name, output = path, format = 'ESRI_Shapefile')    
        



        
            

        
        


        

        
        

        
        

        

           
