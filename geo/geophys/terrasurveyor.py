from os import listdir, makedirs
from os.path import basename, dirname, isdir, join
from re import findall
import numpy as np
import pandas as pd


class XGD:
    """Conversion methods for TerraSurveyor XGD file"""
    def __init__(self, path_to_xgd):
        #self.rdir = dirname(dirname(path_to_xgd))
        self.path_to_xgd = path_to_xgd
        self.lines = self._to_lines()
        self.meta = self._get_metadata()
        self.dummy = 2047.5
        #a = self.to_array()

    def _to_lines(self):
        """Return xgd content as a list of lines"""
        with open(self.path_to_xgd, 'r') as f:
            lines = f.readlines()
        return(lines)
        
    def _get_metadata(self):
        """Return xgd metadata to a dictionary"""
        l = [i for i in self.lines if not i.startswith('<XYV')]
        log_info = l[2].split()
        mode = log_info[4].split('=')[1].replace('/>','').replace('"','')
        grid_info = l[3].split()
        grid = lambda x: float(grid_info[x].split('=')[1].replace('"',''))
        t_len, i_len, t_sep, i_sep = [grid(i) for i in [1,2,3,4]]
        d = {
            'traverse_len': t_len,
            'interval_len': i_len,
            'traverse_sep': t_sep,
            'interval_sep': i_sep,
            'mode': mode,
        }
        return(d)

    def _line_to_xyz(self, line):
        """"""
        a = line.split()[1:4]
        b = [findall(r'\d+', i) for i in a]
        c = [float('.'.join(i)) for i in b]
        return(c)

    def _dummy_array(self):
        """Return an array of dummy values"""
        m = self.meta
        x, y = self._array_shape()
        lst = [[i, j, self.dummy] for i in range(x) for j in range(y)]
        a = np.array(lst)[:,[1,0,2]]
        return(a)

    def _array_shape(self):
        """Return the shape of the grid array"""
        m = self.meta
        x = int(m['interval_len'] / m['interval_sep'])
        y = int(m['traverse_len'] / m['traverse_sep'])
        return(x, y)
 
    def _pad_missing_dummies(self, lst):
        """A situation occurred where dummy values were not recorded but the locations of missing values were evident from associated missing x and y values. This method acts to fill the missing value"""
        a = self._dummy_array()
        array = np.array(lst)
        interval_len = self._array_shape()[0]
        for i in array:
            x,y,v = i
            idx = int(x+y*interval_len)
            a[idx] = [x,y,v]
        return(a)

    def to_list(self):
        """"""
        lst = [self._line_to_xyz(i) for i in self.lines if i.startswith('<XYV')]
        for n, i in enumerate(lst):
            v = i[2]
            if v == 204.7 or v == -204.7 or v == 204.75 or v == -204.75:
                lst[n][2] = self.dummy
        lst = self._pad_missing_dummies(lst).tolist()
        return(lst)

    def to_array(self):
        """"""
        a = np.array(self.to_list())
        m, n = self._array_shape()
        X = np.reshape(a[:,0], (-1, m))
        Y = np.reshape(a[:,1], (-1, m))
        V = np.reshape(a[:,2], (-1, m))
        a = np.array([X,Y,V])
        return(a)

    def to_xyz(self, export=False):
        """"""
        df = pd.DataFrame(self.to_list())
        df.columns = ['X','Y','V']
        df.X = df.X.astype(int)
        df.Y = df.Y.astype(int)
        if export:
            outname = basename(self.path_to_xgd).replace('.xgd','.xyz')
            outpath = join(self.export(), outname)
            df.to_csv(outpath, header=False, index=False)
        else:
            return(df)


class TerraSurveyor(XGD):
    def __init__(self, path_to_project, site_name):
        """Initialise class with path to TerraSurveyor project"""
        self.site_dir = join(path_to_project, site_name)
        self.grid_dir = join(self.site_dir, 'grids')

    def site(self, site):
        """Change the current site; this should also remove all locals associated with the former site"""
        self.site_dir = join(dirname(self.site_dir), site)

    def list_of_grids(self):
        """List the grids existing for site"""
        lst = [i for i in listdir(self.gdir) if i.endswith('.xgd')]
        print(*lst, sep='\n')
        return(lst)

    def get_xgd(self, xgd_id):
        """"""
        fname = str(xgd_id).zfill(2) + '.xgd'
        path_to_xgd = join(self.grid_dir, fname)
        XGD.__init__(self, path_to_xgd)
        return(path_to_xgd)

    def export(self):
        """"""
        d = join(self.site_dir, 'export')
        if not isdir(d):
            makedirs(d)
        return(d)


