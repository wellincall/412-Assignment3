#import basic pyside Desgin functions
from PySide import QtCore, QtGui
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
import sys

#main windown class, where we load the desgin
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)

#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())