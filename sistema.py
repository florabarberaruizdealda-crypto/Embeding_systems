import cv2
from ultralytics import YOLO

model= YOLO('yolov8n.pt')

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error al abrir la cámara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret: 
        break
    results = model(frame)
    anotated_frame = results[0].plot()
    cv2.imshow('Object Detection', anotated_frame)
cap.release()
cv2.destroyAllWindows()