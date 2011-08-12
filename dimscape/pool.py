from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyKDE4.phonon import Phonon
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal, QPointF

from threading import Lock

from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell

class CellPool(object):
	
	Root = 1
	Config = 1<<1
	Menu = 1<<2

	def __init__(self, cells=None):
		object.__init__(self)
		self.cells = cells or []
		self.cellsLock = Lock()

	@staticmethod
	def createWith(flags):
		pool = CellPool()
		if flags & CellPool.Root:
			pool.makeCell(
				CellTypeRegistrar.get().fromName("text"),
				"Root")
		return pool

	def loadCell(self, cell):
		cellsLock.acquire()
		cell.cellId = len(self.cells)
		self.cells.append(cell)
		cellsLock.release()

	def removeCell(self, cell):
		"""Removes the cell from the cell structure, repairing all 
		links."""
		cell.acquire()
		cell.unlink()
		if not cell.isTransient():
			self.cells[cell.cellId] = None
		cell.release()

	def map(self, func, *args, **kw):
		cellsLock.acquire()
		cellMap = map(lambda c: func(c, *args, **kw), 
				filter(lambda c: c != None, self.cells))
		cellsLock.release()
		return cellMap

	def foreach(self, func, *args, **kw):
		for c in self.cells:
			if c != None:
				func(c, *args, **kw)

	def removeLink(self, cell, boundDim, direction=None):
		cell.acquire()
		cell.removeCon(boundDim, repair=True, direction=direction)
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

	@staticmethod
	def makeCell(self, theType, *args, **kw):
		cellsLock.acquire()
		cell = theType(len(self.cells), *args, **kw)
		self.cells.append(cell)
		cellsLock.release()

	def makeCellConcrete(self, transCell):
		transCell.setTransient(False)
		cellsLock.acquire()
		transCell.cellId = len(self.cells)
		self.cells.append(transCell)
		cellsLock.release()
	


