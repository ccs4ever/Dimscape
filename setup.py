#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension


setup(name='Dimscape',
      version='0.1.0',
      description='Multi-dimensional database navigator and editor',
	  license="GPLv3 or later",
      author='Jonathan Kopetz',
      author_email='ccs4ever@gmail.com',
      url='',
	  scripts=['bin/dimscape'],
	  provides=['dimscape'],
	  requires=['PyQt4'],
      packages=['dimscape', 'dimscape.kaukatcr', 'dimscape.types', 'dimscape.menus',
		  'dimscape.ops'],
     )
