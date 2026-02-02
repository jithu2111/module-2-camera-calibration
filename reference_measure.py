import cv2
import numpy as np
import math

# --- CONFIGURATION ---
IMAGE_PATH = '40023.jpg'
# Standard Credit Card/ID width is usually 85.6mm.
# You can stick to 84.14mm if you measured it specifically.
REF_OBJECT_REAL_WIDTH = 84.14

#IPhone 5 actual heigh is

# --- LOAD IMAGE ---
raw_img = cv2.imread(IMAGE_PATH)
if raw_img is None:
    print(f"Error: Could not load {IMAGE_PATH}")
    exit()

# --- CALCULATE SCALE FACTOR ---
# We want the image to fit on a typical screen (e.g., 800px tall)
# This calculates how much we need to shrink it.
TARGET_HEIGHT = 800
h, w = raw_img.shape[:2]
SCALE_FACTOR = TARGET_HEIGHT / h
print(f"Original Size: {w}x{h}")
print(f"Scaling by {SCALE_FACTOR:.2f} to fit screen.")

# --- GLOBAL VARIABLES ---
ref_points = []
img_display = None  # The small image we see
img_clean = None  # Clean copy to reset
pixels_per_metric = None


def click_event(event, x, y, flags, param):
    global ref_points, img_display, pixels_per_metric

    if event == cv2.EVENT_LBUTTONDOWN:
        # 1. VISUAL: Draw on the small display image
        cv2.circle(img_display, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Reference Strategy", img_display)

        # 2. MATH: Convert display click back to ORIGINAL image coordinates
        # We divide by scale factor to "un-shrink" the coordinate
        real_x = x / SCALE_FACTOR
        real_y = y / SCALE_FACTOR
        ref_points.append((real_x, real_y))

        # --- LOGIC ---
        if len(ref_points) == 2:
            # --- MEASURE REFERENCE (ID CARD) ---
            pt1 = ref_points[0]
            pt2 = ref_points[1]

            # Calculate distance using REAL (large) coordinates
            dist_px_real = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
            pixels_per_metric = dist_px_real / REF_OBJECT_REAL_WIDTH

            print(f"\n--- REFERENCE SET ---")
            print(f"Ref Pixels (Real): {dist_px_real:.2f}")
            print(f"Ratio: {pixels_per_metric:.2f} px/mm")
            print(">> Now click the Width of the PHONE.")

            # Draw line on display (using visual coordinates)
            pt1_vis = (int(pt1[0] * SCALE_FACTOR), int(pt1[1] * SCALE_FACTOR))
            pt2_vis = (int(pt2[0] * SCALE_FACTOR), int(pt2[1] * SCALE_FACTOR))
            cv2.line(img_display, pt1_vis, pt2_vis, (0, 0, 255), 2)
            cv2.imshow("Reference Strategy", img_display)

        elif len(ref_points) == 4:
            # --- MEASURE TARGET (PHONE) ---
            pt3 = ref_points[2]
            pt4 = ref_points[3]

            target_px_real = math.sqrt((pt4[0] - pt3[0]) ** 2 + (pt4[1] - pt3[1]) ** 2)
            target_mm = target_px_real / pixels_per_metric

            print(f"\n--- TARGET RESULT ---")
            print(f"Phone Width: {target_mm:.2f} mm")

            # Draw line on display
            pt3_vis = (int(pt3[0] * SCALE_FACTOR), int(pt3[1] * SCALE_FACTOR))
            pt4_vis = (int(pt4[0] * SCALE_FACTOR), int(pt4[1] * SCALE_FACTOR))
            cv2.line(img_display, pt3_vis, pt4_vis, (0, 255, 0), 2)

            # Draw Text
            mid_x = (pt3_vis[0] + pt4_vis[0]) // 2
            mid_y = (pt3_vis[1] + pt4_vis[1]) // 2
            cv2.putText(img_display, f"{target_mm:.1f}mm", (mid_x, mid_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("Reference Strategy", img_display)
            print("\nPress 'r' to reset or 'q' to quit.")


# --- MAIN EXECUTION ---

# Create the resized image for display
img_display = cv2.resize(raw_img, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
img_clean = img_display.copy()

print("INSTRUCTIONS:")
print(f"1. Click the LEFT and RIGHT edges of the ID CARD ({REF_OBJECT_REAL_WIDTH}mm).")
print("2. Click the LEFT and RIGHT edges of the PHONE.")

cv2.imshow("Reference Strategy", img_display)
cv2.setMouseCallback("Reference Strategy", click_event)

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        img_display[:] = img_clean[:]
        ref_points = []
        pixels_per_metric = None
        cv2.imshow("Reference Strategy", img_display)
        print("\n--- RESET ---")

cv2.destroyAllWindows()