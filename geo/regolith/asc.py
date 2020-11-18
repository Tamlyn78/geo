#!/usr/bin/env python

"""Module for Australian Soil Classification System"""

import os

class ASC:
    """Append a human-readable description to a dictionary of soil profiles described according to the Australian Soil Classification nomenclature.
        Attributes:
            lst <list>: list of psycopg2.extras.DictRow, in order of presentation.
    """
    def __init__(self, DictRow):
        """"""
        i = DictRow
        d = ''
        d += self.colour(i)
        d += self.texture(i)
        d += self.strength(i)
        d += self.moisture(i)
        d += self.structure(i)
        d += self.coarse_fraction(i)
        d += self.coarse_fraction(i, second = True)
        d += self.voids(i)
        d += self.roots(i)
        d += self.roots(i, second = True)
        d += self.segregations(i)
        d += self.segregations(i, second = True)
        d += self.lower_boundary(i)
        if d.endswith('; '):
            d = d[:-2]
        d += ' to:-'
        d = d[0].capitalize() + d[1:]
        self.description = d
        
    def colour(self, d):
        c = d['colour']
        hd = d['hue_dry']
        vd = d['value_dry']
        cd = d['chroma_dry']
        hm = d['hue_moist']
        vm = d['value_moist']
        cm = d['chroma_moist']
        t = ''
        t += c if c else ''
        t += ', ' if hd or (hd and vd and cd) or hm or (hm and vm and cm) else ''
    
        t += hd if hd else ''
        t += ' ' if hd and (vd or cd) else ''
        t += vd + '/' + cd + ' (dry)' if vd and hd else ''
        t += ', ' if (hd or (hd and vd and cd)) and (hm or (hm and vm and cm)) else ''
        t += hm if hm else ''
        t += ' ' + vm + '/' + cm + ' (moist)' if hm and vm and cm else ''
        t += '; ' if c or hd or (hd and vd and cd) or hm or (hm and vm and cm) else ''
        return(t)
        
    def texture(self, d):
        ft = d['field_texture']
        tq = d['texture_qualifier']
        si = d['sand_size']
        so = d['sand_sorting']
        t = ''
        t += tq + ' ' if ft and tq else ''
        t += si + ' ' if ft == 'sand' and si else ''
        t += ft if ft else ''
        t += ', ' if so else ''
        t += so + ' sorted' if so else ''
        t += '; ' if ft or tq or si or so else ''
        return(t)
        
    def strength(self, d):
        s = d['strength']
        return(s + ' strength; ' if s else '')
    
    def moisture(self, d):
        m = d['moisture']
        return(m + '; ' if m else '')
    
    def structure(self, d):
        g = d['structure_grade']
        ty = d['structure_type']
        si = d['structure_size']
        t = ''
        t += g if g else ''
        t += ', ' if g and ty else ''
        t += ty if ty else ''
        t += ' structure' if g or ty else ''
        t += ', ' if (g or ty) and si else ''
        t += si + ' peds' if si else ''
        t += '; ' if g or ty or si else ''
        return(t)
        
    def coarse_fraction(self, d, second = False):
        lst = ['coarse_frags_distribution', 'coarse_frags_abundance', 'coarse_frags_size', 'coarse_frags_roundness', 'coarse_frags_sphericity', 'coarse_frags_type']
        if second is True:
            lst = [i.replace('frags', 'frags2') for i in lst]
        di, ab, si, ro, sp, ty = [d[i] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ', ' if ab and (sp or ro or si or ty or di) else ''
        t += sp if sp else ''
        t += ', ' if sp and (ro or si or ty or di) else ''
        t += ro if ro else ''
        t += ', ' if ro and (si or ty or di) else ''
        t += si if si else ''
        t += ', ' if si and (ty or di) else ''
        t += ty if ty else ''
        t += ' coarse fragments' if ab or sp or ro or si or ty else ''
        t += ', ' if ty and (di) else ''
        t += di if di else ''
        t += '; ' if ab or sp or ro or si or ty or di else ''
        return(t)
        
    def voids(self, d):
        cr = d['voids_cracks']
        si = d['voids_pore_size']
        ab = d['voids_pore_abundance']
        t = ''
        t += cr + ' cracks' if cr else ''
        t += ', ' if cr and (si or ab) else ''
        t += si if si else ''
        t += ab if ab else ''
        t += '; ' if cr or si or ab else ''
        return(t)
    
    def roots(self, d, second = False):
        lst = ['roots1_size', 'roots1_abundance']
        if second is True:
            lst = [i.replace('1', '2') for i in lst]
        si, ab = [d[i] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ' ' if ab and si else ''
        t += si if si else ''
        t += ' roots; ' if ab or si else ''
        return(t)

    def segregations(self, d, second = False):
        lst = ['segregations1_abundance', 'segregations1_size', 'segregations1_colour', 'segregations1_form']
        if second is True:
            lst = [i.replace('1', '2') for i in lst]
        ab, si, co, fo = [d[i] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ', ' if ab and (si or co or fo) else ''
        t += si if si else ''
        t += ', ' if si and (co or fo) else ''
        t += co if co else ''
        t += ' ' if co and (fo) else ''
        t += fo if fo else ''
        t += '; ' if co or ab or si or co else ''
        return(t)

    def lower_boundary(self, d):
        di = d['lower_bound_dist']
        sh = d['lower_bound_shape']
        t = ''
        t += di if di else ''
        t += ' and ' if di and sh else ''
        t += sh if sh else ''
        t += ' boundary; ' if di or sh else ''
        return(t)
        
        
        
class australian_soil_classification_bak(object):
    """Append a human-readable description to a dictionary of soil profiles described according to the Australian Soil Classification nomenclature.
        Attributes:
            dic <list>: list of psycopg2.extras.DictRow, in order of presentation.
    """
    def __init__(self, dic):
        self.dic = dic
    
    def profile(self, factor):
        idx = self.idx(factor)
        lst = []
        for i in idx:
            d = self.unit_values(i)
            description = self.description(i)
            d['description'] = description.replace(' to:-', '.') if i == max(idx) else description
            lst += [d]
        return(lst)
        
    def idx(self, factor):
        """Return the indices of the units of a profiles factor id"""
        idx = [n for n, i in enumerate(self.dic['factor']) if i == factor]
        idx = self.order(idx)
        return(idx)
        
    def order(self, idx):
        """Return a list of indices representing the order of units (determined by the 'description_id' field"""
        d = self.dic
        lst = [(n, i) for n, i in enumerate(d['unit_order']) if n in idx]
        lst.sort(key = lambda tup: tup[1])
        lst = [i[0] for i in lst]
        return(lst)
        
    def unit_values(self, idx):
        """Return a dictionary of characteristics for a given unit index"""
        d = {}
        for key in self.dic.keys():
            d[key] = self.dic[key][idx]
        return(d)
        
    def description(self, idx):
        """"""
        i = idx
        d = ''
        d += self.colour(i)
        d += self.texture(i)
        d += self.strength(i)
        d += self.moisture(i)
        d += self.structure(i)
        d += self.coarse_fraction(i)
        d += self.coarse_fraction(i, second = True)
        d += self.voids(i)
        d += self.roots(i)
        d += self.roots(i, second = True)
        d += self.segregations(i)
        d += self.segregations(i, second = True)
        d += self.lower_boundary(i)
        if d.endswith('; '):
            d = d[:-2]
        d += ' to:-'
        d = d.capitalize()
        return(d)
        
    def colour(self, idx):
        d = self.dic
        i = idx
        c = d['colour'][i]
        hd = d['hue_dry'][i]
        vd = d['value_dry'][i]
        cd = d['chroma_dry'][i]
        hm = d['hue_moist'][i]
        vm = d['value_moist'][i]
        cm = d['chroma_moist'][i]
        t = ''
        t += c if c else ''
        t += ', ' if hd or (hd and vd and cd) or hm or (hm and vm and cm) else ''
    
        t += hd if hd else ''
        t += ' ' if hd and (vd or cd) else ''
        t += vd + '/' + cd + ' (dry)' if vd and hd else ''
        t += ', ' if (hd or (hd and vd and cd)) and (hm or (hm and vm and cm)) else ''
        t += hm if hm else ''
        t += ' ' + vm + '/' + cm + ' (moist)' if hm and vm and cm else ''
        t += '; ' if c or hd or (hd and vd and cd) or hm or (hm and vm and cm) else ''
        return(t)
        
    def texture(self, idx):
        d = self.dic
        i = idx
        ft = d['field_texture'][i]
        tq = d['texture_qualifier'][i]
        si = d['sand_size'][i]
        so = d['sand_sorting'][i]
        t = ''
        t += tq + ' ' if tq else ''
        t += ft if ft else ''
        t += ', ' if si or so else ''
        t += si + ' sand' if si else ''
        t += ', ' if so else ''
        t += so + ' sorted' if so else ''
        t += '; ' if ft or tq or si or so else ''
        return(t)
        
    def strength(self, idx):
        i = idx
        d = self.dic
        s = d['strength'][i]
        return(s + ' strength; ' if s else '')
    
    def moisture(self, idx):
        i = idx
        d = self.dic
        m = d['moisture'][i]
        return(m + '; ' if m else '')
    
    def structure(self, idx):
        i = idx
        d = self.dic
        g = d['structure_grade'][i]
        ty = d['structure_type'][i]
        si = d['structure_size'][i]
        t = ''
        t += g if g else ''
        t += ', ' if g and ty else ''
        t += ty if ty else ''
        t += ' structure' if g or ty else ''
        t += ', ' if (g or ty) and si else ''
        t += si + ' peds' if si else ''
        t += '; ' if g or ty or si else ''
        return(t)
        
    def coarse_fraction(self, idx, second = False):
        d = self.dic
        lst = ['coarse_frags_distribution', 'coarse_frags_abundance', 'coarse_frags_size', 'coarse_frags_roundness', 'coarse_frags_sphericity', 'coarse_frags_type']
        if second is True:
            lst = [i.replace('frags', 'frags2') for i in lst]
        di, ab, si, ro, sp, ty = [d[i][idx] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ', ' if ab and (sp or ro or si or ty or di) else ''
        t += sp if sp else ''
        t += ', ' if sp and (ro or si or ty or di) else ''
        t += ro if ro else ''
        t += ', ' if ro and (si or ty or di) else ''
        t += si if si else ''
        t += ', ' if si and (ty or di) else ''
        t += ty if ty else ''
        t += ' coarse fragments' if ab or sp or ro or si or ty else ''
        t += ', ' if ty and (di) else ''
        t += di if di else ''
        t += '; ' if ab or sp or ro or si or ty or di else ''
        return(t)
        
    def voids(self, idx):
        i = idx
        d = self.dic
        cr = d['voids_cracks'][i]
        si = d['voids_pore_size'][i]
        ab = d['voids_pore_abundance'][i]
        t = ''
        t += cr + ' cracks' if cr else ''
        t += ', ' if cr and (si or ab) else ''
        t += si if si else ''
        t += ab if ab else ''
        t += '; ' if cr or si or ab else ''
        return(t)
    
    def roots(self, idx, second = False):
        d = self.dic
        lst = ['roots1_size', 'roots1_abundance']
        if second is True:
            lst = [i.replace('1', '2') for i in lst]
        si, ab = [d[i][idx] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ' ' if ab and si else ''
        t += si if si else ''
        t += ' roots; ' if ab or si else ''
        return(t)

    def segregations(self, idx, second = False):
        d = self.dic
        lst = ['segregations1_abundance', 'segregations1_size', 'segregations1_colour', 'segregations1_form']
        if second is True:
            lst = [i.replace('1', '2') for i in lst]
        ab, si, co, fo = [d[i][idx] for i in lst]
        t = ''
        t += ab if ab else ''
        t += ', ' if ab and (si or co or fo) else ''
        t += si if si else ''
        t += ', ' if si and (co or fo) else ''
        t += co if co else ''
        t += ' ' if co and (fo) else ''
        t += fo if fo else ''
        t += '; ' if co or ab or si or co else ''
        return(t)

    def lower_boundary(self, idx):
        i = idx
        d = self.dic
        di = d['lower_bound_dist'][i]
        sh = d['lower_bound_shape'][i]
        t = ''
        t += di if di else ''
        t += ' and ' if di and sh else ''
        t += sh if sh else ''
        t += ' boundary; ' if di or sh else ''
        return(t)
        
        
