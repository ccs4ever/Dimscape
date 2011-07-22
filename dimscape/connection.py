from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot, QSizeF, QRectF, QPointF
from PyQt4.QtGui import QPen, QBrush, QColor

from dimscape.types.cell import Cell

class Connection(object):

	X = 0
	Y = 1
	Z = 2

	def __init__(self, scene, linkFrom, moveDir, appDim, linkTo):
		object.__init__(self)
		self.scene = scene
		self.linkFrom = linkFrom
		self.linkFrom.posChanged.connect(self.position)
		self.linkTo = linkTo
		self.linkTo.posChanged.connect(self.position)
		self.appDim = appDim
		self.moveDir = moveDir
		self.skin = None

	def __del__(self):
		self.linkFrom.posChanged.disconnect(self.position)
		self.linkTo.posChanged.disconnect(self.position)
		if self.skin:
			del self.skin

	def __str__(self):
		return "({0}, {1})".format(self.linkFrom, self.linkTo)

	def remove(self, cached=False):
		if not self.skin:
			return
		self.scene.removeItem(self.skin)
		if not cached:
			self.skin = None

	# Case 1 X1 < X2, Case 2 X1 > X2
	def positionYRankWithDifferentX(self, path, fromRect, toRect):
		if fromRect.center().x() < toRect.center().x(): 
			s, t = fromRect, toRect
			moveDir = self.moveDir
		else: 
			s, t = toRect, fromRect
			moveDir = Cell.invertDir(self.moveDir)
		if moveDir == Cell.NEG: 
			startY, endY = s.top(), t.bottom()
			sControlY, tControlY = startY-(s.height()/2), endY+(t.height()/2)
		else: 
			startY, endY = s.bottom(), t.top()
			sControlY, tControlY = startY+(s.height()/2), endY-(t.height()/2)
		
		# Source is always left of target
		path.moveTo(s.center().x(), startY)
		sp = QPointF(s.left()+s.width(), sControlY)
		tp = QPointF(t.right()-t.width(), tControlY)
		end = QPointF(t.center().x(), endY)
		path.cubicTo(sp, tp, end)
	
	# Case 1 Y1 < Y2, Case 2 Y1 > Y2
	def positionXRankWithDifferentY(self, path, fromRect, toRect):
		if fromRect.center().y() > toRect.center().y(): 
			s, t = fromRect, toRect
			moveDir = self.moveDir
		else: 
			s, t = toRect, fromRect
			moveDir = Cell.invertDir(self.moveDir)
		sw, sh = s.width(), s.height()
		tw, th = t.width(), t.height()
		if moveDir == Cell.NEG: 
			startX, endX = s.left(), t.right()
			sControlX = startX-(sw); tControlX = endX-(tw)
		else: 
			startX, endX = s.right(), t.left()
			sControlX = startX+(sw); tControlX = endX-(tw)
		
		# Source is always below target
		path.moveTo(startX, s.center().y())
		sp = QPointF(sControlX, s.top()-(sh*2))
		tp = QPointF(tControlX, t.bottom()+(th*2))
		end = QPointF(endX, t.center().y())
		path.cubicTo(sp, tp, end)


	# Case 3 X1 == X2 
	def positionYRingRank(self, path, fromRect, toRect):
		if fromRect.center().y() < toRect.center().y(): 
			s, t = fromRect, toRect
			moveDir = self.moveDir
		else: 
			s, t = toRect, fromRect
			moveDir = Cell.invertDir(self.moveDir)
		rad = max(s.width()/3, t.width()/3)
		if moveDir == Cell.NEG:
			p = QPointF(s.center().x(), s.top())+QPointF(0, -rad)
			leftBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
			p = QPointF(s.center().x(), t.bottom())+QPointF(0, -rad)
			rightBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
		else:
			p = QPointF(s.center().x(), s.bottom())+QPointF(0, rad)
			leftBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
			p = QPointF(s.center().x(), t.top())+QPointF(0, -rad)
			rightBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
		# Source always above target
		path.moveTo(leftBox.left(), s.top())
		path.arcTo(leftBox, -180, -180)
		path.lineTo(rightBox.right(), t.bottom())
		path.arcTo(rightBox, 0, -180)
	
	# Case 3 Y1 == Y2 
	def positionXRingRank(self, path, fromRect, toRect):
		if fromRect.center().x() < toRect.center().x(): 
			s, t = fromRect, toRect
			moveDir = self.moveDir
		else: 
			s, t = toRect, fromRect
			moveDir = Cell.invertDir(self.moveDir)
		rad = max(s.height()/3, t.height()/3)
		if moveDir == Cell.NEG:
			p = QPointF(s.left(), s.center().y())+QPointF(-(rad), -(rad*2))
			leftBox = QtCore.QRectF(p, QSizeF(rad*2,rad*2))
			p = QPointF(t.right(), s.center().y())+QPointF(-(rad), -(rad*2))
			rightBox = QtCore.QRectF(p, QSizeF(rad*2,rad*2))
		else:
			p = QPointF(s.right(), s.center().y())+QPointF(-rad, -rad)
			leftBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
			p = QPointF(t.left(), s.center().y())+QPointF(-rad, -rad)
			rightBox = QtCore.QRectF(p, QSizeF(rad+rad,rad+rad))
		# Source always left of target
		path.moveTo(s.left(), s.center().y())
		path.arcTo(leftBox, -90, -180)
		path.lineTo(rightBox.topLeft())
		path.arcTo(rightBox, 90, -180)
		
	@pyqtSlot()
	def position(self):
		if not self.skin:
			self.skin = QtGui.QGraphicsPathItem()
			self.scene.addItem(self.skin)
			self.skin.setZValue(0)
			self.skin.setPen(QPen(QColor("black"), 1))
		adjRect = self.linkFrom.skin.sceneBoundingRect()
		newRect = self.linkTo.skin.sceneBoundingRect()
		path = QtGui.QPainterPath()
		if self.appDim == self.X:
			yDiff = adjRect.center().y() - newRect.center().y()
			if self.moveDir == self.linkTo.POS:
				fromX, toX = adjRect.right(), newRect.left()
				order = fromX < toX # adjCell - newCell
			else:
				fromX, toX = adjRect.left(), newRect.right()
				order = fromX > toX # newCell - adjCell
			if int(yDiff) == 0 and order: # Case 0
				path.moveTo(fromX, newRect.center().y())
				path.lineTo(toX, newRect.center().y())
			elif int(yDiff) != 0: # Case 1, 2
				self.positionXRankWithDifferentY(path, adjRect, newRect)
			else: # Case 3
				self.positionXRingRank(path, adjRect, newRect)
		elif self.appDim == self.Y:
			xDiff = adjRect.center().x() - newRect.center().x()
			if self.moveDir == self.linkFrom.NEG:
				fromY, toY = adjRect.top(), newRect.bottom()
				comp = fromY > toY
			else:
				fromY, toY = adjRect.bottom(), newRect.top()
				comp = fromY < toY
			if int(xDiff) == 0 and comp: # Case 0
				path.moveTo(newRect.center().x(), fromY)
				path.lineTo(newRect.center().x(), toY)
			elif int(xDiff) != 0: # Case 1, 2
				self.positionYRankWithDifferentX(path, adjRect, newRect)
			else: # Case 3
				self.positionYRingRank(path, adjRect, newRect)
		self.skin.setPath(path)
	
