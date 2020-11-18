
"""
Methods of multivariate analyses
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
import seaborn as sns


class pca(object):
    """Most of the methods are pulled from 'A Little Book of Python for Multivariate Analysis'"""
    def __init__(self, df, scaled = True):
        """Apply a principal-components analysis on a dataframe"""
        if scaled:
            df = pd.DataFrame(scale(df), index = df.index, columns = df.columns)
        
        self.df = df
        self.pca = PCA().fit(self.df)
        
    def summary(self):
        """Print a summary of the components of a PCA analysis. This method was sourced from 'A Little' """
        pca = self.pca
        df = self.df
        names = ["PC" + str(i) for i in range(1, len(pca.explained_variance_ratio_) + 1)]
        a = list(np.std(pca.transform(df), axis = 0))
        b = list(pca.explained_variance_ratio_)
        c = [np.sum(pca.explained_variance_ratio_[:i]) for i in range(1, len(pca.explained_variance_ratio_) + 1)]
        columns = pd.MultiIndex.from_tuples([("sdev", "Standard deviation"), ("varprop", "Proportion of Variance"), ("cumprop", "Cumulative Proportion")])
        summary = pd.DataFrame(list(zip(a, b, c)), index = names, columns = columns)
        return(summary)
        
    def screeplot(self):
        """Create a scree plot of a PCA. A scree plot displays the eigenvalues associated with a component or factor in descending order versus the number of the component or factor."""
        pca = self.pca
        df = self.df
        y = np.std(pca.transform(df), axis = 0)**2
        x = np.arange(len(y)) + 1
        dpi = 96
        plt.figure(figsize = (500 / dpi, 500 / dpi))
        plt.plot(x, y, "o-")
        plt.xticks(x, ["PC" + str(i) for i in x], rotation = 60)
        plt.ylabel("Variance")
        
    def loadings(self):
        analytes = self.df.columns
        for n, v in enumerate(self.pca.components_):
            components = 'PC' + str(n + 1)
            try:
                df[analytes[n]] = v
                idx.append(components)
            except:
                df = pd.DataFrame(v, columns = [analytes[n]], dtype = 'float64')
                idx = [components]
                
        df.index = idx
        return(df)
        
    def principal_components(self, loadings):
        df = self.df
        # find the number of samples in the data set and the number of variables
        numsamples, numvariables = df.shape
        # make a vector to store the component
        for c in loadings.index:
            pc = np.zeros(numsamples)
            loading = loadings.ix[c]
            for sample in range(numsamples):
                valuei = 0
                for analyte in range(numvariables):
                    valueij = df.iloc[sample, analyte]
                    loadingj = loading[analyte]
                    valuei = valuei + (valueij * loadingj)
                pc[sample] = valuei
            try:
                wee[c] = pc
                wee[c].columns = c
            except:
                wee = pd.DataFrame(pc, columns = [c])
        return(wee)

        

        

        

