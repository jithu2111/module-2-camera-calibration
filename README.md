# Camera Calibration and Distance Measurement

A complete computer vision project implementing camera calibration using checkerboard patterns and real-world distance measurement using both reference-based and calibrated approaches.

---

## 📋 Table of Contents
- [Setup Instructions](#setup-instructions)
- [Execution Order](#execution-order)
- [Program Concepts](#program-concepts)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- pip (Python package installer)
- A camera or smartphone to capture calibration images

### 2. Create Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **OpenCV** (opencv-python): For image processing and camera calibration
- **NumPy**: For matrix operations and numerical computations

### 4. Verify Installation

```bash
python -c "import cv2; import numpy as np; print('OpenCV:', cv2.__version__); print('NumPy:', np.__version__)"
```

---

## 🎯 Execution Order

### Step 1: Camera Calibration
```bash
python calibrate.py
```
**What it does**: Processes checkerboard images and generates camera calibration parameters.

**Output**: `camera_params.npz` (camera intrinsic matrix and distortion coefficients)

### Step 2: View Calibration Results (Optional)
```bash
python check_matrix.py
```
**What it does**: Displays the calibration results in a readable format.

### Step 3: Check Image Resolutions (Optional)
```bash
python check_resolution.py
```
**What it does**: Verifies that calibration and measurement images have consistent resolutions.

### Step 4: Measurement Approaches

#### Option A: Reference-Based Measurement
```bash
python reference_measure.py
```
**Use case**: When you have a known reference object (like an ID card) in the same image as the object you want to measure.

#### Option B: Calibrated Distance Measurement
```bash
python dist_measure.py
```
**Use case**: When you know the distance to the object and want to use calibrated camera parameters for accurate measurements.

---

## 📚 Program Concepts

### 1. `calibrate.py` - Camera Calibration

#### Concept: Pinhole Camera Model
Every camera has intrinsic properties (focal length, optical center, lens distortion) that affect how 3D world points are projected onto the 2D image plane. Camera calibration determines these parameters.

#### How It Works:
1. **Checkerboard Pattern**: Uses a printed checkerboard with known dimensions (23mm squares)
2. **Corner Detection**: Automatically finds the inner corners of the checkerboard
3. **Multiple Views**: Processes 52+ images of the checkerboard from different angles and positions
4. **Optimization**: Uses OpenCV's `calibrateCamera()` to compute:
   - **Intrinsic Matrix (K)**: Contains focal lengths (fx, fy) and optical center (cx, cy)
   - **Distortion Coefficients**: Corrects lens distortion (barrel/pincushion effects)

#### Mathematical Representation:
```
Camera Matrix (K):
| fx   0   cx |
|  0  fy   cy |
|  0   0    1 |

where:
- fx, fy = focal lengths in pixels
- cx, cy = principal point (optical center)
```

#### Key Features:
- **Dual Orientation Support**: Handles both landscape (9×6) and portrait (6×9) orientations
- **Sub-pixel Accuracy**: Uses `cornerSubPix()` to refine corner locations
- **Quality Metrics**: Reports reprojection error (<1.0 = excellent, <3.0 = acceptable)

#### Reprojection Error:
Measures the average distance between detected corner points and where the calibration model predicts they should be. Lower values indicate better calibration.

---

### 2. `check_matrix.py` - Calibration Results Viewer

#### Concept: Understanding Camera Parameters
This utility helps interpret the calibration results by presenting them in a human-readable format.

#### What It Shows:
- **Intrinsic Matrix**: The 3×3 camera matrix with focal lengths and optical center
- **Focal Lengths**:
  - `fx`: Horizontal focal length (how much horizontal scaling occurs)
  - `fy`: Vertical focal length (should be close to fx for most cameras)
- **Optical Center**: Where the camera's optical axis intersects the image plane (usually near the image center)
- **Distortion Coefficients**:
  - `k1, k2, k3`: Radial distortion (lens curvature effects)
  - `p1, p2`: Tangential distortion (lens misalignment)

#### Why It Matters:
Understanding these parameters helps verify that calibration is realistic (e.g., optical center near image center, focal lengths similar in both axes).

---

### 3. `check_resolution.py` - Image Resolution Checker

#### Concept: Resolution Consistency
Camera calibration parameters are resolution-dependent. If you calibrate at one resolution and measure at another, you must scale the focal length proportionally.

#### What It Checks:
- Calibration images resolution (from `calibration_images_3/`)
- Measurement images resolution (`validation_2m.jpeg`, `validation_3m.jpeg`)
- Reference image resolution (`40023.jpg`)

#### Why It's Important:
- Focal length (fx, fy) is measured in pixels
- If image resolution changes, the effective focal length changes proportionally
- Formula: `fx_new = fx_original × (width_new / width_original)`

---

### 4. `reference_measure.py` - Reference-Based Measurement

#### Concept: Scale from Known Reference
This approach uses a reference object with known dimensions to establish a pixels-to-millimeters ratio, then measures other objects in the same plane.

#### How It Works:
1. **Reference Object**: User clicks the edges of a known-size object (ID card: 84.14mm)
2. **Calculate Ratio**: `pixels_per_mm = pixel_distance / real_distance`
3. **Measure Target**: User clicks edges of the target object (phone)
4. **Compute Size**: `real_width = pixel_distance / pixels_per_mm`

#### Mathematical Formula:
```
pixels_per_metric = distance_in_pixels / known_real_distance
target_size = target_pixels / pixels_per_metric
```

#### Advantages:
- Simple and intuitive
- No camera calibration needed
- Works well when reference and target are in the same plane

#### Limitations:
- Both objects must be at approximately the same distance from camera
- Sensitive to perspective distortion
- Cannot measure depth

#### Use Case:
Measuring everyday objects using a credit card or ID card as reference.

---

### 5. `dist_measure.py` - Calibrated Distance Measurement

#### Concept: Pinhole Camera Projection
Uses calibrated camera parameters and known distance to compute real-world dimensions based on the pinhole camera model.

#### Pinhole Camera Model:
```
w_pixel = (fx × W_real) / Z

Rearranged:
W_real = (Z × w_pixel) / fx

where:
- W_real = real-world width (mm)
- w_pixel = width in pixels
- fx = focal length (pixels)
- Z = distance from camera to object (mm)
```

#### How It Works:
1. **Load Calibration**: Reads camera matrix and distortion coefficients from `camera_params.npz`
2. **Resolution Scaling**: Adjusts focal length if measurement image has different resolution than calibration images
   - `fx_adjusted = fx_original × (current_width / calibration_width)`
3. **Undistortion**: Removes lens distortion using `cv2.undistort()` for accurate measurements
4. **Interactive Measurement**: User clicks object edges
5. **Compute Size**: Applies pinhole camera formula with known distance (3020mm = 3 meters)

#### Key Features:
- **Focal Length Scaling**: Automatically adjusts for resolution differences
- **Distortion Correction**: Removes lens distortion before measurement
- **Known Distance**: Requires accurate distance measurement (3m in this case)

#### Advantages:
- More accurate than reference-based approach
- Can measure objects at known distances
- Accounts for lens distortion
- Consistent across different images

#### Limitations:
- Requires accurate distance measurement
- Assumes object is perpendicular to camera
- Accuracy depends on calibration quality

#### Use Case:
Precise measurements in controlled environments (e.g., quality control, dimensional analysis) where distance can be measured accurately.

---

## 📁 Project Structure

```
.
├── calibrate.py              # Camera calibration script
├── check_matrix.py           # View calibration results
├── check_resolution.py       # Check image resolutions
├── reference_measure.py      # Reference-based measurement
├── dist_measure.py          # Calibrated distance measurement
├── camera_params.npz        # Calibration output (generated)
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── calibration_images_3/   # Checkerboard calibration images (52 images)
├── patterns/               # Calibration pattern references
│   ├── Checkerboard.png
│   ├── ChArUco_Targets_featured.png
│   └── acircles.png
│
├── 40023.jpg              # Reference measurement image
├── validation_2m.jpeg     # Validation at 2 meters
└── validation_3m.jpeg     # Validation at 3 meters
```


---

## 🤝 Interactive Usage

### For `reference_measure.py`:
1. Run the script
2. Click **LEFT** edge of ID card, then **RIGHT** edge
3. Click **LEFT** edge of phone, then **RIGHT** edge
4. Press 'r' to reset, 'q' to quit

### For `dist_measure.py`:
1. Run the script
2. Click **LEFT** edge of object, then **RIGHT** edge
3. Measurement appears for 2 seconds
4. Repeat for more measurements
5. Press 'q' to quit

---

*This project demonstrates practical computer vision techniques for camera calibration and real-world measurement applications.*