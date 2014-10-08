#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
from TCP_Server import Server
from TCP_Client import Client
import sys
SIZEOF_UINT16 = 2

#TCP functions at:
#https://qt.gitorious.org/pyside/pyside-examples/source/b5c22fb55c33e1fe2b348e6ea379a3cb7df841e0:examples/network
#http://stackoverflow.com/questions/9355511/pyqt-qtcpserver-how-to-return-data-to-multiple-clients

class MainWindow(QtGui.QMainWindow):
    """
    Main window class, where we load the design
    """
    def __init__(self):
        #set up the main window to be the one from VPN_UI.ui
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #initialization of TCP related variables
        self.tcpServer = None
        self.tcpSocket = None

        #secret key variable
        self.secret_key = ""

        #number of the port passed by the user (default 8000)
        self.port = 8000

        #radio buttons
        self.client_mode = self.ui.client
        self.server_mode = self.ui.server

        ### Signals

        #event triggered when start button is clicked
        self.ui.start_btn.clicked.connect(self.start_vpn)

        #event triggered when stop button is clicked
        self.ui.stop_btn.clicked.connect(self.stop_vpn)

        #event triggered when TCP port value is changed
        self.ui.port_box.valueChanged.connect(self.refresh_port)

        #event triggered when write button is clicked
        self.ui.write_btn.clicked.connect(self.send_text)

        #event triggered when read button is clicked
        self.ui.read_btn.clicked.connect(self.read_text)

        #event triggered when the secret key is set
        self.ui.secret_btn.clicked.connect(self.set_secret)

    ### Slots
    def start_vpn(self):
        """
        Checks the mode that is selected and than start an TcP server or waits for a connection
        """

        #disable setting buttons
        self.ui.start_btn.setEnabled(False)

        #checks if the user ants to initialize a server or a client
        if self.client_mode.isChecked():
            #connects to the server
            print "Client mode started"
            #self.TCP_client()
            self.tcpSocket = Client("Localhost", self.port)
        elif self.server_mode.isChecked():
            #starts a  server and listen to clients
            print "Server mode started"
            self.tcpServer = Server(self.port)

    def stop_vpn(self):
        """
        Stops the VPN server/client
        """
        #enable the start button
        self.ui.start_btn.setEnabled(True)

        #if we are working as a server we close the server
        if self.server_mode.isChecked():
            self.tcpServer.close()
            print "Server stopped"

        #if we are working as a client we close the connection
        if self.client_mode.isChecked():
            self.tcpServer.thread.client_connection.close()
            print "Client disconnected"

    def refresh_port(self):
        """
        Updates the value of the TCP port that the user wants to use
        """

        self.port = self.ui.port_box.value()

    def send_text(self):
        """
        send text written in the send text box
        """

        if self.server_mode.isChecked():
            self.tcpServer.server_send_message(self.ui.sent_text.toPlainText())

        #if we are working as a client
        if self.client_mode.isChecked():
            self.tcpSocket.client_send_message(self.ui.sent_text.toPlainText())


        print "message sent"

    def read_text(self):
        """
        send text written in the send text box
        """

        if self.server_mode.isChecked():
            self.ui.received_text.setText(self.tcpServer.thread.textFromClient)

        #if we are working as a client
        if self.client_mode.isChecked():
            self.tcpSocket.read_from_server()
            self.ui.received_text.setText(self.tcpSocket.textFromServer)



    def set_secret(self):
        """
        Set the value of the 'Shared secret Value'
        """

        self.secret_key = self.ui.shared_text.toPlainText()
        print self.secret_key

    def authenticate(self):
        """
        authenticate the message to see if we are receiving the data from the correct host
        """

        #Receive R1 + Alice


        #Send Challenge


        #Receive Challenge response
        pass


#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())