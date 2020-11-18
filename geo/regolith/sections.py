""""""

from os.path import join
import sys
from PIL import Image, ImageDraw, ImageFont
import textwrap

from fonts.ttf import SourceSansPro as Font

class Report:
    def __init__(self, image, schematic, description, outpath):
        """Create a section drawing.
            Attributes:
                image <str>: path to image file;
                schematic <str>: path to schematic file;
                description <list>: an ordered list of dictionaries for each unit;
                outpath <str>: path to output image file;
        """
        self.ipath = image
        self.spath = schematic
        self.description = description
        outfile = outpath
        
        w, h = self.page_dimensions()

        self.page = Image.new('RGB', (w, h), 'white')
        self.draw = ImageDraw.Draw(self.page)
        
        self.image()
        
        self.schematic()

        self.text()
 
        self.page.save(outfile)
        
    def page_dimensions(self):
        """Create pageReturn width and height of page"""
        dpi = 300
        w, h = int(round(11.7 * dpi)), int(round(8.27 * dpi))
        return(w, h)
        
    def leftbox():
        """Return width of left box"""
        w = 2 / 3 * self.page_dimensions()[0]
        return(w)
        
    def image(self):
        """"""
        im = Image.open(self.ipath)
        
        x, y = self.split()
        if self.ratio(im) > 1:
            # wide
            w = x[2] - x[0]
            h = y[1] - y[0]
            im = self.resize_image(im, w)
            x, y = self.imagecenter(im)
            node = (int(round(w / 2 - x)), (int(round(h / 2 - y))))
        else:
            # tall
            w = x[1] - x[0]
            h = y[2] - y[0]
            im = self.resize_image(im, w)
            x, y = self.imagecenter(im)
            node = (int(round(w / 2 - x)), (int(round(h / 2 - y))))
        
        self.page.paste(im, node, im)
        ld, ud = self.depth_range()
        self.scale(im, node, ld - ud)
        
    def schematic(self):
        """"""
        im = Image.open(self.spath)
        x, y = self.split()
        if self.ratio(im) > 1:
            # wide
            w = x[2] - x[0]
            h = y[1] - y[0]
            im = self.resize_image(im, w)
            x, y = self.imagecenter(im)
            node = (int(round(w / 2 - x)), (int(round(h / 2 - y + h))))
        else:
            # tall
            w = x[1] - x[0]
            h = y[2] - y[0]
            im = self.resize_image(im, w)
            x, y = self.imagecenter(im)
            node = (int(round(w / 2 - x + w)), (int(round(h / 2 - y))))
        self.page.paste(im, node, im)
        ld, ud = self.depth_range()
        self.scale(im, node, ld - ud)
        
    def split(self):
        """Return tuples of x and y defining outer edges and centers of page"""
        x0 = 0
        x2 = self.boxwidth()
        x1 = ((x2 - x0) / 2) + x0
        y0 = 0
        y2 = self.page.height
        y1 = ((y2 - y0) / 2) + y0
        return((x0, x1, x2), (y0, y1, y2))
        
    def ratio(self, im):
        """Return ratio of width to height"""
        w, h = im.size
        return(w / h)
       
    def subplot(self, im):
        """"""
        w, h = im.size
        if w > h:
            return(self.boxwidth())
        else:
            return(self.boxwidth() / 2)
            
    def image_node(self, im):
        w, h = im.size
        if w > h:
            return(self.boxwidth())
        else:
            return(self.boxwidth() / 2)
            
    def resize_image(self, im, boxwidth):
        b = int(round(boxwidth * 0.6))
        w, h = im.size
        wee = int(round((h * b / w)))
        rs = im.resize((b, wee))
        return(rs)
         
    def boxwidth(self):
        return(2 / 3 * self.page.width)

    def imagecenter(self, im):
        """Return half the width and height of an image"""
        w, h = im.size
        return(w / 2, h / 2)
        
    def depth_range(self):
        """Needs rewriting to allow for interbedded units"""
        ld = max([i['lower_depth'] for i in self.description if i['lower_depth']]) / 100
        ud = min([i['upper_depth'] for i in self.description]) / 100
        return(ld, ud)
               
    def scale(self, im, node, meters):
        """Return a vertical depth-bar for a given image and tuple containing the coordinates of its upper-left corner"""
        w, h = im.size
        m = meters
        x = node[0] - w / 100 * 4
        y1 = node[1]
        y2 = node[1] + h
        cm = int(round(m * 100))
    
        fs = 32

        # main stem
        self.draw.line((x, y1, x, y2), fill = (0,0,0), width = 3)
        #font = ImageFont.truetype(fontpath, fs)
        font = ImageFont.truetype(Font, fs)
        self.draw.text((x - fs / 2, y1 - fs * 2), '(m)', (0, 0, 0), font = font)
        
        # 1cm ticks

        cmp = (y2 - y1) / cm * 10
        for i in range(0, int(round(cm + 1))):
            x1 = x
            x2 = x + 15
            y = int(round(y1 + cmp * i / 10))
            self.draw.line((x, y, x + 5, y), fill = (0,0,0), width = 2)
            
        # 10 cm ticks
        #font = ImageFont.truetype(fontpath, fs)
        font = ImageFont.truetype(Font, fs)
        dmp = int(round(y2 - y1) / cm * 10)
        for i in range(0, cm, 10):
            label = str(i / 100)
            x1 = x
            x2 = x + 15
            y = y1 + dmp * i / 10
            self.draw.line((x, y, x + 15, y), fill = (0,0,0), width = 3)
            tx = x - fs * 2 + (fs / len(label) / 2)
            self.draw.text((tx, y - (fs / 2)), label, (0, 0, 0), font = font)
            
    def text(self):
        y = self.page.height / 2 / 2
        y = 48
        #font = ImageFont.truetype(fontpath, 48)
        font = ImageFont.truetype(Font, 48)
        self.draw.text((self.boxwidth(), y), 'Field Description', (0, 0, 0), font = font)
        line = 1.75
        for i in self.description:
        
            unit = i['label']
            self.draw.text((self.boxwidth(), y + (line * 48)), unit, (0, 0, 0), font = font)
            
            ud = i['upper_depth']
            ld = i['lower_depth']
            depth = str(ud / 100) + '-' + str(ld / 100) + 'm' if ld else '>' + str(ud / 100)
            self.draw.text((self.boxwidth() + 150, y + (line * 48)), depth, (0, 0, 0), font = font)
            
            for j in textwrap.wrap(i['description'], width = 30):
                self.draw.text((self.boxwidth() + 400, y + (line * 48)), j, (0, 0, 0), font = font)
                line += 1
            line += 1

