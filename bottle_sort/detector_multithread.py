import threading
import torch
import pyrealsense2 as rs
import numpy as np
import cv2
from queue import Queue 

# Create a global variable to store the preview state
preview_enabled = False

def model_thread(model_path, q):
    global preview_enabled
    # Initialize model, pipeline, depth sensor, and depth scale
    model, pipeline, depth_sensor, depth_scale = initialize_model(model_path)

    # Run the model in an infinite loop
    while True:
        # Get the detected objects from the current frame
        detected_objects, color_image, depth_colormap = get_detected_objects(model, pipeline, depth_sensor, depth_scale)
        if not q.empty(): q.get()
        q.put(detected_objects)

        # Check if preview is enabled
        if preview_enabled:
            # Display preview
            display_preview(color_image, depth_colormap, detected_objects)

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

        cv2.rectangle(color_image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
        # Compute center coordinates of bounding box
        x_center = (xmin + xmax) // 2
        y_center = (ymin + ymax) // 2
        # Get depth value at center of bounding box
        depth_val = depth_frame.get_distance(x_center, y_center)

        # Compute 3D position in meters from depth value and scale
        x_pos = x_center
        y_pos = y_center
        z_pos = depth_val

        # Extract color from class name
        color = cls.split('Bottle')[0]

        # Append detected object to list of detected objects
        detected_objects.append({
            'color': color,
            'position': (x_pos, y_pos, z_pos),
            'confidence': conf
        })

    return detected_objects, color_image, depth_colormap

def display_preview(color_image, depth_colormap, detected_objects):
    # Show images
    images = np.hstack((color_image, depth_colormap))
    cv2.imshow('RealSense', images)
    # Display detected objects in preview window
    for detection in detected_objects:
        color = detection['color']
        position = detection['position']
        conf = detection['confidence']
        cv2.putText(color_image, f'{color} ({conf}): {position}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Check if user pressed escape key
        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            global preview_enabled
            preview_enabled = False


def enable_preview():
    global preview_enabled
    preview_enabled = True

def disable_preview():
    global preview_enabled
    preview_enabled = False

def start_detection(model_path):
    q = Queue()
    # Start the model thread
    thread = threading.Thread(target=model_thread, args=(model_path, q))
    thread.start()
    return thread, q;

#def get_object_list():
    #return detected_objects
