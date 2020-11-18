#!/usr/bin/env python

"""Process XRD data"""

import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class gbc_spellman_df3(object):

    """Process data for a GBC Spellman DF3 XRD"""

    def __init__(self, csvDir, specDir, specCsv = 'info', prepCsv = 'prep', peakCsv = 'peaks'):
        """Create data entry csvs if not exist"""
        
        self.specDir = specDir

        # create csvs if not exist
        name2path = lambda csvName: os.path.join(csvDir, csvName + '.csv')
        csvPaths = [name2path(i) for i in [specCsv, prepCsv, peakCsv]]
        csvFields = [self.specFields(), self.prepFields(), self.peakFields()]
        checkPaths = [os.path.isfile(i) for i in csvPaths]
        falsePaths = [x for x, bool in enumerate(checkPaths) if bool == False]
        if falsePaths:
            [self.createCsv(csvPaths[i], csvFields[i]) for i in falsePaths]
        else:
            self.spec, self.prep, self.peaks = [self.csv2dic(i) for i in csvPaths]
        
        spec, prep, peaks = [pd.read_csv(i) for i in csvPaths]
        join = pd.merge(spec, prep, left_on = 'prep_id', right_on = 'id', suffixes = ('', '_y')).sort_values(by = 'id')
        del join['id_y']

        dic = {}
        for i in join['id']:
            dic[i] = join[join['id'] == i].to_dict('records')[0]
            spectra = self.readSpec(str(i))
            dic[i]['spectra'] = spectra
            widdle = peaks[peaks['spec_id'] == i]
            maxpeaks = self.specPeaks(spectra, widdle)
            dic[i]['peaks'] = maxpeaks
                        
        self.dic = dic 
            
    def createCsv(self, path, fields):
        """Create a data entry csv"""
        with open(path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            
    def specFields(self):
        """Return a list of tuples including fields and data types for description"""
        lst = [
            ('id', 'int'),
            ('lab_id', 'str'),
            ('prep_id', 'int'),
            ('notes', 'str')
        ]
        return(lst)
        
    def prepFields(self):
        """Return a list of tuples including fields and data types for description"""
        lst = [
            ('id', 'int'),
            ('lab_id', 'str'),
            ('prep_id', 'int'),
            ('cation', 'str'),
            ('treatment', 'str'),
            ('temperature', 'float'),
            ('orientation', 'str'),
            ('prep_notes', 'str')
        ]
        return(lst)
        
    def peakFields(self):
        """Return a list of tuples including fields and data types for description"""
        lst = [
            ('id', 'int', 'primary key'),
            ('spec_id', 'str', 'primary key of info data'),
            ('xstart', 'float', '2 Theta value lower than peak'),
            ('xend', 'float', '2 Theta value higher than peak'),
            ('labx', 'float', 'x-coordinate for plot label'),
            ('laby', 'float', 'y-coordinate for plot label'),
            ('peak_notes', 'str', 'notes')
        ]
        return(lst)
        
    def csv2dic(self, path):
        """Convert csv to dictionary"""
        f = open(path,  'r')
        reader = csv.DictReader(f, delimiter = ',')
        # raise an exception if the reader is empty
        try:
            info = {i.strip():[j.strip()] for i,j in next(reader).items()}
            for line in reader:
                for i,j in line.items():
                    i = i.strip()
                    info[i].append(j)
            return(info)
        except:
            if not [i for i in reader]:
                print('CSV data missing')
        finally:
            f.close()
            
    def readSpec(self, lab_id):
        """Read spectra csv for row index"""
        path = os.path.join(self.specDir, str(lab_id) + '.csv')
        spec = pd.read_csv(path, names = ['2 Theta', 'Intensity'])
        return(spec)
            
    def specPeaks(self, spectra, peaks):
        """Calculate peaks from ranges"""
        p = peaks.reset_index()
        xlst = []
        ylst = []
        for id in p['id']:
            pmin = p[p['id'] == id]['xstart'].iloc[0]
            pmax = p[p['id'] == id]['xend'].iloc[0]
            x, y = self.maxPeak(spectra, pmin, pmax)
            xlst += [x]
            ylst += [y]
        x = pd.Series(xlst)
        y = pd.Series(ylst)
        xy = pd.concat([x,y], axis = 1)
        out = pd.concat([p, x, y], axis = 1, ignore_index = True)
        out.columns = list(p.columns) + ['x', 'y']
        return(out)

    def maxPeak(self, spectra, min, max):
        """Return the maximum in a range of spectra"""
        s = spectra
        peak = s[(s['2 Theta'] > min) & (s['2 Theta'] < max)]
        m = peak['Intensity'].max()
        idx = peak[peak['Intensity'] == m].index.tolist()
        x = peak['2 Theta'][idx].iloc[0]
        y = peak['Intensity'][idx].iloc[0]
        return(x, y)
        
    def lab_id(self):
        """Return a complete list of lab id's for use in data selection"""
        lst = list(set(self.spec['lab_id']))
        # sort the list by numbers if they exist
        num, txt = [], []
        for i in lst:
            try:
                float(i)
                num.append(i)
            except:
                txt.append(i)
        num.sort(key = float)
        txt.sort()
        outLst = num + txt
        return(outLst)
        
    def lab_id2idx(self, lab_id):
        """Return the spectra indices for a given lab_id"""
        idx = [x for x, val in enumerate(self.spec['lab_id']) if val == lab_id]
        return(idx)
        
    def labspec(self, lab_id):
        """Return the spectra id's for a given lab_id"""
        idx = [x for x, val in enumerate(self.spec['lab_id']) if val == lab_id]
        spec_id = [self.spec['id'][i] for i in idx]
        return(spec_id)
        
    def min_y(self, spectra):
        """Return the minimum y value of a spectra"""
        return(spectra['Intensity'].min())
        
class plot(object):
    """Plot XRD spectra"""
    def __init__(self, title = '', xlab = '2 ${\\theta}$', ylab = 'Intensity', xlim = None, ylim = None):
        """Load data to a plot object"""
        plt.title(title)
        plt.xlabel(xlab)
        #plt.ylabel(ylab)
        
    def series(self, spectra, colour = '0.25', yshift = False):
        """Add a series to a plot"""
        s = spectra
        x = s['2 Theta']
        y = s['Intensity']
        if yshift:
            plt.tick_params(
                axis = 'y', 
                labelleft = 'off'
                )
            plt.ylabel("Relative Intensity")
        plt.plot(x, y, color = colour)
        
    def peak(self, peaks, colour = '0.25'):
        """Plot a peak"""
        for id in peaks['id']:
            x = peaks[peaks['id'] == id]['x'].iloc[0]
            y = peaks[peaks['id'] == id]['y'].iloc[0]
            plt.plot((x, x), (0, y), colour, linestyle = '--')
            A = round(1.5418 / (2 * np.sin(np.deg2rad(x / 2))), 2)
            plt.text(x, y, A, fontsize = 8)
            
    def axes(self):
        plt.xlabel(r"2${\Theta}$")
        if len(self.yshift) == 0:
            plt.ylabel('Intensity')
        else:
            plt.ylabel('Relative intensity')
            plt.tick_params(
                axis = 'y', 
                which = 'both', 
                left = 'off',
                right = 'off',
                labelleft = 'off'
                )
                
    def annotation(self):
        """Plot annotation"""
        self.axes()
                  
    def show(self):
        """Show plot"""
        #self.annotation()
        plt.show()
        
    def save(self, path):
        #self.annotation()
        plt.savefig(path)
        plt.close()
        
        
        