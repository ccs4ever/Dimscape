from __future__ import generators, print_function
# -*- coding: utf-8 -*-

import os,sys

# Import Qt modules
from PyQt4 import QtGui

class DimView(QtGui.QGraphicsView):
	def __init__(self, parent=None):
		QtGui.QGraphicsView.__init__(self, parent)
	
	def keyPressEvent(self, evt):
		QtGui.QWidget.keyPressEvent(self, evt)
