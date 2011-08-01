# -*- coding: utf-8 -*-
"""
This module provides support for reading and writing DimSpace objects to/from 
a JSON file described below:

version: 1
acursedIds: a list of acursed cell ids
allDims: every dim we or the user have created in this space
dimConfig: a list of dims in allDims bound to [X, Y, Z, ...]
cells: a list of cell dicts 
cell: { type: a string type-name registered with the type system,
	data: something the type can use
	cons: dict of cell connections of the form dimension: 
				[negward, posward]
	  - no-connection is represented by -1 in json and None in code
"""

from __future__ import generators, print_function

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

currentVersion = 1

def load(path):
	"""Loads the DimSpace JSON file specified by the 'path'.
	
	The file must exist and be readable by the user, or an IOError will 
	be thrown.
	"""
	fileObj = file(path, "r")
	return load_fromIO(fileObj)

def load_fromIO(fileLike):
	"""Loads a DimSpace from a sufficiently file-like object.

	The close() method is called on 'fileLike'. As such, the caller 
	should not expect to use the 'fileLike' object after invocation
	of this method.

	For testing purposes, a StringIO works just as well.
	"""

	spaceContents = json.load(fileLike)
	fileLike.close()
	space = {}
	space.update(loadMetadata(spaceContents))
	space["cells"] = loadCells(spaceContents)
	return space

def save(path, dimSpace):
	"""Saves the DimSpace JSON file specified by the 'path'.
	
	If the file does exist, it is overwritten. The directory must be 
	writable by the user, or an IOError will be thrown.
	"""
	fileObj = file(path, "w")
	save_toIO(fileObj, dimSpace)
	fileObj.close() # close should flush

def save_toIO(fileLike, dimSpace):
	"""Saves a DimSpace to a sufficiently file-like object.
	
	It is the responsibility of the caller to close the object, since
	StringIO for example, destroys all data on close.

	For testing purposes, a StringIO works just as well:

	>>> from StringIO import StringIO
	>>> from dimscape.space import DimSpace
	>>> sio = StringIO()
	>>> dimSpace = DimSpace()
	>>> save_toIO(sio, dimSpace)
	>>> space = load_fromIO(sio)
	>>> space["version"] == currentVersion
	True
	>>> space["dimConfig"]
	[".ds.1", ".ds.2", ".ds.3"]
	>>> space["allDims"]
	[".ds.1", ".ds.2", ".ds.3"]
	>>> space["cells"] == [ fromCell(dimSpace.getCell(0)) ]
	True
	"""
	savedSpace = {}
	saveMetadata(savedSpace, dimSpace)
	saveCells(savedSpace, dimSpace)
	json.dump(savedSpace, fileLike)

def makeCell(cid, json_cells):
	"""Create a new cell from its JSON representation.

	The returned cell's connections are not loaded yet, since the
	full cell structure must be loaded before the connections can
	be thawed.

	>>> from dimscape.types import CellTypeRegistrar
	>>> json_cells = [{"type": "text", "data":"Root", "cons": {".ds.1":[-1,0]}}]
	>>> cell = makeCell(0, json_cells)
	>>> CellTypeRegistrar.get().isRegistered("text")
	True
	>>> isinstance(cell, CellTypeRegistrar.get().fromName("text"))
	True
	>>> cell.data
	'Root'
	>>> cell.hasCons()
	False

	If a type is requested that is not registered yet, then makeCell
	returns a dummy cell that can be displayed in its place. If the
	type is subsequently registered, the dummy cell will be swapped
	out for a cell of the intended type.

	>>> from dimscape.types import SystemWarnCell, CellTypeRegistrar
	>>> json_cells = [{"type": "not-reg", "data":"Root", "cons": {".ds.1":[-1,0]}}]
	>>> cell = makeCell(0, json_cells)
	>>> CellTypeRegistrar.get().isRegistered("not-reg")
	False
	>>> isinstance(cell, SystemWarnCell)
	True
	>>> cell.data
	'Root'
	>>> cell.hasCons()
	False
	"""
	# deleted cells stored as python None, json 'null'
	cinfo = json_cells[cid]
	if not cinfo:
		return None
	if not "type" in cinfo:
		raise ValueError("A JSON cell must contain a 'type' field")
	reg = CellTypeRegistrar.get()
	tName = cinfo["type"]
	cData = cinfo["data"]
	constructor = reg.fromName(tName)
	if constructor:
		# save cons for cellizeCons later
		madeCell = constructor(cid, cData)
	else:
		madeCell = reg.registerDynamicCell(tName, cid, cData)
	return madeCell

def fromCell(cell):
	"""Return a dictionary of 'cell' values suitable for JSON 
	stringification.
	
	>>> json_cell = {"type": "text", "data":"Root", "cons":{}}
	>>> cell = makeCell(0, [ json_cell ])
	>>> json_cell == fromCell(cell)
	True
	"""
	cType = CellTypeRegistrar.get().fromType(cell)
	return { "type": cType, "data": cell.data, 
				"cons": freezeCellCons(cell) }

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

def thawCellCons(cell, json_cell):
	for (dim, direcs) in json_cell["cons"].iteritems():
		if -1 != direcs[0]:
			targetCell = cells[direcs[0]]
			# cell's None out freshly created connections
			# no need to convert -1 to None
			cell.addNegCon(dim, targetCell)
		if -1 != direcs[1]:
			targetCell = cells[direcs[1]]
			cell.addPosCon(dim, targetCell)

def loadCells(space):
	json_cells = space["cells"]
	cells = []
	# we are O(n^2) atm
	for i in xrange(len(json_cells)):
		cells.append(makeCell(i, json_cells))
	for i in xrange(len(json_cells)):
		thawCellCons(cells[i], json_cells[i])
	return cells

def loadMetadata(space):
	metaData = {}
	# Eventually version will be used for updates
	# right now we are still on 1
	for i in ["allDims", "acursedIds", "dimConfig"]:
		metaData[i] = space[i]
	# acursedId is derived from the first in acursedIds, which assumes that
	# we will only have one cursor per space for now
	# TODO: guru-meditation: cycle through cursors? concept of currentCursor?
	metaData["acursedId"] = metaData["acursedIds"][0]
	return metaData

def saveMetadata(space, memSpace):
	space["version"] = currentVersion
	for (theirs, ours) in [("knownDims", "allDims"), 
					("acursedIds", "acursedIds"), 
					("boundDims", "dimConfig")]:
		space[ours] = memSpace.__getattribute__(theirs)

def saveCells(space, memSpace):
	space["cells"] = []
	# Heard about this trick from python tricks somewhere
	cellsApp = space["cells"].append
	for c in memSpace.getCellPool():
		cellsApp(fromCell(c))

if __name__ == '__main__':
	import doctest
	doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

#
