#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
SIZEOF_UINT16 = 2

class Client(QtNetwork.QTcpSocket):
    """
    Connects to a server according to the port passed by the user
    """

    def __init__(self,host, port):
        #set up the main window to be the one from VPN_UI.ui
        QtNetwork.QTcpSocket.__init__(self)
        self.port = port
        self.host = host
        self.request = None
        self.thread = None

        self.nextBlockSize = 0
        self.textFromServer = ""


        #initializates the message to be send with a string written Ack
        self.msg_to_send = QtGui.QLineEdit("Ack")

        self.initialize()

    def initialize(self):
        self.abort()
        #connects the socket with the server socket established by the user
        self.connectToHost(self.host, self.port)

        #client connected to the server
        print "client connected"


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
        self.write(self.request)
        self.nextBlockSize = 0
        self.request = None
        self.msg_to_send.setText("")

    def read_from_server(self):
        #gets the client socket info
        # self.thread = Thread(self)
        # self.thread.start()
        stream = QtCore.QDataStream(self)
        stream.setVersion(QtCore.QDataStream.Qt_4_2)
        flag = True
        #while the client is connected, it listens the server
        while flag:
            if self.nextBlockSize == 0:
                if self.bytesAvailable() < SIZEOF_UINT16:
                    break
                self.nextBlockSize = stream.readUInt16()
            if self.bytesAvailable() < self.nextBlockSize:
                break
            self.textFromServer = stream.readQString()
            flag = False
