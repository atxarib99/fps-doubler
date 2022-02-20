#!/user/bin/env python

from tracemalloc import start
import cv2
import numpy as np
import time
from PIL import Image, ImageTk
import tkinter as tk
import sys
import argparse

#quick debug switch to limit calc for testing
debug = False
quiet = False

#maybe just do better arg handling
args = sys.argv

parser = argparse.ArgumentParser()

parser.add_argument('--quiet', dest='quiet', action='store_true')
parser.add_argument('--debug', dest='debug', action='store_true')
parser.add_argument('--frames', dest='framestouse', type=int)
parser.add_argument('--visual', dest='visual', action='store_true')
parser.set_defaults(quiet=False)
parser.set_defaults(debug=False)
parser.set_defaults(visual=False)
parser.set_defaults(framestouse=2)
args = parser.parse_args()

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
#frames calculated
frames_calculated = 0

#TODO: There is a unoptimatal solution where we READ,TARGET,READ frames then all three frames get scrapped. When extended out, some frames could be used as reference once and then a target for the next. this is easily fixable by just adding and removing frames
#ie somethign like pastframes = [] targetframe=x futureframes=[] then when iterating, pastframes[0] gets dropped, target frame moves to pastframes[len -1], futureframe[0] becomes target, new frame pulled becomes futureframe[len-1]
#method that performs interpolation that allows number of reference frames to be define
def interpolate(framestouse=2):
    #define globals needed
    global video
    global final_err
    global count
    global frames_calculated
    global starttime
    global success
    global max_err
    global min_err

    #force frames to use to even number/ always up
    while framestouse / 2 != framestouse // 2:
        framestouse += 1
        print("must use even number of frames to perform interpolation")


    while success:
        #internal count of frames used
        framesused = 0

        #limit debug to 1000 frame calc
        if args.debug and count > 1000:
            break
        
        starttime = time.time()
        
        #grab leading frames
        leadingframes = []
        for i in range(0, framestouse // 2):
            success, im_arr = video.read()
            leadingframes.append(im_arr)


        #grab target frame
        success, target_im_arr = video.read()
        
        #grab following frames
        followingframes = []
        for i in range(0, framestouse // 2):
            success, im_arr = video.read()
            followingframes.append(im_arr)
        
        #if we failedto grab a frame, we are done.
        if not success:
            break

        #if we should weight the frames
        #TODO: move this variable and pull from cmd line
        #TODO: rethink this. want to interpolate from many frames, but weighting them just darkens each frame
        weighting = False
        if weighting:
            #reverse list, doesnt matter for calc
            leadingframes.reverse()
            for i in range(0, len(leadingframes)):
                leadingframes[i] = leadingframes[i] * (.5 ** i)
             
            for i in range(0, len(followingframes)):
                leadingframes[i] = followingframes[i] * (.5 ** i)
             

        #calculate next frame from surrounding frames
        calc_im_arr = (sum(leadingframes) + sum(followingframes)) // framestouse
        
        #calculate error of calculated frame vs target
        calc_err = np.sum(np.absolute(target_im_arr - calc_im_arr))
        
        #save frame if this is lowest or highest error seen
        if max_err == 0 or calc_err > max_err:
            max_err = calc_err
            saveFrame(calc_im_arr, target_im_arr, 'max')
        if min_err == 0 or calc_err < min_err:
            min_err = calc_err
            saveFrame(calc_im_arr, target_im_arr, 'min')
        
        if not args.quiet:
            print(calc_err)
            print(str(count) + '/' + str(length), end='\r')
        #summate to final_err
        final_err += calc_err
        #increment usedframes
        count += (framestouse + 1)
        #increment frames calculated after using all these frames we only calculated one
        frames_calculated += 1



for i in range(2,12,2):
    
    #frames calculated
    frames_calculated = 0
    #get video and length
    video = cv2.VideoCapture('STADIUM RACE.mp4')
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    final_err = 0
    count = 0
    #interpolate(args.framestouse)
    interpolate(i)
    #average error over number of frames
    #hmm should this be over calculated frames? instead of total frames? probably.
    final_err /= frames_calculated

    #display final error
    print('FINAL ERROR: ', final_err)



if args.visual:
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

