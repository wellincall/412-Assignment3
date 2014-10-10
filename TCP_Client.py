#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
from Crypto.Cipher import AES
from Crypto import Random
import time
from socket import *
import thread
import binascii
import math
import random
import select
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

        #write flag
        self.w_flag = False
        self.msg_to_write = ""

        #read flag
        self.r_flag = False
        self.read_msg = ""

        #session key variables
        self.g = 4
        self.a = 0
        self.p = 32

    def run(self):
        host = 'localhost'
        buf = 1024

        addr = (host, self.parent.port)
        clientsocket = socket(AF_INET, SOCK_STREAM)
        clientsocket.connect(addr)

        while 1:
            if self.session_started is False:
                try:
                    #Step 1: Request authentication
                    #Send R1 , "Alice"
                    rndfile = Random.new()
                    r1 = str(rndfile.read(16))
                    data = r1 + " , " + self.parent.name
                    clientsocket.send(data)
                    print "Request authentication sent"

                    # Step 2: Receive the challenge
                    # Receive R2 + [E("Bob" , R1 , g^b mod p , k)]
                    data = clientsocket.recv(buf)
                    print "Challenge received from server"

                    obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                    decrypt_challenge = obj.decrypt(binascii.a2b_hex(data[data.find("[")+1:data.find("]")])).split(" , ")
                    # print decrypt_challenge
                    r1_received = decrypt_challenge[1]
                    mod_received = decrypt_challenge[2]

                    #checks if the random variable r1 received is the same as the sent
                    if r1_received == r1:
                        print "R1 checked :", r1
                    else:
                        print "Wrong R1"
                        break

                    r2 = data[:data.find("[")]

                    # Step 3: Send challenge response
                    # Send ["Alice" , R2 , g^a mod p , k]
                    obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                    self.a = random.randint(0, 4)
                    mod = math.pow(self.g, self.a) % self.p
                    msg = self.parent.name + " , " + r2 + " , " + str(mod) + " , " + self.parent.key
                    while len(msg) % 16 != 0:
                        msg += " "
                    ciphertext = obj.encrypt(msg)
                    data = "[" + binascii.b2a_hex(ciphertext) + "]"
                    clientsocket.send(data)
                    print "Challenge response sent"

                    #generate session_key
                    self.session_key = math.pow(float(mod_received), self.a) % self.p

                    #VPN established with success
                    self.session_started = True

                    print "VPN established, session key: ", self.session_key
                except:
                    print "VPN not established"
            else:
                if self.w_flag is True:
                    self.write(clientsocket)
                elif self.r_flag is True:
                    self.read(clientsocket)

        clientsocket.close()

    def write(self, client_socket):
        # print "Client writing"
        client_socket.send(self.msg_to_write)
        self.w_flag = False
        return

    def read(self, client_socket):

        #set time-out if u do not have data to read
        client_socket.setblocking(0)
        ready = select.select([client_socket], [], [], 1)
        if ready[0]:
            self.read_msg = client_socket.recv(1024)

        # print "Client reading"
        self.r_flag = False
        self.parent.msg = self.read_msg
        return