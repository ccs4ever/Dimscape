from pyffmpeg import *
from PyQt4 import QtGui, QtCore
import numpy
import sys, os
from windowUI import Ui_MainWindow 

class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        # This is always the same
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
	self.cells = []

        self.scene=QtGui.QGraphicsScene()
        self.scene.setSceneRect(0,0,1024,768)
        self.ui.dimscapeView.setScene(self.scene)

app = QtGui.QApplication(sys.argv)

window = Main()
window.show()

mp = FFMpegReader()
mp.open("../zzChemDemo-Moore.mov")
mp.seek_to(10)
frame = mp.get_current_frame()
#print (frame)
height = len(frame[0][2])
width = len(frame[0][2][0])
#print (width, height)
fbuf = numpy.core.multiarray.getbuffer(frame[0][2])
img = QtGui.QImage(fbuf, width, height, width*3, QtGui.QImage.Format_RGB888)
#print (img, img.width(), img.height())
pix = QtGui.QPixmap.fromImage(img)
#print (pix)
gpix = window.scene.addPixmap(pix)
window.ui.dimscapeView.centerOn(gpix)
sys.exit(app.exec_())
