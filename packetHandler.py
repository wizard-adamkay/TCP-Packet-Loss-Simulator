import socket, pickle
import sys
import _thread
from packet import Packet
import time
import logging
from GUI import GUI
import random

#logging config
logging.basicConfig(filename="logNetwork",filemode='a',format= '%(message)s',level=logging.INFO)
logging.info("!!! NEW TRANSMISSION !!!")


myHost = ''
transmitterHost = '192.168.0.16'
receiverHost = '192.168.0.18'
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
packetsDropped = 0
sleepBetweenSends = .07

def listenToTransmitter(_lock):
    global transmitterConnected
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket successfully created")
    except socket.error as err:
        print("socket creation failed with error %s" % (err))
    try:
        s.bind((myHost, myPortTransmitter))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + str(msg[1]))
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
            _lock.acquire()
            GUI.update_graph1(0,data_variable.seqNum)
            GUI.update_graph2(0, data_variable.windowSize)
            _lock.release()
            # todo close connection when stop clicked
        connection.close()
    s.close()


# could combine listentoreciever and listen to transmitter into 1 function
def listenToReceiver(_lock):
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
            _lock.acquire()
            GUI.update_graph1(1, data_variable.ackNum)
            _lock.release()
            # todo close connection when stop clicked
        connection.close()
    s.close()


def sendToTransmitter():
    global packetsDropped
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
                packetsDropped += 1
                GUI.update_dropped_packets(packetsDropped)
                print("packet from receiver dropped ack: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
                logging.info("Network X Transmitter: " + str(packetsFromReceiver[lastPacketSentToTransmitter].ackNum))
            lastPacketSentToTransmitter += 1
        time.sleep(sleepBetweenSends)
    s.close()


def sendToReceiver():
    global packetsDropped
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
                packetsDropped += 1
                GUI.update_dropped_packets(packetsDropped)
                print("packet from transmitter dropped seq: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
                logging.info("Network X Receiver: " + str(packetsFromTransmitter[lastPacketSentToReceiver].seqNum))
            lastPacketSentToReceiver += 1
        time.sleep(sleepBetweenSends)
    s.close()


GUI = GUI()
lock = _thread.allocate_lock()
_thread.start_new_thread(listenToTransmitter, (lock,))
_thread.start_new_thread(listenToReceiver, (lock,))
_thread.start_new_thread(sendToTransmitter, ())
_thread.start_new_thread(sendToReceiver, ())
GUI.run()
while 1:
    time.sleep(1)
