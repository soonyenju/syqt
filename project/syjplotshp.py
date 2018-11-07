# -*- coding: utf-8 -*-
import numpy as np
from osgeo import ogr,osr
import matplotlib
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import syjspatial


class plotshp:
	def __init__(self):
		self.shpfile = syjspatial.syjShp()
	def __del__(self):
		del self.shpfile
	
	def cal_patch(self,geom):
		ptchs = []
		for i in range(geom.GetGeometryCount()):
			ring = geom.GetGeometryRef(i)
			pnts = [[ring.GetX(j),ring.GetY(j)] for j in range(ring.GetPointCount())]
			if len(pnts) == 0:
				continue
			ptchs.append(Polygon(pnts))
		return ptchs

	def draw(self,filename, fig):# 添加了 = plt.figure(figsize=(6,3), dpi=150)出现python停止工作
		
		#fig = plt.figure(figsize=(6,3), dpi=150)

		shp = self.shpfile.read(filename)
		spatialref = shp["spatialref"]
		geomtype = shp["geomtype"]
		geomlist = shp["geomlist"] # 只有这个用得到
		fieldlist = shp["fieldlist"]
		reclist = shp["reclist"]

		ax = fig.add_subplot(111)

		cm = matplotlib.cm.get_cmap('Dark2')
		cccol = cm(1.*np.arange(len(geomlist))/len(geomlist))
		
		minx,maxx,miny,maxy = 180,-180,90,-90
		for k in range(len(geomlist)):
			wkt = geomlist[k]
			geom = ogr.CreateGeometryFromWkt(wkt)

			minx_,maxx_,miny_,maxy_= geom.GetEnvelope()
			if minx_<minx:
				minx = minx_
			if miny_<miny:
				miny = miny_
			if maxx_>maxx:
				maxx = maxx_
			if maxy_>maxy:
				maxy = maxy_

			if geom.GetGeometryType() in [1,2,3]:
				ptchs = self.cal_patch(geom)
			elif geom.GetGeometryType() in [4,5,6]:
				ptchs = []
				for i in range(geom.GetGeometryCount()):
					g = geom.GetGeometryRef(i)
					p = self.cal_patch(g)
					ptchs += p

			fc=cccol[k,:]
			ax.add_collection(PatchCollection(ptchs,edgecolor='k', facecolor=fc, linewidths=.1))

		ax.set_xlim(minx,maxx)
		ax.set_ylim(miny,maxy)
		ax.set_aspect(1.0)
		plt.show()

if __name__ == "__main__":
	test = plotshp()
	filename = 'cntry98.shp'
	test.draw(filename)