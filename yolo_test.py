import torch

# Model
model = torch.load('yolov5_model/yolov5n_klopfer/weights/best.pt')

# Images
imgs = ['yolov5_model/detect/exp/11.jpg']  # batch of images

# Inference
results = model(imgs)

# Results
results.print()
results.save()  # or .show()

results.xyxy[0]  # img1 predictions (tensor)
results.pandas().xyxy[0]  # img1 predictions (pandas)
