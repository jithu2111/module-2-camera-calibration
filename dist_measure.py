import cv2
import numpy as np
import math

# --- CONFIGURATION ---
IMAGE_PATH = 'validation_3m.jpeg'
KNOWN_DISTANCE = 3020  # Distance in mm (Z)
ACTUAL_REAL_WIDTH = 84.14  # The Ground Truth width of the card (mm)

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


def click_event(event, x, y, flags, param):
    global ref_points, image_display

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_points.append((x, y))
        cv2.circle(image_display, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Measurement", image_display)

        if len(ref_points) == 2:
            calculate_and_display()
            ref_points = []
            # Wait 3 seconds so you can read it, then reset
            cv2.waitKey(3000)
            image_display[:] = clean_image[:]
            cv2.imshow("Measurement", image_display)


def calculate_and_display():
    pt1 = ref_points[0]
    pt2 = ref_points[1]

    # 1. Pixel Width
    pixel_width = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)

    # 2. Real Width Formula (Perspective Projection)
    # W_real = (Z * w_pixel) / f_x
    measured_width = (KNOWN_DISTANCE * pixel_width) / FOCAL_LENGTH_X

    # 3. --- ERROR CALCULATION CODE ---
    # Formula: |Measured - Actual| / Actual * 100
    error_percent = abs(measured_width - ACTUAL_REAL_WIDTH) / ACTUAL_REAL_WIDTH * 100

    print(f"\n--- Result ---")
    print(f"Distance from which object photo is taken: 3020mm")
    print(f"Pixel Width:    {pixel_width:.1f} px")
    print(f"Measured Width: {measured_width:.2f} mm")
    print(f"Actual Width:   {ACTUAL_REAL_WIDTH:.2f} mm")
    print(f"Error:          {error_percent:.2f} %")

    # 4. Draw line and text on image
    cv2.line(image_display, pt1, pt2, (0, 255, 255), 2)
    mid = ((pt1[0] + pt2[0]) // 2, (pt1[1] + pt2[1]) // 2)

    # Display Width
    cv2.putText(image_display, f"{measured_width:.1f}mm", (mid[0], mid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Display Error (in Red or Green depending on accuracy)
    color = (0, 255, 0) if error_percent < 5.0 else (0, 0, 255)  # Green if <5%, else Red
    cv2.putText(image_display, f"Err: {error_percent:.1f}%", (mid[0], mid[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Measurement", image_display)


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

print("\n--- READY ---")
print("Click the LEFT edge, then the RIGHT edge of the object.")
print("Press 'q' to quit.")

cv2.imshow("Measurement", image_display)
cv2.setMouseCallback("Measurement", click_event)

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()