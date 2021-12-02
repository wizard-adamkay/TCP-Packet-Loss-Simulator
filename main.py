from tkinter import *
import tkinter
import matplotlib.pyplot as plt
import time
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from packet import Packet
top = tkinter.Tk()
top.title("Network Emulator")
top.geometry("700x500")
lineTracker = 1.0
global baseTime
baseTime = time


def update_graph(line, y):
    global baseTime
    t1 = time.time()
    line.set_xdata(np.append(line.get_xdata(), t1 - baseTime))
    line.set_ydata(np.append(line.get_ydata(), y))
    fig.canvas.draw()


def message(msg):
    global lineTracker
    messageBox['state'] = NORMAL
    messageBox.insert(lineTracker, msg + "\n")
    messageBox['state'] = DISABLED
    lineTracker += 1
    messageBox.see("end")


def start_call_back():
    global baseTime
    baseTime = time.time()
    clear_call_back()
    stop['state']=NORMAL
    start['state'] = DISABLED
    message("starting")

def stop_call_back():
    start['state'] = NORMAL
    stop['state'] = DISABLED
    t0=time.time()
    message("stopping, duration was:" + str(t0 - baseTime))


def clear_call_back():
    message("clearing")


def update_error_slider(num):
    errorLabel['text'] = "Error rate: " + num + "%"


def update_delay_slider(num):
    delayLabel['text'] = "Delay: " + num + "(ms)"

# Graph Setup
info = Frame(top)
info.pack(side=BOTTOM)
graphs = Frame(top)
graphs.pack(side=LEFT)
controls = Frame(top)
controls.pack(side=RIGHT)
buttons = Frame(controls)
buttons.pack(side=BOTTOM)
fig = plt.Figure(figsize=(3,2),dpi=100)
a = fig.add_subplot(111)
chart = FigureCanvasTkAgg(fig,graphs)
Label(graphs, text="Sequence Number Over Time").pack()
chart.get_tk_widget().pack()
line1, = a.plot([0],[0],'r-')
a.set_xlim([0,25])
a.set_ylim([0,25])


delaySlider = Scale(controls, orient=HORIZONTAL, from_=0, to=100, length= 300, command=update_delay_slider, showvalue=0)
delayLabel = Label(controls, text="Delay: " + str(delaySlider.get()) + "(ms)")
delayLabel.pack()
delaySlider.pack()
errorSlider = Scale(controls, orient=HORIZONTAL, from_=0, to=100, length= 300, command=update_error_slider, showvalue=0)
errorLabel = Label(controls, text="Error Rate: " + str(errorSlider.get()) + "%")
errorLabel.pack()
errorSlider.pack()

messageBox=Text(info, height=5, width=50, state='disabled')
messageBox.pack()
start=Button(buttons, text="Start", command=start_call_back)
start.pack(side=LEFT)
stop=Button(buttons, text="Stop", command=stop_call_back, state=DISABLED)
stop.pack(side=LEFT)
Button(buttons, text="Clear", command=clear_call_back).pack(side=LEFT)
top.mainloop()
