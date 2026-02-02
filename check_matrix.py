import numpy as np

# Load the file
try:
    data = np.load("camera_params.npz")
    mtx = data['mtx']
    dist = data['dist']
except FileNotFoundError:
    print("Error: 'camera_params.npz' not found. Run calibration first.")
    exit()

print("==========================================")
print("       CAMERA CALIBRATION RESULTS         ")
print("==========================================")

# 1. The Intrinsic Matrix (K)
print("\nIntrinsic Matrix (K):")
print("---------------------")
print(f"| {mtx[0,0]:.2f}   {mtx[0,1]:.2f}   {mtx[0,2]:.2f} |")
print(f"| {mtx[1,0]:.2f}   {mtx[1,1]:.2f}   {mtx[1,2]:.2f} |")
print(f"| {mtx[2,0]:.2f}   {mtx[2,1]:.2f}   {mtx[2,2]:.2f} |")

# Interpretation
fx = mtx[0,0]
fy = mtx[1,1]
cx = mtx[0,2]
cy = mtx[1,2]

print(f"\n> Focal Length X (fx): {fx:.2f} pixels")
print(f"> Focal Length Y (fy): {fy:.2f} pixels")
print(f"> Optical Center     : ({cx:.2f}, {cy:.2f})")

# 2. Distortion Coefficients
print("\nDistortion Coefficients (Lens Curvature):")
print("-----------------------------------------")
print(f"k1: {dist[0,0]:.5f}")
print(f"k2: {dist[0,1]:.5f}")
print(f"p1: {dist[0,2]:.5f}")
print(f"p2: {dist[0,3]:.5f}")
print(f"k3: {dist[0,4]:.5f}")

print("\n==========================================")

