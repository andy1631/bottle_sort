from detector_multithread_log import *
import threading

# Initialize model and start streaming
#start_detection("../yolov5_model/yolov5n_klopfer/weights/best.pt")
def print_results(q):
    while True: 
        if q.empty(): continue
        detected_objects = q.get() 
        # Print detected objects
        print(detected_objects)

def adjust(q)
    for i in range(10):
        if q.empty():
            i -= 1
            continue



t, q = start_detection("../yolov5_model/yolov5n_klopfer/weights/best.pt")

# Enable live preview
enable_preview()

# Get detected objects
t2 = threading.Thread(target=print_results, args=(q,))
t2.start()
t.join()
t2.join()


