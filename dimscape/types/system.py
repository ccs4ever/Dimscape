from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QColor

from text import TextCell

class SystemWarnCell(TextCell):

	def __init__(self, typeName, cid, data, props=None):
		msg = "\'" + typeName + "\'" + " has not be registered with the type system."
		TextCell.__init__(self, cid, msg, props, editable=False)
		self.typeName = typeName
		self._data = data

	def placeChildren(self, space):
		TextCell.placeChildren(self, space)
		self.getChild().setBrush(QColor("red"))

	@property
	def data(self):
		return self._data


class ProgCell(TextCell):
	
	typeInfo = "An in to executable code."

	def __init__(self, cellId, data=None, props=None):
		msg = (data and data[0]) or ""
		TextCell.__init__(self, cellId, msg, props, editable=False)
		self._data = data
		self.execute = None
 
	def placeChildren(self, space):
		TextCell.placeChildren(self, space)
		msg, fun, args = self.data
		if callable(fun):
			self.execute = lambda: fun(*args)
		else:
			self.execute = lambda: 0

	@property
	def data(self):
		return self._data
	@data.setter
	def data(self, val):
		if len(val) != 3 or not callable(val[1]):
			raise ValueError("Cannot create prog cell with invalid parameter: {0}".format(val))
		super(TextCell, self).data = val[0]
		self._data = val

	def createData(self):
		# our default is all we need
		pass

	@pyqtSlot()
	def edit(self):
		text = self.getChild()
		text.setFocus()

