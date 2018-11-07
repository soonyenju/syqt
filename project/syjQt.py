# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication, QCompleter, QComboBox, QMainWindow, QAction, qApp, QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
from osgeo import ogr
import numpy as np 
import matplotlib
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import re # 提取字符串中数字， 自带的包
import os, syjspatial, syjmlearn, syjplotshp, syjplotrst, syjtable


class syjgis(QMainWindow):
	def __init__(self):
		super(syjgis, self).__init__()
		
		self.initUI()
		self.initCanvas()
		# gate是决定是否函数继续执行还是停止，有两个值："go"和"stop",通过函数self.setgate()确定为"go", 一般为"stop"
		self.gate = 'stop'
		self.isoksavetff = 'no'
		self.iptname = ''

	def initUI(self):
		"""
		----------------------------------------------------------------------
		设置Action并将其与函数事件相连接
		----------------------------------------------------------------------
		"""
		# 打开文件
		openAction = QAction(QtGui.QIcon('icon_open.png'), 'Open', self)
		openAction.setShortcut('Ctrl+O')
		openAction.setStatusTip('Open new file')
		openAction.triggered.connect(self.openshp)
		# self.connect(openAction, QtCore.SIGNAL('triggered()'), self.openshp)
		# 保存
		saveAction = QAction(QtGui.QIcon('icon_save.png'), '&Save', self)
		saveAction.setShortcut('Ctrl+S')
		saveAction.setStatusTip('Save Plot')
		saveAction.triggered.connect(self.on_savedialog)
		# 退出
		exitAction = QAction(QtGui.QIcon('icon_exit.png'), '&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(qApp.quit)
		# 显示shpfile
		showAction = QAction(QtGui.QIcon('icon_show.png'), '&showshp', self)
		showAction.setShortcut('Ctrl+i')
		showAction.setStatusTip('Showing shpfile')
		openAction.triggered.connect(self.showshp)
		# self.connect(showAction, QtCore.SIGNAL('triggered()'), self.showshp)
		# 在combobox显示属性字段
		# attAction = QtGui.QAction(QtGui.QIcon('icon_att.png'), '&attribution', self)
		# attAction.setShortcut('Ctrl+a')
		# attAction.setStatusTip('Showing attribution')
		openAction.triggered.connect(self.readatt)
		# self.connect(attAction, QtCore.SIGNAL('triggered()'), self.readatt)
		# 在table里显示属性
		tblAction = QAction(QtGui.QIcon('icon_abt.png'), '&atttable', self)
		tblAction.setShortcut('Ctrl+t')
		tblAction.setStatusTip('Showing attribution')
		tblAction.triggered.connect(self.tableatt)
		# self.connect(tblAction, QtCore.SIGNAL('triggered()'), self.tableatt)
		# 插值
		iptAction = QAction(QtGui.QIcon('icon_ipt.png'),'&interpolation', self)
		iptAction.setShortcut('Ctrl+p')
		iptAction.setStatusTip('interpolation')
		iptAction.triggered.connect(self.itp)
		# self.connect(iptAction, QtCore.SIGNAL('triggered()'), self.itp)
		# 关于
		aboutAction = QAction(QtGui.QIcon('icon_abt.png'), '&About', self)
		aboutAction.setShortcut('Ctrl+A')
		aboutAction.setStatusTip('About')
		aboutAction.triggered.connect(self.on_about)
		

		"""
		----------------------------------------------------------------------
		设置菜单栏目
		----------------------------------------------------------------------
		"""		
		# file菜单
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(openAction)
		fileMenu.addAction(saveAction)
		fileMenu.addSeparator()
		fileMenu.addAction(exitAction)
		
		#process菜单
		proMenu = menubar.addMenu('&Process')
		proMenu.addAction(showAction)
		proMenu.addSeparator()
		# proMenu.addAction(attAction)
		# proMenu.addSeparator()
		proMenu.addAction(tblAction)
		proMenu.addSeparator()
		proMenu.addAction(iptAction)

		#help菜单
		helpMenu = menubar.addMenu('&Help')
		helpMenu.addAction(aboutAction)

		"""
		----------------------------------------------------------------------
		设置工具条
		----------------------------------------------------------------------
		"""
		#toolbar
		toolbar = self.addToolBar('Standard')
		toolbar.addAction(openAction)
		toolbar.addAction(saveAction)
		toolbar.addAction(iptAction)

		#status
		self.statusBar().showMessage('Ready')

		"""
		----------------------------------------------------------------------
		设置状态栏
		----------------------------------------------------------------------
		"""
		#
		self.setGeometry(400, 100, 1000, 800)
		self.setWindowTitle('zhusongyan2015E8007061073')
		self.show()

	def initCanvas(self):
		self.fig = Figure((5.0, 4.0), dpi=100)
		self.axes = self.fig.add_subplot(111)
		self.qwidget = QtWidgets.QWidget()
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.qwidget)
		# Other GUI controls
		self.label = QLabel('Point Number:')
		self.textbox = QLineEdit()
		self.textbox.setMinimumWidth(20)
		self.textbox.editingFinished.connect(self.on_draw) #editingFinished
		self.grid_cb = QCheckBox("Show &Grid")
		self.grid_cb.setChecked(False)
		self.grid_cb.stateChanged.connect(self.on_draw)
		self.combo = QComboBox(self)
		#self.combo.AdjustToContents #不知道怎么用
		self.combo.setMinimumWidth(100)
		self.button = QPushButton('ipt name', self)
		self.button.setFocusPolicy(QtCore.Qt.NoFocus)
		self.button.clicked.connect(self.showDialog)
		# self.connect(self.button, QtCore.SIGNAL('clicked()'), self.showDialog)
		self.setFocus()
		# Layout with box sizers
		hbox = QHBoxLayout()
		hbox.addWidget(self.label)
		hbox.addWidget(self.textbox)
		hbox.addWidget(self.button)
		hbox.addWidget(self.grid_cb)
		hbox.addWidget(self.combo)
		#self.combo.move(130,232)
		# hbox.setAlignment(self.grid_cb, QtCore.Qt.AlignVCenter)
		vbox = QVBoxLayout()
		vbox.addWidget(self.canvas)
		vbox.addLayout(hbox)
		self.qwidget.setLayout(vbox)
		self.setCentralWidget(self.qwidget)
		self.textbox.setText('50')
		# self.on_draw()
		# self.keyPressEvent()
		# self.mousePressEvent()
		# self.mouseMoveEvent()

	def addcombo(self):
		self.combo.clear()
		for i in range(len(self.fld)):
			value = str(self.fld[i])
			self.combo.addItem(value)
		# self.typecomboBox.currentText() # 下拉列表combobox值
		# self.typecomboBox.currentIndex() # 下拉列表combobox的index

	def on_opendialog(self):
		filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\',
			"All files (*);;shape file (*.shp);;tiff file (*.tif)")
		# self.statusBar().showMessage('openned %s' % filename, 2000)
		if filename != '':
			self.setgate()
			return filename
		else:
			self.pop_msg('opn_err')
	
	def openshp(self):
		self.filename = self.on_opendialog()
		if self.gate == 'go':
			self.filename = str(self.filename)		
			#file = open(self.filename) # 不知道干嘛的
			shpfile = syjspatial.syjShp()
			self.shp = shpfile.read(self.filename)
			# data = file.read()
			# self.textEdit.setText(data)
			# self.textbox.setText('ok')
			reclist = self.shp["reclist"]
			self.geomtype = self.shp["geomtype"] # 判断类型决定是否画图插值，point不画但插值，polygon想反
			rec = reclist[0].keys()
			#self.textbox.setText(str(rec))
			fieldlist = self.shp["fieldlist"]
			self.fld = []
			for i in range(len(fieldlist)):
				self.fld.append(fieldlist[i]["name"]) 
			#self.textbox.setText(str(self.fld))
			self.readatt()

	def showshp(self):
		if self.gate == 'go':
			if self.geomtype == 3:
				ps = syjplotshp.plotshp()
				self.filename = str(self.filename)
				fig = plt.gcf()
				ps.draw(self.filename, fig)
			else:
				self.pop_msg('pnt_info')

	def readatt(self):
		self.addcombo()
		self.on_draw() 
	def itp(self):
		if self.gate == 'go':
			if self.geomtype == 1:
				#att = str(self.label.text())
				att = str(self.combo.currentText()) # 下拉列表combobox值
				#self.textbox.setText(unicode(att))
				itpl = syjmlearn.learn()
				orgnarr, rtrnarr = itpl.interpol(self.shp, att)
				self.zi = rtrnarr[2]
				self.geotrans = itpl.svnprmter(rtrnarr)
				reply = self.noeventmsg("Show in canvas?")
				if reply == "yes":
					self.drawincanvas(orgnarr, rtrnarr)
				else:			
					if self.iptname == '':
						itpl.matdraw(orgnarr, rtrnarr)
					else:
						itpl.matdraw(orgnarr, rtrnarr, self.iptname)
				self.isoksavetff = 'ok'
			else:
				self.pop_msg('plygn_info')

	def on_savedialog(self):
		reply = self.noeventmsg("save in tiff?")
		if reply == "no":
			path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', 'C:\\', "PNG (*.png)|*.png"))
			if path:
					self.fig.savefig(path)
					self.statusBar().showMessage('Saved to %s' % path, 2000)
		else:
			if self.isoksavetff == 'ok':
				ref = self.shp["spatialref"]
				ref=ref.ExportToPrettyWkt()
				rst = syjspatial.syjRst()
				name = str(self.dialog("tifname"))
				rst.write(self.zi, self.geotrans, ref, name)
				self.statusBar().showMessage('Saved in tiff')
				self.isoksavetff = 'no'
			else:
				self.pop_msg('sv_wrn')

	def on_about(self):
		msg = """ A demo of using PyQt with matplotlib:
		 * menubar
		 * toolbar
		 * statusbar
		 * QFileDialog
		 * QMessageBox
		 * QWidget
		 * FigureCanvas + Figure (matplotlib)
		"""
		QtGui.QMessageBox.about(self, "About", msg)

	def on_draw(self):
		num = int(self.textbox.text())		
		if self.gate == 'go':
			if self.geomtype == 1:
				geomlist = self.shp["geomlist"]
				x, y = [], []
				for i in range(len(geomlist)):
					gmt = geomlist[i]
					rec = geomlist[i] # 哪冒出来的，有啥用，我为啥要写这行？
					gmt_ = ogr.CreateGeometryFromWkt(gmt)
					xi, yi = gmt_.GetX(), gmt_.GetY()
					x.append(xi)
					y.append(yi)
				s = len(x)/num
				if s < 1:
					s = 1
					self.textbox.setText(str(len(x)))
				self.X = x[0: len(x): s]
				self.Y = y[0: len(y): s]
				self.axes.clear()
				self.axes.grid(self.grid_cb.isChecked())
				self.axes.plot(self.X, self.Y, 'ro')
				self.canvas.draw()
			else:
				self.pop_msg('plygn_info')

	def drawincanvas(self, orgnarr, rtrnarr):
		xi, yi, zi = rtrnarr[0], rtrnarr[1], rtrnarr[2]
		extent=[xi.min(), xi.max(),yi.min(), yi.max()]
		levels= np.arange(5, int(zi.max()), 5)
		self.axes.clear()
		self.axes.imshow(zi, cmap = cm.jet, interpolation='none', aspect='equal',origin='lower', extent=extent)
		CS = self.axes.contour(zi, levels, hold='on', colors='k', origin='lower', extent=extent,aspect='equal')
		plt.clabel(CS, inline=1, fmt='%d', fontsize=10)
		self.axes.set_aspect(1.0)
		self.canvas.draw()	
	
	def pop_msg(self, deci):
		if deci == 'opn_err':
			reply = QtGui.QMessageBox.question(self, 'Message',
			"Not expected input!", QtGui.QMessageBox.Yes | 
			QtGui.QMessageBox.No, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				#deci.accept() # 字符串不是事件无accept()和ignore()
				self.openshp()
			else:
				self.gate = 'stop'
				#os.system("pause") # 让其暂停运行，但是会出现未响应
				# print dir(self.pop_msg)
				#deci.ignore()
		if deci == 'pnt_info':
			reply = QtGui.QMessageBox.question(self, 'Message',
			"Not polygon cannot show", QtGui.QMessageBox.Ok)
		if deci == 'plygn_info':
			reply = QtGui.QMessageBox.question(self, 'Message',
			"type warning: polygon", QtGui.QMessageBox.Ok)
		if deci == 'sv_wrn':
			reply = QtGui.QMessageBox.question(self, 'Message',
			"image not exist", QtGui.QMessageBox.Ok)

	def setgate(self):
			self.gate = 'go'
			return self.gate

	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QtGui.QMessageBox.Yes | 
			QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
	
	def noeventmsg(self, deci):
		reply = QtGui.QMessageBox.question(self, 'Message',
			str(deci), QtGui.QMessageBox.Yes | 
			QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			return 'yes'
		else:		
			return 'no'


	def tableatt(self):
		if self.gate == 'go':
			reclist = self.shp["reclist"]
			self.fld
			tbl = syjtable.MyDialog(self.fld, reclist)
			self.statusBar().showMessage('reading attribution table')
			tbl.show()
			tbl.exec_()
		
	def showDialog(self):
		self.iptname = ''
		text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
			'Enter interpolation name:')
		if ok:
			self.iptname = (unicode(text))

	def dialog(self, deci):
		if deci == 'tifname':
			self.tifname = ''
			text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog',
				'Enter tiff name:')
			if ok:
				self.tifname = str(unicode(text)) + ".tif"
				return self.tifname
			else:
				self.tifname = "defaultname.tif"
				return self.tifname

	"""还需要很多改进才能实现选点弹出属性表
	def keyPressEvent(self, event):
		coor = []
		if event.key() == 16777249:
			click =  QMouseEvent(QEvent.MouseButtonPress, QPoint(116,87),QPoint(116,89), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
			coor = self.mousePressEvent(click)
		mode = re.compile(r'\d+')
		intcoor = mode.findall(coor)
		xi = int(intcoor[0]), yi = int(intcoor[1]) # 屏幕坐标和地理坐标转换
		buf = 10
		x, y = [], []
		x = np.arange((xi - buf), (xi + buf + 1))
		y = np.arange((yi - buf), (yi + buf + 1))
		x_ = [i for i in x if i in self.X]
		y_ = [i for i in y if i in self.Y]
		# 方法2
		# setx = set(x)
		# setX = set(self.X)
		# x_ = [setx & setX] # y坐标同理
		x, y = x_[0], y_[0] # 要随时清空lists以备下次使用
		self.atttable(x, y)
	
	# def eventFilter(self, source, event):
	# 	if event.type() == PyQt4.QtCore.QEvent.MouseMove:
	# 		pos = event.pos()
	# 		self.try_2.setText('x: %d, y: %d' % (pos.x(), pos.y())) ////可以更换其他代码
	# 	return PyQt4.QtGui.QMainWindow.eventFilter(self, source, event)
		 
	
	def mousePressEvent(self, event):
		return event.pos()
	"""
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = syjgis()
	sys.exit(app.exec_())
