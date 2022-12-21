import pyrealsense2 as rs
import numpy as np
import cv2

pipeline = rs.pipeline()

config = rs.config()

config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30) 

# Start streaming
pipeline.start(config)
count = 0
try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
       
        #input("Press Enter for next preview...")
        #cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('Color', color_image)
        input("Press Enter for next image..." + str(count))
        cv2.imwrite('training_images/img_' + str(count) + '.png', color_image)
         
        count += 1


finally:
    pipeline.stop();

