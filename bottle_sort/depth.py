import pyrealsense2 as rs
import numpy as np
import cv2


# Create pipeline
pipeline = rs.pipeline()

# Create configuration
config = rs.config()

# Enable depth stream
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

pipeline.start(config)

while True:

    frames = pipeline.wait_for_frames()

    depth_frame = frames.get_depth_frame()

    depth_image = np.asanyarray(depth_frame.get_data())

    # Apply colormap to depth image
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    # Resize depth colormap to match color image dimensions
    #depth_colormap = cv2.resize(depth_colormap, (color_image.shape[1], color_image.shape[0]))


    # Create image to display

    # Display image
    cv2.imshow('Preview', depth_colormap)
    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyAllWindows()
        global preview_enabled
        preview_enabled = False

