from __future__ import generators, print_function
# -*- coding: utf-8 -*-

import os,sys

# Import Qt modules
from PyQt4 import QtGui

class DimView(QtGui.QGraphicsView):
	
	def __init__(self, scene, space=None, parent=None):
		QtGui.QGraphicsView.__init__(self, scene, parent)
		if space: self.space = space
		else: self.space = DimSpace()
		CellTypeRegistrar.get().dynamicCellsRegistered.connect(
				self.updateDynamicallyTypedCells)
	
	@pyqtSlot(list)
	def updateDynamicallyTypedCells(self, cells):
		for c in cells:
			old_c = self.space.getCell(c.cellId)
			if self.space.acursedCell == old_c:
				self.space.setAcursed(c)
			old_c.remove(self.scene, cached=False)
			self.cells[c.cellId] = c
		self.redraw()
	
	def keyPressEvent(self, evt):
		QtGui.QWidget.keyPressEvent(self, evt)
	
	def redraw(self, clear=True):
		if clear:
			self.clear()
		self.broadcast(self.redrawCell, self.acursedCell)
		if not (clear and self.connections):
			self.broadcast(self.drawCons, self.acursedCell, allCons=True)

	def redrawCell(self, cell, prevCell=None,
				moveDir=None, dimen=None):
		if prevCell == None:
			cell.add(self)
			cell.setPos(self.origin)
			return
		self.placeRelativeTo(cell, prevCell, moveDir, dimen)

	def drawCons(self, cell, prevCell=None,
				moveDir=None, dimen=None):
		if prevCell == None:
			return
		conMap = map(lambda x: (x.linkTo, x.linkFrom), self.connections) 
		if (prevCell, cell) in conMap:
			return
		con = Connection(self.scene, prevCell, moveDir, dimen, cell)
		con.position()
		self.connections.append(con)

	def placeRelativeTo(self, cell, adjCell, moveDir, dimen):
		# TODO: Z will crash and burn atm
		cell.add(self)
		if adjCell == self.acursedCell:
			cell.setZValue(6)
		elif adjCell.isConnectedTo(self.acursedCell):
			cell.setZValue(4)
		newRect = QtCore.QRectF(cell.skin.sceneBoundingRect())
		adjRect = adjCell.skin.sceneBoundingRect()
		if dimen == self.X:
			if moveDir == self.NEG:
				newRect.moveCenter(QPointF(
					adjRect.left() - 10 - newRect.width()/2, 
					adjRect.center().y()))
			else:
				newRect.moveCenter(QPointF(
					adjRect.right() + 10 + newRect.width()/2, 
					adjRect.center().y()))
		elif dimen == self.Y:
			if moveDir == self.NEG:
				newRect.moveCenter(QPointF(
					adjRect.center().x(), 
					adjRect.top() - 10 - newRect.height()/2))
			else:
				newRect.moveCenter(QPointF(
					adjRect.center().x(), 
					adjRect.bottom() + 10 + newRect.height()/2))
		center = (newRect.center().x(), newRect.center().y())
		cell.setPos(center)
		return True
	
	def clear(self):
		# Cache our cell skins in our cells
		for c in self.cells:
			if c:
				c.remove(self.scene)
		# Clear connections from scene
		for con in self.connections:
			con.remove()
		self.connections = []
