from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyKDE4.phonon import Phonon
from PyQt4.QtCore import QObject, QMutex, pyqtSlot, pyqtSignal, QPointF

from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell

class CellPool(QObject):
	
	Root = 1
	Config = 1<<1
	Menu = 1<<2

	def __init__(self, cells=None):
		QObject.__init__(self)
		self.cells = cells or []
		self.readLock = QMutex()
		self.writeLock = QMutex()

	@staticmethod
	def createWith(flags):
		pool = CellPool()
		if flags & CellPool.Root:
			root = CellTypeRegistrar.get().fromName(
					"text")(0, "Root")
			pool.loadCell(root)
		return pool

	def loadCell(self, cell):
		# We do not need the write lock here
		cell.cellId = len(self.cells)
		self.cells.append(cell)

	def getCell(self, cellId):
		"""Return either a cell (mind the rug), or None"""
		self.readLock.lock()
		cell = self.cells[cellId]
		self.readLock.unlock()
		return cell

	def removeCell(self, cell):
		"""Removes the cell from the cell structure, repairing all 
		links."""
		self.writeLock.lock()
		self.readLock.lock()
		cell.unlink()
		self.cells[cell.cellId] = None
		self.readLock.unlock()
		self.writeLock.unlock()

	@pyqtSlot(list)
	def updateDynamicallyTypedCells(self, cells):
		for c in cells:
			old_c = self.cells[c.cellId]
			if self.acursedCell == old_c:
				self.setAcursed(c)
			old_c.remove(self.space, cached=False)
			self.cells[c.cellId] = c
		self.redraw()

	def __iter__(self):
		return iter(self.cells) # temporary

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
	


