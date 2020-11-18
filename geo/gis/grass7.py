import os
from os.path import expanduser, join
import sys
import subprocess

def gisbase7(binpath):
    """
        Set environment variables to allow import of grass into an external python session (for python3 Grass version must be <= 7.7. 
        Note that when OSGEO4W64 installation is used, the global dll files are not accessible; they either need to manually moved or the global dll folder added to the system path.
        Find binpath on your current system by manually opening a grass terminal and typing g.gisenv get='GISBASE'"""
    startcmd = [binpath, '--config', 'path']
    p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if p.returncode != 0:
        print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
        sys.exit(-1)
    else:
        gisbase = out.strip('\n\r')
        os.environ['GISBASE'] = gisbase
        py = join(gisbase, "etc", "python")
        sys.path.append(py)
        return(gisbase)

class GISBASE7:
    """
        Set environment variables to allow import of grass into an external python session (for python3 Grass version must be <= 7.7. 
        Note that when OSGEO4W64 installation is used, the global dll files are not accessible; they either need to manually moved or the global dll folder added to the system path.
    """
    def __init__(self, binpath):
        """Find binpath on your current system by manually opening a grass terminal and typing g.gisenv get='GISBASE'"""
        self.gisbase = self._gisbase(binpath)

    def _gisbase(self, binpath):
        """"""
        startcmd = [binpath, '--config', 'path']
        p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if p.returncode != 0:
            print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
            sys.exit(-1)
        else:
            gisbase = out.strip('\n\r')
            os.environ['GISBASE'] = gisbase
            py = join(gisbase, "etc", "python")
            sys.path.append(py)
            return(gisbase)


