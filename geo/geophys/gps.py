"""Useful classes and methods for GPS instuments"""

class TrimbleR10:
    """Define the data output structure for the Dualem-421"""

    def __init__(self):
        """"""
        self.columns = self._columns()
        self.dtypes = self._dtypes()

    def _nmea(self):
        """Return a list of pandas data types for Dualem421 NMEA output"""
        lst = [
                ('ID', 'str'),
                ('UTC', 'int32'), 
                ('Latitude', 'float64'), 
                ('Direction_of_Latitude', 'str'), 
                ('Longitude', 'float64'), 
                ('Direction_of_Longitude', 'str'),
                ('Quality', 'int8'),
                ('SVs', 'int8'), 
                ('HDOP', 'float32'), 
                ('Height', 'float32'), 
                ('Height_Units', 'str'), 
                ('Geoid_Separation', 'float32'), 
                ('Separation_Units', 'str'),
                ('Age_of_Diff_Record', 'int8'),
                ('Ref_station_and_checksum', 'str'),
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

   
