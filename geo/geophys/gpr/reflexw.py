
"""RelflexW GPR data processing module.

This module reads data exported from the Sandmeir ReflexW geophysical data processing software 
(seismic and ground-penetrating radar data) and exports analytical images.


Example:
	Examples can be given using either the ``Example`` or ``Examples``
	sections. Sections support any reStructuredText formatting, including
	literal blocks::

		$ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
	module_level_variable1 (int): Module level variables may be documented in
		either the ``Attributes`` section of the module docstring, or in an
		inline docstring immediately following the variable.

		Either form is acceptable, but the two should not be mixed. Choose
		one convention to document module level variables and be consistent
		with it.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import os
import sys
import subprocess
import csv
import tempfile
import shutil
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib as mpl
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.axes_grid1.parasite_axes import SubplotHost
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from gis.grass7 import cartography as ct
from gis.grass7 import mapset as ms

class radarGram(object):

	"""
	Create timeslices from processed radargrams exported as 3-column ASCII files from ReflexW software
	"""
	
	def __init__(self, reflexDir, lineDic):
	
		"""Define inputted and fixed variables of the grid and ReflexW project directory structure.
		
		Arguments:
		
			reflexDir: The path to the ReflexW project (string);
			ascName: Name of a 3-column ASCII file exported from ReflexW
				
		"""
	
		try:

			self.reflexDir = reflexDir
			self.surveyId = lineDic["survey"]
			self.lineId = lineDic["id"]
			self.ascName = lineDic["filename"]
			self.velocity = float(lineDic["velocity"])

			ascPath = os.path.join(self.reflexDir, "ASCII", self.ascName + ".ASC")
			
			f = open(ascPath, "r")

			dat = []


			for line in f.readlines():
				line = line.strip()
				cols = line.split()
				x = float(cols[0])
				y = float(cols[1])
				z = float(cols[2])
				dat.append([x,y,z])

			x = list(set([i[0] for i in dat]))
			x.sort()
			y = list(set([i[1] for i in dat]))
			y.sort()
			self.x = x
			self.y = y
			self.asp =  (max(y) - min(y)) / (max(x) - min(x))

			vector = []
			
			for i in dat:
				vector.append(i[2])
				
			self.matrix = np.reshape(vector, (len(y), len(x)), order = 'F')


		except:
		
			pass
		
			
	def pngOut(self, outName = None, asp = 0.2):
		
		try:
		
			if not outName:
				outName = self.ascName
				
			outDir = os.path.join(self.reflexDir, "PNG")
			
			if not asp:
				asp = self.asp

			if not os.path.isdir(outDir):
				os.makedirs(outDir)

			outPath = os.path.join(outDir, outName + ".png")

			matrix = self.matrix
			
			####### working ###########
			plt.figure()
			#plt.imshow(self.matrix, cmap = 'Greys_r', extent=[min(self.x), max(self.x), max(self.y), min(self.y)], aspect = 0.2)
			plt.imshow(self.matrix, cmap = 'Greys_r', extent=[min(self.x), max(self.x), max(self.y) / 2 * self.velocity, min(self.y) / 2 * self.velocity], aspect = 2.8)
			font = {'family': 'Arial',
					'color':  'black',
					'weight': 'normal',
					'size': 8,
					}
			plt.xticks(fontsize = 6)
			plt.yticks(fontsize = 6)
			plt.xlabel('Distance (m)', fontdict = font)
			#plt.ylabel('Time (ns)', fontdict = font)
			plt.ylabel('Depth (m)', fontdict = font)
			#plt.show()
			print("Survey" + self.surveyId + "\t Line" + self.lineId)
			print(outPath)
			plt.savefig(outPath, dpi = 600, bbox_inches = 'tight')
			plt.close()
			####### end working #########
			
			

			#fig = plt.figure()
			#ax1 = SubplotHost(fig, 1,1,1)
			#fig.add_subplot(ax1)

			#ax1.imshow(self.matrix, cmap = 'Greys_r', extent=[min(self.x), max(self.x), max(self.y), min(self.y)], aspect = 0.2)
			#formatter = FuncFormatter(lambda y, pos: '{:0.1f}'.format(y * float(self.velocity)))

			#majorLocator = MultipleLocator(1 / self.velocity)
			#majorFormatter = FormatStrFormatter('%d')
			#ax2.yaxis.set_major_formatter(formatter)
			#ax2 = ax1.twinx()

			#ax2.yaxis.set_major_locator(majorLocator)
			#ax2.yaxis.set_major_formatter(majorFormatter)

			#plt.show()
			
			#plt.figure()
			
			#im = plt.imshow(matrix, cmap = 'Greys_r', interpolation = "bicubic", extent=[min(self.x), max(self.x), max(self.y), min(self.y)], aspect = 0.2)
			#im = plt.imshow(matrix, cmap = 'Greys_r', extent=[min(self.x), max(self.x), max(self.y), min(self.y)], aspect = asp)

			#font = {'family': 'Arial',
			#		'color':  'black',
			#		'weight': 'normal',
			#		'size': 8,
			#		}

					#im2 = twiny()

			#ax = plt.subplot(1,1,1)
			#ax.plot(im)
			#ax2 = ax.twinx()
			#ax2._sharey = ax # share both x and y
			#fmtr = mpl.ticker.FuncFormatter(lambda x,pos: "%.2f"%np.exp(x))
			#ax2.yaxis.set_major_formatter(fmtr)
			#plt.draw() 
					
			#im2 = im.twiny()
			
			#im.set_xlabel('Distance (m)', fontdict = font)
			#im.set_ylabel('Time (ns)', fontdict = font)
			#im2.set_ylabel('Depth (m)', fontdict = font)


			#plt.xticks(fontsize = 6)
			#plt.yticks(fontsize = 6)
			#plt.xlabel('Distance (m)', fontdict = font)
			#plt.ylabel('Time (ns)', fontdict = font)
			#plt.show()
			#print("Survey" + self.surveyId + "\t Line" + self.lineId)

			#fig.savefig(outPath, dpi = 600, bbox_inches = 'tight')

			#outDir = r'C:\Users\samp'
			#outPath = os.path.join(outDir, "test.png")
			#plt.savefig(outPath, dpi = 300)
			#plt.show()
			#fig.close()

			
		except:
		
			pass
		

class timeSlice(object):

    """
    Create timeslices from processed radargrams exported as 3-column ASCII files from ReflexW software

    """

    def __init__(self, reflexDir, gridId, gridDic, velocity = 0.1):

        """Define inputed and fixed variables of the grid and ReflexW project directory structure.
		
		Arguments:
		
			reflexDir: The path to the ReflexW project (string);
			gridId: A unique identifyer for the grid (string);
			gridDic: A dictionary including the following keys:
			
				Keys:
					
					id: Unique identifier for a single GPR line (integer);
					survey (REQUIRED): Unique identifier for the group of lines, usually by date (string);
					filename: Filename of a single GPR line, usually DAT_000"X" for MALA data;
					grid (REQUIRED): Inique identifier for a grid of GPR lines to be used in a single time slice (string);
					x1 (REQUIRED): x-coordinate of the start-location;
					x2 (REQUIRED): x-coordinate of the end-location;
					y1 (REQUIRED): y-coordinate of the start-location;
					y2 (REQUIRED): y-coordinate of the end-location;
					velocity: velocity (m/ns);
					notes: Notes for the survey line.
				
		"""
        
        try:

			self.reflexDir = reflexDir
			self.gridId = gridId
			self.gridDic = gridDic

			self.ascList = [i["filename"] for i in gridDic]
		
			self.ascDir = os.path.join(reflexDir, "ASCII")
			self.sliceDir = os.path.join(reflexDir, "SLICES")
			self.pngDir = os.path.join(reflexDir, "PNG")

			ascList = self.ascList
	
			ascDir = os.path.join(self.reflexDir, "ASCII")
		
			datLst = []

			for i in range(0, len(ascList)):
			#for i in range(0, 3):
				f = os.path.join(ascDir, ascList[i] + ".ASC")
				
				print(os.path.basename(f))
				
				gprLine = []

				for line in open(f, 'r'):
					
				
					line = line.strip()
					cols = line.split()
					
					x = float(cols[0])
					time = float(cols[1])
					amp = float(cols[2])
					
					y = float(self.gridDic[i]["y2"]) # this needs to account for non-regular lines and triangulate against x to find the correct value at each point of x
					
					velocity = float(self.gridDic[i]["velocity"])
					
					depth = velocity * time

					xMin = float(self.gridDic[i]["x1"])
					xMax = float(self.gridDic[i]["x2"])
					
					if x >= xMin and x <= xMax:
					
						gprLine.append(tuple([x + xMin, y, time, amp]))

				datLst.append(gprLine)
				
			self.datLst = datLst
			
			# calculate the spatial dimensions of the grid for correct image output; currently assumes parrallel grid lines
			self.xy = [(j[0], j[1]) for i in self.datLst for j in i]
			xmin = min([i[0] for i in self.xy])
			xmax = max([i[0] for i in self.xy])
			ymin = min([i[1] for i in self.xy])
			ymax = max([i[1] for i in self.xy])
			self.asp =  (ymax - ymin) / (xmax - xmin)
			
		
        except:

            print("Error at " + __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

					
    def checkTimes(self, gridDat = None):

        """Create a list of radar data."""
        
        try:
		
			if not gridDat:
				gridDat = self.datLst

			gprTime = []
			
			for i in range(0, len(gridDat)):

				lst = [j[2] for j in gridDat[i]]
				lst = list(set(lst))
				lst.sort()
				gprTime.append(lst)
				
			check = set([len(i) for i in gprTime])
			check = list(check)
			
			if len(check) > 1:

				return(raw_input("times are not equal")) # script should break here

			else:

				return(gprTime[0])


        except:

            print("Error at " + __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

			
    def sliceDat(self, sliceTime, sliceName = None, sliceDir = None):

        """Text here."""
        
        try:

			# subset a slice of grid data
			sliceDat = [j for i in self.datLst for j in i if j[2] == sliceTime]

			if not sliceName:
			
				sliceName = "GRID" + str(self.gridId) + "-" + str(sliceTime).replace(".","_") #+ str(self.gridID) # + "-" + str(sliceTime)

			if not sliceDir:
				sliceDir = self.sliceDir

			if not os.path.isdir(sliceDir):
				os.makedirs(sliceDir)

			slicePath = os.path.join(sliceDir, sliceName + ".ASC")
			
			sliceFile = open(slicePath, "w")

			for i in sliceDat:

				x = i[0]
				y = i[1]
				z = i[2]
				val = i[3]
				
				sliceFile.write(str(x) + "\t" + str(y) + "\t" + str(val) + "\n")
				
			sliceFile.close()
			
			return(slicePath)
				
			
        except:

            print("Error at " + __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

			
	def meanSlice(self):
	
		"""
		Average a number of slices representing a thickness.
		"""
	
		print("meanSlice")
		
		
	# the custom grass7 modules cartography (ct) and mapset (ms) were previously imported globally but this depends on 
    def sliceMap(self, grass, sliceTime, pngName, pngDir = None):

        """Create a list of radar data."""
        
        try:

			g = grass
			
			slicePath = self.sliceDat(sliceTime)

			if not pngDir:
				pngDir = self.pngDir

			if not os.path.isdir(pngDir):
				os.makedirs(pngDir)
				
			pngPath = os.path.join(pngDir, pngName + ".png")

			# create a temporary mapset
			mapPath = ms(g).tmp()
	
			# import ascii data
			g.run_command('v.in.ascii', overwrite = True, input = slicePath, output = "tmp", separator = "tab", z = 3)

			# set region to bounds of data
			g.run_command('g.region', vector = "tmp", res = 0.05)
			g.run_command('g.region', flags = "p")

			# interpolate over grid
			g.run_command('v.surf.rst', overwrite = True, input = "tmp", elevation = "tmp", theta = 0)
			g.run_command('g.region', raster = "tmp", res = 0.05)

			# make all raster values positive
			g.mapcalc("tmp2 = tmp + abs(min(tmp))", overwrite = True)

			# assign a colour ramp
			g.run_command('r.colors', map = "tmp", color = "rainbow")

			# output image
			ct(g, pngPath, width = 1000, height = self.asp * 1000).png(self.cartography)

			# remove temporary mapset
			shutil.rmtree(mapPath)
		
        except:

			print("Error at " + __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)
			
			
    def cartography(self, grass):

        """Define GRASS GIS commands for map output (grass must be defined as 'g')."""

        try:

            g = grass

            g.run_command('d.rast', map = "tmp")
        
        except:

            print("Error at " + __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

			