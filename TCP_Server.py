#import basic pyside Desgin functions
from PySide import QtCore, QtGui, QtNetwork
from Crypto.Cipher import AES
from Crypto import Random
from socket import *
import math
import binascii
import random
import select

SIZEOF_UINT16 = 2


class Server(QtNetwork.QTcpServer):
    """
    Starts a TCP server at the port passed by the user
    """

    def __init__(self, port, key):
        #set up the main window to be the one from VPN_UI.ui
        QtNetwork.QTcpServer.__init__(self)

        #initializes TCP required info
        self.port = port

        #initializes server info
        self.name = "Bob"
        self.key = "1234567891234567"#key

        self.msg = ""

        #initializes client info
        self.thread = Thread(self, self.key)
        self.thread.start()


class Thread(QtCore.QThread):

    #lock = QReadWriteLock()

    def __init__(self, parent, key):
        super(Thread, self).__init__(parent)
        #gets TCP server info
        self.parent = parent

        #gets TCP server key
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
        self.b = 0
        self.p = 32

    def run(self):
        host = 'localhost'
        addr = (host, self.parent.port)
        serversocket = socket(AF_INET, SOCK_STREAM)
        serversocket.bind(addr)
        serversocket.listen(2)

        while 1:
            print "Server is listening for connections\n"

            clientsocket, clientaddr = serversocket.accept()
            #thread.start_new_thread(self.handler, (clientsocket, clientaddr))
            self.handler(clientsocket, clientaddr)
        serversocket.close()

    def handler(self, clientsocket, clientaddr):
        print "Accepted connection from: ", clientaddr

        while 1:
            if self.session_started is False:
                try:
                    #Step 1: Receive authentication request
                    #Receive R1 , "Alice"
                    data = clientsocket.recv(1024)

                    #Step 2: Send challenge
                    # Send R2 + [E("Bob" , R1 , g^b mod p , k)]
                    obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                    r1 = data[:data.find(" , ")]
                    self.b = random.randint(0, 4)
                    mod = math.pow(self.g, self.b) % self.p
                    data = self.parent.name + " , " + r1 + " , " + str(mod) + " , " + self.parent.key
                    while len(data) % 16 != 0:
                        data += " "
                    ciphertext = obj.encrypt(data)

                    #create r2
                    rndfile = Random.new()
                    r2 = str(rndfile.read(9))

                    #create msg R2 + [E("Bob" , R1 , g^b mod p , k)]
                    msg = r2 + "[" + binascii.b2a_hex(ciphertext) + "]"
                    clientsocket.send(msg)
                    print "Challenge sent to client"

                    #Step 3: Receive challenge response
                    # Receive ["Alice" , R2 , g^a mod p , k]
                    data = clientsocket.recv(1024)
                    print "Challenge response received"
                    obj = AES.new(self.parent.key, AES.MODE_CBC, 'This is an IV456')
                    decrypt_challenge = obj.decrypt(binascii.a2b_hex(data[data.find("[")+1:data.find("]")])).split(" , ")
                    r2_received = decrypt_challenge[1]
                    mod_received = decrypt_challenge[2]

                    #checks if the random variable r2 received is the same as the sent
                    if r2_received == r2:
                        print "R2 checked :", r2
                    else:
                        print "Wrong R2"
                        break

                    #generate session_key
                    self.session_key = math.pow(float(mod_received), self.b) % self.p

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
        # print "Server writing"
        client_socket.send(self.msg_to_write)
        self.w_flag = False
        return

    def read(self, client_socket):

        #set time-out if u do not have data to read
        client_socket.setblocking(0)
        ready = select.select([client_socket], [], [], 1)
        if ready[0]:
            self.read_msg = client_socket.recv(1024)

        # print "Server reading"
        self.r_flag = False
        self.parent.msg = self.read_msg
        return
