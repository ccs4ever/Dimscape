from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QPointF

from jsonBackend import DJSONBackend
from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell
from dimscape.connection import Connection

import logging
dlog = logging.getLogger("dimscape.space")

class DimSpace(QtCore.QObject):
	NEG = Cell.NEG
	POS = Cell.POS

	X=0
	Y=1
	Z=2
	
	dimChanged = pyqtSignal(int, str)
	reg = CellTypeRegistrar.get()

	def __init__(self, scene):
		QtCore.QObject.__init__(self)
		self.scene = scene
		self.back = None
		self.connections = []
		self.reg.dynamicCellsRegistered.connect(self.updateDynamicallyTypedCells)

	@pyqtSlot(list)
	def updateDynamicallyTypedCells(self, cells):
		for c in cells:
			old_c = self.cells[c.cellId]
			if self.acursedCell == old_c:
				self.setAcursed(c)
			old_c.remove(self.space, cached=False)
			self.cells[c.cellId] = c
		self.redraw()

	def save(self):
		# self.dims always points to the latest dims
		self.back.dimConfig = self.dims
		# we maintain the acursedCell, the backends maintains the
		# acursedId, the two need only meet at save time
		self.back.acursedId = self.acursedCell.cellId
		self.back.save()
	
	def saveAs(self, path):
		filey = file(path, "w")
		self.back.saveAs(filey)
	
	def load(self, origin, path=None):
		if self.back:
			self.clear()
		if path:
			filey = file(path, "r")
			self.back = DJSONBackend(filey)
		else:
			rootCell = self.reg.fromName("text")(0, "Root")
			self.back = DJSONBackend.createNew(rootCell)
		self.acursedCell = self.back.cells[self.back.acursedId]
		# needs to update the backend's version at save time
		self.dims = self.back.dimConfig
		self.dimsStack = [ self.dims ]
		# just pointers to the backend's structures, no need to update
		self.allDims = self.back.allDims
		self.cells = self.back.cells
		self.origin = origin
		self.redraw()
		self.acursedCell.select()

	def swapDims(self):
		self.dims[0], self.dims[1] = self.dims[1], self.dims[0]
		self.dimChanged.emit(self.X, self.dims[0])
		self.dimChanged.emit(self.Y, self.dims[1])
	
	def nameDim(self, dim):
		if not dim in self.allDims:
			self.allDims.append(dim)

	def pushDims(self):
		self.dimsStack.append(list(self.dims))
		self.dims = self.dimsStack[-1]

	def popDims(self):
		if len(self.dimsStack) > 1:
			othDims = self.dimsStack.pop()
			self.dims = self.dimsStack[-1]
			for i in xrange(len(self.dims)):
				if self.dims[i] != othDims[i]:
					self.dimChanged.emit(i, self.dims[i])

	def setDim(self, appDim, boundDim):
		self.dims[appDim] = boundDim
		self.dimChanged.emit(appDim, boundDim)

	def getDim(self, appDim):
		return self.dims[appDim]

	def dirToString(self, direc):
		if direc == self.NEG: 
			return "Negward"
		return "Posward"

	def dimToString(self, appDim):
		return chr(appDim + ord('X'))

	def removeCell(self, cell):
		cell.remove(self.scene)
		cell.unlink()
		if not cell.isTransient():
			self.cells[cell.cellId] = None

	def removeLink(self, cell, appDim, direction=None):
		cell.removeCon(self.dims[appDim], repair=True, direction=direction)

	def link(self, linkFrom, moveDir, appDim, linkTo,
			exclusive=None):
		if exclusive:
			linkFrom.unlink(repair=False)
		if self.POS == moveDir:
			linkFrom.addPosCon(self.dims[appDim], linkTo)
			linkTo.addNegCon(self.dims[appDim], linkFrom)
		else:
			linkFrom.addNegCon(self.dims[appDim], linkTo)
			linkTo.addPosCon(self.dims[appDim], linkFrom)

	def makeTransientCell(self, theType, *args):
		# cellId is really only checked at save time now that
		# we use cells as connections for in memory cells
		# Since we ignore transient cells anyway, this id can
		# be any garbage value
		cell = theType(-1, *args)
		cell.setTransient()
		cell.sel_brush = QtGui.QBrush(QtGui.QColor("magenta"))
		return cell

	@staticmethod
	def makeCell(self, theType, *args):
		cell = theType(len(self.cells), *args)
		self.cells.append(cell)

	def makeCellConcrete(self, transCell):
		transCell.setTransient(False)
		transCell.cellId = len(self.cells)
		transCell.sel_brush = QtGui.QBrush(QtGui.QColor("cyan"))
		self.cells.append(transCell)

	def setAcursed(self, cell):
		self.acursedCell.deselect()
		cell.select()
		self.acursedCell = cell
		self.acursedId = cell.cellId

	def removeTransientCells(self, cell, prevCell=None, 
			moveDir=None, dimen=None):
		if cell.isTransient():
			# cannot unlink yet
			cell.remove(self.scene, cached=False)
			self.cells[cell.cellId] = None
		return True

	def chugDim(self, moveDir, appDim):
		dim = self.dims[appDim]
		if moveDir == self.NEG: direc = -1
		else: direc = 1
		print ("dims:", self.allDims)
		ind = (self.allDims.index(dim) + direc) % len(self.allDims)
		self.dims[appDim] = self.allDims[ind]
		self.dimChanged.emit(appDim, self.dims[appDim])

	def redraw(self):
		"""Call after dimensions are changed"""
		self.clear()
		self.broadcast(self.redrawCell, self.acursedCell)
		self.broadcast(self.drawCons, self.acursedCell, allCons=True)

	def fixOverlap(self, cell, prevCell=None,
			moveDir=None, dimen=None):
		if not prevCell:
			return
		self.placeRelativeTo(cell, prevCell, moveDir, dimen)

	def redrawCell(self, cell, prevCell=None,
				moveDir=None, dimen=None):
		if prevCell == None:
			cell.add(self)
			cell.setPos(self.origin)
			return
		self.placeRelativeTo(cell, prevCell, moveDir, dimen)

	def chugDraw(self):
		"""No new cells to create, regroup cells around new acursed"""
		self.broadcast(self.chugDrawCell, self.acursedCell)
		if not self.connections and len(self.cells) > 1:
			self.broadcast(self.drawCons, self.acursedCell, allCons=True)

	def chugDrawCell(self, cell, prevCell=None,
				moveDir=None, dimen=None):
		if prevCell == None:
			cell.add(self)
			cell.setPos(self.origin)
			return
		self.placeRelativeTo(cell, prevCell, moveDir, dimen)

	def removeOverlap(self, cell, prevCell=None,
				moveDir=None, dimen=None):
		if prevCell == None:
			return
		items = cell.collidingItems(QtCore.Qt.IntersectsItemBoundingRect)
		if items:
			for item in items:
				if isinstance(item, QtGui.QGraphicsSimpleTextItem):
					inter = cell.rect().intersected(item.rect())

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
		adjRect.moveTopLeft(adjCell.skin.targetPos())
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

	def colwiseTraversal(self, func, curCell, 
			allCons=False, marked=None, moveDir=None):
		if not marked:
			marked = [ curCell ]
		func(curCell, None, None, None)
		if cell.hasCon(self.dims[self.X], self.NEG) and not \
				self.POS == moveDir:
			cony = cell.getCon(self.dims[self.X], self.NEG)
			if cony not in marked:
				marked.append(cony)
				self.colwiseTraversal(func, cony, allCons, 
						marked, self.NEG)
			elif allCons:
				func(cony, cell, self.NEG, self.X)
		if cell.hasCon(self.dims[self.X], self.POS) and not \
				self.NEG == moveDir:
			cony = cell.getCon(self.dims[self.X], self.POS)
			if cony not in marked:
				marked.append(cony)
				self.colwiseTraversal(func, cony, allCons, 
						marked, self.POS)
			elif allCons:
				func(cony, cell, self.POS, self.X)
		if cell.hasCon(self.dims[self.Y], self.NEG) and not \
				self.POS == moveDir:
			cony = cell.getCon(self.dims[self.Y], self.NEG)
			if cony not in marked:
				marked.append(cony)
				self.colwiseTraversal(func, cony, allCons, 
						marked, self.NEG)
			elif allCons:
				func(cony, cell, self.NEG, self.Y)
		if cell.hasCon(self.dims[self.Y], self.POS) and not \
				self.NEG == moveDir:
			cony = cell.getCon(self.dims[self.Y], self.POS)
			if cony not in marked:
				marked.append(cony)
				self.colwiseTraversal(func, cony, allCons, 
						marked, self.POS)
			elif allCons:
				func(cony, cell, self.POS, self.Y)

	def broadcast(self, func, curCell, allCons=False):
		#if not isinstance(curCell, list):
			#curCell = [ curCell ]
		#marked = [ curCell[0] ]
		#goCons = [ (cell, None, None, None) for cell in curCell ] 
		marked = [ curCell ] 
		goCons = [ (curCell, None, None, None) ]
		for (cell, prevCell, moveDir, dimen) in goCons:
			func(cell, prevCell, moveDir, dimen)
			for i in xrange(len(self.dims)):
				if cell.hasCon(self.dims[i], self.NEG) and not \
						(i == dimen and self.POS == moveDir):
					cony = cell.getCon(self.dims[i], self.NEG)
					if cony not in marked:
						marked.append(cony)
						goCons.append((cony, cell, self.NEG, i))
					elif allCons:
						func(cony, cell, self.NEG, i)
				if cell.hasCon(self.dims[i], self.POS) and not \
						(i == dimen and self.NEG == moveDir):
					cony = cell.getCon(self.dims[i], self.POS)
					if cony not in marked:
						marked.append(cony)
						goCons.append((cony, cell, self.POS, i))
					elif allCons:
						func(cony, cell, self.POS, i)

	def executeCell(self):
		print ("executing cell:", self.acursedCell, 
				self.acursedCell.getChild())
		self.acursedCell.execute()
	
	def editCell(self):
		self.acursedCell.edit()

	def clear(self):
		# Cache our cell skins in our cells
		for c in self.cells:
			if c:
				c.remove(self.scene)
		# Clear connections from scene
		for con in self.connections:
			con.remove()
		self.connections = []

	def chug(self, direction, apparentDim):
		if apparentDim < len(self.dims) and apparentDim >= 0:
			curDim = self.dims[apparentDim]
			if self.acursedCell.hasCon(curDim, direction):
				self.setAcursed(self.acursedCell.getCon(curDim, 
								direction))
				return True
		return False

	def chugWhile(self, count, direc, dim):
		if callable(count):
			while count(self.acursedCell) and self.chug(direc, dim):
				pass
		else:
			while count >= 0 and chug(direc, dim):
				count -= 1

