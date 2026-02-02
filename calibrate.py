import numpy as np
import cv2
import glob
import os

# --- 1. SETTINGS ---
# Define the number of INNER corners (not squares)
# Tuple format: (Columns, Rows) -> (Width, Height)
CHECKERBOARD_LANDSCAPE = (9, 6)
CHECKERBOARD_PORTRAIT = (6, 9)

# UPDATE: Real world square size in millimeters
SQUARE_SIZE = 23

# --- 2. PREPARE IDEAL 3D OBJECT POINTS ---
# We need 3D coordinates for the corners in the real world (X, Y, Z=0)

def create_objpoints(board_size, square_size):
    """
    Generates the 3D points for a specific board dimension.
    board_size: tuple (cols, rows)
    """
    cols, rows = board_size

    # Create a grid of points
    # We use mgrid to create a grid of coordinates:
    # 0:cols generates x-coords (0, 1, ... 8)
    # 0:rows generates y-coords (0, 1, ... 5)
    objp = np.zeros((rows * cols, 3), np.float32)

    # The .T transpose ensures the order matches OpenCV's row-by-row scan
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)

    # Scale by the actual square size
    return objp * square_size


# Generate the two sets of points
objp_landscape = create_objpoints(CHECKERBOARD_LANDSCAPE, SQUARE_SIZE)
objp_portrait = create_objpoints(CHECKERBOARD_PORTRAIT, SQUARE_SIZE)

# Storage for results
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

# --- 3. LOAD IMAGES ---
# Make sure this path is correct for your folder structure!
image_path = 'calibration_images_3/*.jpg'
images = glob.glob(image_path)

print(f"Searching in: {image_path}")
print(f"Found {len(images)} images.")

if len(images) == 0:
    print("ERROR: No images found. Check your folder path.")
    exit()

count = 0

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"Warning: Could not read {fname}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strategy: Try Landscape first, if that fails, try Portrait

    # 1. Try Landscape (9, 6)
    ret, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD_LANDSCAPE,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    curr_objp = objp_landscape

    # 2. If Landscape failed, try Portrait (6, 9)
    if not ret:
        ret, corners = cv2.findChessboardCorners(
            gray,
            CHECKERBOARD_PORTRAIT,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE
        )
        curr_objp = objp_portrait

    # 3. If either worked, save the data
    if ret == True:
        objpoints.append(curr_objp)

        # Refine corner locations for higher accuracy
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        imgpoints.append(corners2)
        count += 1
        print(f"OK: {os.path.basename(fname)}")
    else:
        print(f"FAIL: {os.path.basename(fname)} (Corners not found)")

print(f"\n--- CALIBRATION ---")
print(f"Processing with {count} valid images...")

if count > 0:
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    print(f"Reprojection Error: {ret:.4f}")

    # Check quality
    if ret < 1.0:
        print("Result: EXCELLENT ✅")
    elif ret < 3.0:
        print("Result: ACCEPTABLE ⚠️")
    else:
        print("Result: BAD ❌ (Check lighting, flatness, or print quality)")

    print("\nCamera Matrix (K):\n", mtx)
    print("\nDistortion Coeffs (D):\n", dist)

    # Save the results for Step 2
    np.savez("camera_params.npz", mtx=mtx, dist=dist)
    print("\nSaved 'camera_params.npz' for the next step.")

else:
    print("Calibration failed: No valid images found.")