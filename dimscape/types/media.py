from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QColor
try:
	# I hear KDE's version of Phonon is more recent
	# use it if available
	from PyKDE4.phonon import Phonon
except ImportError:
	from PyQt4.phonon import Phonon

import os

from cell import CellSkin

class VideoCell(CellSkin):

	typeInfo = "A video for to be playing which is backed by a file on your filesystem."

	initialSeekTime = 1000

	def __init__(self, cellId, path=None, props=None):
		CellSkin.__init__(self, cellId, path or "")
		self.canSeek = False
		self.imageReplaced = False
		self.fileNotFound = False
		self.sought = False
		self.posterImage = None
 
 	@QtCore.pyqtSlot(int)
	def buffer_change(self, percent):
		print ("Buffer percent:", percent)
    
  	@QtCore.pyqtSlot(int, int)
	def state_change(self, newState, oldState):
		print (oldState, "->", newState)
		if self.canSeek and not self.sought and newState == Phonon.PausedState:
			vid = self.getChild().widget()
			# Do a one off seek to get us past the black
			self.sought = True
			# We need to get the ticks going
			vid.play()
			vid.seek(self.initialSeekTime)
			print ("time after seek:", vid.currentTime())

	@QtCore.pyqtSlot(bool)
	def seek_change(self, canSeek):
		print ("Can seek?", canSeek)
		self.canSeek = canSeek
	
	@pyqtSlot()
	def finish(self):
		print ("called finished")
		self.replaceWithPosterImage()

	@pyqtSlot(int)
	def ticked(self):
		wid = self.getChild().widget()
		if wid.currentTime() >= 0:
			# Our seek finally came through
			# Cancel tick
			wid.mediaObject().tick.disconnect(self.ticked)
			wid.mediaObject().setTickInterval(0)
			wid.pause()
			self.replaceWithPosterImage()

	def replaceWithPosterImage(self):
		print ("replacing with poster image")
		gwid = self.getChild()
		scene = gwid.scene()
		scene.removeItem(gwid)
		if not self.posterImage:
			pix = QtGui.QPixmap.grabWidget(gwid.widget())
			self.posterImage = QtGui.QGraphicsPixmapItem(pix, self.skin)
		else:
			self.posterImage.setParentItem(self.skin)
		self.imageReplaced = True

	def removePosterImage(self):
		print ("removing poster image")
		gpix = self.getChild()
		scene = gpix.scene()
		scene.removeItem(gpix)
		self.loadVideo()
		self.imageReplaced = False

	def placeChildren(self, space):
		# TODO: This ignores dataInline atm
		# videos should be out-of-line by default
		if os.path.exists(self.data):
			vid = self.loadVideo()
			mobj = vid.mediaObject()
			mobj.setTickInterval(100)
			mobj.tick.connect(self.ticked)
		else:
			text = QtGui.QGraphicsSimpleTextItem(self.skin)
			text.setText("\'" + self.data + "\'" + " could not be found.")
			text.setBrush(QColor("red"))
			self.fileNotFound = True

	def loadVideo(self):
		vid = Phonon.VideoPlayer(Phonon.VideoCategory)
		mobj = vid.mediaObject()
		mobj.stateChanged.connect(self.state_change)
		mobj.bufferStatus.connect(self.buffer_change)
		mobj.seekableChanged.connect(self.seek_change)
		vid.load(Phonon.MediaSource(self.data))	
		vid.resize(QtCore.QSize(320, 240))
		vid.finished.connect(self.finish)
		proxy_wid = QtGui.QGraphicsProxyWidget(self.skin)
		proxy_wid.setWidget(vid)
		vid.pause()
		return vid

	@pyqtSlot()
	def execute(self):
		if not self.fileNotFound:
			if self.imageReplaced:
				self.removePosterImage()
			vid = self.getChild().widget()
			if vid.isPlaying(): 
				vid.pause()
			else: 
				vid.play()

	@pyqtSlot()
	def edit(self):
		pass

	def createData(self, scene):
		main = scene.views()[0]
		self.data = QtGui.QFileDialog.getOpenFileName(main, 
				QtCore.QObject().tr("Open Video File"),
				QtCore.QDir.homePath())
		if self.data:
			self.data = str(self.data)


class AudioCell(CellSkin):
	pass

class ImageCell(CellSkin):
	pass
