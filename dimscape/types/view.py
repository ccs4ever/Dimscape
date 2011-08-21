from __future__ import generators, print_function
# -*- coding: utf-8 -*-

import os,sys

# Import Qt modules
from PyQt4 import QtGui

from dimscape.dimview import DimView
from dimscape.space import DimSpace

class ViewCell(CellSkin):
	def __init__(self, cellId, data=None, props=None):
		CellSkin.__init__(self, cellId, data, props)

	def placeChildren(self, parentView):
		view = DimView(self.data)
		gview = QtGraphicsProxyWidget(view)
		view.setGeometry(parentView.geometry())
		self.skin.setTransform(QtGui.QTransform.fromScale(0.33, 0.33), False)

