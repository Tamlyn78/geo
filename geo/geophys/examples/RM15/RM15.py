from os import listdir, makedirs
from os.path import abspath, basename, dirname, isdir, join
import re
import csv
import numpy as np
import pandas as pd
from scipy import stats, ndimage, signal
import matplotlib.pyplot as plt 
from matplotlib import cm, rc
from mpl_toolkits.axes_grid1 import make_axes_locatable
from math import ceil

from geo.geo.geophys.terrasurveyor import TerraSurveyor
from geo.geo.geophys.xyz import *

def site_to_id(site):
    """Return site name for a given id"""
    uid = sites.loc[sites['name'] == site]['id'].values[0]
    return(uid)

def id_to_site(uid):
    """Return site name for a given id"""
    site = sites.loc[sites['id'] == uid]['name'].values[0]
    return(site)

def metadata(site_id):
    df = surveys.loc[(surveys['site'] == site_id) & (surveys['status'] == True)].copy()
    return(df)

def mkdir(d):
    if not isdir(d):
        makedirs(d)
    return(d)

def get_array(metadata):
    m = metadata
    site = id_to_site(m.site)
    ts = TerraSurveyor(ts_dir, site)
    ts.get_xgd(m.filename)
    a = ts.to_array()
    a = a[2,:,:].copy()
    a = rotate_array(a, m.rotation)
    a = dummies_to_nan(a)
    return(a)


def append_arrays(df, arrays):
    """"""
    df = df.copy()
    df.reset_index(inplace=True)
    try:
        df.sort_values(by=['x','y'], axis=0, inplace=True)
    except Exception as e:
        print(e)
        return(df)

    for n, i in df.groupby('y'):
        for m, j in i.iterrows():
            a = arrays[m]
            try:
                x = np.append(x, a, axis=0)
            except:
                x = a
        try:
            y = np.append(y, x, axis=1)
        except:
            y = x
        x = object
    return(y)


def repair_xgd():
    """Repair all xgd files and export to xyz to allow import to TerraSurveyor"""
    for n, i in surveys.iterrows():
        site = id_to_site(i.site)
        ts = TerraSurveyor(ts_dir, site)
        ts.get_xgd(i.filename)
        ts.to_xyz(export=True)

def skazka_park():
    """"""
    site_name = 'Skazka Park'
    site_id = site_to_id(site_name)
    m = metadata(site_id).copy()
    m.reset_index(inplace=True)
    arrays = [get_array(i) for n, i in m.iterrows()]
    a = append_arrays(m, arrays)
    a = clip_to_border(a)
    a = clip_array(a, std=1)
    a = zero_array(a)
 
    d = mkdir(join(out_dir, site_name))
    outpath = join(d, site_name)
    vmin, vmax = 0, 30
    plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax)
    plot(a, outpath=outpath, vmin=vmin, vmax=vmax, interpolation='bilinear')
    plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, axes=False, interpolation='bilinear', grid=True)

def odishi_road():
    """"""
    site_name = 'Odishi Road'
    site_id = site_to_id(site_name)
    m = metadata(site_id).copy()
    m.reset_index(inplace=True)
    arrays = [get_array(i) for n, i in m.iterrows()]

    a = arrays[0]
    a = clip_to_border(a)
    a = clip_array(a, std=1)
    a = zero_array(a)

    d = mkdir(join(out_dir, site_name))
    outpath = join(d, site_name)
    vmin, vmax = 0, 7
    plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
    plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
    plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)


def bakery():
    """Four separate surveys were done requiring four outputs"""
    site_name = 'Bakery'
    site_id = site_to_id(site_name)
    m = metadata(site_id).copy()
    m.reset_index(inplace=True)
    arrays = [get_array(i) for n, i in m.iterrows()]

    def s1():
        a = arrays[0]
        a = a[:9,:]
        a = clip_to_border(a)
        a = clip_array(a, std=1)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '1')
        vmin, vmax = None, None
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)
    
    def s2():
        a = arrays[0]
        a = a[9:,:]
        a = clip_to_border(a)
        a = clip_array(a, std=1)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '2')
        vmin, vmax = None, None
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)

    def s3():    
        a = arrays[1]
        a = a[:,34:]

        # deal with doubled lines
        error_cols = [4,12]
        L1 = a[:,4]
        L1a = np.append(L1[0:29], np.array([np.nan for i in range(60-len(L1[0:29]))]))
        L1a = np.expand_dims(L1a, axis=1)
        L1b = np.append(np.array([np.nan]), L1[29:])
        L1b = np.append(L1b, np.array([np.nan for i in range(60-len(L1b))]))
        L1b = np.expand_dims(L1b, axis=1)

        L2 = a[:,12]
        L2a = np.append(L2[0:28], np.array([np.nan for i in range(60-len(L2[0:28]))]))
        L2a = np.expand_dims(L2a, axis=1)
        L2b = np.append(np.array([np.nan]), L2[28:])
        L2b = np.append(L2b, np.array([np.nan for i in range(60-len(L2b))]))
        L2b = np.expand_dims(L2b, axis=1)

        b = np.append(a[:,:4], L1a, axis=1)
        b = np.append(b, L1b, axis=1)
        b = np.append(b, a[:,5:12], axis=1)
        b = np.append(b, L2a, axis=1)
        b = np.append(b, L2b, axis=1)
        b = np.append(b, a[:,13:], axis=1)

        a = b 
        a = clip_to_border(a)
        a = clip_array(a, std=0.25)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '3')
        vmin, vmax = None, 7 
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)
    
    def s4():
        a = arrays[1]
        a = a[:,8:17]
        
        a = clip_to_border(a)
        a = clip_array(a, std=1)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '4')
        vmin, vmax = None, None
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath+'-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)

        #a = moving_average(a, radius=3)
        #plot(a, outpath=outpath+'-highpass', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16')

    s1()
    s2()
    s3()
    s4()


def aquarium():
    """Four separate surveys were done requiring four outputs"""
    site_name = 'Aquarium'
    site_id = site_to_id(site_name)
    m = metadata(site_id).copy()
    m.reset_index(inplace=True)
    arrays = [get_array(i) for n, i in m.iterrows()]
 
    def s1():
        # survey1
        a = arrays[0]
        # remove bad rows
        a[20:,] = np.nan
        a = clip_to_border(a)
        a = clip_array(a)
        a = zero_array(a)

        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '-' + str(1))
        # results are fairly awful; skipping this
     
    def s2():
        # survey2
        a = arrays[1]
        # remove bad rows
        a[20:,] = np.nan
        a = clip_to_border(a)
        a = clip_array(a, std=0.25)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '-' + str(2))
        vmin, vmax = 0, 50
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath + '-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)
    
    def s3():
        # survey3
        # all digital data bad; manual data entered and processed
        meta = m.loc[m['filename'] == 3].iloc[0]
        
        ts = TerraSurveyor(ts_dir, site_name)
        path = ts.get_xgd(meta.filename).replace('.xgd','.csv')
        a = ReadXYZ(path).to_array(meta.length, meta.sample_interval)
        a[a==2047.5] = np.nan
        a = clip_to_border(a)
        a = clip_array(a, std=0.25)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '-' + str(3))
        vmin, vmax = 0, 40
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath + '-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)
    
    def s4():
        # survey4
        # all digital data bad; manual data entered and processed
        meta = m.loc[m['filename'] == 4].iloc[0]
        a = get_array(meta)
    
        # remove bad rows
        a[:,44:] = np.nan
        a = clip_to_border(a)
        a = clip_array(a, std=1)
        a = zero_array(a)
    
        d = mkdir(join(out_dir, site_name))
        outpath = join(d, site_name + '-' + str(meta.filename))
        vmin, vmax = 0, 40
        plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
        plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
        plot(a, outpath=outpath + '-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, axes=False, interpolation='spline16', grid=True)
    
    s2()
    s3()
    s4()

def residential_cottage():
    """"""
    site_name = 'Residential Cottage'
    site_id = site_to_id(site_name)
    m = metadata(site_id)
    arrays = [get_array(i) for n, i in m.iterrows()]
    arrays[0] = arrays[0][:-1,:]
    a = append_arrays(m, arrays)

    a = clip_to_border(a)
    a = clip_array(a, std=1)
    a = zero_array(a)

    d = mkdir(join(out_dir, site_name))
    outpath = join(d, site_name)
    vmin, vmax = 0, 120
    plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5)
    plot(a, outpath=outpath, vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16')
    plot(a, outpath=outpath + '-noaxis', vmin=vmin, vmax=vmax, xint=0.5, yint=0.5, interpolation='spline16', axes=False, grid=True)

def tolyatti():
    """"""
    site_name = 'Tolyatti Sanatorium'
    site_id = site_to_id(site_name)
    m = metadata(site_id).copy()
    m.reset_index(inplace=True)
    arrays = [get_array(i) for n, i in m.iterrows()]
   
    # fix survey squares that were too close to remote probes by shifting the average
    error_squares = m.filename.isin([13,14,15])
    means = [get_mean(arrays[i]) for i in m.loc[~error_squares].index]
    mean = sum(means) / len(means)
    for i in m.loc[error_squares].index:
        a = arrays[i]
        a = a + mean - get_mean(a)
        arrays[i] = a

    # output each survey square individually
    d = mkdir(join(out_dir, site_name))
    def output_all():
        for n,i in enumerate(arrays):
            a = clip_array(i, std=1)
            a = zero_array(a)
            f = m.at[n, 'filename']
            o = join(d, str(f)) 
            plot(a, o + '-raw')
            plot(a, o, interpolation='spline16')
            plot(a, o + '-noaxis', interpolation='spline16', axes=False)
            
    output_all()

    # append survey squares and output
    a = append_arrays(m, arrays)
    a = clip_to_border(a)
    a = clip_array(a, std=1)
    a = zero_array(a)

    outpath = join(d, site_name)
    vmin, vmax = None, None
    plot(a, outpath=outpath + '-raw', vmin=vmin, vmax=vmax)
    plot(a, outpath=outpath, vmin=vmin, vmax=vmax, interpolation='spline16')
    plot(a, outpath=outpath + '-noaxis', vmin=vmin, vmax=vmax, axes=False, interpolation='spline16', grid=True)


data_dir = abspath('data')
out_dir = abspath('output')
ts_dir = join(data_dir, 'TerraSurveyor')
sites = pd.read_csv(join(data_dir, 'sites.csv'))
surveys = pd.read_csv(join(data_dir, 'surveys.csv'))


#repair_xgd()
#skazka_park()
#odishi_road()
#bakery()
aquarium()
#residential_cottage()
#tolyatti()


