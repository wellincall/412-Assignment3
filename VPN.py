#import basic PySide design functions
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

        self.first_time = True

        #secret key variable
        self.secret_key = ""

        #number of the port passed by the user (default 8000)
        self.port = 8000

        #radio buttons
        self.client_mode = self.ui.client
        self.server_mode = self.ui.server

        ### Signals

        #event triggered when start button is clicked
        self.ui.start_btn.setEnabled(False)
        self.ui.start_btn.clicked.connect(self.start_vpn)

        #event triggered when stop button is clicked
        self.ui.stop_btn.setEnabled(False)
        self.ui.stop_btn.clicked.connect(self.stop_vpn)

        #event triggered when TCP port value is changed
        self.ui.port_box.valueChanged.connect(self.refresh_port)

        #event triggered when write button is clicked
        self.ui.write_btn.clicked.connect(self.send_text)

        #event triggered when read button is clicked
        self.ui.read_btn.clicked.connect(self.read_text)

        #event triggered when the secret key is set
        self.ui.secret_btn.clicked.connect(self.set_secret)

        #time_out trigger timer to 'rescue' data from thread
        self.timer = QtCore.QTimer(self)
        #connects timeout with read function, this way updating the read box
        self.timer.timeout.connect(self.read_text)

        #counter to see if we need to activate the timeout
        self.read_timer = 0

    ### Slots
    def start_vpn(self):
        """
        Checks the mode that is selected and than start an TcP server or waits for a connection
        """

        #disable setting buttons
        self.ui.start_btn.setEnabled(False)
        self.ui.stop_btn.setEnabled(True)

        #checks if the user ants to initialize a server or a client
        if self.client_mode.isChecked():
            #connects to the server
            print "Client mode started"
            #self.TCP_client()
            self.tcpSocket = Client(self.ui.ip_lbl.toPlainText(), self.port, str(self.secret_key))

        elif self.server_mode.isChecked():
            #starts a  server and listen to clients
            print "Server mode started"
            self.tcpServer = Server(self.port, str(self.secret_key))

    def stop_vpn(self):
        """
        Stops the VPN server/client
        """

        #enable the start button
        self.ui.start_btn.setEnabled(True)
        self.ui.stop_btn.setEnabled(False)
        self.ui.secret_btn.setEnabled(True)

        #if we are working as a server we close the server
        if self.server_mode.isChecked():
            try:
                self.tcpServer.thread.terminated()
            except:
                pass
            print "Server stopped"

        #if we are working as a client we close the connection
        if self.client_mode.isChecked():
            try:
                self.tcpSocket.thread.terminated()
            except:
                pass
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

        #if server mode is selected
        if self.server_mode.isChecked():
            self.tcpServer.thread.msg_to_write = self.ui.sent_text.toPlainText()
            self.tcpServer.thread.w_flag = True

        #if client mode is selected
        if self.client_mode.isChecked():
            self.tcpSocket.thread.msg_to_write = self.ui.sent_text.toPlainText()
            self.tcpSocket.thread.w_flag = True

    def read_text(self):
        """
        send text written in the send text box
        """

        #checks if we are read the info, if yes we stop the timer
        if self.read_timer >= 2:
            self.timer.stop()
            self.read_timer = 0
        else:
            self.timer.start(1)

        #increments counter saying how many times we entered in this function
        self.read_timer += 1

        #if we are in server mode
        if self.server_mode.isChecked():
            self.ui.received_text.setText(self.tcpServer.thread.read_msg)
            self.tcpServer.thread.r_flag = True
            self.ui.received_text.setText(self.tcpServer.thread.read_msg)

        #if we are in client mdoe
        if self.client_mode.isChecked():
            self.ui.received_text.setText(self.tcpSocket.thread.read_msg)
            self.tcpSocket.thread.r_flag = True
            self.ui.received_text.setText(self.tcpSocket.thread.read_msg)

    def set_secret(self):
        """
        Set the value of the 'Shared secret Value'
        """

        self.secret_key = self.ui.shared_text.toPlainText()

        #checks if the key has the correct length, if not does not enable start button
        if len(str(self.secret_key )) == 16:
            #enable start button and disable stop button
            self.ui.secret_btn.setEnabled(False)
            self.ui.start_btn.setEnabled(True)

#script`s main function
if __name__ == '__main__':
    #starts Qt app
    app = QtGui.QApplication(sys.argv)

    #constructs Qt interface main window
    window = MainWindow()

    #show interface
    window.show()

    #close app
    sys.exit(app.exec_())