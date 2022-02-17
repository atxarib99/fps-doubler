from email.mime import image
from time import sleep, time
import cv2
import tkinter as tk
from PIL import Image, ImageTk

cap = cv2.VideoCapture('/Users/aribdhuka/Pictures/lincoln 2019 enduro.mp4')
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print( length )

success = True
im_arr = None
#pick not first
for i in range(0,1000):
    success, im_arr = cap.read()

im_arr = im_arr[..., [2,1,0]]
img = Image.fromarray(im_arr)


root = tk.Tk()
canvas = tk.Canvas(root, width=1920, height=1080)
canvas.pack()

imgtk = ImageTk.PhotoImage(img)
# imgtk = ImageTk.BitmapImage(im_arr)
print(imgtk)

canvas.create_image(0, 0, anchor=tk.NW, image = imgtk)
canvas.pack()

root.update()

sleep(10)