import cv2
import numpy as np
import math
import logging as log

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
        get_score()


def get_score(**kwargs):
    distance_from_center = math.sqrt((kwargs['mouseX'] - kwargs['dartboard_center_x']) ** 2 + (kwargs['mouse_y'] - kwargs['dartboard_center_y']) ** 2)
    # 18° per score; 9° offset
    angle = math.atan2(kwargs['mouse_y'] - kwargs['dartboard_center_y'], kwargs['mouse_x'] - kwargs['dartboard_center_x'])
    angle = math.degrees(angle)
    angle += (9 + (5 * 18))
    angle = (angle + 360) % 360
    # 20 -> 1 -> 18 -> 4 -> 13 -> 6 -> 10 -> 15 -> 2 -> 17 -> 3 -> 19 -> 7 -> 16 -> 8 -> 11 -> 14 -> 9 -> 12 -> 5
    score_array = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    log.debug(f'Distance from center: {distance_from_center}; Angle: {angle}')
    multiplier = 1
    # Bull
    if 0 < distance_from_center < radius_1:
        log.info(f'Bull: 50')
        return 50
    # Iris
    elif radius_1 < distance_from_center < radius_2:
        log.info(f'Iris: 25')
        return 25
    # Triple ring
    if radius_3 < distance_from_center < radius_4:
        log.info(f'Triple: score * 3')
        multiplier = 3
    # Double ring
    elif radius_5 < distance_from_center < radius_6:
        log.info(f'Double: score * 2')
        multiplier = 2
    # Out of bounds
    if radius_6 < distance_from_center:
        log.info(f'Out of bounds: 0')
        return 0
    # Other
    else:
        for idx, calc in enumerate(range(0, 360, 18)):
            if calc < angle < (calc + 18):
                score = score_array[idx] * multiplier
                log.info(f'Score: {score}')
                return score


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
