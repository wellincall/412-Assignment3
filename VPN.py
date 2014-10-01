#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
import sys
import socket


class MainWindow(QtGui.QMainWindow):
    """
    Main window class, where we load the design
    """
    def __init__(self):
        #set up the main window to be the one from VPN_UI.ui
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.tcpServer = None
        self.tcpSocket = None

        #number of the port passed by the user
        self.port = 8000

        #radio buttons
        self.client_mode = self.ui.client
        self.server_mode = self.ui.server


    ### Signals
        self.ui.start_btn.clicked.connect(self.start_vpn)
        self.ui.stop_btn.clicked.connect(self.stop_vpn)
        #event triggered when TCP port value is changed
        self.ui.port_box.valueChanged.connect(self.refresh_port)

    ### Slots
    def start_vpn(self):
        """
        Checks the mode that is selected and than start an TcP server or waits for a connection
        """

        #disable setting buttons
        self.ui.start_btn.setEnabled(False)

        #http://www.binarytides.com/python-socket-server-code-example/ sample codes of TCP
        if self.client_mode.isChecked():
            #connects to the server
            print "Client mode started"
            self.TCP_client()
        elif self.server_mode.isChecked():
            #starts a  server and listen
            print "Server mode started"
            self.TCP_server()

    def stop_vpn(self):
        """
        Stops the VPN server/client
        """
        self.ui.start_btn.setEnabled(True)
        if self.server_mode.isChecked():
            self.tcpServer.close()

    def refresh_port(self):
        """
        Updates the value of the TCP port that the user wants to use
        """
        self.port = self.ui.port_box.value()



    #TCP functions
    def TCP_client(self):
        """
        Connects to a server according to the port passed by the user
        """
        self.tcpSocket = QtNetwork.QTcpSocket(self)
        self.tcpSocket.abort()
        self.tcpSocket.connectToHost( "Localhost", self.port)

    def TCP_server(self):
        """
        Starts a TCP server at the port passed by the user
        """

        self.tcpServer = QtNetwork.QTcpServer(self)


        if not self.tcpServer.listen(QtNetwork.QHostAddress("127.0.0.1"), self.port):
            QtGui.QMessageBox.critical(self, self.tr("Fortune Server"),
                                       self.tr("Unable to start the server: %(error)s.")
                                       % {'error': self.tcpServer.errorString()})
            self.close()
            return

        print self.tcpServer.serverPort()

        self.tcpServer.newConnection.connect(self.accept_connection)

    def accept_connection(self):
        print "Client received"




#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())