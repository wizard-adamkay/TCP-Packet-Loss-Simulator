import socket, pickle
from packet import Packet
import time
from _thread import *
import sys
nextAck = None
packetList = []
relayConnected = False
myHost = ''
relayHost = 'localhost'
myPort = 8004
relayPort = 8003

# setup server to receive acks
def receive():
    global nextAck
    global relayConnected
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPort))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Client Connection:', address)  # Print the connected client address
        relayConnected = True
        print("got here")
        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("received seq: " + str(data_variable.seqNum) + "\n", end='')
            packetList.append(data_variable)
            nextAck = Packet(data_variable.packetType,0,b'',0,data_variable.seqNum)
            if data_variable.packetType == 2:
                break
        connection.close()
    s.close()


def sendToRelay():
    while not relayConnected:
        time.sleep(1)
    global nextAck
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((relayHost, relayPort))
    while 1:
        if nextAck is not None:
            packet = pickle.dumps(nextAck)
            s.send(packet)
            print("sent ack: " + str(nextAck.ackNum))
            nextAck = None
        time.sleep(1)
    s.close()


start_new_thread(sendToRelay, ())
start_new_thread(receive, ())
done = False
while not done:
    time.sleep(1)
print('Data Sent to Server')
