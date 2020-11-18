
import sys
from PIL import Image, ImageDraw, ImageFont

def rd(f):
    """Round float to nearest integer"""
    return(round(int(f)))

def page(orientation):
    """Return width and height for an A4 page"""
    w = rd(11.7 * 300)
    h = rd(8.27 * 300)
    if orientation == 'landscape':
        return(w, h)
    elif orientation == 'portrait':
        return(h, w)
        
def pagecenter_x(w, boxwidth):
    """Return the centre of the left and right box (two thirds of the page width)"""
    l = rd(boxwidth / 2)
    r = rd((w - boxwidth) / 2 + boxwidth)
    return(l, r)
        
def pagecenter_y(w, h):
    """Return the centre of the upper and lower half of the page height"""
    c = h / 2
    cu = c / 2
    cl = c + cu
    return(rd(cu), rd(cl))
    
def imagecenter(im):
    """Return half the width and height of an image"""
    w, h = im.size
    return(rd(w / 2), rd(h / 2))
    
def resize_image(im, boxwidth):
    b = rd(boxwidth * 0.8)
    w, h = im.size
    p = b / w
    rs = im.resize((b, rd(h * p)))
    return(rs)
    
def scale(im, node, meters, draw):
    """Return a vertical depth-bar for a given image and tuple containing the coordinates of its upper-left corner"""
    w, h = im.size
    m = meters
    x = node[0] - w / 100 * 4
    y1 = node[1]
    y2 = node[1] + h
    #print([i for i in meters])
    cm = rd(m * 100)
    
    fs = 32

    # main stem
    draw.line((x, y1, x, y2), fill = (0,0,0), width = 3)
    font = ImageFont.truetype(r'C:\Windows\Fonts\ARIALN.TTF', fs)
    draw.text((x - fs / 2, y1 - fs * 2), '(m)', (0, 0, 0), font = font)
    
    # 1cm ticks
    cmp = rd((y2 - y1) / cm * 10)
    for i in range(0, cm + 1):
        x1 = x
        x2 = x + 15
        y = y1 + cmp * i / 10
        draw.line((x, y, x + 5, y), fill = (0,0,0), width = 2)

    # 10 cm ticks
    
    font = ImageFont.truetype(r'C:\Windows\Fonts\ARIALN.TTF', fs)
    dmp = rd((y2 - y1) / cm * 10)
    for i in range(0, cm, 10):
        label = str(i / 100)
        x1 = x
        x2 = x + 15
        y = y1 + dmp * i / 10
        draw.line((x, y, x + 15, y), fill = (0,0,0), width = 3)
        tx = x - fs * 2 + (fs / len(label) / 2)
        draw.text((tx, y - (fs / 2)), label, (0, 0, 0), font = font)
    

    
def main(dic):
    # create page and findcenters
    d = dic
    w, h = page('landscape')
    p = Image.new('RGB', (w, h), 'white')
    boxwidth = rd(2 / 3 * w)
    x1, x2 = pagecenter_x(w, boxwidth)
    y1, y2 = pagecenter_y(w, h)

    # load images and find centers
    im = Image.open(d['image'])
    sc = Image.open(d['schematic'])

    # resize images to fill left boxwidth
    im = resize_image(im, boxwidth)
    sc = resize_image(sc, boxwidth)

    # find image centers
    im_x, im_y = imagecenter(im)
    sc_x, sc_y = imagecenter(sc)

    # paste images to page
    imnode = (x1 - im_x, y1 - im_y)
    scnode = (x1 - sc_x, y2 - sc_y)
    p.paste(im, imnode, im)
    p.paste(sc, scnode, sc)

    draw = ImageDraw.Draw(p)
    font = ImageFont.truetype(r'C:\Windows\Fonts\ARIALN.TTF', 48)
    txt = """Field Description"""
    draw.text((x2, y1), txt, (0, 0, 0), font = font)
    print(d['description'])
    
    scale(im, imnode, 0.32, draw)
    scale(sc, scnode, 0.32, draw)

    p.save(d['output'])


# # create page and findcenters
# w, h = page('landscape')
# p = Image.new('RGB', (w, h), 'white')
# boxwidth = rd(2 / 3 * w)
# x1, x2 = pagecenter_x(w, boxwidth)
# y1, y2 = pagecenter_y(w, h)

# # load images and find centers
# im = Image.open('image.png')
# sc = Image.open('schematic.png')

# # resize images to fill left boxwidth
# im = resize_image(im, boxwidth)
# sc = resize_image(sc, boxwidth)

# # find image centers
# im_x, im_y = imagecenter(im)
# sc_x, sc_y = imagecenter(sc)

# # paste images to page
# imnode = (x1 - im_x, y1 - im_y)
# scnode = (x1 - sc_x, y2 - sc_y)
# p.paste(im, imnode, im)
# p.paste(sc, scnode, sc)

# draw = ImageDraw.Draw(p)
# font = ImageFont.truetype(r'C:\Windows\Fonts\ARIALN.TTF', 48)
# txt = """Field Description

# More description here"""
# draw.text((x2, y1), txt, (0, 0, 0), font = font)
# scale(im, imnode, 0.32)
# scale(sc, scnode, 0.32)

# p.save('page.png')

