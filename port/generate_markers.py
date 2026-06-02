"""
generate_markers.py — Smart Port ArUco Marker Generator
Run: python generate_markers.py
ඒකෙන් markers/ folder එකේ images save වෙනවා
"""

import cv2
import cv2.aruco as aruco
import numpy as np
import os

# Output folder
os.makedirs("markers", exist_ok=True)

# DICT_4X4_50 — app.py එකේ use කරන එකම dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# Marker size pixels (print කරන්න 500x500 හොඳයි)
MARKER_SIZE = 500
BORDER = 60  # White border

markers = {
    1: "SLOT_A1",
    2: "SLOT_A2",
    3: "SLOT_B1",
    4: "SLOT_B2",
    5: "TRUCK_01",
    6: "TRUCK_02",
}

for marker_id, label in markers.items():
    # Marker generate කරන්න
    marker_img = np.zeros((MARKER_SIZE, MARKER_SIZE), dtype=np.uint8)
    marker_img = aruco.generateImageMarker(aruco_dict, marker_id, MARKER_SIZE, marker_img, 1)

    # White border add කරන්න
    bordered = cv2.copyMakeBorder(
        marker_img,
        BORDER, BORDER, BORDER, BORDER,
        cv2.BORDER_CONSTANT,
        value=255
    )

    # Label text add කරන්න
    total_h = bordered.shape[0] + 80
    final_img = np.ones((total_h, bordered.shape[1]), dtype=np.uint8) * 255
    final_img[:bordered.shape[0], :] = bordered

    # ID number
    cv2.putText(final_img, f"ID: {marker_id}  |  {label}",
                (30, bordered.shape[0] + 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 2, cv2.LINE_AA)

    # Save
    filename = f"markers/marker_{marker_id}_{label}.png"
    cv2.imwrite(filename, final_img)
    print(f"✅ Saved: {filename}")

print("\n🎉 All markers saved to 'markers/' folder!")
print("Print each image at 5x5 cm or larger for best detection.")