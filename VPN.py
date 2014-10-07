#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
#imports VPN ui class converted with pyside-uic
from VPN_UI import Ui_MainWindow
import sys
SIZEOF_UINT16 = 2

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
        self.client_connection = None
        self.request = None
        self.thread = None

        #initializates the message to be send with a string written Ack
        self.msg_to_send = QtGui.QLineEdit("Ack")

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
            self.TCP_client()
        elif self.server_mode.isChecked():
            #starts a  server and listen to clients
            print "Server mode started"
            self.TCP_server()

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
            self.client_connection.close()
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

        self.client_send_message(self.ui.sent_text.toPlainText())

    def read_text(self):
        """
        send text written in the send text box
        """

        print self.thread.textFromClient
        self.ui.received_text.setText(self.thread.textFromClient)

    ###TCP functions
    #TCP functions at:
    #https://qt.gitorious.org/pyside/pyside-examples/source/b5c22fb55c33e1fe2b348e6ea379a3cb7df841e0:examples/network
    #http://stackoverflow.com/questions/9355511/pyqt-qtcpserver-how-to-return-data-to-multiple-clients

    ### TCP client commands
    def TCP_client(self):
        """
        Connects to a server according to the port passed by the user
        """

        #create a new socket
        self.tcpSocket = QtNetwork.QTcpSocket(self)
        self.tcpSocket.abort()

        #connects the socket with the server socket established by the user
        self.tcpSocket.connectToHost("Localhost", self.port)

        #client connected to the server
        print "client connected"

        #send message to server saying the he connected
        self.client_send_message("Sent from client: client connected")

    def client_send_message(self, msg):
        """
        Send passed message from the client to the server
        """

        self.msg_to_send.setText(msg)
        self.request = QtCore.QByteArray()
        stream = QtCore.QDataStream(self.request, QtCore.QIODevice.WriteOnly)
        stream.setVersion(QtCore.QDataStream.Qt_4_2)
        stream.writeUInt16(0)
        stream.writeQString(self.msg_to_send.text())
        stream.device().seek(0)
        stream.writeUInt16(self.request.size() - SIZEOF_UINT16)
        self.tcpSocket.write(self.request)
        self.nextBlockSize = 0
        self.request = None
        self.msg_to_send.setText("")

    ###TCP Server commands
    def TCP_server(self):
        """
        Starts a TCP server at the port passed by the user
        """

        #creates a new Tcp server
        self.tcpServer = QtNetwork.QTcpServer(self)

        #checks if the server is listenin to the socket established by the user, otherwise triggers an error an close
        #the server
        if not self.tcpServer.listen(QtNetwork.QHostAddress("127.0.0.1"), self.port):
            QtGui.QMessageBox.critical(self, self.tr("Fortune Server"),
                                       self.tr("Unable to start the server: %(error)s.")
                                       % {'error': self.tcpServer.errorString()})
            #closes the server in case of an error
            self.close()
            return
        # print self.tcpServer.serverPort()

        #in case of a new client connection we trigger an event and go to accept_connection function
        self.tcpServer.newConnection.connect(self.accept_connection)

    def accept_connection(self):
        """
        Treats the event of receiving a client
        """

        print "Client received"
        #gets the client socket info
        self.thread = Thread(self, self.tcpServer.nextPendingConnection())
        self.thread.start()



class Thread(QtCore.QThread):

    #lock = QReadWriteLock()

    def __init__(self, parent, client):
        super(Thread, self).__init__(parent)
        self.client_connection = client
        self.textFromClient = ""


    def run(self):
        #while the client is connected, it listens to messages from the client
        while self.client_connection.state()== QtNetwork.QAbstractSocket.ConnectedState:
            nextBlockSize = 0
            stream = QtCore.QDataStream(self.client_connection)
            stream.setVersion( QtCore.QDataStream.Qt_4_2)
            if (self.client_connection.waitForReadyRead(-1) and self.client_connection.bytesAvailable() >= SIZEOF_UINT16):
                nextBlockSize = stream.readUInt16()
            else:
                self.sendError("Cannot read client request")
                return
            if self.client_connection.bytesAvailable() < nextBlockSize:
                if (not self.client_connection.waitForReadyRead(-1) or
                    self.client_connection.bytesAvailable() < nextBlockSize):
                    self.sendError("Cannot read client data")
                    return

            #reads the string from the client
            self.textFromClient = stream.readQString()

#script main function
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())