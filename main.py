import logging as log
import math

import cv2
import numpy as np

global mouseX, mouseY
global dartboard_centerX, dartboard_centerY, dartboard_radius
global radius_1, radius_2, radius_3, radius_4, radius_5, radius_6

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def draw_circle(event, x, y, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(img, (x, y), 2, (255, 255, 0), -1)
        mouseX, mouseY = x, y
        log.debug(f'X: {str(x)} Y: {str(y)}')
        try:
            dartboard_coordinates = (dartboard_centerX, dartboard_centerY)
            dart_coordinates = (x, y)
            get_score(dartboard_coordinates=dartboard_coordinates, dart_coordinates=dart_coordinates, dartboard_radius=dartboard_radius)
        except ValueError as e:
            log.exception(f'Error: {e}')
        except Exception as e:
            log.exception(f'An unexpected error occurred: {e}')


def get_score(**kwargs):
    """
    Calculate the score based on dartboard and dart coordinates.

    Parameters:
    - dartboard_coordinates (tuple): Tuple containing the (x, y) coordinates of the dartboard center (int / numpy.uint16, int / numpy.uint16).
    - dart_coordinates (tuple): Tuple containing the (x, y) coordinates of the dart (int / numpy.uint16, int / numpy.uint16).
    - dartboard_radius (int / numpy.uint16): Radius of the dartboard.
    - last_round (bool): Whether the function should consider if it is the last round or not. [Default = False]
    - current_score (int / numpy.uint16): The current score, may not be negative. [Default = 0]
    - max_score (int / numpy.uint16): The score at which the player can win, may not be negative. [Default = 501]

    Returns:
    - int: The calculated score.

    Raises:
    - ValueError: If required parameters are missing or if coordinate tuples do not have exactly 2 values or if an optional parameter is negative.
    """
    # Local variables
    dartboard_center_x = dartboard_center_y = dart_x = dart_y = dartboard_radius = current_score = 0
    max_score = 501
    last_round = can_win = False

    # Check params
    required_params = ['dartboard_coordinates', 'dart_coordinates', 'dartboard_radius']
    optional_params = ['last_round', 'current_score', 'max_score']
    # Required
    for param in required_params:
        if param not in kwargs:
            raise ValueError(f'Missing required parameter: {param}')  # Parameter is missing
        if (param == 'dartboard_coordinates' or param == 'dart_coordinates') and not isinstance(kwargs[param], tuple):
            raise ValueError(f'{param} must be of type tuple, got {type(kwargs[param])}')  # Parameter is not the expected data type
        if param == 'dartboard_radius' and not isinstance(kwargs[param], (int, np.uint16)):
            raise ValueError(f'{param} must be of type integer or numpy.uint16, got {type(kwargs[param])}')
    # Optional
    for param in kwargs:
        if param not in optional_params:
            continue
        if param == 'last_round':
            if isinstance(kwargs[param], bool):
                last_round = kwargs['last_round']
            else:
                raise ValueError(f'{param} must be of type boolean, got {type(kwargs[param])}')
        elif param == 'current_score':
            if kwargs['current_score'] < 0:
                raise ValueError(f'{param} can not be lower than 0')
            elif not isinstance(kwargs[param], (int, np.uint16)):
                raise ValueError(f'{param} must be of type integer or numpy.uint16, got {type(kwargs[param])}')
            else:
                current_score = kwargs['current_score']
        elif param == 'max_score':

            if kwargs['max_score'] < 0:
                raise ValueError(f'{param} can not be lower than 0')
            elif not isinstance(kwargs[param], (int, np.uint16)):
                raise ValueError(f'{param} must be of type integer or numpy.uint16, got {type(kwargs[param])}')
            else:
                max_score = kwargs['max_score']

    # Check the number of values and data type in each tuple
    if len(kwargs['dartboard_coordinates']) != 2:
        raise ValueError(f'Dartboard coordinates should have exactly 2 values, X and Y, but got {len(kwargs["dartboard_coordinates"])} values.')
    elif not isinstance(kwargs['dartboard_coordinates'][0], (int, np.uint16)):
        raise ValueError(f'Dartboard coordinates must of type integer or numpy.uint16, got {type(kwargs["dartboard_coordinates"][0])} [0]')
    elif not isinstance(kwargs['dartboard_coordinates'][1], (int, np.uint16)):
        raise ValueError(f'Dartboard coordinates must of type integer or numpy.uint16, got {type(kwargs["dartboard_coordinates"][1])} [1]')
    if len(kwargs['dart_coordinates']) != 2:
        raise ValueError(f'Dart coordinates should have exactly 2 values, X and Y, but got {len(kwargs["dart_coordinates"])} values.')
    elif not isinstance(kwargs['dart_coordinates'][0], (int, np.uint16)):
        raise ValueError(f'Dart coordinates must of type integer or numpy.uint16, got {type(kwargs["dart_coordinates"][0])} [0]')
    elif not isinstance(kwargs['dart_coordinates'][1], (int, np.uint16)):
        raise ValueError(f'Dart coordinates must of type integer or numpy.uint16, got {type(kwargs["dart_coordinates"][1])} [1]')

    # Extract coordinates
    dart_x, dart_y = kwargs['dart_coordinates']
    dartboard_center_x, dartboard_center_y = kwargs['dartboard_coordinates']
    # Get dartboard radius
    dartboard_radius = kwargs['dartboard_radius']

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

    # Score map
    # 20 -> 1 -> 18 -> 4 -> 13 -> 6 -> 10 -> 15 -> 2 -> 17 -> 3 -> 19 -> 7 -> 16 -> 8 -> 11 -> 14 -> 9 -> 12 -> 5
    score_array = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    log.debug(f'Distance from center: {distance_from_center}; Angle: {angle}')

    # Score logic
    multiplier = 1
    skip_score_calculation = False
    score = 0
    total_score = 0

    # Bull
    if 0 < distance_from_center < bull:
        log.info(f'Bull: 50')
        score = 50
        can_win = True
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
        can_win = True
    # Out of bounds
    if double_outer < distance_from_center:
        log.info(f'Out of bounds: 0')
        skip_score_calculation = True
    # Calculate score
    elif not skip_score_calculation:
        for idx, calc in enumerate(range(0, 360, 18)):
            if calc < angle < (calc + 18):
                score = score_array[idx] * multiplier
                log.info(f'Score: {score}')

    # Total score
    total_score = score + current_score

    # Checks if the player does get the core or not
    if last_round and not can_win:
        total_score = current_score
    if last_round and can_win:
        if total_score > max_score:
            total_score = current_score

    # Return the score
    return total_score


if __name__ == "__main__":
    # Read image.
    img = cv2.imread('dartboard2.jpg', cv2.IMREAD_COLOR)

    # Convert to grayscale.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Blur using 3 * 3 kernel.
    gray_blurred = cv2.blur(gray, (3, 3))

    # Apply Hough transform on the blurred image.
    detected_circles = cv2.HoughCircles(gray,
                                        cv2.HOUGH_GRADIENT, 0.6, 50, param1=1250,
                                        param2=50, minRadius=430, maxRadius=450)
    print("detected circles:\n{0}".format(detected_circles))
    # Draw circles that are detected.
    if detected_circles is not None:

        # Convert the circle parameters a, b and r to integers.
        detected_circles = np.uint16(np.around(detected_circles))

        for pt in detected_circles[0, :]:
            a, b, r = pt[0], pt[1], pt[2]
            dartboard_centerX = a
            dartboard_centerY = b
            dartboard_radius = r

            print("X: " + str(a) + ", Y: " + str(b) + ", R: " + str(r))

            # Draw the circumference of the circle.
            cv2.circle(img, (a, b), r, (0, 255, 0), 2)

            '''
            Draw lines
            Center: a, b
            20 triangles
            360° / 20 = 18°
            '''
            for line in range(0, 20):
                xPos = round(a + (r * math.cos(math.radians(9 + 18 * line))))
                yPos = round(b + (r * math.sin(math.radians(9 + 18 * line))))
                cv2.line(img, (a, b), (xPos, yPos), (255, 0, 0), 1)

            radius_6 = round(((170 / (451 / 2)) * r))
            radius_5 = round(((170 / (451 / 2)) * r) - ((8 / (451 / 2)) * r))
            radius_4 = round(((107 / (451 / 2)) * r))
            radius_3 = round(((107 / (451 / 2)) * r) - ((8 / (451 / 2)) * r))
            radius_2 = round(((32 / 451) * r))
            radius_1 = round(((12.7 / 451) * r))

            log.debug(
                f'\nR1: {radius_1}\nR2: {radius_2}\nR3: {radius_3}\nR4: {radius_4}\nR5: {radius_5}\nR6: {radius_6}')

            cv2.circle(img, (a, b), radius_1, (255, 0, 255), 1)
            cv2.circle(img, (a, b), radius_2, (255, 0, 255), 1)
            cv2.circle(img, (a, b), radius_3, (255, 0, 255), 1)
            cv2.circle(img, (a, b), radius_4, (255, 0, 255), 1)
            cv2.circle(img, (a, b), radius_5, (255, 0, 255), 1)
            cv2.circle(img, (a, b), radius_6, (255, 0, 255), 1)

            cv2.namedWindow("Detected Circle")
            cv2.setMouseCallback("Detected Circle", draw_circle)

            while 1:
                cv2.imshow("Detected Circle", img)
                if cv2.waitKey(20) & 0xFF == 27:
                    break
