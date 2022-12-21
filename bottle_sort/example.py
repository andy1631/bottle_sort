from detector import *

# Initialize model and start streaming
(model, pipeline, depth_sensor, depth_scale) = initialize_model("../yolov5_model/yolov5n_klopfer/weights/best.pt")
# Get detected objects
detected_objects, color_image, depth_colormap = get_detected_objects(model, pipeline, depth_sensor, depth_scale)

# Print detected objects
print(detected_objects)

# Enable live preview
#enable_preview(color_image, depth_colormap)

