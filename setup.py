#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

import os

gst_pc = 'pkg-config gstreamer-0.10 gstreamer-interfaces-0.10 '

#pkgconfig = os.popen(gst_pc + '--cflags')
#pkg_flags = pkgconfig.readline().strip()
#gst_inc = [ x[2:] for x in pkg_flags.split() if x[:2] == '-I']
#gst_extra = [ x for x in pkg_flags.split() if x[:2] != '-I']
#pkgconfig.close()
#pkgconfig = os.popen(gst_pc + '--libs')
#pkg_libs = pkgconfig.readline().strip()
#gst_libdirs = [ x[2:] for x in pkg_libs.split() if x[0:2] == "-L"]
#gst_libs = [ x[2:] for x in pkg_libs.split() if x[0:2] == "-l"]
#pkgconfig.close

#print (pkg_flags, gst_extra, gst_libdirs, gst_libs)

#gst_mod = Extension('dimscape.types._gst-videocell', 
		#sources=['lib/_gst-videocell.c'],
		#include_dirs=gst_inc,
		#extra_compile_args=gst_extra,
		#library_dirs=gst_libdirs,
		#libraries=gst_libs)

setup(name='Dimscape',
      version='0.1.0',
      description='Multi-dimensional database navigator and editor',
	  license="GPLv3 or later",
      author='Jonathan Kopetz',
      author_email='ccs4ever@gmail.com',
      url='',
	  #ext_modules=[gst_mod],
	  scripts=['bin/dimscape'],
	  provides=['dimscape'],
	  requires=['PyQt4', 'PyKDE4'],
      packages=['dimscape', 'dimscape.kaukatcr', 'dimscape.types', 'dimscape.menus',
		  'dimscape.ops'],
     )
