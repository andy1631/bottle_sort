import torch
import pyrealsense2 as rs

# Load the custom YOLOv5 model using PyTorch
model = torch.jit.load("yolov5_model/yolov5s_klopfer3/weights/last.pt")

# Initialize the camera
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Capture and process frames from the camera
try:
    while True:
        # Wait for a new frame from the camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        # Convert the frame to a NumPy array
        color_image = np.asanyarray(color_frame.get_data())

        # Use the model to detect objects in the frame
        detections = model(color_image)

        # Draw bounding boxes around the detected objects
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            label = detection["label"]
            confidence = detection["confidence"]
            color = (0, 255, 0)
            cv2.rectangle(color_image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(color_image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Show the frame with the detections
        cv2.imshow("Camera", color_image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # Stop the camera and close all windows
    pipeline.stop()
    cv2.destroyAllWindows()

