from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyKDE4.phonon import Phonon
from PyQt4.QtCore import pyqtSlot, pyqtSignal, QPointF

import jsonBackend
from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell
from dimscape.pool import CellPool

class DimSpace(QtCore.QObject):
	NEG = Cell.NEG
	POS = Cell.POS

	X=0
	Y=1
	Z=2
	
	dimChanged = pyqtSignal(int, str)
	reg = CellTypeRegistrar.get()

	def __init__(self, path=None):
		QtCore.QObject.__init__(self)
		self.load(path)

	def load(self, path=None):
		if path:
			back = jsonBackend.load(path)
			self.pool = CellPool(back["cells"])
			self.initSpace(back["acursedIds"],
					self.pool.getCell(back["acursedId"]),
					back["boundDims"],
					back["knownDims"])
		else:
			self.pool = CellPool.createWith(CellPool.Root)
			self.initSpace([ 0 ], self.pool.getCell(0),
					[".ds.1", ".ds.2", ".ds.3"],
					[".ds.1", ".ds.2", ".ds.3"])
		self.currentFile = path

	def getCellPool(self):
		return iter(self.pool)

	def initSpace(self, ids, acur, bound, known):
		self.acursedCell = acur
		self.acursedIds = ids
		self.acursedId = ids[0]
		self.boundDims = bound
		self.dimsStack = [ bound ]
		self.knownDims = known

	def save(self):
		self.saveAs(self.currentFile)
	
	def saveAs(self, path):
		cellId = self.acursedCell.cellId
		# bail if we are transient
		if cellId == -1: cellId = self.pool.getCell(0).cellId
		jsonBackend.saveAs(path, cellId, self.pool.getCells())
	
	def swapDims(self):
		self.dims[0], self.dims[1] = self.dims[1], self.dims[0]
		self.dimChanged.emit(self.X, self.dims[0])
		self.dimChanged.emit(self.Y, self.dims[1])
		
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

	def setAcursed(self, cell):
		self.acursedCell.deselect()
		cell.select()
		self.acursedCell = cell
		self.acursedId = cell.cellId

	def chugDim(self, moveDir, appDim):
		dim = self.dims[appDim]
		if moveDir == self.NEG: direc = -1
		else: direc = 1
		print ("dims:", self.allDims)
		ind = (self.allDims.index(dim) + direc) % len(self.allDims)
		self.dims[appDim] = self.allDims[ind]
		self.dimChanged.emit(appDim, self.dims[appDim])

	def broadcast(self, func, curCell, allCons=False):
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
		self.acursedCell.execute()
	
	def editCell(self):
		self.acursedCell.edit()

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

