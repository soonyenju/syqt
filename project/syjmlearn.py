# -*- coding: utf-8 -*-
"""
是否可以去掉x, y, z 只保留xi, yi, zi
"""
from osgeo import ogr
import numpy as np 
from scipy import interpolate
import matplotlib.pyplot as plt
from matplotlib import cm
import syjspatial

class learn(object):
	"""docstring for interpol"""
	def __init__(self):
		pass
	def __del__(self):
		pass

	def interpol(self, shpfile, att = "ANN_PREC"):
		spatialref = shpfile["spatialref"]
		geomtype = shpfile["geomtype"]
		geomlist = shpfile["geomlist"]
		reclist = shpfile["reclist"]
		ref=spatialref.ExportToPrettyWkt()
		
		info_ = []

		for i in range(len(geomlist)):
			gmt = geomlist[i]
			rec = reclist[i]
			gmt_ = ogr.CreateGeometryFromWkt(gmt)
			x, y, p = gmt_.GetX(), gmt_.GetY(), rec[att]
			info_.append([x, y, p])

		info = np.array(info_)
		x = info[:, 0]	# x coordinate
		y = info[:, 1]	# y coordinate
		z = info[:, 2]	# precipitation
		arrx = np.linspace(np.min(x), np.max(x), 100)	#create 100 points in range bewtween minx and maxx
		arry = np.linspace(np.min(y), np.max(y), 100)
		xi, yi = np.meshgrid(arrx, arry)	#Return coordinate matrices from coordinate vectors
		rbf = interpolate.Rbf(x, y, z, epsilon = 2) # radial basis function interpolator instance
		zi = rbf(xi,yi)	# interpolated values
		# zi = zi.tolist() 不好用，改变了维度2维变1维
		orgnarr = [x, y, z]
		rtrnarr = [xi, yi, zi]
		return orgnarr, rtrnarr
		"""
		method2
		np.save("x.npy",x); np.save("y.npy",y); np.save("z.npy",z)
		np.save("xi.npy",xi); np.save("yi.npy",yi); np.save("zi.npy",zi)
		orgnname = ["x.npy", "y.npy", "z.npy"]
		rtrnname = ["xi.npy", "yi.npy", "zi.npy"]
		return orgnname, rtrnname

	def matdraw(self, orgnname, rtrnname, ttl = 'default_name interpolation'):
		x, y, z = np.load(str(orgnname[0])), np.load(str(orgnname[1])), np.load(str(orgnname[2]))
		xi, yi, zi = np.load(str(rtrnname[0])), np.load(str(rtrnname[1])), np.load(str(rtrnname[2]))
		"""
	def matdraw(self, orgnarr, rtrnarr, ttl = 'default_name interpolation'):
		x, y, z = orgnarr[0], orgnarr[1], orgnarr[2]
		xi, yi, zi = rtrnarr[0], rtrnarr[1], rtrnarr[2]
		#Get the current Axes instance on the current figure matching the given keyword args, or create one.
		plt.gca().set_aspect(1.0) # same scaling from data to plot units for x and y
		#Return a subplot axes positioned by the given grid definition.
		#subplot(nrows, ncols, plot_number)
		plt.subplot(1, 1, 1)
		#Create a pseudocolor plot of a 2-D array. cmap is color map
		plt.pcolor(xi, yi, zi, cmap = cm.jet)

		#Make a scatter plot of x vs y, where x and y are sequence like objects of the same lengths.
		plt.scatter(x, y, 100, z, cmap = cm.jet)
		plt.title(ttl)
		plt.xlim(x.min(),x.max())
		plt.ylim(y.min(),y.max())
		#Add a colorbar to a plot.
		plt.colorbar()
		extent=[x.min(), x.max(),y.min(), y.max()]

		levels= np.arange(5, int(zi.max()), 5)
		CS = plt.contour(zi, levels, hold = 'on', colors = 'k', origin = 'upper', extent = extent, aspect = 'equal')
		#Label a contour plot.
		plt.clabel(CS, inline = 1, fmt = '%d', fontsize = 10)
		#Tune the subplot layout.
		plt.subplots_adjust(left = 0.15)
		plt.show()

	def svnprmter(self, coor):
		xi, yi = coor[0], coor[1]
		x = xi[0,0]
		y = yi[0,0]
		x_ = xi[0,1]-xi[0,0]
		y_ = yi[1,0]-yi[0,0]
		geotrans=[x, x_, 0, y, 0, -y_]

		return geotrans
#----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	shpfile = syjspatial.syjShp()
	shp = shpfile.read("stations.shp")
	lrn = learn()
	orgn, rtrn = lrn.interpol(shp)
	lrn.matdraw(orgn, rtrn)