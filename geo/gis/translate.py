"""Translate geographical data"""

import math
from math import modf, sin, cos, radians


def ddm2dg(ddm):
    """Convert decimal degree minutes to decimal degrees. The first instance this was needed was for translating raw NMEA data from a TrimbleR10. The Longitudes and Latitudes were all in DDM format.
        Attributes:
            ddm <float>: A single float representing a longitude or latitude.
    """
    decimal, integer = modf(ddm / 100)
    decimal = decimal / 60 * 100
    dg = integer + decimal
    return(dg)



    
import osr, ogr
src = osr.SpatialReference()
src.ImportFromEPSG(4326)
dst = osr.SpatialReference()
dst.ImportFromEPSG(28354) 
transform = osr.CoordinateTransformation(src, dst)

def crs_transformbak(x, y):
    """"""
    point = ogr.CreateGeometryFromWkt("POINT ("+str(x)+" "+str(y)+")")
    point.Transform(transform)
    e = point.GetX()
    n = point.GetY()
    return(e, n)

def crs_transform(from_epsg, to_epsg):
    """"""
    sr = osr.SpatialReference()
    src, dst = (sr,) * 2
    src.ImportFromEPSG(from_epsg)
    dst.ImportFromEPSG(to_epsg)
    t = osr.CoordinateTransformation(src, dst)
    return(t)


def epsg2epsg(tup, from_epsg, to_epsg):
    """Convert a coordinate pair by epsg code"""
    x, y = tup
    t = crs_transform(from_epsg, to_epsg)
    point = ogr.CreateGeometryFromWkt("POINT(" + str(x) + " " + str(y) + ")")
    point.Transform(transform)
    e = point.GetX()
    n = point.GetY()
    return(e, n)


    #print(x2, y2)
    #ll = ['Longitude', 'Latitude']
    #en = ['Easting', 'Northing']
    #x, y = df[ll[0]], df[ll[1]]
    #x, y = coords
    #print(x, y)
    #df[en] = pd.DataFrame([crs_transform(i, j) for i, j in zip(x,y)])
    #df.drop(ll, axis=1, inplace=True) 
    #df = df[en + [i for i in df.columns[:-2]]]
    #return(df)


