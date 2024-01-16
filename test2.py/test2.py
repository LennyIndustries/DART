import cv2
import numpy as np
import math
import logging as log
import time

# Initialize logging
log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global Variables
dartboard_centerX, dartboard_centerY, dartboard_radius = 0, 0, 0
radius_1, radius_2, radius_3, radius_4, radius_5, radius_6 = [0] * 6
circle_detected = False
dart_detected = False
dartX, dartY = 0, 0
last_score_time = time.time()

def get_score():
    global dartboard_centerX, dartboard_centerY, dartboard_radius, dartX, dartY
    global radius_1, radius_2, radius_3, radius_4, radius_5, radius_6
    distanceFromCenter = math.sqrt((dartX - dartboard_centerX)**2 + (dartY - dartboard_centerY)**2)
    angle = math.atan2(dartY - dartboard_centerY, dartX - dartboard_centerX)
    angle = math.degrees(angle)
    angle += (9 + (5 * 18))
    angle = (angle + 360) % 360
    scoreArray = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    log.debug(f'Distance from center: {distanceFromCenter}; Angle: {angle}')
    multiplier = 1
    if 0 < distanceFromCenter < radius_1:
        log.info(f'Bull: 50')
        return 50
    elif radius_1 < distanceFromCenter < radius_2:
        log.info(f'Iris: 25')
        return 25
    if radius_3 < distanceFromCenter < radius_4:
        log.info(f'Triple: * 3')
        multiplier = 3
    elif radius_5 < distanceFromCenter < radius_6:
        log.info(f'Double: * 2')
        multiplier = 2
    if radius_6 < distanceFromCenter:
        log.info(f'Out of bounds: 0')
        return 0
    else:
        for idx, calc in enumerate(range(0, 360, 18)):
            if calc < angle < (calc + 18):
                score = scoreArray[idx] * multiplier
                log.info(f'Score: {score}')
                return score

def trackbar_change(x):
    pass

if __name__ == "__main__":
    # Initialize camera
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Detected Circle")
    cv2.createTrackbar("Param1", "Detected Circle", 100, 2000, trackbar_change)
    cv2.createTrackbar("Param2", "Detected Circle", 50, 100, trackbar_change)
    cv2.createTrackbar("MinRadius", "Detected Circle", 135, 500, trackbar_change)
    cv2.createTrackbar("MaxRadius", "Detected Circle", 450, 500, trackbar_change)

    while True:
        ret, img = cap.read()
        if not ret:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.blur(gray, (3, 3))

        # Detect circles if not already detected
        if not circle_detected:
            # Get current positions of trackbars
            param1 = cv2.getTrackbarPos("Param1", "Detected Circle")
            param2 = cv2.getTrackbarPos("Param2", "Detected Circle")
            minRadius = cv2.getTrackbarPos("MinRadius", "Detected Circle")
            maxRadius = cv2.getTrackbarPos("MaxRadius", "Detected Circle")

            # Apply Hough transform
            detected_circles = cv2.HoughCircles(gray_blurred,
                                                cv2.HOUGH_GRADIENT, 0.6, 50,
                                                param1=param1, param2=param2,
                                                minRadius=minRadius, maxRadius=maxRadius)

            # Draw circles and calculate dartboard dimensions
            if detected_circles is not None:
                detected_circles = np.uint16(np.around(detected_circles))
                for pt in detected_circles[0, :]:
                    a, b, r = pt[0], pt[1], pt[2]
                    dartboard_centerX, dartboard_centerY, dartboard_radius = a, b, r
                    circle_detected = True

                    # Draw the circumference of the circle and segments
                    cv2.circle(img, (a, b), r, (0, 255, 0), 2)
                    for line in range(0, 20):
                        xPos = round(a + (r * math.cos(math.radians(9 + 18 * line))))
                        yPos = round(b + (r * math.sin(math.radians(9 + 18 * line))))
                        cv2.line(img, (a, b), (xPos, yPos), (255, 0, 0), 1)

                    # Calculate radii of dartboard zones
                    radius_6 = round(((170 / (451 / 2)) * r))
                    radius_5 = round(((170 / (451 / 2)) * r) - ((8 / (451 / 2)) * r))
                    radius_4 = round(((107 / (451 / 2)) * r))
                    radius_3 = round(((107 / (451 / 2)) * r) - ((8 / (451 / 2)) * r))
                    radius_2 = round(((32 / 451) * r))
                    radius_1 = round(((12.7 / 451) * r))

                    # Draw inner circles
                    cv2.circle(img, (a, b), radius_1, (255, 0, 255), 1)
                    cv2.circle(img, (a, b), radius_2, (255, 0, 255), 1)
                    cv2.circle(img, (a, b), radius_3, (255, 0, 255), 1)
                    cv2.circle(img, (a, b), radius_4, (255, 0, 255), 1)
                    cv2.circle(img, (a, b), radius_5, (255, 0, 255), 1)
                    cv2.circle(img, (a, b), radius_6, (255, 0, 255), 1)

        # Convert to HSV color space for red dart detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        # Second range to cover hue value wrap-around
        lower_red = np.array([170, 120, 70])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)
        mask = mask1 + mask2

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Dart detection and position update
        if circle_detected:
            largest_contour = max(contours, key=cv2.contourArea, default=None)
            if largest_contour is not None and cv2.contourArea(largest_contour) > 20:  # Adjust threshold
                M = cv2.moments(largest_contour)
                if M['m00'] != 0:
                    dartX = int(M['m10'] / M['m00'])
                    dartY = int(M['m01'] / M['m00'])
                    cv2.circle(img, (dartX, dartY), 5, (0, 0, 255), -1)
                    dart_detected = True

        # Periodic score calculation every 5 seconds
        if dart_detected and (time.time() - last_score_time > 5):
            get_score()
            last_score_time = time.time()

        # Display the resulting frame
        cv2.imshow("Detected Circle", img)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
