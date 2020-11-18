"""Return a dictionary of paths to map decorations contained within the current folder"""

import os

paths = {}
cwd = os.path.dirname(__file__)
for i in os.listdir(cwd):
    name, ext = os.path.splitext(i)
    if ext != '.py' and ext != '.pyc':
        paths[name] = os.path.join(cwd, i)

def north():
    """"""
    d = {}
    northdir = os.path.join(cwd, 'north')
    for i in os.listdir(northdir):
        name, ext = os.path.splitext(i)
        d[name] = os.path.join(northdir, i)
    return(d)