#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
from Crypto.Cipher import AES
from Crypto import Random
import time
from socket import *
import thread
import binascii

SIZEOF_UINT16 = 2

class Client(QtNetwork.QTcpSocket):
    """
    Connects to a server according to the port passed by the user
    """

    def __init__(self,host, port, key):
        #set up the main window to be the one from VPN_UI.ui
        QtNetwork.QTcpSocket.__init__(self)

        #initializes TCP required info
        self.port = port
        self.host = host

        #initializes client info
        self.name = "Alice"
        self.key = "1234567891234567"#key

        #initializes TCP client Thread
        self.thread = Thread(self, self.key)
        self.thread.start()


class Thread(QtCore.QThread):

    #lock = QReadWriteLock()

    def __init__(self, parent, key):
        super(Thread, self).__init__(parent)
        #gets TCP client info
        self.parent = parent

        #gets TCP client key
        self.key = key

        #initializes session key
        self.session_key = None
        self.session_started = False



    def run(self):
        host = 'localhost'
        port = 55567
        buf = 1024

        addr = (host, self.parent.port)
        clientsocket = socket(AF_INET, SOCK_STREAM)
        clientsocket.connect(addr)

        while 1:
            if self.session_started is False:
                #Step 1: Request authentication
                #Send R1 , "Alice"
                rndfile = Random.new()
                r1 = str(rndfile.read(16))
                data = r1 + " , " + self.parent.name
                clientsocket.send(data)
                print "Request authentication sent"

                # Step 2: Receive the challenge
                # Receive R2 + ["Bob" , R1 , k]
                data = clientsocket.recv(buf)
                print "Challenge received from server"

                obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                decrypt_challenge = obj.decrypt(binascii.a2b_hex(data[data.find("[")+1:data.find("]")])).split(" , ")
                r1_received = decrypt_challenge[1]

                if r1_received == r1:
                    print "R1 checked :", r1

                r2 = data[:data.find("[")]


                # Step 3: Send challenge response
                # Send ["Alice" + R2, k]
                obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                msg = self.parent.name + " , " + r2 + " , " + self.parent.key
                while len(msg) % 16 != 0:
                    msg += " "
                ciphertext = obj.encrypt(msg)
                data = "[" + binascii.b2a_hex(ciphertext) + "]"
                clientsocket.send(data)
                print "Challenge response sent"

                #VPN established with success
                self.session_started = True

        clientsocket.close()