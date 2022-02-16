#!/user/bin/env python

from tracemalloc import start
import cv2
import numpy as np
import time
from PIL import Image

video = cv2.VideoCapture('/mnt/d/Splitgate Highlights/RAWs/ATLANTIS RACE.mp4')
length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

success = True
# print(type(imarr))
# img = Image.fromarray(imarr)
# exit(0)

final_err = 0
count = 0
starttime = 0
while success:
    starttime = time.time()
    #grab primary frame
    success, im_arr = video.read()
    #grab target frame
    success, target_im_arr = video.read()
    #grab next frame
    success,next_im_arr = video.read()
    if not success:
        break
    #calculate difference between two frames
    # calc_im_arr = im_arr.copy()
    # for r in range(0, len(im_arr)):
    #     for c in range(0, len(im_arr[r])):
    #         for p in range(0, len(im_arr[r][c])):
    #             calc_im_arr[r][c][p] = (int(im_arr[r][c][p]) + int(next_im_arr[r][c][p])) / 2
    
    calc_im_arr = (im_arr + next_im_arr) / 2
    
    #calc err
    # for r in range(0, len(im_arr)):
    #     for c in range(0, len(im_arr[r])):
    #         for p in range(0, len(im_arr[r][c])):
    #             calc_err += abs((int(target_im_arr[r][c][p]) - int(calc_im_arr[r][c][p])))
    
    calc_err = np.sum(np.absolute(target_im_arr - calc_im_arr))

    print(calc_err)
    # print(str(count) + '/' + str(length) + " time taken: " + str(time.time() - starttime), end='\r')
    print(str(count) + '/' + str(length), end='\r')
    final_err += calc_err
    #grabbing 3 frames
    count += 3

final_err /= count

print('FINAL ERROR: ', final_err)

