"""A module of useful filesystem operations"""

from os import getcwd, makedirs, walk
from os.path import dirname, isdir, join, splitext

def mjoin(*paths):
    """This method extends the os.path.join method by creating the root path of the basename. It ensures that the directory structure exists before a file is saved"""
    p = join(*paths)
    d = dirname(p)
    if not isdir(d):
        makedirs(d)
    return(p)

class Paths:
    """Recursively get all files matching a base path. Class was first developed to retrieve a set of MALA GPR files with the same base file path and only differing extensions. It would also be useful for some GIS file formats."""
    def __init__(self, path):
        """Define the root directory of the path"""
        self.basepath = splitext(path)[0]

    def get_rdir(self):
        """Return the root directory of the input path"""
        p = self.basepath
        rdir = p if isdir(p) else dirname(p)
        return(rdir)
 
    def file_list(self):
        """Recursively list all files in the root directory"""
        p = []
        for root, dirs, files in walk(self.get_rdir()):
            for name in files:
                p += [join(root, name)]
        return(p)

    def get_basepaths(self):
        """Return a list of unique base file paths from the file list"""
        s = []
        b = [splitext(i)[0] for i in self.file_list()]
        for i in b:
            if i not in s:
                s += [i]
        s = [i for i in s if self.basepath in i]
        return(s)

    def get_file_groups(self):
        """Return"""
        f = self.file_list()
        p = []
        for i in self.get_basepaths():
            ext = [j for j in f if i in j]
            p += [ext]
        return(p)

    def get_extension(self, path, ext):
        """Return an existing file path matching case-insensitive extension"""
        path_list = glob(path + '*')
        p = [i for i in path_list if splitext(i)[1].lower() == ext].pop()
        return(p)
 
