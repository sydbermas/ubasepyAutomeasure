from os import name, system
import sys
from tkinter.constants import HORIZONTAL, LEFT, RIGHT
from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import tkinter as tk
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import Label, StringVar, ttk
from tkinter.messagebox import showinfo
import gspread
from numpy import empty
from oauth2client.client import Error
from oauth2client.service_account import ServiceAccountCredentials
import time
import pyautogui

scope = ["https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]

#CREDENTIALS FROM GOOGLE SERVICE ACCOUNT
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1Pfn_Dx_hEWGChU74iamO3BM4giSL7MpbuepGVo6_Bpk")  
styleDtlSheet = sheet.worksheet("code")
SamplePOMSheet = sheet.worksheet("RAWDATA")


#Set up GUI
window = tk.Tk()  #Makes main window
window.wm_title("Ubase Automeasure")
window.config(background="#FFFFFF")

#Graphics window
imageFrame = tk.Frame(window, width=600, height=500)
imageFrame.pack(side=LEFT, expand=False)

#Capture video frames
lmain = tk.Label(imageFrame)
lmain.pack(side=LEFT, expand=False) 
cap = cv.VideoCapture(0)
def show_frame():
    _, frame = cap.read()
    frame = cv.flip(frame, 1)
    cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame) 

# store email address and password
stylenum = tk.StringVar()
sizeset = tk.StringVar()
view = tk.StringVar()

views = ('Front', 'Back', 'Other')
selected_view = tk.StringVar()

sizes = ('XS', 'S', 'M','L', 'XL', 'XXL')
selected_sizes = tk.StringVar()


def proceed_clicked():
    global prevImg
    _, frame = cap.read()
    cv2image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    prevImg = Image.fromarray(cv2image)
    ImageTk.PhotoImage(image=prevImg)
    if (len(sys.argv) < 2):
        filepath = "Result.jpg"
    else:
        filepath = sys.argv[1]

    print ("Output file to: " + filepath)
    prevImg.save(filepath)

    """ callback when the button clicked
    """
    msg = f'You entered stylenum: {stylenum.get()}, stylenum: {sizeset_entry.get()}, and view: {view_entry.get()}. Please wait for the result'
    styleDtlSheet.update('B2', stylenum.get())
    styleDtlSheet.update('B3', sizeset_entry.get())
    styleDtlSheet.update('B4', view_entry.get())
    

    showinfo(
        title='Information',
        message=msg
    )
    pomIDs = styleDtlSheet.col_values(5)
    print(pomIDs)
    

    imageToBeInspected = 'calresult\\imageCap.jpg'    #acting as camera
    # pomID = '7M71906MFRONTLENGTHFROMHPS'   # change later for stylenum while loop
    
    for poms in pomIDs[1:]:

        try:
            
            cell = SamplePOMSheet.find(poms)
            
            pomID1 = (cell.row)
            # pomOffset =[[20,10,300,50]]
            offsetX = int(SamplePOMSheet.cell(pomID1,14).value)
            offsetY = int(SamplePOMSheet.cell(pomID1,15).value)
            offsetX2 = int(SamplePOMSheet.cell(pomID1,16).value)
            offsetY2 = int(SamplePOMSheet.cell(pomID1,17).value)
            pomOffset = [[offsetX,offsetY,offsetX2,offsetY2]]
            pomUID = SamplePOMSheet.cell(pomID1,2).value
            styleName = SamplePOMSheet.cell(pomID1,3).value
            output1 = 'subImages\\'+styleName+'\subImg1\\'+pomUID+'.JPG'
            output2 = 'subImages\\'+styleName+'\subImg2\\'+pomUID+'.JPG'
            print(pomOffset)
            pomIndex = 0
            pixelToInch = 16 #camera height - 39 inches to 40
            resultD = []

            # for pom in poms:

            img = cv.imread(imageToBeInspected,0)
            
            img2 = img.copy()
            
            templAB = cv.imread(output1,0) 
            templBA = cv.imread(output2,0)
            w, h = templAB.shape[::-1]
            w2, h2 = templBA.shape[::-1]
            # All the 6 methods for comparison in a list
            methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
                    'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
            meth = methods[1] # Mehtod setting
            img = img2.copy()
            methodAB = eval(meth)
            # Apply template Matchingpip i
            res = cv.matchTemplate(img,templAB,methodAB)
            res2 = cv.matchTemplate(img,templBA,methodAB)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            min_val2, max_val2, min_loc2, max_loc2 = cv.minMaxLoc(res2)
            
            # print(min_loc, max_loc, min_loc2, max_loc2)
            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if methodAB in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
                top_left = min_loc
                top_left2 = min_loc2
                
            else:
                top_left = max_loc
                top_left2 = max_loc2
                print (top_left)
                print (top_left2)

            subImg1pom = (top_left[0] + pomOffset[pomIndex][0], top_left[1] + pomOffset[pomIndex][1])
            
            subImg2pom = (top_left2[0] + pomOffset[pomIndex][2], top_left2[1] + pomOffset[pomIndex][3])
            
            resultD.append((subImg2pom[1]+subImg1pom[1])/pixelToInch)

            # Return True
            
            print(pomUID+":",round(resultD[pomIndex],2),"inches") # pom end
            SamplePOMSheet.update_cell(pomID1, 18 , (round(resultD[pomIndex],2)))
            
            text.set(str(styleDtlSheet.cell(2,6).value)+"/"+str(styleDtlSheet.cell(2,3).value))
            window.update_idletasks()
            
        except NameError as e:
            print(e)
            
        cv.rectangle(img,subImg1pom, subImg2pom, 255, 2)    
        cv.putText(img, str(round(resultD[pomIndex],2)) , (np.add(subImg2pom,[0,250])), cv.FONT_HERSHEY_SIMPLEX, 0.4, (36,255,12), 2, -1, )
        time.sleep(2.3)
    result = int(styleDtlSheet.cell(2,6).value)
    total = int(styleDtlSheet.cell(2,3).value)
    if result == total :
            # plt.subplot(121),plt.imshow(res,cmap = 'gray')
        # plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(121),plt.imshow(img,cmap = 'gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)
        mng = plt.get_current_fig_manager()
        mng.window.state("zoomed")
        plt.show()
        pomIndex +=1    #pomindex a to b
    else:
        showinfo(
            title='Information',
            message="Not completed!"
        )
    
def clear_clicked():
    
    """ callback when the button clicked
    """
    msg = f'You clear all data results!'
    # SamplePOMSheet.clear('R2:R', "")

    sheet.values_clear("RAWDATA!R2:R10000")
  
    showinfo(
        title='Information',
        message=msg
    )
    stylenum.set("")
    selected_sizes.set("")
    selected_view.set("")
    text.set("")    
    
# # Sign in frame
# proceed = ttk.Frame(window)
# proceed.pack(padx=10, pady=10, fill='x', expand=True)

# stylenums
stylenum_label = ttk.Label(window, text="Style Number:")
stylenum_label.pack(fill='x', expand=False)

stylenum_entry = ttk.Entry(window, textvariable=stylenum)
stylenum_entry.pack(fill='x', expand=False)
stylenum_entry.focus()

# sizesets
sizeset_label = ttk.Label(window, text="Sizeset:")
sizeset_label.pack(fill='x', expand=False)

sizeset_entry = ttk.Combobox(window, textvariable=selected_sizes)
sizeset_entry['values'] = sizes
sizeset_entry['state'] = 'readonly'  # normal
sizeset_entry.pack(fill='x', expand=False)

# views
view_label = ttk.Label(window, text="View:")
view_label.pack(fill='x', expand=False)

view_entry = ttk.Combobox(window, textvariable=selected_view)
view_entry['values'] = views
view_entry['state'] = 'readonly'  # normal
view_entry.pack(fill='x', expand=False)

# login button
proceed_button = ttk.Button(window, text="Proceed", command=proceed_clicked)
proceed_button.pack(fill='x', expand=False, pady=3)

# login button
clear_button = ttk.Button(window, text="Clear", command=clear_clicked)
clear_button.pack(fill='x', expand=False, pady=3)


text = StringVar()

taskLabel = Label(window,textvariable=text).pack(fill='x', expand=False)

show_frame()  #Display 2
window.mainloop()  #Starts GUI