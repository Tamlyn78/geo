""""""


import sys
from PIL import Image, ImageDraw, ImageFont
import textwrap

# fonts need to be automated for cross-platform somehow
#fontpath = r"C:\Windows\Fonts\ARIAL.TTF"
fontpath = "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf" # need code to check for the presence of the font and give error


class page_dimensions(object):
    """Return width and height of a given page dimension"""
    
    def A4(self, layout, dpi = 300):
        w = int(round(11.7 * dpi))
        h = int(round(8.27 * dpi))
        if layout == 'landscape':
            return(w, h)
        elif layout == 'portrait':
            return(h, w)
        
class landscape(object):
    def __init__(self, dic):
        """Create a landscape section drawing"""
        d = dic
        image = d['image']
        schematic = d['schematic']
        description = d['description']
        outfile = d['output']
        
        w, h = page_dimensions().A4('landscape')
        
        page = Image.new('RGB', (w, h), 'white')
        boxwidth = 2 / 3 * w
        x1, x2 = self.pagecenter_x(w, boxwidth)
        y1, y2 = self.pagecenter_y(w, h)        

        # load images and find centers
        im = Image.open(image)
        sc = Image.open(schematic)
 
        # resize images to fill left boxwidth
        im = self.resize_image(im, boxwidth)
        sc = self.resize_image(sc, boxwidth)
        
        # find image centers
        im_x, im_y = self.imagecenter(im)
        sc_x, sc_y = self.imagecenter(sc)

        # paste images to page
        imnode = (int(round(x1 - im_x)), (int(round(y1 - im_y))))
        scnode = (int(round(x1 - sc_x)), (int(round(y2 - sc_y))))
        page.paste(im, imnode, im)
        page.paste(sc, scnode, sc)

        # draw text
        draw = ImageDraw.Draw(page)
        font = ImageFont.truetype(fontpath, 48)

        draw.text((boxwidth, y1), 'Field Description', (0, 0, 0), font = font)
        
        line = 1.75
        for i in description:
        
            unit = i['label']
            draw.text((boxwidth, y1 + (line * 48)), unit, (0, 0, 0), font = font)
            
            ud = i['upper_depth']
            ld = i['lower_depth']
            depth = str(ud / 100) + '-' + str(ld / 100) + 'm' if ld else '>' + str(ud / 100)
            draw.text((boxwidth + 150, y1 + (line * 48)), depth, (0, 0, 0), font = font)
            
            for j in textwrap.wrap(i['description'], width = 30):
                draw.text((boxwidth + 400, y1 + (line * 48)), j, (0, 0, 0), font = font)
                line += 1
            line += 1
        
        ud = min([i['upper_depth'] for i in description]) / 100
        ld = max([i['lower_depth'] for i in description if i['lower_depth']]) / 100
        
        self.scale(draw, im, imnode, ld - ud)

        self.scale(draw, sc, scnode, ld - ud)
        
        page.save(outfile)

    def pagecenter_x(self, w, boxwidth):
        """Return the centre of the left and right box (two thirds of the page width)"""
        l = boxwidth / 2
        r = (w - boxwidth) / 2 + boxwidth
        return(l, r)
        
    def pagecenter_y(self, w, h):
        """Return the centre of the upper and lower half of the page height"""
        c = h / 2
        cu = c / 2
        cl = c + cu
        return(cu, cl)
        
    def imagecenter(self, im):
        """Return half the width and height of an image"""
        w, h = im.size
        return(w / 2, h / 2)
        
    def resize_image(self, im, boxwidth):
        b = int(round(boxwidth * 0.6))
        w, h = im.size
        wee = int(round((h * b / w)))
        rs = im.resize((b, wee))
        return(rs)
        
    def scale(self, draw, im, node, meters):
        """Return a vertical depth-bar for a given image and tuple containing the coordinates of its upper-left corner"""
        w, h = im.size
        m = meters
        x = node[0] - w / 100 * 4
        y1 = node[1]
        y2 = node[1] + h
        cm = int(round(m * 100))
    
        fs = 32

        # main stem
        draw.line((x, y1, x, y2), fill = (0,0,0), width = 3)
        font = ImageFont.truetype(fontpath, fs)
        
        draw.text((x - fs / 2, y1 - fs * 2), '(m)', (0, 0, 0), font = font)
        
    
        # 1cm ticks
        cmp = (y2 - y1) / cm * 10
        
        for i in range(0, int(round(cm + 1))):
            x1 = x
            x2 = x + 15
            y = int(round(y1 + cmp * i / 10))
            
            draw.line((x, y, x + 5, y), fill = (0,0,0), width = 2)
            

        # 10 cm ticks
    
        font = ImageFont.truetype(fontpath, fs)
        dmp = int(round(y2 - y1) / cm * 10)
        for i in range(0, cm, 10):
            label = str(i / 100)
            x1 = x
            x2 = x + 15
            y = y1 + dmp * i / 10
            draw.line((x, y, x + 15, y), fill = (0,0,0), width = 3)
            tx = x - fs * 2 + (fs / len(label) / 2)
            draw.text((tx, y - (fs / 2)), label, (0, 0, 0), font = font)        

    
