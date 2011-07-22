from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QObject, pyqtSlot

from operation import Operation
from dimscape.menus import NewCellMenu
from dimscape.types.cell import Cell

class NewCellOperation(Operation, QObject):

	def __init__(self, space, attachOrigin, msg_space):
		QObject.__init__(self)
		Operation.__init__(self, space, msg_space)
		self.attachOrigin = attachOrigin
		self.newCell = None
		self.newCellMenu = NewCellMenu(space, attachOrigin)
		self.newCellMenu.submit.connect(self.toCellInsertStage)

	def cancel(self):
		Operation.cancel(self)
		self.newCellMenu.close()

	def __del__(self):
		self.newCellMenu.submit.disconnect(self.toCellInsertStage)

	def show(self):
		self.newCellMenu.open()
		self.report("Below is a list of cell types. Move the cursor over one and press ENTER to select the type of your new cell. Or press ESC to cancel.")

	@pyqtSlot(Cell)
	def toCellInsertStage(self, cell):
		self.report("Press a navigation key to attach the new cell along that apparent dimension.")
		self.newCell = cell

	def processKeys(self, k, mods):
		if self.needsInput:
			if k == Qt.Key_Escape:
				if self.newCellMenu.isOpen():
					self.newCellMenu.close()
				if self.newCell:
					self.space.removeCell(self.newCell)
					self.newCell = None
					self.space.redraw()
				self.finish("Connection attempt cancelled.")
			if not self.newCell:
				return False
			return self.processCellInsertKeys(k, mods)
		return True
	
	def processCellInsertKeys(self, k, mods):
		linkDir = None
		if k == Qt.Key_Up:
			if mods == Qt.ControlModifier:
				linkDir = (self.space.NEG, self.space.Z)
			else:
				linkDir = (self.space.NEG, self.space.Y)
		elif k == Qt.Key_Down:
			if mods == Qt.ControlModifier:
				linkDir = (self.space.POS, self.space.Z)
			else:
				linkDir = (self.space.POS, self.space.Y)
		elif k == Qt.Key_Right:
			linkDir = (self.space.POS, self.space.X)
		elif k == Qt.Key_Left:
			linkDir = (self.space.NEG, self.space.X)
		
		if linkDir:
			direc, appDim = linkDir
			self.space.makeCellConcrete(self.newCell)
			self.space.link(self.attachOrigin, direc, appDim, 
					self.newCell)
			self.newCell.add(self.space)
			self.space.setAcursed(self.newCell)
			self.finish("New cell created successfully.")
			# we are responsible for the changes we make to scene
			self.space.redraw()
			# We consumed the key, so inform the client not to try it
			return True
		return False
