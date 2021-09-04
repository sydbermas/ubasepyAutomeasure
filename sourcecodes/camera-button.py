from main import pom
import tkinter as tk
import os
import cv2
import sys
from PIL import Image, ImageTk
import numpy as np

fileName = os.environ['ALLUSERSPROFILE'] + "\WebcamCap.txt"
cancel = False

def prompt_ok(event = 0):
    global cancel, button, button2
    cancel = True

    button.place_forget()
   
    # button1 = tk.Button(mainWindow, text="Good Image!", command=saveAndExit)
    button2 = tk.Button(mainWindow, text="Try Again", command=resume)
    # button1.place(anchor=tk.CENTER, relx=0.2, rely=0.9, width=150, height=50)
    button2.place(anchor=tk.CENTER, relx=0.8, rely=0.9, width=150, height=50)
    # button1.focus()
    saveAndExit()
    pom()

def def_pos(event = 0):
    

def saveAndExit(event = 0):
    global prevImg

    if (len(sys.argv) < 2):
        filepath = "calresult\\imageCap.jpg"
    else:
        filepath = sys.argv[1]

    print ("Output file to: " + filepath)
    prevImg.save(filepath)
    mainWindow.quit()


def resume(event = 0):
    global button1, button2, button, lmain, cancel

    cancel = False

    # button1.place_forget()
    button2.place_forget()

    mainWindow.bind('<Return>', prompt_ok)
    button.place(bordermode=tk.INSIDE, relx=0.5, rely=0.9, anchor=tk.CENTER, width=300, height=50)
    lmain.after(10, show_frame)

def changeCam(event=0, nextCam=-1):
    global camIndex, cap, fileName

    if nextCam == -1:
        camIndex += 1
    else:
        camIndex = nextCam
    del(cap)
    cap = cv2.VideoCapture(camIndex,cv2.CAP_DSHOW)

    #try to get a frame, if it returns nothing
    success, frame = cap.read()
    if not success:
        camIndex = 2
        del(cap)
        cap = cv2.VideoCapture(camIndex,cv2.CAP_DSHOW)

    f = open(fileName, 'w')
    f.write(str(camIndex))
    f.close()

try:
    f = open(fileName, 'r')
    camIndex = int(f.readline())
except:
    camIndex = 0

cap = cv2.VideoCapture(camIndex,cv2.CAP_DSHOW)
 
capWidth = cap.get(3)
capHeight = cap.get(4)


success, frame = cap.read()
if not success:
    if camIndex == 0:
        print("Error, No webcam found!")
        sys.exit(1)
    else:
        changeCam(nextCam=0)
        success, frame = cap.read()
        if not success:
            print("Error, No webcam found!")
            sys.exit(1)


mainWindow = tk.Tk(screenName="Camera Capture")
mainWindow.resizable(width=False, height=False)
mainWindow.bind('<Escape>', lambda e: mainWindow.quit())
lmain = tk.Label(mainWindow, compound=tk.CENTER, anchor=tk.CENTER, relief=tk.RAISED)
button = tk.Button(mainWindow, text="Capture", command=prompt_ok)
button1 = tk.Button(mainWindow,text="Set Position", command=def_pos)


button_changeCam = tk.Button(mainWindow, text="Switch Camera", command=changeCam)

lmain.pack()
button.place(bordermode=tk.INSIDE, relx=0.5, rely=0.9, anchor=tk.CENTER, width=300, height=50)
button.focus()
button1.place(bordermode=tk.INSIDE, relx=0.5, rely=0.9, anchor=tk.CENTER, width=300, height=50)
button1.focus()

button_changeCam.place(bordermode=tk.INSIDE, relx=0.85, rely=0.1, anchor=tk.CENTER, width=150, height=50)

def show_frame():
    global cancel, prevImg, button

    _, frame = cap.read()
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    prevImg = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=prevImg)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    if not cancel:
        lmain.after(10, show_frame)

# show_frame()

def show_pos():
    global cancel, prevImg, button1
    logo = cv2.imread('contours.png')
    # size = 400
    logo = cv2.resize(logo, (640, 480))
    img2gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)
    ret, frame = cap.read()
    if ret:
        # Flip the frame
        frame = cv2.flip(frame, 1)

        # Region of Image (ROI), where we want to insert logo
        roi = frame

        # Set an index of where the mask is
        roi[np.where(mask)] = 0
        roi += logo

    prevImg = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=prevImg)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    if not cancel:
        lmain.after(10, show_pos)

show_pos()
mainWindow.mainloop()