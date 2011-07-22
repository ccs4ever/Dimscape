from __future__ import generators, print_function
# -*- coding: utf-8 -*-


from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell


class NewCellMenu(QObject):

	submit = pyqtSignal(Cell)

	def __init__(self, space, attachCell):
		QObject.__init__(self)
		self.space = space
		self.attachCell = attachCell
		self.amOpen = False
		self.transientCells = []

	def isOpen(self):
		return self.amOpen

	def _createTypedCell(self, aType):
		self.close() # acursed cell back at start
		# TODO: bad things will happen if anyone else fiddles with
		# self.cells in another thread, when kaukatcr comes in, many
		# changes will need to be made
		cell = self.space.makeTransientCell(aType)
		cell.createData(self.space.scene)
		self.submit.emit(cell)
	
	def open(self):
		reg = CellTypeRegistrar.get()
		self.amOpen = True
		self.space.pushDims()
		self.space.setDim(self.space.X, ".ds.new-cell-type-info")
		self.space.setDim(self.space.Y, ".ds.new-cell-types")
		self.space.setDim(self.space.Z, ".ds.new-cell-subtypes")
		chugCell = self.space.acursedCell
		infoChugCell = None
		
		prog = reg.fromName("prog")
		text = reg.fromName("text")

		for (n, t) in reg.registrants():
			# the tuple operator is ',' never forget
			cell = self.space.makeTransientCell(prog, 
					(n, self._createTypedCell, (t,)))
			infoCell = self.space.makeTransientCell(text, 
					reg.typeInfo(t))
			self.transientCells.extend([cell, infoCell])
			# hook up our prog cell downward
			self.space.link(chugCell, self.space.POS, self.space.Y,
					cell)
			# hook up info cell rightward
			self.space.link(cell, self.space.POS, self.space.X,
					infoCell)
			# hook up info cell downward
			if infoChugCell:
				self.space.link(infoChugCell, self.space.POS, 
						self.space.Y, infoCell)
			chugCell = cell
			infoChugCell = infoCell
		# hook up our prog cell ring rank
		self.space.link(self.transientCells[-2], self.space.POS,
				self.space.Y, self.attachCell)
		# hook up info cell ring rank
		self.space.link(self.transientCells[-1], self.space.POS,
				self.space.Y, self.transientCells[1])
		self.space.redraw()

	def close(self):
		self.amOpen = False
		self.space.setAcursed(self.attachCell)
		# Only the head cell/tail cell is linked to a concrete cell
		self.transientCells[0].unlink(repair=False)
		self.transientCells[-2].unlink(repair=False)
		self.cleanup()
		self.space.popDims()
		self.space.redraw()

	def cleanup(self):
		for cell in self.transientCells:
			cell.remove(self.space.scene, cached=False)
		self.transientCells = []

