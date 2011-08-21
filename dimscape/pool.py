from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyKDE4.phonon import Phonon
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal, QPointF

from threading import Lock

from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell

class CellPool(object):
	
	def __init__(self, cells=None):
		object.__init__(self)
		self.cells = cells or {}
		self.cellsLock = Lock()
		self.validId = 0

	def getValidId(self):
		self.validId += 1
		return self.validId-1

	def replaceCell(self, cell):
		cell.acquire()
		if cell.isTransient():
			self.setTransient(False)
		old_cell = self.cells[cell.cellId]
		cellsLock.acquire()

		cellsLock.release()
		cell.release()

	def loadCell(self, theType, cid, data, *args, **kw):
		if isinstance(theType, str):
			reg = CellRegistrar.get()
			if reg.isLoaded(theType):
				constructor = reg.fromName(tName)
				cell = constructor(*args, **kw)
			elif not reg.isRegistered(theType)
				reg.register(theType, None)
				cell = reg.createWarnCell(theType, *lar, **lakw)
				self.storeDynamicCell(reg, theType, cell)
			else:
				self.storeDynamicCell(reg, theType, cell)
		else:
			cell = theType(cid, *args, **kw)
		cellsLock.acquire()
		self.cells[cell.cellId] = cell
		cellsLock.release()

	def storeDynamicCell(self, reg, typeName, cell):


	def getCell(self, cellId):
		return self.cells[cellId]

	def removeCell(self, cell):
		"""Removes the cell from the cell structure, repairing all 
		links."""
		cell.acquire()
		cell.unlink()
		if not cell.isTransient():
			self.cells[cell.cellId] = None
		cell.release()

	def map(self, func, *args, **kw):
		def alter_cell(c, *args, **kw):
			c.acquire()
			func(c, *args, **kw)
			c.release()
		cellMap = map(lambda c: alter_cell(c, *args, **kw), 
				self.cells.itervalues())
		return cellMap

	def foreach(self, func, *args, **kw):
		for c in self.cells.itervalues():
			c.acquire()
			func(c, *args, **kw)
			c.release()

	def removeLink(self, cell, boundDim, direction=None):
		cell.acquire()
		toCell = cell.getCon(boundDim, direction)
		toCell.acquire()
		cell.removeCon(boundDim, repair=True, direction=direction)
		toCell.release()
		cell.release()

	def link(self, linkFrom, moveDir, boundDim, linkTo,
			exclusive=None):
		linkFrom.acquire()
		linkTo.acquire()
		if exclusive:
			linkFrom.unlink(repair=False)
		if self.POS == moveDir:
			linkFrom.addPosCon(boundDim, linkTo)
			linkTo.addNegCon(boundDim, linkFrom)
		else:
			linkFrom.addNegCon(boundDim, linkTo)
			linkTo.addPosCon(boundDim, linkFrom)
		linkTo.release()
		linkFrom.release()

	def makeTransientCell(self, theType, *args, **kw):
		# cellId is really only checked at save time now that
		# we use cells as connections for in memory cells
		# Since we ignore transient cells anyway, this id can
		# be any garbage value
		cell = theType(-1, *args, **kw)
		cell.setTransient()
		return cell

	def makeCell(self, theType, *args, **kw):
		cellsLock.acquire()
		cell = theType(self.getValidId(), *args, **kw)
		self.cells[cell.cellId] = cell
		cellsLock.release()

	def makeCellConcrete(self, transCell):
		transCell.setTransient(False)
		cellsLock.acquire()
		transCell.cellId = self.getValidId()
		self.cells[transCell.cellId] = transCell
		cellsLock.release()
	


