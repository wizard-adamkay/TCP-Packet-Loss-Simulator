# TCP-Packet-Loss-Simulator
Packet loss simulator with options to delay or drop packets entirely, graphing results in real time.


## How to run:
Download the application to three different machines connected on a local network. Specify the IP addresses and ports of the other machines inside of reciever.py, testTransmitter.py, and packetHandler.py. Run reciever.py, testTransmitter.py, and packetHandler.py on all three machines.

**Network Diagram**

![image](https://github.com/wizard-adamkay/TCP-Packet-Loss-Simulator/assets/37917852/3b0c10bd-3c4b-450f-b3c5-975ec4acc221)

## How It's Made:

**Tech used:** Python, Matplotlib, Numpy

The Packet Loss Simulator operates by initiating the transmission of packets from the transmitter to a relay. The relay, under user-defined specifications, can introduce delays or drop packets entirely before forwarding them to the receiver. Subsequently, the receiver communicates an acknowledgment (ACK) back to the relay, and this information is relayed back to the transmitter. The transmitter dynamically adjusts its window size and retransmits packets based on the observed occurrences of dropped or delayed packets, with these adjustments reflected in the graphical user interface (GUI) of the relay. In total, the application utilizes four distinct ports: two for acknowledgments and two for packets containing data.

![image](https://github.com/wizard-adamkay/TCP-Packet-Loss-Simulator/assets/37917852/fe86b2f9-5105-4111-8e3f-2463d7eb7246)

## Lessons Learned:

An essential takeaway from this project is the importance of meticulous planning and the implementation of comprehensive logging mechanisms. Adequate planning, particularly in defining user requirements and system architecture, laid a solid foundation for smooth development and effective bug resolution. Properly designed logging, capturing relevant information during runtime, emerged as a critical tool for diagnosing and fixing issues. The ability to trace the flow of data and identify specific points of failure greatly expedited the debugging process. This project underscores that strategic planning and robust logging practices are indispensable elements in not only preventing but swiftly addressing and resolving bugs in a software system.
