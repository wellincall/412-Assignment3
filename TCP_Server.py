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