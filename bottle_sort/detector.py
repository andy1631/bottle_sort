import torch
import pyrealsense2 as rs
import numpy as np
import cv2

def initialize_model(model_path):
    # Load pre-trained YOLOv5 object detection model from file
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)

    # Create pipeline
    pipeline = rs.pipeline()

    # Create configuration
    config = rs.config()

    # Enable depth stream
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Enable color stream
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Create depth sensor
    depth_sensor = pipeline.get_active_profile().get_device().first_depth_sensor()

    # Create depth scale
    depth_scale = depth_sensor.get_depth_scale()

    # Return initialized model, pipeline, and depth sensor
    return (model, pipeline, depth_sensor, depth_scale)

def get_detected_objects(model, pipeline, depth_sensor, depth_scale):
    # Wait for new frames
    frames = pipeline.wait_for_frames()

    # Get depth and color frames
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # Skip frames if any of them is None
    if not depth_frame or not color_frame:
        return []

    # Convert frames to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    # Apply colormap to depth image
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    # Resize depth colormap to match color image dimensions
    depth_colormap = cv2.resize(depth_colormap, (color_image.shape[1], color_image.shape[0]))

    # Run object detection on color image
    detections = model(color_image).pandas()

    # Loop over detected objects
    detected_objects = []
    for detection in detections.xyxy[0].to_dict(orient="records"):
        # Skip detections with low confidence
        if detection['confidence'] < 0.80:
            continue

        # Get object class and confidence
        cls = detection['name']
        conf = round(detection['confidence'], 2)

        # Get bounding box coordinates
        xmin, ymin = int(detection['xmin']), int(detection['ymin'])
        xmax, ymax = int(detection['xmax']), int(detection['ymax'])

        # Compute center coordinates of bounding box
        x_center = (xmin + xmax) // 2
        y_center = (ymin + ymax) // 2
            # Get depth value at center of bounding box
        depth_val = depth_frame.get_distance(x_center, y_center)

        # Compute 3D position in meters from depth value and scale
        x_pos = (x_center - depth_frame.profile.intrinsics.ppx) * depth_val * depth_scale
        y_pos = (y_center - depth_frame.profile.intrinsics.ppy) * depth_val * depth_scale
        z_pos = depth_val

        # Extract color from class name
        color = cls.split('Bottle')[0]

        # Append detected object to list of detected objects
        detected_objects.append({
            'color': color,
            'position': (x_pos, y_pos, z_pos)
        })

    return detected_objects
 

def enable_preview(color_image, depth_colormap):
    # Loop until user presses escape key
    while True:
        # Show images
        cv2.namedWindow("Color", cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow("Depth", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Color", color_image)
        cv2.imshow("Depth", depth_colormap)
            # Check if user pressed escape key
        key = cv2.waitKey(1)
        if key == 27:
            break

    # Destroy windows
    cv2.destroyAllWindows()

