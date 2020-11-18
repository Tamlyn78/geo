"""Geometric operations predominatly using the shapely package"""

from shapely.geometry import Point, LineString 

def xy_to_point(x, y):
    p = Point(x, y)
    return(p)

def points_to_line(list_of_points):
    """"""
    p = list_of_points
    line = LineString(p)
    return(line)

def shapely_to_wkt(obj):
    w = obj.wkt
    retun(w)

class AffineTransForm:
    def __init__(self, x0=0, y0=0, x1=0, y1=0, theta=0):
        """
        Attributes:
            theta <float>: The angle in degrees between the source and destination grid (anticlockwise).
        """
        from shapely import affinity
        self.a = affinity
        #print(x0,y0,x1,y1,theta)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        #self.theta = theta - 90 # if rotation is zero then this doesnt work
        self.theta = theta # if rotation is zero then this doesnt work
        self.origin = Point(x0, y0)
        self.origin2 = Point(x1, y1)
        self.p1 = Point(x0, y0)
        self.p2 = Point(x1, y1)

    def translate(self, geom):    
        t = self.a.translate
        x = self.p2.x - self.p1.x
        y = self.p2.y - self.p1.y
        trans = t(geom, xoff=x, yoff=y)
        return(trans)

    def rotate(self, geom):
        rot =  self.a.rotate(geom, self.theta, origin=self.p2)
        return(rot)

    def convert(self, x, y):
        p = Point(x,y)
        p = self.translate(p)
        p = self.rotate(p)
        x, y = p.x, p.y
        return(x, y)



class AffineTransFormOld:
    """
    This is a rough affine transformation (translate and rotate only). This should be replaced by a custom matrix affine transformation or a third-party package such as 'affine', once it can be worked out how to use. 
    Transform coordinates between two Cartesian grids with a known common point and orientation.
        Attributes:
            x0 <float>: x-coordinate of the from-grid origin;
            y0 <float>: y-coordinate of the from-grid origin;
            x1 <float>: x-coordinate of the to-grid origin;
            y1 <float>: y-coordinate of the to-grid origin;
            theta <float>: angle (degrees) between the from-grid and to-grid y-axes (anticlockwise).
    """
    def __init__(self, x0, y0, x1, y1, theta):
        """Initialise class with input values."""
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.theta = theta

    def convert(self, x, y):
        """Convert x and y-coordinates between grids."""
        x0, y0 = self.x0, self.y0
        x1, y1 = self.x1, self.y1
        dx, dy = self._rotate(x-x0, y-y0)
        qx, qy = self._quadrant(x, y)
        if qx == True and qy == True:
            x, y = (x1 + dy), (y1 + dx) # this one appears correct
        elif qx == True and qy == False:
            x, y = (x1 + dx), (y1 - dy)
        elif qx == False and qy == True:
            x, y = (x1 - dy), (y1 + abs(dx))
        elif qx == False and qy == False:
            x, y = (x1 - dx), (y1 - dy)
        return(x,y)

    def _rotate(self, x, y):
        """Rotate x and y-coordinates anti-clockwise around zero."""
        c = cos(radians(self.theta))
        s = sin(radians(self.theta))
        dx = (x * c) - (y * s)
        dy = (y * c) + (x * s)
        return(dx, dy)

    def _quadrant(self, x, y):
        """Return true for a positive quadrant and false for negative."""
        x0, y0 = self.x0, self.y0
        x, y = x - x0, y - y0
        x = True if x >= 0 else False
        y = True if y >= 0 else False 
        return(x, y)

       
