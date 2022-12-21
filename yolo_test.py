import torch
import pyrealsense2 as rs
import numpy as np
import cv2

# Model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='./yolov5_model/yolov5n_klopfer/weights/best.pt')


pipeline = rs.pipeline()

config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30) 

# Start streaming
pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame: 
            continue
       
       # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape


        results = model(color_image).pandas().xyxy[0].to_dict(orient="records")
        for res in results:
            con = round(res['confidence'], 2)

            #if con < 0.80: continue

            cl = res['name']
            pos_min = (int(res['xmin']), int(res['ymin']))
            pos_max = (int(res['xmax']), int(res['ymax']))
            depth_value = depth_frame.get_distance(int((pos_min[0] + pos_max[0]) / 2), 
                    int((pos_min[1] + pos_max[1]) / 2))
            cv2.rectangle(color_image, pos_min , pos_max, (255, 0, 0), 2)
            cv2.putText(color_image, str(cl) + ' (' + str(tuple(((pos_min[0] + pos_max[0]) / 2 , (pos_min[1] + pos_max[1]) / 2, depth_value))) + ')', pos_min, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(cl + ', ' + str(((pos_min[0] + pos_max[0]) / 2 , (pos_min[1] + pos_max[1]) / 2, depth_value)))
        

        #results.print();
        # Show images
        cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Depth', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Color', color_image)
        cv2.imshow('Depth', depth_colormap)
        cv2.waitKey(1)
finally:
    pipeline.stop();

