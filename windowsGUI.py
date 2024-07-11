from tkinter import *
import serial
import queue
import threading
from stopwatch import Stopwatch
from datetime import date
import tkinter.filedialog
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def read_data():
    global ser
    while True:
        try:
            data = ser.readline()
            if start and stopwatch.duration <= float(Duration.get()) and not pause:
                data_queue.put([str(stopwatch.duration), data])
        except:
            continue
x = []
y = []
y2 = []
def update_gui():
    try:
        new_data = []
        while not data_queue.empty():
            data = data_queue.get_nowait()
            try:
                value = data[1].decode('utf-8').strip("\r\n").split(",")
                new_data.append(data[0] + " sec, " + value[0] + " Pressure," + value[-1] + " Pulse\n")
                try:
                    x.append(float(data[0]))
                    y.append(float(value[0]))
                    y2.append(float(value[1]))
                except:
                    print("skiiiip")
            except ValueError:
                print('Skipped')
    except queue.Empty:
        pass
    if new_data:
        notepad.insert(END,''.join(new_data))
        notepad.see("end")
    root.after(100, update_gui)
real_x = []
real_y = []
real_y2 = []
def grapher(frame):
    global ax, chart_type, real_x, real_y, x, y, y2
    if len(x) > 1 and len(y) > 1 and len(y2) > 0:
        real_x.append(round(x[-1], 2))
        real_y.append(y[-1])
        real_y2.append(y2[-1])
        ax.clear()
        ax.plot(x, y, color = "blue")
        ax2.plot(x, y2, color = "red")
        chart_type.draw()
    root.after(500, grapher, frame+1)

def save_text():
    global Subject, Trial, Operator
    filename = Subject.get() + "_trial_" + Trial.get() + "_" + Operator.get() + "-"+ str(date.today().strftime("%m_%d_%Y"))
    filetypes = [('Text', '*.txt'),('All files', '*')]
    filenam = tkinter.filedialog.asksaveasfilename(defaultextension='.txt', filetypes = filetypes, initialfile = filename)
    f = open(filenam, 'w')
    f.write(notepad.get('1.0', 'end'))
    f.close()

def on_closing():
    plot_queue.put(None)  # Add sentinel value to stop the plot thread
    plot_thread.join()    # Wait for the plot thread to finish
    root.destroy()

# Changes pluggedin to True when correct port is selected
# This is necessary to activate the run button
def on_select(selection):
    global ser, pluggedin
    ser = serial.Serial(selection.name, 115200)
    pluggedin = True

# Pauses and Resumes Recording of data from Arduino
def pauseClick():
    global pause
    if pause == False:
        pause = True
        stopwatch.stop()
    else:
        pause = False
        stopwatch.start()

# Begins recording data from Arduino
def runClick():
    global start, pause, stopwatch
    start = True
    pause = False
    RunB["state"] = "disable"
    PauseB["state"] = "active"
    EndB["state"] = "active"
    NextTrialB["state"] = "active"
    stopwatch.restart()

def nextTrialClick():
    global start, time, stopwatch, real_x, real_y, real_y2, ax, x, y, y2
    start = False
    try:
        testingCount = int(Trial.get())
    except:
        testingCound = 0
        print("Not Valid Trial Input")
    print(testingCount)
    TrialE.delete(0, END)
    TrialE.insert(0, testingCount + 1)
    SystolicE.delete(0, END)
    DiastolicE.delete(0, END)
    PulseE.delete(0, END)
    notepad.delete("1.0","end")
    stopwatch.reset()
    real_x, real_y, real_y2 = [], [], []
    x,y,y2 = [], [], []
    ax.clear()
    ax2.clear()
    ax.plot([], [], color="blue")  # Redraw an empty plot
    ax2.plot([], [], color="red")  # Redraw an empty plot
    chart_type.draw()


# Clears trial, graph, and text box
def endClick():
    global start, time, stopwatch, real_x, real_y, real_y2, ax, x, y, y2
    TrialE.delete(0, END)
    SubjectE.delete(0, END)
    OperatorE.delete(0, END)
    SystolicE.delete(0, END)
    DiastolicE.delete(0, END)
    PulseE.delete(0, END)
    start = False
    PauseB["state"] = "disable"
    NextTrialB["state"] = "disable"
    notepad.delete("1.0","end")
    stopwatch.reset()
    real_x, real_y, real_y2 = [], [], []
    x,y,y2 = [], [], []
    ax.clear()
    ax2.clear()
    ax.plot([], [], color="blue")  # Redraw an empty plot
    ax2.plot([], [], color="red")  # Redraw an empty plot
    chart_type.draw()

# Activates Run button when the correct port is selected and all test parameters are set
def button_activator(a,b,c):
    global Subject, Trial, Operator
    if len(Subject.get()) > 1 and len(Trial.get()) > 0 and len(Operator.get()) > 1:
        RunB['state'] = 'active'
    else:
        RunB['state'] = 'disable'

# Uploads results onto the text box
def submit():
    global Systolic, Diastolic, FinalPulse
    notepad.insert(END, "Systolic Pressure: " + Systolic.get() +"\nDiastolic Pressure: " + Diastolic.get() + '\nFinal Pulse: ' + FinalPulse.get() + '\nSubject: ' + Subject.get() + '\nOperator: ' + Operator.get() + '\nTrial: ' + Trial.get())

root = Tk()
root.title("Heart Rate Sensor")
root.geometry("1240x730")

start = False
pause, running, pluggedin = False, False, False
stopwatch = Stopwatch(2)
data_queue = queue.Queue()
plot_queue = queue.Queue()
Duration = StringVar()
Subject = StringVar()
Trial = StringVar()
Operator = StringVar()
Systolic = StringVar()
Diastolic = StringVar()
FinalPulse = StringVar()

# Creation and formatting of the graph
fig, ax = plt.subplots(figsize = (8,7))
ax2 = ax.twinx()
fig.suptitle("Sensor Data Graph")
ax.tick_params(axis='y', colors='red')
ax2.tick_params(axis='y', colors='blue')
ax.set_xlabel('Time (s)')
chart_type = FigureCanvasTkAgg(fig, root)
chart_type.get_tk_widget().grid(row= 0, column = 1, rowspan=4)

testParam = LabelFrame(root, text = "Test Parameters", padx = 5, pady = 5)

#Port Selection and Connection
ports = serial.tools.list_ports.comports()
default = StringVar(root, "Please Select Port")
yuppy = ['No Ports Conncted, Please connect Arduino and Rerun Application']
if ports == []:
    OptionMenu(testParam, default, *yuppy , command=on_select).grid(row = 0, column=3, sticky="e")
else:
    OptionMenu(testParam, default, *ports , command=on_select).grid(row = 0, column=3, sticky="e")

# Text Fields of all test parameters (Time Limit, Subject, Trial, Operator)
TimeLimE = Entry(testParam, textvariable=Duration, width = 40)
SubjectE = Entry(testParam, textvariable=Subject, width = 40)
TrialE = Entry(testParam, textvariable=Trial, width= 40)
OperatorE = Entry(testParam, textvariable=Operator, width= 40)

# Text Labels of all test parameters (Time Limit, Subject, Trial, Operator)
ComPorts = Label(testParam, text="COM ports:")
TimeLimT = Label(testParam, text="Time Limit (sec):")
SubjectT = Label(testParam, text="Subject: ")
TrialT = Label(testParam, text="Trial: ")
OperatorT = Label(testParam, text="Operator: ")

# Elapsed and Results Section
elapsedS = LabelFrame(root, text="Elapsed,  Output", padx = 5, pady = 5)
notepad = Text(elapsedS, width = 50, height = 20)

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label = "File", menu = filemenu)
filemenu.add_command(label = "Save as ...", command = save_text)
root.config(menu = menubar)

data_thread = threading.Thread(target = read_data)
data_thread.start()

# Result Section
resultParam = LabelFrame(root, text = "Results", padx = 5, pady = 5)
resultParam.grid(row = 2, column = 0, padx = 10, sticky="nsew")

# Text Fields of Results section
SystolicE = Entry(resultParam, textvariable=Systolic, width = 40)
DiastolicE = Entry(resultParam, textvariable=Diastolic, width = 40)
PulseE = Entry(resultParam, textvariable=FinalPulse, width=40)
ResultEnter = Button(resultParam, text = "Submit", width = 12, command=submit)

# Text Labels of Results section
SystolicT = Label(resultParam, text="Systolic Pressure: ")
DiastolicT = Label(resultParam, text="Diastolic Pressure: ")
PulseT = Label(resultParam, text = 'Final Pulse: ')

# Test Controls Buttons
testControl = LabelFrame(root, text = " Test controls", padx = 5, pady = 5)
RunB = Button(testControl, text="Run", width = 10, command=runClick)
PauseB = Button(testControl, text = "Pause Resume", width = 10, command=pauseClick)
EndB = Button(testControl, text = "Restart", width = 10, command = endClick)
NextTrialB = Button(testControl, text = "Next Trial", width = 10, command = nextTrialClick)
SaveB = Button(testControl, text = "Save", width = 10, command=save_text)
Subject.trace('w', button_activator)
Trial.trace('w', button_activator)
Operator.trace('w', button_activator)

PauseB["state"] = "disable"
EndB["state"] = "disable"
RunB['state'] = 'disable'
NextTrialB["state"] = 'disable'

# Position of test control buttons
RunB.pack(expand=True, side = "left")
PauseB.pack(expand=True,side="left")
EndB.pack(expand = True, side= "left")
NextTrialB.pack(expand = True, side = "left")
SaveB.pack(expand = True, side = "left")

testParam.grid(row = 0, column = 0, padx = 10, sticky="nsew")

# Position of each element in the frame
ComPorts.grid(row=0, column=0, sticky="w")
TimeLimT.grid(row = 1, column= 0, sticky="w")
TimeLimE.grid(row = 1, column = 1, columnspan = 3)
SubjectT.grid(row = 2, column = 0, sticky="w")
SubjectE.grid(row = 2, column = 1, columnspan= 3)
TrialT.grid(row = 3, column = 0, sticky="w")
TrialE.grid(row = 3, column = 1, columnspan=3)
OperatorT.grid(row = 4, column = 0, sticky="w")
OperatorE.grid(row = 4, column = 1, columnspan=3)

elapsedS.grid(row = 1, column= 0, padx =10)
notepad.grid(row=0, column = 0)

# Position of labels and text fields on the GUI
SystolicT.grid(row = 1, column= 0, sticky="w")
SystolicE.grid(row = 1, column = 1, columnspan = 3, sticky="e")
DiastolicT.grid(row = 2, column = 0, sticky="w")
DiastolicE.grid(row = 2, column = 1, columnspan= 3, sticky="e")
PulseT.grid(row=3, column = 0, sticky ='w')
PulseE.grid(row=3, column = 1, columnspan = 3,sticky = 'e')
ResultEnter.grid(row = 4, column = 3, columnspan=3)

canvas = Canvas(root)
canvas.create_oval(10, 10, 20, 20, outline="black", fill="red", width=0.5)
canvas.create_text(25, 15, anchor=W, font="Purisa", text=" Pulse")
canvas.create_oval(90, 10, 100, 20, outline="black", fill="blue", width=0.5)
canvas.create_text(105, 15, anchor=W, font="Purisa", text=" Pressure")
canvas.grid(row=4, column=0)

testControl.grid(row = 3, column = 0, padx = 10, sticky="nsew")

root.after(100, update_gui)
root.after(500, grapher, 0)

root.mainloop()