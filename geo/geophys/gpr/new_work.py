
from os.path import basename, dirname

from .gpr import Format
from .filesystem import find_extension

class LoadDirectory:
    """Load all raw survey data from a directory."""
    def __init__(self, path, fmt='RD3'):
        """Create filesystem; gpr survey data into the folder named 'data'."""
        self.path = path
        self.dat = getattr(Format, fmt)

    def get_list(self):
        """Return a sorted list of data files."""
        p, e = self.path, self.dat.ext
        lst = find_extension(p, e)
        return(lst)

    def get_path(self, n):
        """Return the path of an item from 'print_list'"""
        lst = self.get_list()
        try:
            path = lst[n-1]
            return(path)
        except Exception as e:
            print(e)
    
    def print_list(self):
        """Print a list of data files"""
        lst = self.get_list()
        for n, i in enumerate(lst, start=1):
            folder = basename(dirname(i))
            name = basename(i)
            print(n, folder, name)

    def get_data(self, n):
        """Using the id from 'print_list' get gpr data for a line."""
        path = self.get_path(n)
        d = self.dat(path)
        return(d)


