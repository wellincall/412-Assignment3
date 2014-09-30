#import basic pyside Desgin functions
from PySide import QtCore, QtGui
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
import sys

#main windown class, where we load the desgin
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        #set up the main window to be the one from VPN_UI.ui
        QtGui.QMainWindow.__init__(self)
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)

    ### Signals
        self.ui.start_btn.clicked.connect(self.start_vpn)

    ### Slots
    def start_vpn(self):
        print "yo"


#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())