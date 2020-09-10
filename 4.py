import numpy
import pyaudio
import nidaqmx as dq
import math
import time
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import font
from tkinter import ttk
import _thread
#---------------------------------------------------------#
GRW = 1000
GRH = 500
XOL = 20
YOT = 25
CANVASwidth = GRW + 2 * XOL
CANVASheight = GRH + 2 * YOT + 48
Ymin = YOT
Ymax = YOT + GRH
LONGsweep = False
LONGchunk = LONGsweep
Samplelist = [1000, 2000, 2500, 5000, 7500, 10000, 20000, 40000]
CHvdiv = [0.01, 0.1, 1.0, 10.0, 20.0, 50.0, 100.0, 1000.0]  # Sensitivity list in mv/div
TIMEdiv = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]  # Time list in ms/div
ADzero = False
COLORframes = "#000080"  # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"
COLORgrid = "#808080"
COLORzeroline = "#0000ff"
COLORtrace1 = "#00ff00"
COLORtrace2 = "#ff8000"
COLORtext = "#ffffff"
COLORtrigger = "#ff0000"
Buttonwidth1 = 12
Buttonwidth2 = 12
TRACES = 1
TRACESread = 0
RUNstatus = 1
SAMPLErate = 15000
Devicedict = {}
output = True
flag = True
mode = 0
#-------------------------------------------------------------------------------
Devicename1 = []
Devicename2 = []
Devicedict = {}



class channels:
   global NItask
   def __init__(self):
      self.timediv = 6
      self.chdiv = len(CHvdiv) - 1
      self.Tline = []
      self.AUDIOsignal = []
      self.Triggerline = []
      self.SHOWsamples = GRW
      self.NItask = None
      self.stream = None
      self.CurDeviceName = None
      self.offset = 0
      self.AUDIOdevin = None
      self.ADsens = 1000
      self.audiosize = int (SAMPLErate * TIMEdiv[self.timediv] * 10 /1000)
      self.PA = None
      self.triggerlevel = -200
      self.outputtask = dq.Task()
   def setaudiosize(self):
       self.audiosize = int (SAMPLErate * TIMEdiv[self.timediv] * 10 / 1000)
   def maketrace(self, c):
       global XOL
       global YOT
       global GRW
       global GRH
       global Ymin
       global Ymax
       global TRACES
       global RUNstatus
       global CHvdiv
       global TIMEdiv
       global SAMPLErate
       TRACEsize = len(self.AUDIOsignal)
       # print(TRACEsize)
       # print(self.AUDIOsignal)
       if TRACEsize == 0:
           self.Tline = []
           return()
       Yconv = float(GRH / 10) * 1000 / (self.ADsens * CHvdiv[self.chdiv])
       self.SHOWsamples = SAMPLErate * 10 * TIMEdiv[self.timediv] / 1000
       self.Tline = []
       t = 0
       x = 0
       Tstep = 0
       if (self.SHOWsamples >= GRW):
           self.SHOWsamples = GRW
           Tstep = (int)(self.SHOWsamples/ GRW)
       if (self.SHOWsamples < GRW):
           expand = []
           n = int(GRW / self.SHOWsamples) + 1
           for o in range(0, len(self.AUDIOsignal)):
                for i in range(0,n):
                    expand.append(self.AUDIOsignal[o])
           self.AUDIOsignal = expand
           Tstep = 1
       Xstep = 1
       x1 = 0
       y1 = 0.0
       while(x <= GRW):
           x1 = x + XOL
           y = float(self.AUDIOsignal[t])
           ytemp = int(c - Yconv * y)
           if (ytemp < Ymin):
               ytemp = Ymin
           if (ytemp > Ymax):
               ytemp = Ymax
           self.Tline.append(int(x1))
           self.Tline.append(int(ytemp))
           t = t + Tstep
           x = x + Xstep
       x1 = XOL
       y1 =int(c - Yconv * float(0))
       if (y1 < Ymin):
           y1 = Ymin
       if (y1 > Ymax):
           y1 = Ymax
       print(self.Tline)
       self.Triggerline.append(int(XOL - 5))
       self.Triggerline.append(int(y1))
       self.Triggerline.append(int(XOL + 5))
       self.Triggerline.append(int(y1))
channel1 = channels()
# channel2 = channels()

def generate():
    global channel1
    global mode
    global RUNstatus
    while True:
        if mode == 1 or mode == 2:
            width = 0.01
            period = 0.1 - (width*6)
            if (RUNstatus == 0):
                while True:
                    a = 0
            if RUNstatus == 1:
                while channel1.CurDeviceName == None or channel1.outputtask == None:
                    a = 0
                try:
                    channel1.outputtask.close()
                except:
                    pass
                try:
                    channel1.outputtask = dq.Task()
                    channel1.outputtask.do_channels.add_do_chan(channel1.CurDeviceName[:-3] + "port0/line0")
                except:
                    pass
            if RUNstatus == 2 :
                channel1.outputtask.start()
                start0 = time.time()
                for i in range(0, 3):
                    start = time.time()
                    channel1.outputtask.write(True)
                    while (time.time() - start < width):
                        a = 1
                        # time.sleep(width - 0.0025)
                    start = time.time()
                    channel1.outputtask.write(False)
                    while (time.time() - start < width):
                        a = 1

                while (time.time() - start0 < period):
                     a = 1
                # time.sleep( period - 2*width*3)
                channel1.outputtask.stop()
            if RUNstatus == 3 or RUNstatus == 4:
                channel1.outputtask.close()
                channel1.outputtask = None


def BTrigger1():
    channel1.triggerlevel -= CHvdiv[channel1.chdiv] / 10
    print(channel1.triggerlevel)
    RUNstatus = 1
    UpdateScreen()

def BTrigger2():
    channel1.triggerlevel += CHvdiv[channel1.chdiv] / 10
    print(channel1.triggerlevel)
    RUNstatus = 1
    UpdateScreen()

def BStart():
    global RUNstatus
    if (RUNstatus == 0):
         RUNstatus = 1
    UpdateScreen()


def BTime1(channel : channels):
    global RUNstatus
    if (channel.timediv >= 1):
        channel.timediv = channel.timediv - 1
    if RUNstatus == 2:
        RUNstatus = 4
    UpdateTrace()

def BTime2(channel : channels):
    global RUNstatus
    global TIMEdiv
    if (channel.timediv < len(TIMEdiv) - 1):
        channel.timediv = channel.timediv + 1
    if RUNstatus == 2:
        RUNstatus = 4
    UpdateTrace()

def BCHlevel1(channel : channels):
    global RUNstatus
    if (channel.chdiv >= 1):
        channel.chdiv = channel.chdiv - 1
    UpdateTrace()

def BCHlevel2(channel : channels):
    global RUNstatus
    if (channel.chdiv < len(CHvdiv) - 1):
        channel.chdiv = channel.chdiv + 1
    UpdateTrace()


def BSetup(*args):
    global ADzero
    global SAMPLErate
    global RUNstatus


    s = title.get()
    if (s == None):  # If Cancel pressed, then None
        return ()

    try:  # Error if for example no numeric characters or OK pressed without input (s = ""), then v = 0
        v = int(s)
    except:
        v = 0

    if v != 0:
        SAMPLErate = v
        print(SAMPLErate)
    if (RUNstatus == 2):
        RUNstatus = 4
    UpdateScreen()

def AUDIOin():
    global channel1
    global channel2
    global RUNstatus
    global mode
    while(True):
        channel1.setaudiosize()
        # channel2.setaudiosize()
        if (channel1.AUDIOdevin == None):
            RUNstatus = 0
        if (RUNstatus == 1):
            Action1(channel1)
        #UpdateScreen()
        if (RUNstatus == 2 ):
            if mode == 2 or mode == 0:
                Action2(channel1)
            elif mode == 1:
                channel1.AUDIOsignal = numpy.zeros(int(1.5 * channel1.audiosize),dtype=numpy.bool)
                MakeScreen()
            # if (TRACES == 2):
            #     Action2(channel2)
        if (RUNstatus == 3) or (RUNstatus == 4):
            Action3(channel1)
            if (TRACES == 2):
                Action3(channel2)
        UpdateAll()
        root.update_idletasks()
        root.update()

def Action1(channel : channels):
    global RUNstatus
    global output
    global flag
    if (channel.AUDIOdevin != None):
        PA = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        chunkbuffer = int(3000)
        if (channel.AUDIOdevin < 15):
            try:
                channel.stream = PA.open(format=FORMAT,
                                         channels=TRACES,
                                         rate=SAMPLErate,
                                         input=True,
                                         output=False,
                                         frames_per_buffer=int(chunkbuffer),
                                         input_device_index=channel.AUDIOdevin)
                RUNstatus = 2
            except:
                RUNstatus = 0
                txt = "Something wrong when creating stream for the device"
                messagebox.showerror("Cannot open Audio Stream", txt)
        else:
            try:
                channel.NItask.close()
            except:
                pass
            channel.NItask = dq.Task()
            for i in Devicedict.keys():
                if Devicedict.get(i) == channel.AUDIOdevin:
                    channel.CurDeviceName = i
                    break
            try:
                addedChan = False
                for i in channel.NItask.ai_channels:
                    if i.name == channel.CurDeviceName:
                        addedChan = True
                if addedChan == False:
                    channel.NItask.ai_channels.add_ai_voltage_chan(channel.CurDeviceName)
                channel.NItask.start()
                flag = True
                RUNstatus = 2
            except Exception as e:
                RUNstatus = 0
                txt = "Task cannot be created, check the device connection and channel name"
                messagebox.showerror("Error when creating NI tasks", txt)
                print(e)



def Action2(channel : channels):
    global RUNstatus
    global output
    AUDIOsignals = []
    if (channel.AUDIOdevin != None):
        if (channel.AUDIOdevin < 15):
            while len(AUDIOsignals) < channel.audiosize:
                buffervalue = channel.stream.get_read_available()
                if buffervalue > 1024:
                    signals = channel.stream.read(buffervalue)
                    AUDIOsignals.extend(numpy.fromstring(signals, "Int16"))
        else:
            while len(AUDIOsignals) < 1.5 * channel.audiosize:
                signals = channel.NItask.read(80)
                for i in range(0, len(signals)):
                    signals[i] = signals[i] * 1000
                AUDIOsignals.extend(signals)
            channel.NItask.stop()
    while (len(AUDIOsignals) > 0 and AUDIOsignals[0] < channel.triggerlevel):
        del AUDIOsignals[0]
    channel.AUDIOsignal = AUDIOsignals
    # MakeScreen()
def Action3(channel : channels):
    global RUNstatus
    global flag
    if (channel.AUDIOdevin != None):
        if (channel.AUDIOdevin < 15):
            channel.stream.stop_stream()
            channel.stream.close()
        else:
            channel.NItask.close()
            channel.NItask = None
            # flag = False

    if (channel.PA != None):
        channel.PA.terminate()
    if RUNstatus == 3:
        RUNstatus = 0
    if RUNstatus == 4:
        RUNstatus = 1

def UpdateAll():
    CalculateData()
    MakeTrace()
    UpdateScreen()

def UpdateTrace():
    MakeTrace()
    UpdateScreen()

def UpdateScreen():
    MakeScreen()
    root.update()

def MakeScreen():
    global XOL
    global YOT
    global GRW
    global GRH
    global Ymin
    global Ymax
    global CHvdiv
    global TIMEdiv
    global CANVASwidth
    global CANVASheight
    global ADsens
    global SAMPLErate
    global channel1
    global channel2
    de = ca.find_enclosed(0, 0, CANVASwidth + 1000, CANVASheight + 1000)
    for n in de:
        ca.delete(n)
    i = 0
    x1 = XOL
    x2 = XOL + GRW
    while (i < 11):
        y = YOT + i * GRH / 10
        Dline = [x1, y, x2, y]
        ca.create_line(Dline, fill=COLORgrid)
        i = i + 1
    if TRACES == 1:
        y = YOT + 5 * GRH / 10
        Dline = [x1, y, x2, y]
        ca.create_line(Dline, fill = COLORzeroline)
    if TRACES == 2:
        y = YOT + GRH / 4
        Dline = [x1,y,x2,y]
        ca.create_line(Dline, fill=COLORzeroline)       # Blue horizontal line 1 for 2 traces
        y = YOT + 3 * GRH / 4
        Dline = [x1,y,x2,y]
        ca.create_line(Dline, fill=COLORzeroline)
    i = 0
    y1 = YOT
    y2 = YOT + GRH
    while (i < 11):
        x = XOL + i * GRW / 10
        Dline = [x, y1, x, y2]
        ca.create_line(Dline, fill=COLORgrid)
        i = i + 1
    vx = TIMEdiv[channel1.timediv]
    if vx >= 1000:
        txt = str(int(vx / 1000)) + "s/div"
    if vx < 1000 and vx >= 1:
        txt = str(int(vx)) + "ms/div"
    if vx < 1:
        txt = "0." + str(int(vx * 10)) + "ms/div"
    if vx <= 0.01:
        txt = "0." + "0" + str(int(vx * 100)) + "ms/div"
    x = XOL
    y = YOT + GRH + 12
    ca.create_text(x, y, text= txt, anchor = W, fill = COLORtext)
    vy = CHvdiv[channel1.chdiv]
    txt = ""
    if vy >= 1000:
        txt = txt + str(int(vy/1000)) + " V/div"
    if vy < 1000 and vy >= 1:
        txt = txt + str(int(vy)) + " mV/div"
    if vy < 1:
        txt = txt + "0." + str(int(vy * 10)) + " mV/div"
    x = XOL
    y = YOT+GRH+24
    idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    txt = ""
    # vx = TIMEdiv[channel2.timediv]
    # if vx >= 1000:
    #     txt = str(int(vx / 1000)) + "s/div"
    # if vx < 1000 and vx >= 1:
    #     txt = str(int(vx)) + "ms/div"
    # if vx < 1:
    #     txt = "0." + str(int(vx * 10)) + "ms/div"
    # if vx <= 0.01:
    #     txt = "0." + "0" + str(int(vx * 100)) + "ms/div"
    # x = XOL
    # y = YOT + GRH + 36
    # ca.create_text(x, y, text= txt, anchor = W, fill = COLORtext)
    # txt = ""
    # vy = CHvdiv[channel2.chdiv]
    # txt = ""
    # if vy >= 1000:
    #     txt = txt + str(int(vy/1000)) + " V/div"
    # if vy < 1000 and vy >= 1:
    #     txt = txt + str(int(vy)) + " mV/div"
    # if vy < 1:
    #     txt = txt + "0." + str(int(vy * 10)) + " mV/div"
    # x = XOL
    # y = YOT+GRH+48
    # idTXT = ca.create_text (x, y, text=txt, anchor=W, fill=COLORtext)
    if (len(channel1.Tline) > 4):
        ca.create_line(channel1.Tline, fill = COLORtrace1)
    # if (TRACES == 2):
    #     if (len(channel2.Tline) > 4):
    #         ca.create_line(channel2.Tline, fill = COLORtrace2)
    i = 0
def MakeTrace():
    global channel1
    global channel2
    global XOL
    global YOT
    global GRW
    global GRH
    global Ymin
    global Ymax
    global TRACES
    global RUNstatus
    global CHvdiv
    global TIMEdiv
    global SAMPLErate
    if len(channel1.AUDIOsignal) == 0:
        return
    Yconv1 = float(GRH / 10) * 1000 / (channel1.ADsens * CHvdiv[channel1.chdiv])
    if (TRACES == 1):
        c1 = GRH / 2 + YOT - channel1.offset
    if (TRACES == 2):
        c1 = GRH / 4 + YOT - channel1.offset
        c2 = 3 * GRH / 4 + YOT - channel2.offset
        channel2.maketrace(c = c2)
    channel1.maketrace(c = c1)





def ReadInDevice():
    global Devicename1
    global Devicename2
    global Devicedict
    Devicename1 = []
    Devicename2 = []
    PA = pyaudio.PyAudio()
    s = PA.get_device_info_by_index(0)
    Devicedict[s['name']] = s['index']
    Devicename1.append(s['name'])
    nisystem = dq.system.System.local()
    nidenum = len(nisystem.devices)
    n = 15
    for i in range(nidenum):
        channels = nisystem.devices[i].ai_physical_chans
        cnum = len(channels)
        for j in range(cnum):
            Devicename1.append(channels[j].name)
            Devicedict[channels[j].name] = n
            n = n + 1
        PA.terminate()
    Devicename2 = Devicename1
    Devicebox1['values'] = Devicename1
    # Devicebox2['values'] = Devicename2

def change(*args):
    global channel1
    global RUNstatus
    s = Devicebox1.get()
    channel1.AUDIOdevin = Devicedict[s]
    print(s + ":" + str(channel1.AUDIOdevin))
    if (RUNstatus == 2) or RUNstatus == 1:
        RUNstatus = 4
    RUNstatus = 1

def Bmode0():
    global mode
    global RUNstatus
    mode = 0
    if RUNstatus == 2 or RUNstatus == 1:
        RUNstatus = 4
    RUNstatus = 1

def Bmode1():
    global mode
    global RUNstatus
    mode = 1
    if RUNstatus == 2 or RUNstatus == 1:
        RUNstatus = 4
    RUNstatus = 1
def Bmode2():
    global mode
    global RUNstatus
    mode = 1
    if RUNstatus == 2 or RUNstatus == 1:
        RUNstatus = 4
    RUNstatus = 1
    mode = 2

# def change_1(*args):
#     global channel2
#     global RUNstatus
#     s = Devicebox2.get()
#     channel2.AUDIOdevin = Devicedict[s]
#     print(s + ":" + str(channel2.AUDIOdevin))
#     if (RUNstatus == 2):
#         RUNstatus = 4
#     RUNstatus = 1


def CalculateData():
    return()

def BStop():
    global RUNstatus
    if (RUNstatus == 1):
        RUNstatus = 0
    elif (RUNstatus == 2):
        RUNstatus = 3
    elif (RUNstatus == 3):
        RUNstatus = 3
    elif (RUNstatus == 4):
        RUNstatus = 3

# def BTraces():
#     global TRACES
#     global RUNstatus
#
#     if (TRACES == 1):
#         TRACES = 2
#     else:
#         TRACES = 1
#
#     if RUNstatus == 2:  # Restart if running
#         RUNstatus = 1

root = Tk()
root.title("OscilloscopeV02a.py(w) (13-10-2018): Audio Oscilloscope")
root.minsize(100, 100)
title = StringVar()
title.set(10000)
frame1 = Frame(root, background=COLORframes, borderwidth=5, relief=RIDGE)
frame1.pack(side=LEFT, expand=1, fill=Y)

frame2 = Frame(root, background="black", borderwidth=5, relief=RIDGE)
frame2.pack(side=TOP, expand=1, fill=X)

frame3 = Frame(root, background=COLORframes, borderwidth=5, relief=RIDGE)
frame3.pack(side=TOP, expand=1, fill=X)

ca = Canvas(frame2, width=CANVASwidth, height=CANVASheight, background=COLORcanvas)
ca.pack(side=TOP)

# b = Button(frame1, text="1/2 Channels", width=Buttonwidth1, command=BTraces)
# b.pack(side=LEFT, padx=5, pady=5)
b = Button(frame1, text = "trigger+", width = Buttonwidth2, command = BTrigger2)
b.pack(side = TOP, padx = 10, pady = 10)
b = Button(frame1, text = "trigger-", width = Buttonwidth2, command = BTrigger1)
b.pack(side = TOP, padx = 10, pady = 10)
b = Button(frame1, text="mode1", width=Buttonwidth2, command=Bmode0)
b.pack(side= TOP, padx=10, pady=10)
b = Button(frame1, text="mode2", width=Buttonwidth2, command=Bmode1)
b.pack(side= TOP, padx=10, pady=10)
b = Button(frame1, text="mode3", width=Buttonwidth2, command=Bmode2)
b.pack(side= TOP, padx=10, pady=10)
b = Label(frame1, text = "Samplerate", width = Buttonwidth2,bg = COLORframes, fg = COLORtext)
b.pack(side = TOP, padx = 5, pady = 2)
m=OptionMenu(frame1,title,*Samplelist)
m.config(width=Buttonwidth2-5)
m.pack(side=TOP,padx=5,pady=5)
b = Label(frame1, text = "Devices", width = Buttonwidth2,bg = COLORframes, fg = COLORtext)
b.pack(side = TOP, padx = 5, pady = 2)
Devicebox1=ttk.Combobox(frame1, width=Buttonwidth2 - 2, postcommand=ReadInDevice, values=Devicename1, )
Devicebox1.pack(side=TOP, padx=5, pady=2)
Devicebox1.bind("<<ComboboxSelected>>",change)



b = Button(frame3, text="Start", width=Buttonwidth2, command=BStart)
b.pack(side=LEFT, padx=5, pady=5)
b = Button(frame3, text="Stop", width=Buttonwidth2, command=BStop)
b.pack(side=LEFT, padx=5, pady=5)

b = Button(frame3, text="-Time", width=Buttonwidth2, command=lambda : BTime1(channel1))
b.pack(side=LEFT, padx=5, pady=5)

b = Button(frame3, text="+Time", width=Buttonwidth2, command=lambda : BTime2(channel1))
b.pack(side=LEFT, padx=5, pady=5)

b = Button(frame3, text="-CH1", width=Buttonwidth2, command= lambda : BCHlevel1(channel1))
b.pack(side=LEFT, padx=5, pady=5)

b = Button(frame3, text="+CH1", width=Buttonwidth2, command= lambda : BCHlevel2(channel1))
b.pack(side=LEFT, padx=5, pady=5)
# Devicebox2=ttk.Combobox(frame1, width=Buttonwidth1, postcommand=ReadInDevice, values=Devicename2, )
# Devicebox2.pack(side=RIGHT, padx=5, pady=5)
# Devicebox2.bind("<<ComboboxSelected>>",change_1)
#l = Label(frame1,text="Devices:",background="#000080",fg="#ffffff")
#l.pack(side=RIGHT, padx=5, pady=5)
title.trace_variable('w', BSetup)
if __name__ == '__main__':
    root.update()
    _thread.start_new(generate, ())
    AUDIOin()


