from dataclasses import dataclass
from typing import List

class Packet:

    def __init__(self, packetType: int, seqNum: int, data: bytes, windowSize: int, ackNum: int):
        self.packetType = packetType
        self.seqNum = seqNum
        self.data = data
        self.windowSize = windowSize
        self.ackNum = ackNum