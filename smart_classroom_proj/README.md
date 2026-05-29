# AI-Powered Smart Classroom Monitoring & Attendance System

A Django-based system using face recognition for automatic attendance, behaviour
analysis (phone usage / sleeping), timetable-driven faculty alerts, and parent
notifications for absent students.

## Tech Stack
- **Python:** 3.10 (recommended — works cleanly with all dependencies)
- **Backend:** Django 4.2
- **Frontend:** Django Templates + Bootstrap 5 + HTMX + Chart.js
- **Face Recognition:** OpenCV + face_recognition (dlib)
- **Behaviour Detection:** YOLOv8 (ultralytics)
- **Scheduling:** APScheduler
- **Database:** SQLite (dev) / MySQL or PostgreSQL (production)
- **Webcam:** OpenCV VideoCapture + MJPEG streaming

---

## Setup Instructions (Python 3.10)

### 1. Prerequisites

- **Python 3.10** (download from python.org if needed)
- A working webcam
- **Windows users:** No extra setup if using `dlib-bin` (recommended below)
- **Linux users:** `sudo apt install build-essential cmake libopenblas-dev liblapack-dev libx11-dev`
- **Mac users:** `brew install cmake`

### 2. Create virtual environment

```bash
cd smart_classroom_proj
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies — IMPORTANT: follow this order

This avoids the common `dlib` compilation errors.

```bash
pip install --upgrade pip setuptools wheel
pip install numpy==1.24.3
pip install cmake
```

**On Windows** (use the pre-built wheel — no C++ compiler needed):
```bash
pip install dlib-bin
```

**On Linux/Mac** (compiles from source):
```bash
pip install dlib
```

Then continue:
```bash
pip install face-recognition --no-deps
pip install face-recognition-models
pip install -r requirements.txt
```

### 4. Verify install

```bash
python -c "import face_recognition, cv2, ultralytics; print('All good!')"
```

If that prints `All good!`, you're ready.

### 5. Initialize database

```bash
python manage.py makemigrations attendance
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the server

```bash
python manage.py runserver
```
Open: **http://127.0.0.1:8000/**

---

## First-Time Usage

1. **Login** with the superuser credentials you created.
2. Go to **Admin Panel** (`/admin/`) and add:
   - At least one **Department** (e.g., "MCA", code "MCA")
   - At least one **Subject**
   - One or more **Faculty** entries via "Faculty" page (upload a clear front-facing photo)
   - One or more **Students** via "Students" page (clear photo required)
   - **Timetable** entries (day, time, subject, faculty)
3. Click **Live Monitor** → the webcam starts. Recognized students get auto-marked
   for the currently scheduled class. Toggle **Behaviour Detection** to also detect
   phone usage and sleeping.
4. Check **Attendance Report** and **Behaviour Report** for analytics.

---

## How Each Feature Maps to Your Abstract

| Abstract requirement                      | Implementation                          |
|-------------------------------------------|-----------------------------------------|
| Face recognition for students & faculty   | `attendance/face_engine.py`             |
| Multiple faces in one frame               | `face_recognition.face_locations()`     |
| Different angles, lighting, expressions   | dlib's HOG/CNN model handles this       |
| Mobile phone & sleep detection            | `attendance/behaviour.py` (YOLOv8)      |
| 10-min advance faculty alerts             | `scheduler.py` → `check_upcoming_classes` |
| HOD/Principal alert if faculty absent     | `scheduler.py` → `check_late_faculty`   |
| Parent notification if student absent     | `scheduler.py` → `notify_absent_students` (runs at 6 PM) |
| Centralized database                      | Django ORM (SQLite / MySQL)             |
| Reporting & analysis                      | `views.py` reports + Chart.js dashboards|

---

## Email Configuration (production)

Edit `smart_classroom/settings.py` and replace the console backend:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'   # Gmail App Password, not your real one
```

Also set HOD/Principal emails in `attendance/scheduler.py` (`check_late_faculty`).

---

## Switching to MySQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_classroom',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
Then: `pip install mysqlclient` and re-run migrations.

---

## Project Structure
```
smart_classroom_proj/
├── manage.py
├── requirements.txt
├── README.md
├── smart_classroom/         # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── attendance/              # Main app
│   ├── models.py            # DB schema (Student, Faculty, Attendance, etc.)
│   ├── views.py             # Request handlers
│   ├── urls.py
│   ├── admin.py
│   ├── forms.py
│   ├── face_engine.py       # Face recognition core
│   ├── behaviour.py         # YOLOv8 phone/sleep detection
│   ├── camera.py            # Webcam streaming + auto-attendance
│   ├── notifications.py     # Email alerts
│   └── scheduler.py         # APScheduler jobs
├── templates/attendance/    # HTML templates
└── media/                   # Uploaded photos (auto-created)
```

---

## Common Issues

| Problem | Fix |
|---|---|
| `dlib` won't install on Windows | Use `pip install dlib-bin` (pre-built wheel) |
| `dlib` fails on Linux | Install `build-essential cmake libopenblas-dev` first |
| Webcam opens but nothing shown | Another app is using the camera. Close it. |
| "No face detected in photo" | Use a clearer, well-lit, front-facing photo |
| Scheduler emails not sending | You're on console backend → check terminal output |
| YOLOv8 first run is slow | It downloads `yolov8n.pt` (~6 MB) once |
| ImportError: numpy | Make sure you installed `numpy==1.24.3` BEFORE other packages |

---

## Author
**Garikina Lakshmi Kanth** (Regd No: 24Q71F0016)
Department of MCA
Avanthi Institute of Engineering and Technology
