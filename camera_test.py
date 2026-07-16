import cv2
from ultralytics import YOLO

model = YOLO("btcas_yolov8s_v2_best.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame)

    annotated = results[0].plot()

    cv2.imshow("BTCAS Camera", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

results = model(frame)

for r in results:
    if r.boxes is not None:
        print("Detections:", len(r.boxes))