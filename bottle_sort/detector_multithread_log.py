import threading
import torch
import pyrealsense2 as rs
import numpy as np
import cv2
from queue import Queue
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Create a global variable to store the preview state
preview_enabled = False

def model_thread(model_path, q):
    global preview_enabled
    # Initialize model, pipeline, depth sensor, and depth scale
    logger.debug('Initializing model...')
    model, pipeline, depth_intrinsics = initialize_model(model_path)
    logger.debug('Model initialized')
    
    # Run the model in an infinite loop
    while True:
        # Get the detected objects from the current frame
        logger.debug('Getting detected objects...')
        detected_objects, color_image, depth_colormap = get_detected_objects(model, pipeline, depth_intrinsics)
        if not q.empty(): q.get()
        q.put(detected_objects)
        logger.debug('Got detected objects')

        # Check if preview is enabled
        if preview_enabled:
            # Display preview
            logger.debug('Displaying preview...')
            display_preview(color_image, depth_colormap, detected_objects)
            logger.debug('Preview displayed')

def initialize_model(model_path):
    # Load pre-trained YOLOv5 object detection model from file
    logger.debug('Loading model...')
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
    #model.to(torch.device("cuda:0"))
    logger.debug('Model loaded')

    # Create pipeline
    logger.debug('Creating pipeline...')
    pipeline = rs.pipeline()
    logger.debug('Pipeline created')

    # Create configuration
    logger.debug('Creating configuration...')
    config = rs.config()
    logger.debug('Configuration created')

    # Enable depth stream
    logger.debug('Enabling depth stream...')
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    logger.debug('Depth stream enabled')

    # Enable color stream
    logger.debug('Enabling color stream...')
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    logger.debug('Color stream enabled')

    # Start streaming
    logger.debug('Starting streaming...')
    profile = pipeline.start(config)
    logger.debug('Streaming started')

    depth_intrinsics = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
    # Return initialized model, pipeline, and depth sensor
    return (model, pipeline, depth_intrinsics)

def get_detected_objects(model, pipeline, depth_intrinsics):
    # Wait for new frames
    logger.debug('Waiting for new frames...')
    frames = pipeline.wait_for_frames()
    logger.debug('Got new frames')

    # Get depth and color frames
    logger.debug('Getting depth and color frames...')
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
    logger.debug('Running object detection on color image...')
    detections = model(color_image).pandas()
    logger.debug('Object detection finished')

    # Loop over detected objects
    detected_objects = []
    for detection in detections.xyxy[0].to_dict(orient="records"):
        # Skip detections with low confidence
        #if detection['confidence'] < 0.80:
        #    continue

        # Get object class and confidence
        cls = detection['name']
        if cls == "GreenBottle": continue
        conf = round(detection['confidence'], 2)

        # Get bounding box coordinates
        xmin, ymin = int(detection['xmin']), int(detection['ymin'])
        xmax, ymax = int(detection['xmax']), int(detection['ymax'])

        cv2.rectangle(color_image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
        # Compute center coordinates of bounding box
        x_center = (xmin + xmax) // 2
        y_center = ((ymin + ymax) // 2)
        # Get depth value at center of bounding box
        depth_value = depth_frame.get_distance(x_center, y_center)

        pos_x = (x_center - depth_intrinsics.ppx) * depth_value / depth_intrinsics.fx 
        pos_y = (y_center - depth_intrinsics.ppy) * depth_value / depth_intrinsics.fy
        # Skip object if depth value is invalid
        if np.isnan(depth_value) or np.isinf(depth_value):
            continue

        # Append detected object to list
        detected_objects.append((cls, conf, x_center, y_center, pos_x, pos_y, depth_value))
        logger.info('Detected object: %s with confidence %.2f', cls, conf)

    # Return detected objects and color and depth images
    return (detected_objects, color_image, depth_colormap)

def display_preview(color_image, depth_colormap, detected_objects):
    # Create image to display
    display_image = np.hstack((color_image, depth_colormap))

    # Loop over detected objects
    for detection in detected_objects:
        # Get object class, confidence, and coordinates
        cls, conf, x, y, pos_x, pos_y, depth = detection

        # Draw detection on image
        cv2.putText(display_image, f'{cls} ({conf:.2f})', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.circle(display_image, (x, y), 2, (255, 0, 0), -1)

    # Display image
    cv2.imshow('Preview', display_image)
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
