"""Useful classes and methods for EM instuments"""

class Dualem421:
    """Define the data output structure for the Dualem-421"""

    def __init__(self):
        """"""
        self.columns = self._columns()
        self.dtypes = self._dtypes()

    def _nmea(self):
        """Return a list of pandas data types for Dualem421 NMEA output"""
        lst = [
                ('Array', 'str'),
                ('Time', 'int32'), 
                ('HCP_cond', 'float64'), 
                ('HCP_inphase', 'float64'), 
                ('PRP_cond', 'float64'), 
                ('PRP_inphase', 'float64'), 
        ]
        return(lst)

    def _columns(self):
        """"""
        c = [i[0] for i in self._nmea()]
        return(c)

    def _dtypes(self):
        """"""
        dt = [i[1] for i in self._nmea()]
        return(dt)


