import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog
import PySimpleGUI as sg
import os

# global variables
ix, iy = -1, -1
drawing = False
point1, point2 = None, None
reference = None
real_world_distance = None
fullscreen = False

# function to open a dialog and ask for real world distance
def ask_for_distance():
    root = tk.Tk()
    root.withdraw()
    distance = simpledialog.askfloat("Input", "Please enter the real world distance for the reference:", minvalue=0.0)
    return distance

# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, point1, point2, reference, real_world_distance

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        if point1 is None:
            point1 = [ix, iy]
            cv2.circle(img, (ix, iy), 3, (0, 0, 255), -1)  # red point for point1
        elif point2 is None:
            point2 = [ix, iy]
            cv2.circle(img, (ix, iy), 3, (0, 0, 255), -1)  # red point for point2

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            pass

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if point1 is not None and point2 is not None:
            cv2.line(img, tuple(point1), tuple(point2), (0, 255, 0), 2)  # green line
            pixel_distance = np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

            if reference is None:  # if it is the first measurement
                reference = pixel_distance  # set the reference pixel distance
                real_world_distance = ask_for_distance()  # open a dialog to ask for distance
            else:  # calculate real world distance for the next measurements
                distance = round((pixel_distance / reference) * real_world_distance, 4)
                cv2.putText(img, str(distance), (point2[0], point2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # white text
            
            point1, point2 = None, None  # reset points

# PySimpleGUI window for file selection
layout = [  # layout for the GUI
    [sg.Text("Choose an image file to measure: ")],
    [sg.Input(), sg.FileBrowse(file_types=(("All Files", "*.*"),), key="-IN-"), sg.Button("Open")]
]

window = sg.Window("Image Selection", layout)

while True:
    event, values = window.read()
    if event == "Open":
        file_path = values["-IN-"]
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
            break
        else:
            sg.Popup('Error', 'Please select an image file (jpg, jpeg, png, bmp, tif, tiff)')
    elif event == sg.WINDOW_CLOSED:
        break

window.close()

# loading the image
img = cv2.imread(file_path)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('image', draw_circle)

while True:
    cv2.imshow('image', img)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('f'):  # 'f' for fullscreen
        fullscreen = not fullscreen
        if fullscreen:
            cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    elif key & 0xFF == 27:  # escape key
        break

cv2.destroyAllWindows()
