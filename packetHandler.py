import socket, pickle
import sys
from _thread import *
from packet import Packet
import time
import logging
from GUI import GUI
import random

#logging config
logging.basicConfig(filename="logNetwork",filemode='a',format= '%(message)s',level=logging.INFO)
logging.info("!!! NEW TRANSMISSION !!!")


myHost = ''
transmitterHost = 'localhost'
receiverHost = 'localhost'
myPortTransmitter = 8000
myPortReceiver = 8003
receiverPort = 8004
transmitterPort = 8001
packetsFromTransmitter = []
packetsFromTransmitterTimes = []
lastPacketSentToReceiver = 0
packetsFromReceiver = []
packetsFromReceiverTimes = []
lastPacketSentToTransmitter = 0
transmitterConnected = False

def listenToTransmitter():
    global transmitterConnected
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPortTransmitter))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Transmitter Connection:', address)  # Print the connected client address
        transmitterConnected = True
        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("received from transmitter seq:" + str(data_variable.seqNum))
            logging.info("Transmitter > Network: " + str(data_variable.seqNum))
            packetsFromTransmitter.append(data_variable)
            packetsFromTransmitterTimes.append(time.time())
            # todo close connection when stop clicked
        connection.close()
    s.close()


# could combine listentoreciever and listen to transmitter into 1 function
def listenToReceiver():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPortReceiver))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')
    print("listening")
    s.listen(1)
    while True:  # listen until process killed
        connection, address = s.accept()
        print('Receiver Connection:', address)  # Print the connected client address

        while True:
            data = connection.recv(1024)  # read the client message
            data_variable = pickle.loads(data)
            print("received from receiver ack:" + str(data_variable.ackNum))
            logging.info("Receiver > Network: " + str(data_variable.ackNum))
            packetsFromReceiver.append(data_variable)
            packetsFromReceiverTimes.append(time.time())
            # todo close connection when stop clicked
        connection.close()
    s.close()


def sendToTransmitter():
    while not transmitterConnected:
        time.sleep(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((transmitterHost, transmitterPort))
    global lastPacketSentToTransmitter
    while 1:
        if len(packetsFromReceiver) > lastPacketSentToTransmitter and time.time() - packetsFromReceiverTimes[lastPacketSentToTransmitter] >= (float(GUI.delay) * .001):
            if random.randint(1, 100) >= int(GUI.packetLoss):
                packet = pickle.dumps(packetsFromReceiver[lastPacketSentToTransmitter])
                s.send(packet)
                print("packet sent to transmitter ack: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
                logging.info("Network > Transmitter: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
            else:
                print("packet from receiver dropped ack: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
                logging.info("Network X Transmitter: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
            lastPacketSentToTransmitter += 1
            continue
        time.sleep(.05)
    s.close()


def sendToReceiver():
    while not transmitterConnected:
        time.sleep(1)
        GUI.printTest()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((receiverHost, receiverPort))
    global lastPacketSentToReceiver
    while 1:
        if len(packetsFromTransmitter) > lastPacketSentToReceiver and time.time() - packetsFromTransmitterTimes[lastPacketSentToReceiver] >= (float(GUI.delay) * .001):
            if random.randint(1, 100) >= int(GUI.packetLoss):
                packet = pickle.dumps(packetsFromTransmitter[lastPacketSentToReceiver])
                s.send(packet)
                print("packet sent to receiver seq: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
                logging.info("Network > Receiver: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
            else:
                print("packet from transmitter dropped seq: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
                logging.info("Network X Receiver: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
            lastPacketSentToReceiver += 1
        time.sleep(.03)
    s.close()


GUI = GUI(0, 0)
start_new_thread(listenToTransmitter, ())
start_new_thread(listenToReceiver, ())
start_new_thread(sendToTransmitter, ())
start_new_thread(sendToReceiver, ())
GUI.run()
while 1:
    time.sleep(1)
