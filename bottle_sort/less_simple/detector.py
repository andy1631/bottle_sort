import torch
import pyrealsense2 as rs
import numpy as np
import cv2 
import logging 
# Configure logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


color_ratios = {
        "blue": (0.0, 0.4, 0.6),
        "yellow": (0.8, 0.2, 0.0),
        "pink": (0.7, 0.0, 0.3)
        }


def init_camera():
    # Create pipeline
    logger.debug('Creating pipeline...')
    pipeline = rs.pipeline()
    logger.debug('Pipeline created')

    # Create configuration
    logger.debug('Creating configuration...')
    config = rs.config()
    logger.debug('Configuration created')

    # Enable color stream
    logger.debug('Enabling color stream...')
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    logger.debug('Color stream enabled')

    # Start streaming
    logger.debug('Starting streaming...')
    profile = pipeline.start(config)
    logger.debug('Streaming started')
    
    return pipeline



def init_model(model_path):
    # Load pre-trained YOLOv5 object detection model from file
    logger.debug('Loading model...')
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
    #model.to(torch.device("cuda:0"))
    logger.debug('Model loaded')
    # Return initialized model and pipeline
    return (model)

def get_image(pipeline):
    # Wait for new frames
    logger.debug('Waiting for new frames...')
    frames = pipeline.wait_for_frames()
    logger.debug('Got new frames')

    # Get depth and color frames
    logger.debug('Getting depth and color frames...')
    frame = frames.get_color_frame()

    # Convert frames to numpy arrays
    image = np.asanyarray(frame.get_data())

    return image


def get_detected_objects(image, model):
        # Run object detection on color image
    logger.debug('Running object detection on color image...')
    detections = model(image).pandas()
    logger.debug('Object detection finished')

    # Loop over detected objects
    detected_objects = []
    for detection in detections.xyxy[0].to_dict(orient="records"):
        # Skip detections with low confidence
        if detection['confidence'] < 0.80:
            continue

        # Get bounding box coordinates
        xmin, ymin = int(detection['xmin']), int(detection['ymin'])
        xmax, ymax = int(detection['xmax']), int(detection['ymax'])

        center_pos = (((xmin + xmax) // 2), ((ymin + ymax) // 2))

        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)

        # Append detected object to list
        detected_objects.append(center_pos)

    # Return detected objects and color and depth images
    return (detected_objects, image)

def get_color(image, pos):
    b, g, r = image[pos[1], pos[0]]
    s = int(b) + int(g) + int(r)
    ratio = (r / s, g / s, b / s)
    diff = {sum(abs(x - y) for x, y in zip(ratio, color_ratios["blue"])): "blue",
            sum(abs(x - y) for x, y in zip(ratio, color_ratios["yellow"])): "yellow",
            sum(abs(x - y) for x, y in zip(ratio, color_ratios["pink"])): "pink"
            }
    print(f"diff: {diff}")

    res = diff[min(diff.keys())]
    return res 



def display_preview(image):

    # Create image to display
    cv2.imshow('Preview', image)
    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyAllWindows()
        global preview_enabled
        preview_enabled = False

