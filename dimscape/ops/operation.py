from __future__ import generators, print_function
# -*- coding: utf-8 -*-

class Operation(object):
	
	def __init__(self, space, msg_space):
		object.__init__(self)
		self.space = space
		self.msg_space = msg_space
		self.needsInput = True
	
	def show(self):
		pass

	def cancel(self):
		self.needsInput = False

	def isFinished(self):
		return (not self.needsInput)

	def finish(self, msg):
		self.report(msg)
		self.needsInput = False

	def report(self, msg):
		self.msg_space.setPlainText(msg)

	def reportError(self, err, fatal=False):
		if fatal: self.finish(err)
		else: self.report(err)




