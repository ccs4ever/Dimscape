from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QRectF
from PyQt4.QtGui import QBrush, QPen, QColor

class Cell(QObject):

	NEG = 0
	POS = 1

	def __init__(self, cellId, data, cons=None, props=None):
		QObject.__init__(self)
		self._cellId = cellId
		self._data = data
		self.cons = {}
		if cons:
			self.addCons(cons)
		self.dataInline = True
		self.transient = False
		if props and "file-backed" in props:
			self.dataInline = not props["file-backed"]

	# do this so that subclasses (Text, etc.) can propertyize at will
	@property
	def data(self):
		return self._data
	@data.setter
	def data(self, val):
		self._data = val

	def isTransient(self):
		return self.transient

	def setTransient(self, trans=None):
		if trans == None: self.transient = True
		else: self.transient = trans

	@classmethod
	def invertDir(cls, direc):
		if direc == cls.NEG: 
			return cls.POS
		return cls.NEG

	def removeCons(self, dims, repair=True):
		for dim in dims:
			self.removeCon(dim, repair)

	def removeCon(self, dim, repair=True, direction=None):
		if direction != None:
			if direction == self.NEG:
				self.removeNegCon(dim, repair)
			else:
				self.removePosCon(dim, repair)
			return
		d = self.cons.pop(dim, None)
		if d:
			neg_cell, pos_cell = d[0], d[1]
			if None != neg_cell and None != pos_cell:
				if repair:
					neg_cell.addPosCon(dim, pos_cell, replace=True)
					pos_cell.addNegCon(dim, neg_cell, replace=True)
				else:
					neg_cell.removePosCon(dim)
					pos_cell.removeNegCon(dim)
			elif None != neg_cell:
				neg_cell.removePosCon(dim)
			elif None != pos_cell:
				pos_cell.removeNegCon(dim)

	def removeNegCon(self, dim, repair=True):
		if dim in self.cons:
			d = self.cons[dim]
			if d[0] and repair:
				d[0].removePosCon(dim, repair=False)
			self.cons[dim] = (None, d[1])
			if self.cons[dim] == (None, None):
				self.cons.pop(dim)
	
	def removePosCon(self, dim, repair=True):
		if dim in self.cons:
			d = self.cons[dim]
			if d[1] and repair:
				d[1].removeNegCon(dim, repair=False)
			self.cons[dim] = (d[0], None)
			if self.cons[dim] == (None, None):
				self.cons.pop(dim)
	
	def addCons(self, dim_dict):
		for k,v in dim_dict.iteritems():
			self.addCon(k, v)

	def addCon(self, dim, direcs, replace=False):
		self.addNegCon(dim, direcs[0], replace)
		self.addPosCon(dim, direcs[1], replace)

	def addNegCon(self, dim, neg_cell, replace=False):
		d = self.cons.setdefault(dim, (None,None))
		if None != d[0] and not replace:
			d[0].addPosCon(dim, neg_cell, replace=True)
			neg_cell.addNegCon(dim, d[0], replace=True)
		self.cons[dim] = (neg_cell, d[1])

	def addPosCon(self, dim, pos_cell, replace=False):
		d = self.cons.setdefault(dim, (None,None))
		if None != d[1] and not replace:
			d[1].addNegCon(dim, pos_cell, replace=True)
			pos_cell.addPosCon(dim, d[1], replace=True)
		self.cons[dim] = (d[0], pos_cell)

	def hasCon(self, dim, direc=None):
		if dim in self.cons:
			if direc in [self.NEG, self.POS]:
				return (self.cons[dim][direc] != None)
			return True
		return False

	def isConnectedTo(self, cell):
		for (n, p) in self.cons.itervalues():
			if n == cell or p == cell:
				return True
		return False

	def unlink(self, repair=True):
		self.removeCons(list(self.cons.iterkeys()), repair)

	def hasCons(self):
		return (len(self.cons) != 0)

	def getCon(self, dim, direction):
		if self.cons[dim][direction] == None:
			return None
		return self.cons[dim][direction]

	# Property cellId
	@property
	def cellId(self):
		return self._cellId
	@cellId.setter
	def cellId(self, oth):
		if (oth < 0):
			raise ValueError("Cell id cannot be less than zero.")
		self._cellId = oth

	def execute(self):
		pass
	
	def edit(self):
		pass

class CellSkin(Cell):

	sel_brush = QBrush(QColor("cyan"))
	sel_pen = QPen(QBrush(QColor("black")), 3)
	posChanged = pyqtSignal()

	def __init__(self, cid, data, cons=None, props=None):
		Cell.__init__(self, cid, data, cons, props)
		self.skin = None
		self.old_brush = None
		self.old_pen = None
		self.loaded = False

	# Called when we can't find the attribute, probably going
	# to skin
	def __getattr__(self, name):
		if name in self.__dict__:
			return self.__dict__["name"]
		return self.__dict__['skin'].__getattribute__(name)

	def __del__(self):
		if self.skin:
			del self.skin

	def getChild(self, num=0):
		childs = self.skin.childItems()
		if self.skin and num >= 0 and \
				num < len(childs): 
			return childs[num]
		return None

	def add(self, space):
		if not self.loaded:
			if not self.skin:
				self.skin = space.scene.addRect(QRectF(), 
						QPen(QBrush(QColor("black")), 1), 
						QBrush(QColor("tan")))
				self.placeChildren(space)
				self.updateRect()
				self.skin.setZValue(2)
			else:
				space.scene.addItem(self.skin)
			self.loaded = True

	@pyqtSlot()
	def updateRect(self):
		if self.skin:
			self.skin.setRect(self.skin.childrenBoundingRect())

	def setPos(self, center):
		if self.skin:
			rect = self.skin.sceneBoundingRect()
			# setPos works in terms of topLeft, but center point is
			# easiest on the frontend, so convert
			self.skin.setPos(center[0] - rect.width()/2, 
							center[1] - rect.height()/2)
			self.posChanged.emit()

	def remove(self, scene, cached=True):
		if not self.loaded:
			return
		scene.removeItem(self.skin)
		self.loaded = False
		if not cached:
			self.beforeSkinDestroyHook()
			self.skin = None

	def beforeSkinDestroyHook(self):
		pass

	def select(self):
		# subclasses can play with these, so save them
		self.old_brush = self.skin.brush()
		self.old_pen = self.skin.pen()
		self.skin.setBrush(self.sel_brush)
		self.skin.setPen(self.sel_pen)
		self.skin.setZValue(8)

	def deselect(self):
		if self.old_brush:
			self.skin.setBrush(self.old_brush)
			self.skin.setPen(self.old_pen)
		self.skin.setZValue(2)
