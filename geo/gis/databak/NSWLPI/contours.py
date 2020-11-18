#!/usr/bin/env python

import os
import shutil
import tempfile

name = 'contour'

class grass7(object):
        
    def __init__(self, gisdir, mapset = 'PERMANENT'):
    
        import grass.script as g
        self.g = g
        self.path = os.path.join(gisdir, name + '.shp')
        env = self.gisenv()
        
        try:

            lst = g.read_command('g.list', flags = 'm', type = 'vect', pattern = name)
            if not lst:
                location = self.create_location(env['db'])
                mapname = self.v_in_ogr()
                g.run_command('g.mapset', mapset = mapset, location = env['lc'])
                self.v_proj(location, mapset, mapname, output = name)
                shutil.rmtree(os.path.join(env['db'], location))
            
            self.output = name
        
        except Exception as e:
            print(e)
        finally:
            g.run_command('g.mapset', mapset = env['ms'], location = env['lc'])
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
        
    def create_location(self, gisdbase):
        """Create a temporary location to import the dataset"""
        try:
            name = os.path.basename(tempfile.mktemp(dir = gisdbase))
            self.g.run_command('g.proj', epsg = 4326, location = name)
            self.g.run_command('g.mapset', flags = 'c', mapset = 'PERMANENT', location = name)
            return(name)
        except Exception as e:
            print(e)
            
    def v_in_ogr(self):
        try:
            output = 'tmp'
            self.g.run_command('v.in.ogr', overwrite = True, input = self.path, output = output)
            return(output)
        except Exception as e:
            print(e)

    def v_proj(self, location, mapset, input, output):
        """"""
        try:
            self.g.run_command('v.proj', location = location, mapset = mapset, input = input, output = output)
        except Exception as e:
            print(e)
       
    def d_vect(self, color = 'red', fill_color = 'none', width = 15):
        try:
            self.g.run_command('d.vect', map = name, color = color, fill_color = fill_color, width = width)
        except:
            pass
    