from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt

from operation import Operation

class LinkOperation(Operation):

	def __init__(self, space, linkOrigin, msg_space):
		Operation.__init__(self, space, msg_space)
		self.linkOrigin = linkOrigin
		self.linkDir = None
		self.onPickDirStage = True
	
	def show(self):
		self.report("Press a navigation key to connect a cell " + \
				"to that open location.")
		
	def processKeys(self, k, mods):
		if self.needsInput:
			if self.onPickDirStage:
				return self.processPickDirKeys(k, mods)
			return self.processMarkTargetKeys(k, mods)
		return False

	def processMarkTargetKeys(self, k, mods):
		
		if k == Qt.Key_M:
			direc, appDim = self.linkDir[0], self.linkDir[1]
			markCell = self.space.acursedCell
			if markCell.hasCon(self.space.getDim(appDim)):
				if not self.linkOrigin.hasCon(self.space.getDim(appDim),
						direc):
					markDir = markCell.invertDir(direc)
					self.space.removeLink(markCell, appDim, markDir)
				else:
					self.space.removeLink(markCell, appDim)
			self.space.link(self.linkOrigin, direc, appDim, 
					markCell)
			self.space.redraw()
			self.reportSuccessfulCompletion()
			return True
		return False

	def processPickDirKeys(self, k, mods):
		
		if k == Qt.Key_Escape:
			self.finish("Connection attempt cancelled.")
		elif k == Qt.Key_Up:
			if mods == Qt.ControlModifier:
				self.linkDir = (self.space.NEG, self.space.Z)
			else:
				self.linkDir = (self.space.NEG, self.space.Y)
		elif k == Qt.Key_Down:
			if mods == Qt.ControlModifier:
				self.linkDir = (self.space.POS, self.space.Z)
			else:
				self.linkDir = (self.space.POS, self.space.Y)
		elif k == Qt.Key_Right:
			self.linkDir = (self.space.POS, self.space.X)
		elif k == Qt.Key_Left:
			self.linkDir = (self.space.NEG, self.space.X)
		
		if self.linkDir:
			direc, appDim = self.linkDir
			self.onPickDirStage = False
			self.report("Selection Stage complete! Press M to mark " + \
						"a cell for linking.")
			# We consumed the key, so inform the client not to try it
			return True
		return False

	def reportSuccessfulCompletion(self):
		strDir = self.space.dirToString(self.linkDir[0]).lower()
		strDim = self.space.dimToString(self.linkDir[1])
		tmpl8 = "Connected (%d) to (%d) %s on the %s dimension successfully."
		self.finish(tmpl8 % (self.linkOrigin.cellId, 
			self.space.acursedCell.cellId, strDir, strDim))

	def reportLinkOccupiedError(self):
		strDir = self.space.dirToString(self.linkDir[0])
		strDim = self.space.dimToString(self.linkDir[1])
		tmpl8 = "Error: The link (%s, %s) is occupied. " + \
			"You can either pick an open space or cancel with ESC." 
		self.reportError(tmpl8 % (strDir, strDim))
