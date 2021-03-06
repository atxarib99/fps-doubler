#!/user/bin/env python

from tracemalloc import start
import cv2
import numpy as np
import time
from PIL import Image, ImageTk
import tkinter as tk

#quick debug switch to limit calc for testing
debug = False

#get video and length
video = cv2.VideoCapture('STADIUM RACE.mp4')
length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

#success is True if last frame was read sucessfully
success = True

#tkinter stuff
root = tk.Tk()

#holds the max/min error found
max_err = 0
min_err = 0

#holds the max/min calc+target frames
max_frame_calc = None
max_frame_target = None
min_frame_calc = None
min_frame_target = None

#save the calc vs target frame for outer boundaries
def saveFrame(calc_frame, target_frame, minormax):
    global max_frame_calc
    global min_frame_calc
    global max_frame_target
    global min_frame_target
    if minormax == 'max':
        max_frame_calc = calc_frame
        max_frame_target = target_frame
    else:
        min_frame_calc = calc_frame
        min_frame_target = target_frame

#total error. metric used to calculate performance of image generation
final_err = 0
#current frame count
count = 0
#timer for computation performance
starttime = 0
while success:
    #limit debug to 1000 frame calc
    if debug and count > 1000:
        break
    starttime = time.time()
    #grab primary frame
    success, im_arr = video.read()
    #grab target frame
    success, target_im_arr = video.read()
    #grab next frame
    success,next_im_arr = video.read()
    if not success:
        break
    
    #calculate next frame from surrounding frames
    calc_im_arr = (im_arr + next_im_arr) // 2
    
    #calculate error of calculated frame vs target
    calc_err = np.sum(np.absolute(target_im_arr - calc_im_arr))
    
    #save frame if this is lowest or highest error seen
    if max_err == 0 or calc_err > max_err:
        max_err = calc_err
        saveFrame(calc_im_arr, target_im_arr, 'max')
    if min_err == 0 or calc_err < min_err:
        min_err = calc_err
        saveFrame(calc_im_arr, target_im_arr, 'min')

    print(calc_err)
    print(str(count) + '/' + str(length), end='\r')
    #summate to final_err
    final_err += calc_err
    #grabbing 3 frames
    count += 3

#average error over number of frames
#hmm should this be over calculated frames? instead of total frames? probably.
final_err /= count

#display final error
print('FINAL ERROR: ', final_err)

#display calculated frame that had highest error
max_calc_canvas = tk.Canvas(root, width=1920, height=1080)
max_calc_canvas.pack()

max_frame_calc = max_frame_calc[...,[2,1,0]]
img = Image.fromarray(max_frame_calc)
imgtk = ImageTk.PhotoImage(img)
max_calc_canvas.create_image(0, 0, anchor=tk.NW, image = imgtk)
max_calc_canvas.create_text(100,10,text="max_frame_calc")
max_calc_canvas.pack()

#display target frame for highest error
root2 = tk.Toplevel(root)
max_target_canvas = tk.Canvas(root2, width=1920, height=1080)
max_target_canvas.pack()

img2 = Image.fromarray(max_frame_target)
imgtk2 = ImageTk.PhotoImage(img2)
max_target_canvas.create_image(0, 0, anchor=tk.NW, image = imgtk2)
max_target_canvas.create_text(100,10,text="max_frame_target")
max_target_canvas.pack()

#display calculated frame that had lowest error
root3 = tk.Toplevel(root)
min_calc_canvas = tk.Canvas(root3, width=1920, height=1080)
min_calc_canvas.pack()

img3 = Image.fromarray(min_frame_calc)
imgtk3 = ImageTk.PhotoImage(img3)
min_calc_canvas.create_image(0, 0, anchor=tk.NW, image = imgtk3)
min_calc_canvas.create_text(100,10,text="min_frame_calc")
min_calc_canvas.pack()

#display target frame for lowest error
root4 = tk.Toplevel(root)
min_target_canvas = tk.Canvas(root4, width=1920, height=1080)
min_target_canvas.pack()

img4 = Image.fromarray(min_frame_target)
imgtk4 = ImageTk.PhotoImage(img4)
min_target_canvas.create_image(0, 0, anchor=tk.NW, image = imgtk4)
min_target_canvas.create_text(100,10,text="min_frame_target")
min_target_canvas.pack()

#update tkinter canvases
root.update()
root2.update()
root3.update()
root4.update()

#let tkinter do its thang
root.mainloop()
