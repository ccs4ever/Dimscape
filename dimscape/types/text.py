from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot, QPointF

from cell import CellSkin

import logging
dlog = logging.getLogger("dimscape.types")

class TextCell(CellSkin):

	typeInfo = "Some text to commence with the reading. May be file backed, may be not."

	def __init__(self, cellId, text=None, cons=None, props=None, editable=True):
		CellSkin.__init__(self, cellId, text or "", cons, props)
		self.initData = self._data
		self.editable = editable

	def execute(self):
		pass

	def placeChildren(self, space):
		if self.editable: Text = QtGui.QGraphicsTextItem
		else: Text = QtGui.QGraphicsSimpleTextItem
		if self.dataInline:
			text = Text(self.initData, self.getSkin())
		elif os.path.exists(self.data):
			filey = file(self.initData, "r")
			conts = filey.read()
			filey.close()
			text = Text(conts, self.getSkin())
		self.space = space
		self.initData = None
		if self.editable:
			qt = QtCore.Qt
			text.setTextInteractionFlags(qt.TextEditorInteraction|qt.TextBrowserInteraction)
			text.document().contentsChanged.connect(self.redrawMe)

	@pyqtSlot()
	def redrawMe(self):
		if not self.initialMove:
			self.space.chugDraw()
	
	def createData(self, scene):
		# our default is all we need
		pass

	def getText(self):
		if self.editable:
			return self.getChild().toPlainText()
		return self.getChild().text()
	
	def setText(self, text):
		wid = self.getChild()
		if self.editable: wid.setPlainText(text)
		else: wid.setText(text)

	def remove(self, scene, cached=True):
		if self.loaded and not cached:
			self.initData = self.data
		CellSkin.remove(self, scene, cached)

	@property
	def data(self):
		if self.skin:
			return str(self.getText())
		return self.initData
	@data.setter
	def data(self, val):
		if self.skin:
			self.setText(val)
		else:
			self.initData = val

	@pyqtSlot()
	def edit(self):
		if self.editable:
			text = self.getChild()
			text.setFocus()

