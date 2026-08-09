# 🚢 Smart Port — Container Yard Management System

An exhibition prototype that uses **computer vision** to monitor container yard slot occupancy and truck movement in real time, with a live web dashboard for port operators and admins.

---

## 📌 Overview

Traditional container yard tracking relies on manual checks or expensive fixed sensors. **Smart Port** uses a camera and **ArUco fiducial markers** to identify yard slots and trucks, letting a single video feed report free/occupied status and traffic activity live — a low-cost, camera-only alternative to hardware-heavy yard management systems.

## 🚀 Key Features

- **Marker-Based Detection** — ArUco markers (`DICT_4X4_50`) tag yard slots (`SLOT_A1`, `SLOT_A2`, `SLOT_B1`, `SLOT_B2`) and trucks (`TRUCK_01`, `TRUCK_02`), detected live via OpenCV.
- **Real-Time Occupancy Dashboard** — Streamlit web app shows free/occupied status per slot, live video feed, and traffic metrics.
- **Authentication & Roles** — Supabase-backed sign-in with **Admin** and **Operator** roles, bcrypt password hashing, and session tokens.
- **Marker Generator Utility** — Standalone script (`generate_markers.py`) to print physical ArUco markers for slots and trucks.

## 🛠️ Tech Stack

- **Computer Vision:** OpenCV (`opencv-python-headless`), `cv2.aruco`
- **Frontend / Dashboard:** Streamlit
- **Backend / Auth / DB:** Supabase (Postgres + Auth), `bcrypt` for password hashing
- **Language:** Python 3

## 📂 Project Structure

```
port/
├── pages/
│   └── app.py            # Main dashboard (post-login) — live feed, slot status, metrics
├── login_page.py         # Sign-in UI (entry point)
├── db.py                 # Supabase client, auth, and user helpers
├── generate_markers.py   # Generates printable ArUco marker images
├── markers/               # Generated marker images (slots + trucks)
└── requirements.txt
```

## ⚙️ Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (starts at the login page)
streamlit run login_page.py
```

Sign in with an admin or operator account to reach the live dashboard.

## 🎯 Status

Exhibition prototype (v1.0) — built as a proof of concept for low-cost, camera-based container yard monitoring.
