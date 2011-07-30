from __future__ import generators, print_function
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject, pyqtSignal
from cell import Cell
from system import SystemWarnCell, ProgCell

class CellTypeRegistrar(QObject):

	dynamicCellsRegistered = pyqtSignal(list)

	registrar = None
	
	def __init__(self):
		QObject.__init__(self)
		self.typeToName = {}
		self.nameToType = {}
		self.nameToProps = {}
		self.cellsToRegister = {}
	
	def fromType(self, cell_or_type):
		if hasattr(cell_or_type, "typeName"):
			return cell_or_type.typeName
		if isinstance(cell_or_type, Cell):
			return self.typeToName[type(cell_or_type)]
		return self.typeToName[cell_or_type]

	def fromName(self, aName):
		return self.nameToType.get(aName, None)

	@classmethod
	def get(cls):
		if not cls.registrar:
			cls.registrar = CellTypeRegistrar()
		return cls.registrar

	def types(self):
		return self.typeToName.iterkeys()

	def names(self):
		return self.nameToType.iterkeys()

	def registrants(self):
		return self.nameToType.iteritems()

	def isRegistered(self, aIdent):
		if isinstance(aIdent, str):
			return (aIdent in self.nameToType)
		return (aIdent in self.typeToName)

	def typeInfo(self, aType):
		if hasattr(aType, "typeInfo"):
			return aType.typeInfo
		return aType.__doc__

	def register(self, aName, aType, props=None, system=False):
		# TODO: make system and user types, user types are
		# enumerable, createable by the user, system types
		# like SystemWarnCell are only used internally or by
		# kaukatcr/python extensions
		if not system:
			self.typeToName[aType] = aName
			self.nameToType[aName] = aType
			if props:
				self.nameToProps[aName] = props
		if aName in self.cellsToRegister:
			cells = self.cellsToRegister[aName]
			self.typeCastCells(cells, aType)
			self.cellsToRegister.pop(aName)

	def typeCast(self, cells, newType):
		for i in xrange(len(cells)):
			cells[i] = newType.fromCell(cell)
		self.dynamicCellsRegistered(c)
	
	def registerMany(self, iterable):
		for (n, t) in iterable:
			self.register(n, t)

	def registerDynamicCell(self, typeName, cid, data):
		dynCells = self.cellsToRegister.setdefault(typeName, [])
		t = SystemWarnCell(typeName, cid, data)
		dynCells.append(t)
		return t

