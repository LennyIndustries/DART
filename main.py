import logging as log
import math
import time

import cv2
import numpy as np

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_score(**kwargs):
    """
    Calculate the score based on dartboard and dart coordinates.

    Parameters:
    - dartboard_coordinates (tuple): Tuple containing the (x, y) coordinates of the dartboard center (int / numpy.uint16, int / numpy.uint16).
    - dart_coordinates (tuple): Tuple containing the (x, y) coordinates of the dart (int / numpy.uint16, int / numpy.uint16).
    - dartboard_radius (int / numpy.uint16): Radius of the dartboard.
    - current_score (int / numpy.uint16): The current score, may not be negative. [Default = 0]

    Returns:
    - numpy.uint16: The calculated score.

    Raises:
    - ValueError: Missing parameter, data type mismatch, negative current_score, tuple does not have exactly 2 values
    """

    # Local variables
    dartboard_center_x = dartboard_center_y = dart_x = dart_y = dartboard_radius = current_score = 0

    """
    Check the parameters:
    - Required must be provided
    - Optional may be provided
    """
    required_params = ['dartboard_coordinates', 'dart_coordinates', 'dartboard_radius']
    optional_params = ['current_score']
    # Required
    for param in required_params:
        if param not in kwargs:
            raise ValueError(f'Missing required parameter: {param}')  # Parameter is missing
        if (param == 'dartboard_coordinates' or param == 'dart_coordinates') and not isinstance(kwargs[param], tuple):
            raise ValueError(f'{param} must be of type tuple, got {type(kwargs[param])}')  # Parameter is not the expected data type
        if param == 'dartboard_radius' and not isinstance(kwargs[param], (int, np.uint16)):
            raise ValueError(f'{param} must be of type integer or numpy.uint16, got {type(kwargs[param])}')  # Parameter is not the expected data type
    # Optional
    for param in kwargs:
        if param not in optional_params:  # Parameter is required and already checked
            continue
        elif param == 'current_score':
            if kwargs['current_score'] < 0:
                raise ValueError(f'{param} can not be lower than 0')  # Parameter is negative
            elif not isinstance(kwargs[param], (int, np.uint16)):
                raise ValueError(f'{param} must be of type integer or numpy.uint16, got {type(kwargs[param])}')  # Parameter is not the expected data type
            else:
                current_score = kwargs['current_score']

    """
    Check the tuples, count and data type
    """
    if len(kwargs['dartboard_coordinates']) != 2:
        raise ValueError(f'Dartboard coordinates should have exactly 2 values, X and Y, but got {len(kwargs["dartboard_coordinates"])} values.')  # Tuple does not have exactly 2 values
    elif not isinstance(kwargs['dartboard_coordinates'][0], (int, np.uint16)):
        raise ValueError(f'Dartboard coordinates must of type integer or numpy.uint16, got {type(kwargs["dartboard_coordinates"][0])} [0]')  # Parameter is not the expected data type
    elif not isinstance(kwargs['dartboard_coordinates'][1], (int, np.uint16)):
        raise ValueError(f'Dartboard coordinates must of type integer or numpy.uint16, got {type(kwargs["dartboard_coordinates"][1])} [1]')  # Parameter is not the expected data type
    if len(kwargs['dart_coordinates']) != 2:
        raise ValueError(f'Dart coordinates should have exactly 2 values, X and Y, but got {len(kwargs["dart_coordinates"])} values.')  # Tuple does not have exactly 2 values
    elif not isinstance(kwargs['dart_coordinates'][0], (int, np.uint16)):
        raise ValueError(f'Dart coordinates must of type integer or numpy.uint16, got {type(kwargs["dart_coordinates"][0])} [0]')  # Parameter is not the expected data type
    elif not isinstance(kwargs['dart_coordinates'][1], (int, np.uint16)):
        raise ValueError(f'Dart coordinates must of type integer or numpy.uint16, got {type(kwargs["dart_coordinates"][1])} [1]')  # Parameter is not the expected data type

    """
    Extract the data
    """
    # Extract coordinates
    dart_x, dart_y = kwargs['dart_coordinates']
    dartboard_center_x, dartboard_center_y = kwargs['dartboard_coordinates']
    # Get dartboard radius
    dartboard_radius = kwargs['dartboard_radius']

    """
    Black magic AKA Math
    """
    # Calculate distance from center
    distance_from_center = math.sqrt((dart_x - dartboard_center_x) ** 2 + (dart_y - dartboard_center_y) ** 2)

    # Calculate angle
    # 18° per score; 9° offset
    angle = math.atan2(dart_y - dartboard_center_y, dart_x - dartboard_center_x)  # Get angle
    angle = math.degrees(angle)  # Convert to degrees
    angle += (9 + (5 * 18))  # Apply offset, left of 20 is 0°, right of 20 is 18°, continues to increase clockwise
    angle = (angle + 360) % 360  # Get back to a 360° circle

    # Calculate radii
    bull = round(((12.7 / 451) * dartboard_radius))
    iris = round(((32 / 451) * dartboard_radius))
    triple_inner = round(((107 / (451 / 2)) * dartboard_radius) - ((8 / (451 / 2)) * dartboard_radius))
    triple_outer = round(((107 / (451 / 2)) * dartboard_radius))
    double_inner = round(((170 / (451 / 2)) * dartboard_radius) - ((8 / (451 / 2)) * dartboard_radius))
    double_outer = round(((170 / (451 / 2)) * dartboard_radius))  # Also end of board

    """
    Map the possible scores on the dartboard, going clockwise from 20 (top)
    """
    score_array = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    log.debug(f'Distance from center: {distance_from_center}; Angle: {angle}')

    """
    Calculate the score based on the location of the dart
    """
    multiplier = 1
    skip_score_calculation = False
    score = 0

    # Bull
    if 0 < distance_from_center < bull:
        log.info(f'Bull: 50')
        score = 50
        skip_score_calculation = True
    # Iris
    elif bull < distance_from_center < iris:
        log.info(f'Iris: 25')
        score = 25
        skip_score_calculation = True
    # Triple ring
    if triple_inner < distance_from_center < triple_outer:
        log.info(f'Triple: score * 3')
        multiplier = 3
    # Double ring
    elif double_inner < distance_from_center < double_outer:
        log.info(f'Double: score * 2')
        multiplier = 2
    # Out of bounds
    if double_outer < distance_from_center:
        log.info(f'Out of bounds: 0')
    # Calculate score
    elif not skip_score_calculation:
        for idx, calc in enumerate(range(0, 360, 18)):
            if calc < angle < (calc + 18):
                score = score_array[idx] * multiplier

    log.info(f'Score: {score} + {current_score}')
    # Total score
    total_score = np.uint16(score + current_score)
    # Return the score
    return total_score


def trackbar_change(x):
    pass


if __name__ == "__main__":
    dartboard_center_x = dartboard_center_y = dart_x = dart_y = dartboard_radius = last_score_time = 0
    circle_detected = dart_detected = False
    # Initialize camera
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Detected Circle")
    cv2.createTrackbar("Param1", "Detected Circle", 100, 2000, trackbar_change)
    cv2.createTrackbar("Param2", "Detected Circle", 50, 100, trackbar_change)
    cv2.createTrackbar("MinRadius", "Detected Circle", 135, 500, trackbar_change)
    cv2.createTrackbar("MaxRadius", "Detected Circle", 450, 500, trackbar_change)

    while True:
        ret, img = cap.read()
        img = cv2.flip(img, 1)
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
                    dartboard_center_x, dartboard_center_y, dartboard_radius = pt[0], pt[1], pt[2]
                    circle_detected = True

        # Draw the circumference of the circle and segments
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), dartboard_radius, (0, 255, 0), 2)
        for line in range(0, 20):
            xPos = round(dartboard_center_x + (dartboard_radius * math.cos(math.radians(9 + 18 * line))))
            yPos = round(dartboard_center_y + (dartboard_radius * math.sin(math.radians(9 + 18 * line))))
            cv2.line(img, (dartboard_center_x, dartboard_center_y), (xPos, yPos), (255, 0, 0), 1)

        # Calculate radii of dartboard zones
        radius_6 = round(((170 / (451 / 2)) * dartboard_radius))
        radius_5 = round(((170 / (451 / 2)) * dartboard_radius) - ((8 / (451 / 2)) * dartboard_radius))
        radius_4 = round(((107 / (451 / 2)) * dartboard_radius))
        radius_3 = round(((107 / (451 / 2)) * dartboard_radius) - ((8 / (451 / 2)) * dartboard_radius))
        radius_2 = round(((32 / 451) * dartboard_radius))
        radius_1 = round(((12.7 / 451) * dartboard_radius))

        # Draw inner circles
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_1, (255, 0, 255), 1)
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_2, (255, 0, 255), 1)
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_3, (255, 0, 255), 1)
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_4, (255, 0, 255), 1)
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_5, (255, 0, 255), 1)
        cv2.circle(img, (dartboard_center_x, dartboard_center_y), radius_6, (255, 0, 255), 1)

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
                    dart_x = int(M['m10'] / M['m00'])
                    dart_y = int(M['m01'] / M['m00'])
                    cv2.circle(img, (dart_x, dart_y), 5, (0, 0, 255), -1)
                    dart_detected = True

        # Periodic score calculation every 5 seconds
        if dart_detected and (time.time() - last_score_time > 5):
            score = get_score(dart_coordinates=(dart_x, dart_y), dartboard_coordinates=(dartboard_center_x, dartboard_center_y), dartboard_radius=dartboard_radius, current_score=0)
            log.debug(f'Score: {score}')
            last_score_time = time.time()

        # Display the resulting frame
        cv2.imshow("Detected Circle", img)
        if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
