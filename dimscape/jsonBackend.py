from __future__ import generators, print_function
# -*- coding: utf-8 -*-
"""
This is the "backend" module.

It provides the DJSONBackend class, which encapsulates our physical data.
You start her up, and then query. Each change of value *should* be stored.

"""
import sys, os
from PyQt4 import QtCore, QtGui, QtSql
from PyKDE4.phonon import Phonon
from PyQt4.QtCore import pyqtSlot, pyqtSignal
try:
	import simplejson as json
except ImportError:
	try:
		import json
	except ImportError:
		print ("Either json or simplejson is required to run Dimscape", file=sys.stderr)
from dimscape.types import CellTypeRegistrar
from dimscape.types.cell import Cell

class DJSONBackend(object):

	NEG = Cell.NEG
	POS = Cell.POS

	reg = CellTypeRegistrar.get()

	def __setattr__(self, name, val):
		self.__dict__[name] = val

	def __init__(self, filey=None):
		# Only want this ever done once, since we will have a backend
		# managing each view
		object.__init__(self)
		self.filey = filey
		if self.filey:
			self.load(filey)

	@classmethod
	def makeCell(cls, cid, json_cells):
		# deleted cells stored as python None, json 'null'
		cinfo = json_cells[cid]
		if not cinfo:
			return None
		if not "type" in cinfo:
			raise ValueError("A JSON cell must contain a 'type' field")
		tName = cinfo["type"]
		cData = cinfo["data"]
		constructor = cls.reg.fromName(tName)
		if constructor:
			# save cons for cellizeCons later
			madeCell = constructor(cid, cData)
		else:
			madeCell = cls.reg.registerDynamicCell(tName, cid, cData)
		return madeCell

	@classmethod
	def fromCell(cls, cell):
		cType = cls.reg.fromType(cell)
		return { "type": cType, "data": cell.data, 
					"cons": cls.freezeCellCons(cell) }

	@staticmethod
	def createNew(rootCell):
		me = DJSONBackend()
		DJSONBackend.createDummy(me)
		me.cells.append(rootCell)
		me.acursedId = 0
		me.acursedIds.append(me.acursedId)
		return me

	@staticmethod
	def createDummy(back):
		# Eventually version will be useful for something
		back.version = 1
		for i in ["allDims", "acursedIds", "dimConfig", "cells"]:
			back.__setattr__(i, [])
		startDims = [".ds.1", ".ds.2", ".ds.3"]
		back.allDims.extend(startDims)
		back.dimConfig.extend(list(startDims))
	
	def load(self, filey):
		# I want to use 'with filey:' here, but for testing purposes
		# filey might be a StringIO, which doesn't humor me with an
		# __exit__/__enter__ method pair
		self.filey = filey 
		space = json.load(self.filey)
		self.loadMetadata(space)
		self.loadCells(space)
		filey.close()

	@staticmethod
	def freezeCellCons(cell):
		cons = {}
		for (dim, d) in cell.cons.iteritems():
			if None != d[0] and None != d[1]:
				cons.update({dim: [d[0].cellId, d[1].cellId]})
			elif None != d[0]:
				cons.update({dim: [d[0].cellId, -1]})
			else:
				cons.update({dim: [-1, d[1].cellId]})
		return cons

	def thawCellCons(self, cell, json_cell):
		for (dim, direcs) in json_cell["cons"].iteritems():
			if -1 != direcs[0]:
				targetCell = self.cells[direcs[0]]
				cell.addNegCon(dim, targetCell)
			if -1 != direcs[1]:
				targetCell = self.cells[direcs[1]]
				cell.addPosCon(dim, targetCell)

	def loadCells(self, space):
		json_cells = space["cells"]
		self.cells = []
		# we are O(n^2) atm
		for i in xrange(len(json_cells)):
			self.cells.append(self.makeCell(i, json_cells))
		for i in xrange(len(json_cells)):
			self.thawCellCons(self.cells[i], json_cells[i])

	def loadMetadata(self, space):
		# Eventually version will be useful for something
		self.version = space["version"]
		for i in ["allDims", "acursedIds", "dimConfig"]:
			self.__setattr__(i, space[i])
		self.acursedId = self.acursedIds[0]

	def saveMetadata(self, space):
		self.acursedIds[0] = self.acursedId
		space["version"] = self.version
		for i in ["allDims", "acursedIds", "dimConfig"]:
			space[i] = self.__getattribute__(i)
	
	def saveCells(self, space):
		space["cells"] = []
		# Heard about this trick from python tricks somewhere
		cellsApp = space["cells"].append
		for c in self.cells:
			cellsApp(self.fromCell(c))
	
	def saveAs(self, filey):
		"""Save everything to filey's location and direct further operations 
there, thereafter."""
		self.filey = filey
		self.save()

	def save(self):
		if self.filey:
			space = {}
			self.saveMetadata(space)
			self.saveCells(space)
			if hasattr(self.filey, 'name'):
				# We are probably a file-backed thing
				self.filey = file(self.filey.name, "w")
				json.dump(space, self.filey)
				self.filey.close() # close should flush
			else:
				# StringIO, something file-like, probably
				# for testing
				self.filey.truncate(0)
				json.dump(self.space, self.filey)	
#
