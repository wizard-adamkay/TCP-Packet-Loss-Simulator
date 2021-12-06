from tkinter import *
import tkinter
import matplotlib.pyplot as plt
import time
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from packet import Packet


class GUI:
    fig = plt.Figure(figsize=(3, 2), dpi=100)
    delay = 0
    packetLoss = 0
    baseTime = time.time()
    a = fig.add_subplot(111)
    line1, = a.plot([0], [0], 'r-')
    line2, = a.plot([0], [0], 'b-')

    def printTest(self):
        print("Delay: " + str(self.delay) + " Loss: " + str(self.packetLoss))

    def update_graph(self, lineNum, y):
        print("lineNum: " + str(lineNum) + " y: " + str(y))
        t1 = time.time()
        self.line1.set_xdata(np.append(self.line1.get_xdata(), t1 - self.baseTime))
        self.line1.set_ydata(np.append(self.line1.get_ydata(), y))
        self.a.set_xlim([0, max(30, t1 - self.baseTime + 2)])
        self.a.set_ylim([0, max(50, y + 2)])
        self.fig.canvas.draw()

    def run(self):
        top = tkinter.Tk()
        top.title("Network Emulator")
        top.geometry("700x500")
        lineTracker = 1.0
        baseTime = time

        def message(msg):
            global lineTracker
            messageBox['state'] = NORMAL
            messageBox.insert(lineTracker, msg + "\n")
            messageBox['state'] = DISABLED
            lineTracker += 1
            messageBox.see("end")

        def start_call_back():
            self.baseTime = time.time()
            clear_call_back()
            stop['state'] = NORMAL
            start['state'] = DISABLED
            message("starting")

        def stop_call_back():
            start['state'] = NORMAL
            stop['state'] = DISABLED
            t0 = time.time()
            message("stopping, duration was:" + str(t0 - baseTime))

        def clear_call_back():
            t1 = time.time()
            self.line1.set_xdata(np.append(self.line1.get_xdata(), t1 - self.baseTime))
            self.line1.set_ydata(np.append(self.line1.get_ydata(), 1))
            self.fig.canvas.draw()
            #message("clearing")

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
        buttons = Frame(controls)
        buttons.pack(side=BOTTOM)
        chart = FigureCanvasTkAgg(self.fig, graphs)
        Label(graphs, text="Sequence Number Over Time").pack()
        chart.get_tk_widget().pack()
        self.a.set_xlim([0, 30])
        self.a.set_ylim([0, 50])

        delaySlider = Scale(controls, orient=HORIZONTAL, from_=0, to=1000, length=300, command=update_delay_slider,
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
        start = Button(buttons, text="Start", command=start_call_back)
        start.pack(side=LEFT)
        stop = Button(buttons, text="Stop", command=stop_call_back, state=DISABLED)
        stop.pack(side=LEFT)
        Button(buttons, text="Clear", command=clear_call_back).pack(side=LEFT)

        top.mainloop()