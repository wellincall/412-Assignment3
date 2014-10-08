#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
SIZEOF_UINT16 = 2

class Server(QtNetwork.QTcpServer):
    """
    Starts a TCP server at the port passed by the user
    """

    def __init__(self, port):
        #set up the main window to be the one from VPN_UI.ui
        QtNetwork.QTcpServer.__init__(self)
        self.port = port
        self.thread = None
        #initializates the message to be send with a string written Ack
        self.msg_to_send = QtGui.QLineEdit("Ack")
        self.request = None
        self.initialize()

    def initialize(self):
        if not self.listen(QtNetwork.QHostAddress("127.0.0.1"), self.port):
            QtGui.QMessageBox.critical(self, self.tr("Fortune Server"),
                                       self.tr("Unable to start the server: %(error)s.")
                                       % {'error': self.errorString()})
            #closes the server in case of an error
            self.close()
            return

        self.newConnection.connect(self.accept_connection)

    def accept_connection(self):
        """
        Treats the event of receiving a client
        """

        print "Client received"
        #gets the client socket info
        self.thread = Thread(self, self.nextPendingConnection())
        self.thread.start()


    def server_send_message(self, msg):
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
        self.thread.client_connection.write(self.request)
        self.nextBlockSize = 0
        self.request = None
        self.msg_to_send.setText("")



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
            print self.textFromClient