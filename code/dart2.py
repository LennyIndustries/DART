import cv2
import numpy as np

def detect_circle(frame):
    try:
        # Convert the frame to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create a binary mask using inRange()
        mask = cv2.inRange(hsv, (0, 0, 150), (180, 255, 255))

        # Apply Gaussian blur to the mask to remove noise
        mask = cv2.GaussianBlur(mask, (5, 5), 0)

        # Detect circles using HoughCircles()
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 100, param1=80, param2=40, minRadius=160, maxRadius=210)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

                # Draw the corresponding zone number based on the angle
                angle = np.arctan2(x - 320, 240 - y) * 180 / np.pi
                zone = int((angle + 18) / 36) + 1
                cv2.putText(frame, str(zone), (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return frame
    except Exception as e:
        print("Error: ", str(e))
        return frame

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_circle(frame)
    cv2.imshow('image', frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # Escape key to stop
        break

cap.release()
cv2.destroyAllWindows()