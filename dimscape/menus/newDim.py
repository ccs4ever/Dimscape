from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from dimscape.types import CellTypeRegistrar

class NewDimMenu(object):

	def __init__(self, space, attachCell, submitCallback):
		object.__init__(self)
		self.space = space
		self.attachCell = attachCell
		self.amOpen = False
		self.entryCell = None
		self.submitCell = None
		self.submitCallback = submitCallback

	def isOpen(self):
		return self.amOpen

	def createDim(self):
		dim = str(self.entryCell.getText())
		self.close() 
		self.submitCallback(dim)
	
	def open(self):
		reg = CellTypeRegistrar.get()
		self.amOpen = True
		self.space.pushDims()
		self.space.setDim(self.space.X, ".ds.submit")
		self.space.setDim(self.space.Y, ".ds.entry")
		self.space.setDim(self.space.Z, ".ds.nil")

		self.entryCell = self.space.makeTransientCell(reg.fromName("text"), 
					"")
		self.submitCell = self.space.makeTransientCell(reg.fromName("prog"),
				("Submit", self.createDim, ()))
		# link up entry cell
		self.space.link(self.attachCell, self.space.POS, 
				self.space.Y, self.entryCell)
		# link up submit button
		self.space.link(self.entryCell, self.space.POS,
				self.space.X, self.submitCell)
		# We want return to submit, just like a normal text entry
		self.entryCell.execute = self.createDim
		self.space.redraw()

	def close(self):
		self.amOpen = False
		self.space.setAcursed(self.attachCell)
		self.entryCell.unlink(repair=False)
		self.cleanup()
		self.space.popDims()
		self.space.redraw()

	def cleanup(self):
		# Since an unlink isn't nescessary and these are transient cells
		# we don't need to go through self.space.removeCell
		for cell in [self.entryCell, self.submitCell]:
			cell.remove(self.space.scene, cached=False)
