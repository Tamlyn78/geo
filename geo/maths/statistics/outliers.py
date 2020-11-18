
"""
Methods to identify outliers of a dataset
"""

from scipy import stats
import pandas as pd

def peirces_criterion(s):
    """
        Peirce's criterion. Some interweb sources suggest this is a more robust method than Chauvenet's but is not commonly used; other references suggest the method can only remove two or more outliers; nothing has been verified yet.
    """
   
def chauvenets_criterion(s):
    """
        Chauvenet's criterion
    """
    n = len(s)
    mean = s.mean()
    std = s.std()
    z = pd.Series([abs((i - mean)) / std for i in s])
    T = abs(stats.norm.ppf(1 / (4 * n)))
    outliers = z > T
    indices = outliers[outliers == True].index
    return(indices)