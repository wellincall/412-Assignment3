#import basic pyside Desgin functions
from PySide import QtCore, QtGui
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
import sys
import socket

#main windown class, where we load the desgin
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        #set up the main window to be the one from VPN_UI.ui
        QtGui.QMainWindow.__init__(self)
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)

        #radio buttons
        self.client_mode = self.ui.client
        self.server_mode = self.ui.server

    ### Signals
        self.ui.start_btn.clicked.connect(self.start_vpn)

    ### Slots
    def start_vpn(self):
        """
        Checks the mode that is selected and than start an TcP server or waits for a connection
        """

        #http://www.binarytides.com/python-socket-server-code-example/ sample codes of TCP
        if self.client_mode.isChecked():
            #connects to the server
            print "Client mode started"
        elif self.server_mode.isChecked():
            #starts a  server and listen
            print "Server mode started"





#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())