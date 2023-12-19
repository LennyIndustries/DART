import cv2
import numpy as np

def detect_score(frame):
    try:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to the grayscale image to remove noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges using Canny edge detection
        edges = cv2.Canny(blur, 50, 150)

        # Detect circles using HoughCircles()
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)

        if circles is not None:
            # Extract circle information
            circle = np.round(circles[0, :]).astype("int")[0]

            # Draw the outer circle
            cv2.circle(frame, (circle[0], circle[1]), circle[2], (0, 255, 0), 4)

            # Apply flood fill algorithm
            h, w = frame.shape[:2]
            mask = np.zeros((h+2, w+2), np.uint8)
            cv2.floodFill(frame, mask, (int(circle[0]), int(circle[1])), 255)

            # Find contours of the circle and the points inside the circle
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            # Filter contours to keep only the points inside the circle
            points = []
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                if cv2.pointPolygonTest(c, (x, y), False) >= 0:
                    points.append((x, y))

            # Draw the points inside the circle
            for point in points:
                cv2.circle(frame, point, 2, (0, 0, 255), -1)

    except Exception as e:
        print(f"Error: {e}")

    return frame

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_score(frame)
    cv2.imshow('image', frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27: # Escape key to stop
        break

cap.release()
cv2.destroyAllWindows()