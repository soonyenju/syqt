# -*- coding: utf-8 -*-
'''
--------------
exportToPrettyWkt怎么用？
ref=spatialref.ExportToPrettyWkt()
--------------

'''
from osgeo import gdal, ogr, osr
from osgeo.gdalconst import *
import osgeo
import os
import numpy as np 

class syjRst:
	def __init__(self):
		pass

	def __del__(self):
		pass

	def read(self, fname):
		ds = gdal.Open(fname)
		#ds = gdal.Open("fdem.tif")
		width = ds.RasterXSize
		height = ds.RasterYSize
		bands = ds.RasterCount
		geotrans = ds.GetGeoTransform()
		proj = ds.GetProjection()

		image = ds.ReadAsArray(0, 0, width, height)
		raster = {"data": image, "geotrans": geotrans, "proj": proj}
		return raster
		del ds

	def write(self, im_data, im_geotrans, im_proj, tifname = "pre.tif"):
		if 'int8' in im_data.dtype.name:
			datatype = gdal.GDT_Byte
		elif 'int16' in im_data.dtype.name:
			datatype = gdal.GDT_UInt16
		else:
			datatype = gdal.GDT_Float32

		if len(im_data.shape) == 3:
			im_bands, im_height, im_width = im_data.shape
		else:
			im_bands, (im_height, im_width) = 1, im_data.shape

		driver = gdal.GetDriverByName("GTiff")
		ds = driver.Create(tifname, im_width, im_height, im_bands, datatype)
		ds.SetGeoTransform(im_geotrans) #写入仿射变换参数
		ds.SetProjection(im_proj) #写入投影

		if im_bands == 1:
			ds.GetRasterBand(1).WriteArray(im_data) #写入数组数据
		else:
			for i in range(im_bands):
				ds.GetRasterBand(i+1).WriteArray(im_data[i])
		del ds
	def coorTrans(self):
		#源图像投影，目标图像投影
		sr1 = osr.SpatialReference()
		sr1.ImportFromEPSG(32650) #WGS84/ UTM ZONE 50
		sr2 = osr.SpatialReference()
		sr2.ImportFromEPSG(3857) #Google, Web Mercator
		coordTrans = osr.CoordinateTransformation(sr1, sr2)
		#打开源图像文件
		ds1 = gdal.Open("fdem.tif")
		#insr = ds1.GetProjection() #WGS84 / UTM Zone 50N
		mat1 = ds1.GetGeoTransform()
		#源图像的左上角与右下角像素，在目标图像中的坐标
		(ulx, uly, ulz ) = coordTrans.TransformPoint(mat1 [0], mat1 [3])
		(lrx, lry, lrz ) = coordTrans.TransformPoint(mat1 [0] + mat1[1]*ds1.RasterXSize, \
		mat1[3] + mat1[5]* ds1.RasterYSize )
		#创建目标图像文件（空白图像） ，行列数、波段数以及数值类型仍等同原图像
		driver = gdal.GetDriverByName("GTiff")
		ds2 = driver.Create("fdem_lonlat.tif", ds1.RasterXSize, ds1.RasterYSize, 1, GDT_UInt16)
		resolution = (int)((lrx-ulx)/ ds1.RasterXSize)
		mat2=[ulx, resolution,0,uly,0, -resolution]
		ds2.SetGeoTransform(mat2)
		ds2.SetProjection(sr2.ExportToWkt())
		#投影转换与重采样（gdal.GRA_NearestNeighbour, gdal.GRA_Cubic, gdal.GRA_Bilinear）
		gdal.ReprojectImage(ds1, ds2, sr1.ExportToWkt(), sr2.ExportToWkt(), gdal.GRA_Bilinear)
		#关闭
		ds1 = None
		ds2 = None

class syjShp:
	def __init__(self):
		pass

	def __del__(self):
		pass
	def read(self, filename = "cntry98.shp"):
		ds = ogr.Open(filename, False) #代开 Shape 文件（False - read only, True - read/write）
		layer = ds.GetLayer(0) #获取图层
		# layer = ds.GetLayerByName(filename[-4:])
		spatialref = layer.GetSpatialRef() #投影信息
		lydefn = layer.GetLayerDefn() #图层定义信息
		geomtype = lydefn.GetGeomType() #几何对象类型（wkbPoint, wkbLineString, wkbPolygon）
		fieldlist = [] #字段列表 （字段类型，OFTInteger, OFTReal, OFTString, OFTDateTime）
		for i in range(lydefn.GetFieldCount()):
			fddefn = lydefn.GetFieldDefn(i)
			fddict = {'name':fddefn.GetName(),'type':fddefn.GetType(),
			'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
			fieldlist += [fddict]
		geomlist, reclist = [], [] #SF 数据记录 – 几何对象及其对应属性
		feature = layer.GetNextFeature() #获得第一个 SF
		while feature is not None:
			geom = feature.GetGeometryRef()
			geomlist += [geom.ExportToWkt()]
			rec = {}
			for fd in fieldlist:
				rec[fd['name']] = feature.GetField(fd['name'])
			reclist += [rec]
			feature = layer.GetNextFeature()
		shpfile = {"spatialref":spatialref, "fieldlist":fieldlist, 
				"geomtype":geomtype, "geomlist":geomlist, "reclist":reclist} 
		return shpfile
		ds.Destroy() #关闭数据源
	
	def write(self, fieldlist, geomtype, geomlist, reclist):
		osgeo.gdal.SetConfigOption('GDAL_FILENAME_IS_UTF8', 'NO') # 解决中文路径
		osgeo.gdal.SetConfigOption('SHAPE_ENCODING', 'gb2312') # 解决 SHAPE 文件的属性值
		
		filename = "cntry98_new.shp"
		driver = ogr.GetDriverByName("ESRI Shapefile")
		if os.access(filename, os.F_OK ): #如文件已存在，则删除
			driver.DeleteDataSource(filename)

		ds = driver.CreateDataSource(filename) #创建 Shape 文件

		#spatialref = osr.SpatialReference( 'LOCAL_CS["arbitrary"]' )
		spatialref = osr.SpatialReference()
		spatialref.ImportFromEPSG(4326)
		geomtype = ogr. wkbPolygon

		layer = ds.CreateLayer(filename [:-4], srs=spatialref, geom_type=geomtype) #创建图层
		for fd in fieldlist: #将字段列表写入图层
			field = ogr.FieldDefn(fd['name'],fd['type'])
			if fd.has_key('width'):
				field.SetWidth(fd['width'])
			if fd.has_key('decimal'):
				field.SetPrecision(fd['decimal'])
			layer.CreateField(field)
		for i in range(len(reclist)): #将 SF 数据记录（几何对象及其属性写入图层）
			geom = ogr.CreateGeometryFromWkt(geomlist[i])
			feat = ogr.Feature(layer.GetLayerDefn()) #创建 SF
			feat.SetGeometry(geom)
			for fd in fieldlist:
				feat.SetField(fd['name'], reclist[i][fd['name']])
			layer.CreateFeature(feat) #将 SF 写入图层
		ds.Destroy() #关闭文件

	def shpToRst(self):
		'''
		还没试过！用的时候再说吧！
		'''
		#定义投影
		sr = osr.SpatialReference('LOCAL_CS["arbitrary"]' )
		#在内存中，创建一个 Shape 文件的图层，含有一个多边形和一条线
		source_ds = ogr.GetDriverByName('Memory').CreateDataSource( 'wrk' )
		mem_lyr = source_ds.CreateLayer( 'poly', srs=sr ,geom_type=ogr.wkbPolygon )
		mem_lyr.CreateField(ogr.FieldDefn('TCODE',ogr.OFTReal))
		wkt_geom = ['POLYGON((1020 1030 40,1020 1045 30,1050 1045 20,1050 1030 35,1020 1030 40))',
					'POLYGON((1010 1046 85,1015 1055 35,1055 1060 26,1054 1048 35,1010 1046 85))']
		celsius_field_values = [50,200,60]
		for i in range(len(wkt_geom)):
			feat = ogr.Feature(mem_lyr.GetLayerDefn() )
			feat.SetGeometryDirectly( ogr.Geometry(wkt = wkt_geom[i]) )
			feat.SetField( 'CELSIUS', celsius_field_values[i] )
			mem_lyr.CreateFeature( feat )
		#在内存中，创建一个 100*100 大小的 3 波段的空白图像
		target_ds = gdal.GetDriverByName('MEM').Create('', 100, 100, 1, gdal.GDT_Byte )
		target_ds.SetGeoTransform( (1000,1,0,1100,0,-1) )
		target_ds.SetProjection( sr.ExportToWkt())
		#调用栅格化函数
		err = gdal.RasterizeLayer( target_ds, [1], mem_lyr, options= ["ATTRIBUTE=TCODE"])
		#将内存中的图像，存储到硬盘文件上
		gdal.GetDriverByName('GTiff').CreateCopy('rasterized_poly.tif', target_ds)
		del target_ds
		del source_ds

	def coorTrans(self):
		source = osr.SpatialReference()
		source.ImportFromEPSG(4326) #wgs84
		target = osr.SpatialReference()
		target.ImportFromEPSG(3857) #Google
		coordTrans = osr.CoordinateTransformation(source, target)
		#投影转换
		coordTrans.TransformPoint(117,40) #简单的点转换
		coordTrans.TransformPoints([(117,40),(117.5,39.5)]) #点数组转换
		g= ogr.CreateGeometryFromWkt("POINT(117 40)") #复杂的 SF 几何对象转换
		g.ExportToWkt()
		g.GetX(), g.GetY()
		g.Transform(coordTrans)
		g.ExportToWkt()
		g.GetX(), g.GetY()
#----------------------------------------------------------------------------------------------


if __name__ == "__main__":
	rst = syjRst()
	image = rst.read("fdem.tif")
	data, geotrans, proj = image["data"], image["geotrans"], image["proj"]
	rst.write(data, geotrans, proj)

	shp = syjShp()
	shpfile = shp.read() 
	fieldlist = shpfile["fieldlist"]
	geomtype = shpfile["geomtype"]
	geomlist = shpfile["geomlist"]
	reclist = shpfile["reclist"]
	shp.write(fieldlist, geomtype, geomlist, reclist)

	print('ok')