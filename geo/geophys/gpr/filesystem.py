
"""Useful filesystem operations"""

from os import walk
from os.path import basename, dirname, join, splitext
from glob import glob

def get_file_path(path, ext):
    """Return the path to an existing file from a root example.
        Attributes:
            path <str>: A filesystem path with or without an extension;
            ext <str>: An case-insensitive extension required for output.
    """
    b, e = splitext(path)
    lst = [i for i in glob(b + '*') if splitext(i)[1].lower() == ext.lower()]
    try:
        return(lst.pop())
    except:
        return(None)


def list_gpr_data(path, ext):
    """Find all files recursively with the given extension (case insensitive)."""
    lst = []
    for r, d, f in walk(path):
        for i in f:
            lcase = i.lower()
            if lcase.endswith(('.' + ext.lower())):
                lst.append(join(r, i))
    lst.sort()
    return(lst)

def get_folder_and_filename(path):
    """Return a tuple of the folder and filename from a GPR data path."""
    d = basename(dirname(path))
    f = splitext(basename(path))[0]
    l = [d, f]
    return(l)

