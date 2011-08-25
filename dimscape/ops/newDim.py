from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt

from operation import Operation
from dimscape.menus import NewDimMenu
from dimscape.types.cell import Cell

class NewDimOperation(Operation):
	
	def __init__(self, space, attachOrigin, msg_space):
		Operation.__init__(self, space, msg_space)
		self.attachOrigin = attachOrigin
		self.newDim = None
		self.newDimMenu = NewDimMenu(space, attachOrigin,
				self.toDimInsertStage)

	def cancel(self):
		Operation.cancel(self)
		self.newDimMenu.close()

	def __del__(self):
		self.newDimMenu.submit.disconnect(self.toDimInsertStage)

	def show(self):
		self.newDimMenu.open()
		self.report("Below is a space to enter the name of a new dimension. Enter a name and press ENTER to create that dimension. Or press ESC to cancel.")

	def toDimInsertStage(self, dim):
		self.newDimMenu.close()
		if self.space.nameDim(dim):
			self.finish("New dim: '{0}' created successfully.".format(dim))
		else:
			self.finish("Dim '{0}' already exists.".format(dim))

	def processKeys(self, k, mods):
		if self.needsInput:
			if k == Qt.Key_Escape:
				if self.newDimMenu.isOpen():
					self.newDimMenu.close()
				self.finish("New dimension creation cancelled.")
				return True
		return False
