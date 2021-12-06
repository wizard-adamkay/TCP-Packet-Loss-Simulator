import socket, pickle
from packet import Packet
import time
from _thread import *
import sys
import logging

#logging config
logging.basicConfig(filename="logTransmit",filemode='a',format= '%(message)s',level=logging.INFO)
logging.info("!!! NEW TRANSMISSION !!!")

myHost = ''
myPort = 8001
relayHost = 'localhost'
relayPort = 8000
timeOfLastSend = time.time()
timeOutThreshhold = 1
lastAckedNum = 0
windowSize = 1
acksReceivedSinceWindowChange = 0
duplicateAckReceived = False
done = False
# build packets
packets = []
with open('Adam.png', "rb") as f:
    seqNum = 0
    CHUNK_SIZE = 50
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
    global duplicateAckReceived

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
        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("recieved ack: " + str(data_variable.ackNum) + "\n", end='')
            logging.info("ACKed: " + str(data_variable.ackNum))
            # If EOT packet sent, will close
            if data_variable.packetType == 2:
                global done
                done = True
                break
            if data_variable.ackNum == lastAckedNum:
                print("duplicate ack detected!")
                duplicateAckReceived = True
                continue

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
    global windowSize
    global timeOfLastSend
    global timeOutThreshhold
    global  duplicateAckReceived
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((relayHost, relayPort))
    currentPacket = 0
    while 1:
        # Checks for duplicate acks
        # will divide windowsize in half and start from last acked packet if triggered
        if duplicateAckReceived:
            duplicateAckReceived = False
            windowSize = max(windowSize / 2, 1)
            currentPacket = lastAckedNum + 1
        # Checking for timeout, will trigger if a packet hasn't been sent in timeOutThreshhold seconds
        # Will reset windowsize to 1 and start from last acked packet if triggered
        if time.time() - timeOfLastSend >= timeOutThreshhold:
            windowSize = 1
            currentPacket = lastAckedNum + 1
            print("TIMEOUT " + str(time.time() - timeOfLastSend))
            timeOfLastSend = time.time()
            timeOutThreshhold *= 1.2
        #Checks available windowsize to see if room for another packet
        if currentPacket - lastAckedNum <= windowSize:
            packets[currentPacket].windowSize = windowSize
            packet = pickle.dumps(packets[currentPacket])
            s.send(packet)
            timeOfLastSend = time.time()
            timeOutThreshhold = max(timeOutThreshhold*.85, 1)
            print("sent packet: " + str(packets[currentPacket].seqNum) + "\n", end='')
            logging.info("Sent: " + str(packets[currentPacket].seqNum))
            if packets[currentPacket].packetType == 2:
                global done
                done = True
                break
            time.sleep(.001)
            currentPacket =min(currentPacket + 1, len(packets) - 1)
        if done:
            break
    s.close()


start_new_thread(receive, ())
start_new_thread(transmit, ())

while not done:
    time.sleep(1)
print(str(done))
print('Data Sent to Server')
