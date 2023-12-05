import cv2
import numpy as np

# Global variables
roi_defined = False

# Function to define the region of interest (ROI)
def define_roi():
    global roi_defined
    ix, iy, roi_width, roi_height = cv2.selectROI("Define ROI", frame, fromCenter=False)
    roi_defined = True
    return ix, iy, roi_width, roi_height

# Function for adaptive thresholding based on the ROI
def adaptive_thresholding(roi):
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    threshold_value = cv2.adaptiveThreshold(
        gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return threshold_value

# Open the video capture (0 for default camera)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    if not ret:
        break

    # If ROI is not defined, use keyboard input to specify the ROI
    if not roi_defined:
        ix, iy, roi_width, roi_height = define_roi()

    # If ROI is defined, perform adaptive thresholding within the ROI
    else:
        # Set the ROI based on user input
        roi = frame[iy:iy + roi_height, ix:ix + roi_width]

        # Apply adaptive thresholding to the ROI
        threshold_value = adaptive_thresholding(roi)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(
            threshold_value, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours based on area to reduce false positives
        min_contour_area = 500
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

        # Draw valid contours on the original frame, adjusting for ROI position
        for cnt in valid_contours:
            cnt_adjusted = cnt + (ix, iy)
            cv2.drawContours(frame, [cnt_adjusted], -1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Dart Detection", frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
