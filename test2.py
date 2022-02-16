from email.mime import image
import cv2
import tkinter as tk
from PIL import Image, ImageTk

cap = cv2.VideoCapture('/mnt/d/Splitgate Highlights/RAWs/ATLANTIS RACE.mp4')
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print( length )

success, im_arr = cap.read()

img = Image.fromarray(im_arr)

root = tk.Tk()
canvas = tk.Canvas(root)
canvas.pack()

imgtk = ImageTk.PhotoImage(img)

canvas.create_image(image=imgtk)