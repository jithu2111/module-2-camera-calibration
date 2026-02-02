import cv2
import glob

# 1. Check one of your Calibration images
calib_images = glob.glob('calibration_images_3/*.jpg')
if calib_images:
    img_calib = cv2.imread(calib_images[0])
    print(f"Calibration Image Size: {img_calib.shape[1]} x {img_calib.shape[0]}")
else:
    print("No calibration images found to check.")

# 2. Check your Step 2 Measurement image
# Replace with your actual step 2 filename
img_measure = cv2.imread('validation_2m.jpeg')
if img_measure is not None:
    print(f"Measurement Image Size: {img_measure.shape[1]} x {img_measure.shape[0]}")
else:
    print("Measurement image not found.")

ref_img = cv2.imread('40023.jpg')
if ref_img is not None:
    print(f"Reference Image Size: {ref_img.shape[1]} x {ref_img.shape[0]}")
else:
    print("Reference image not found.")