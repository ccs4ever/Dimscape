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

	def __init__(self, cellId, path=None, cons=None, props=None):
		CellSkin.__init__(self, cellId, path or "", cons)
		self.canSeek = False
 
 	@QtCore.pyqtSlot(int)
	def buffer_change(self, percent):
		print ("Buffer percent:", percent)
    
  	@QtCore.pyqtSlot(int, int)
	def state_change(self, newState, oldState):
		print (oldState, "->", newState)
		vid = self.getChild().widget()
		print ("time:", vid.currentTime())
		if self.canSeek and newState == Phonon.StoppedState:
			self.canSeek = False
			vid.play()
			vid.seek(1000)
			vid.pause()
			print ("time after seek:", vid.currentTime())

	@QtCore.pyqtSlot(bool)
	def seek_change(self, canSeek):
		print ("Can seek?", canSeek)
		self.canSeek = canSeek
	
	@pyqtSlot()
	def finish(self):
		self.getChild().widget().stop()

	def placeChildren(self, space):
		# TODO: This ignores dataInline atm
		# videos should be out-of-line by default
		if os.path.exists(self.data):
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
		else:
			text = QtGui.QGraphicsSimpleTextItem(self.skin)
			text.setText("\'" + self.data + "\'" + " could not be found.")
			text.setBrush(QColor("red"))

	@pyqtSlot()
	def execute(self):
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
