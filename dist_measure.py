import cv2
import numpy as np
import math

# --- CONFIGURATION ---
IMAGE_PATH = 'validation_2m.jpeg'
KNOWN_DISTANCE = 3020  # Distance in mm (Z)
ACTUAL_REAL_WIDTH = 84.14  # The Ground Truth width of the card (mm)
ACTUAL_REAL_HEIGHT = 51.0  # The Ground Truth height of the card (mm)

CALIB_WIDTH_ORIGINAL = 4000.0  # Resolution of your calibration images

# --- LOAD CALIBRATION DATA ---
try:
    with np.load('camera_params.npz') as data:
        mtx = data['mtx']
        dist = data['dist']
        print(f"Original Calibrated fx: {mtx[0, 0]:.2f} px")
except FileNotFoundError:
    print("ERROR: 'camera_params.npz' not found. Run Step 1 first.")
    exit()

# Global variables
ref_points = []
image_display = None
clean_image = None
FOCAL_LENGTH_X = 0
measurement_stage = "width"  # Track which measurement we're on: "width" or "height"
width_points = []
height_points = []
measured_width = 0
measured_height = 0


def click_event(event, x, y, flags, param):
    global ref_points, image_display, measurement_stage, width_points, height_points
    global measured_width, measured_height

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_points.append((x, y))
        cv2.circle(image_display, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Measurement", image_display)

        if len(ref_points) == 2:
            if measurement_stage == "width":
                # Calculate width
                width_points = ref_points.copy()
                measured_width = calculate_measurement(width_points, "Width")

                # Draw width measurement on image
                pt1, pt2 = width_points[0], width_points[1]
                cv2.line(image_display, pt1, pt2, (0, 255, 255), 2)
                mid = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)
                cv2.putText(image_display, f"Width: {measured_width:.1f}mm", (mid[0], mid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow("Measurement", image_display)

                # Wait 2 seconds before moving to height
                cv2.waitKey(2000)

                # Reset to clean image for height measurement (remove width line)
                image_display[:] = clean_image[:]

                # Update instruction text for height measurement
                instruction_text = "STEP 2: Measure HEIGHT (TOP to BOTTOM edge)"
                text_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                text_x = (image_display.shape[1] - text_size[0]) // 2
                text_y = 40
                cv2.rectangle(image_display, (text_x - 10, text_y - 30),
                              (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
                cv2.putText(image_display, instruction_text, (text_x, text_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
                cv2.imshow("Measurement", image_display)

                # Move to height measurement
                measurement_stage = "height"
                ref_points = []
                print("\n--- STEP 2: Measure HEIGHT ---")
                print("Click the TOP edge, then the BOTTOM edge of the object.")

            elif measurement_stage == "height":
                # Calculate height
                height_points = ref_points.copy()
                measured_height = calculate_measurement(height_points, "Height")

                # Draw height measurement on image
                pt1, pt2 = height_points[0], height_points[1]
                cv2.line(image_display, pt1, pt2, (255, 0, 255), 2)
                mid = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)
                cv2.putText(image_display, f"Height: {measured_height:.1f}mm", (mid[0] + 10, mid[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                cv2.imshow("Measurement", image_display)

                # Display final results
                display_final_results()

                # Wait 3 seconds then close window and exit program
                cv2.waitKey(3000)
                cv2.destroyAllWindows()
                exit()


def calculate_measurement(points, dimension_name):
    """Calculate the real-world measurement from two points"""
    pt1 = points[0]
    pt2 = points[1]

    # Calculate pixel distance
    pixel_distance = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)

    # Real measurement formula (Perspective Projection)
    # Measurement = (Z * pixel_distance) / f_x
    real_measurement = (KNOWN_DISTANCE * pixel_distance) / FOCAL_LENGTH_X

    print(f"\n--- {dimension_name} Measurement ---")
    print(f"Pixel Distance: {pixel_distance:.1f} px")
    print(f"Measured {dimension_name}: {real_measurement:.2f} mm")

    return real_measurement


def display_final_results():
    """Display final results with error calculations for both width and height"""
    # Calculate errors
    width_error = abs(measured_width - ACTUAL_REAL_WIDTH) / ACTUAL_REAL_WIDTH * 100
    height_error = abs(measured_height - ACTUAL_REAL_HEIGHT) / ACTUAL_REAL_HEIGHT * 100

    print(f"\n{'='*50}")
    print(f"{'FINAL RESULTS':^50}")
    print(f"{'='*50}")
    print(f"Distance from camera: {KNOWN_DISTANCE} mm\n")

    print(f"WIDTH:")
    print(f"  Measured: {measured_width:.2f} mm")
    print(f"  Actual:   {ACTUAL_REAL_WIDTH:.2f} mm")
    print(f"  Error:    {width_error:.2f} %\n")

    print(f"HEIGHT:")
    print(f"  Measured: {measured_height:.2f} mm")
    print(f"  Actual:   {ACTUAL_REAL_HEIGHT:.2f} mm")
    print(f"  Error:    {height_error:.2f} %")
    print(f"{'='*50}")


# --- MAIN EXECUTION ---
raw_img = cv2.imread(IMAGE_PATH)
if raw_img is None:
    print(f"Error: Could not load {IMAGE_PATH}")
    exit()

# 1. SCALING FIX
current_h, current_w = raw_img.shape[:2]
scale_factor = current_w / CALIB_WIDTH_ORIGINAL

# Scale the focal length!
# Note: Using mtx[1,1] (fy) often gives better results for non-square pixels
FOCAL_LENGTH_X = mtx[0, 0] * scale_factor

print(f"Current Image Width:  {current_w}")
print(f"Scale Factor:         {scale_factor:.4f}")
print(f"New Adjusted fx:      {FOCAL_LENGTH_X:.2f} px")

# 2. Undistort (Optional but recommended)
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (current_w, current_h), 1, (current_w, current_h))
dst = cv2.undistort(raw_img, mtx, dist, None, newcameramtx)
x, y, w, h = roi
dst = dst[y:y + h, x:x + w]

image_display = dst.copy()
clean_image = dst.copy()

# Add instruction text to the image window
instruction_text = "STEP 1: Measure WIDTH first (LEFT to RIGHT edge)"
text_size = cv2.getTextSize(instruction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
text_x = (image_display.shape[1] - text_size[0]) // 2
text_y = 40

# Add background rectangle for better visibility
cv2.rectangle(image_display, (text_x - 10, text_y - 30),
              (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)
cv2.putText(image_display, instruction_text, (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

print("\n--- READY ---")
print("STEP 1: Measure WIDTH - Click the LEFT edge, then the RIGHT edge of the object.")
print("Press 'q' to quit.")

cv2.imshow("Measurement", image_display)
cv2.setMouseCallback("Measurement", click_event)

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()