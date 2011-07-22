from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt

from operation import Operation

class UnlinkCellOperation(Operation):

	def __init__(self, space, attachCell, msg_space, allLinks=True):
		Operation.__init__(self, space, msg_space)
		self.attachCell = attachCell
		self.allLinks = allLinks
	
	def show(self):
		if self.allLinks:
			self.report("Press a navigation key to disconnect that cell from all cells in all dimensions and remove it, or ESC to cancel.")
		else:
			self.report("Press a navigation key to disconnect that cell from the currently selected cell, or ESC to cancel.")
	
	def removeCell(self, connected_cell, aDir, appDim):
		if self.allLinks:
			self.space.removeCell(connected_cell)
		else:
			self.space.removeLink(self.attachCell, appDim, direction=aDir)
		self.space.redraw()

	def processKeys(self, k, mods):
		if self.needsInput:
			return self.processPickDirKeys(k, mods)
		return False

	def processPickDirKeys(self, k, mods):
		linkDir = None
		if k == Qt.Key_Escape:
			if self.allLinks: self.finish("Cell deletion attempt cancelled.")
			else: self.finish("Link deletion attempt cancelled.")
			return True
		elif k == Qt.Key_Up:
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
			if self.attachCell.hasCon(self.space.getDim(appDim), direc):
				cony = self.attachCell.getCon(
					self.space.getDim(appDim), direc)
				cid = cony.cellId
				self.removeCell(cony, direc, appDim)
				if self.allLinks:
					self.finish("Disconnected and removed cell {0} \
successfully.".format(cid))
				else:
					self.finish("Disconnected cell {0} successfully.".format(cid))
			else:
				self.reportLinkUnOccupiedError(linkDir)
			# We consumed the key, so inform the client not to try it
			return True
		return False

	def reportLinkUnOccupiedError(self, linkDir):
		strDir = self.space.dirToString(linkDir[0])
		strDim = self.space.dimToString(linkDir[1])
		tmpl8 = "Error: The link (%s, %s) is unoccupied. " + \
			"You can either pick an occupied space or cancel with ESC." 
		self.reportError(tmpl8 % (strDir, strDim))
