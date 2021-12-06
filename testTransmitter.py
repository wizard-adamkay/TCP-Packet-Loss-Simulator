import socket, pickle
import main
from packet import Packet
import time
from _thread import *
import sys
import logging

#logging config
logging.basicConfig(filename="logTransmit",filemode='a',format= '%(message)s',level=logging.INFO)
logging.info("!!! NEW TRANSMISSION !!!")

lastAckedNum = 0
windowSize = 1
acksReceivedSinceWindowChange = 0
# build packets
packets = []
with open('Adam.png', "rb") as f:
    seqNum = 0
    CHUNK_SIZE = 500
    while True:
        bytes_read = f.read(CHUNK_SIZE)
        if not bytes_read:
            break
        p = Packet(0, seqNum, bytes_read, 0, 1)
        packets.append(p)
        seqNum += 1
packets.append(Packet(2, (seqNum), b'', 0, 0))


# setup server to receive acks
def receive():
    global lastAckedNum
    global acksReceivedSinceWindowChange
    global windowSize
    myHost = ''
    transmitterPort = 8001
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, transmitterPort))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Client Connection:', address)  # Print the connected client address
        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("recieved ack: " + str(data_variable.ackNum) + "\n", end='')
            logging.info("ACKed: " + str(data_variable.ackNum))
            acksReceivedSinceWindowChange+=1
            if acksReceivedSinceWindowChange >= windowSize and windowSize < 16:
                windowSize*=2
            lastAckedNum = data_variable.ackNum
            if data_variable.packetType == 2:
                break
        connection.close()
    s.close()


# Start sending to middleman
def transmit():
    HOST = 'localhost'
    PORT = 8000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    currentPacket = 0
    while 1:
        if currentPacket - (lastAckedNum - 1) <= windowSize:
            packets[currentPacket].windowSize = windowSize
            packet = pickle.dumps(packets[currentPacket])
            s.send(packet)
            print("sent packet: " + str(packets[currentPacket].seqNum) + "\n", end='')
            logging.info("Sent: " + str(packets[currentPacket].seqNum))
            time.sleep(.1)
            if packets[currentPacket].packetType == 2:
                global done
                done = True
                break
            currentPacket += 1
    s.close()


start_new_thread(receive, ())
start_new_thread(transmit, ())
done = False
while not done:
    time.sleep(1)
print('Data Sent to Server')
