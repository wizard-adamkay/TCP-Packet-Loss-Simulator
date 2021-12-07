from tkinter import *
import tkinter
import matplotlib.pyplot as plt
import time
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from packet import Packet


class GUI:
    fig = plt.Figure(figsize=(6, 3), dpi=100)
    fig2 = plt.Figure(figsize=(6, 3), dpi=100)
    seqNumGraphyMax = 50
    winSizeGraphyMax = 16
    delay = 0
    packetLoss = 0
    baseTime = time.time()
    a = fig.add_subplot(111)
    b = fig2.add_subplot(111)
    line1, = a.plot([0], [0], 'r-')
    line2, = a.plot([0], [0], 'b-')
    lineList = [line1, line2]
    line3, = b.plot([0], [0], 'r-')
    line4, = b.plot([0], [0], 'b-')
    lineList2 = [line3, line4]

    def printTest(self):
        print("Delay: " + str(self.delay) + " Loss: " + str(self.packetLoss))

    def update_graph1(self, lineNum, y):
        t1 = time.time()
        self.lineList[lineNum].set_xdata(np.append(self.lineList[lineNum].get_xdata(), t1 - self.baseTime))
        self.lineList[lineNum].set_ydata(np.append(self.lineList[lineNum].get_ydata(), y))
        self.seqNumGraphyMax = max(self.seqNumGraphyMax, max(50, y + 10))
        self.a.set_xlim([0, max(30, t1 - self.baseTime + 2)])
        self.a.set_ylim([0, self.seqNumGraphyMax])
        self.fig.canvas.draw()


    def update_graph2(self, lineNum, y):
        t1 = time.time()
        self.lineList2[lineNum].set_xdata(np.append(self.lineList2[lineNum].get_xdata(), t1 - self.baseTime))
        self.lineList2[lineNum].set_ydata(np.append(self.lineList2[lineNum].get_ydata(), y))
        self.winSizeGraphyMax = max(self.winSizeGraphyMax, max(16, y + 10))
        self.b.set_xlim([0, max(30, t1 - self.baseTime + 2)])
        self.b.set_ylim([0, self.winSizeGraphyMax])
        self.fig2.canvas.draw()

    def run(self):
        top = tkinter.Tk()
        top.title("Network Emulator")
        top.geometry("1920x1080")
        lineTracker = 1.0

        def message(msg):
            global lineTracker
            messageBox['state'] = NORMAL
            messageBox.insert(lineTracker, msg + "\n")
            messageBox['state'] = DISABLED
            lineTracker += 1
            messageBox.see("end")


        def update_error_slider(num):
            errorLabel['text'] = "Error rate: " + num + "%"
            self.packetLoss = num

        def update_delay_slider(num):
            delayLabel['text'] = "Delay: " + num + "(ms)"
            self.delay = num

        # Graph Setup
        info = Frame(top)
        info.pack(side=BOTTOM)
        graphs = Frame(top)
        graphs.pack(side=LEFT)
        controls = Frame(top)
        controls.pack(side=RIGHT)
        chart = FigureCanvasTkAgg(self.fig, graphs)
        chart2 = FigureCanvasTkAgg(self.fig2, graphs)
        Label(graphs, text="Sequence Number Over Time").pack()
        chart.get_tk_widget().pack()
        chart2.get_tk_widget().pack()
        self.a.set_xlim([0, 30])
        self.a.set_ylim([0, 50])
        self.b.set_xlim([0, 30])
        self.b.set_ylim([0, 16])

        delaySlider = Scale(controls, orient=HORIZONTAL, from_=0, to=10000, length=300, command=update_delay_slider,
                            showvalue=0)
        delayLabel = Label(controls, text="Delay: " + str(delaySlider.get()) + "(ms)")
        delayLabel.pack()
        delaySlider.pack()
        errorSlider = Scale(controls, orient=HORIZONTAL, from_=0, to=100, length=300, command=update_error_slider,
                            showvalue=0)
        errorLabel = Label(controls, text="Error Rate: " + str(errorSlider.get()) + "%")
        errorLabel.pack()
        errorSlider.pack()

        messageBox = Text(info, height=5, width=100, state='disabled')
        messageBox.pack()
        top.mainloop()