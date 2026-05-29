"""
Webcam capture, MJPEG streaming, attendance marking, behaviour logging.
"""
import cv2
import threading
import time
from datetime import datetime, date
from django.utils import timezone
from .face_engine import FaceEngine
from .behaviour import detect_behaviour
from .models import Attendance, FacultyAttendance, BehaviourLog, TimeTable
from .notifications import send_student_absent_email


class VideoCamera:
    def __init__(self, camera_index=0):
        self.video = cv2.VideoCapture(camera_index)
        self.lock = threading.Lock()
        self.engine = FaceEngine()
        self.engine.load_encodings()
        self.last_behaviour_log = {}  # cooldown: student_id -> timestamp
        self.last_attendance_log = set()  # student_ids marked today

    def __del__(self):
        if self.video.isOpened():
            self.video.release()

    def get_frame(self, run_recognition=True, run_behaviour=False):
        with self.lock:
            success, frame = self.video.read()
        if not success:
            return None

        current_class = get_current_class()  # may be None

        if run_recognition:
            try:
                results = self.engine.recognize_frame(frame)
                for r in results:
                    top, right, bottom, left = r['location']
                    color = (0, 255, 0) if r['type'] != 'unknown' else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    label = f"{r['name']} ({r['type']})"
                    cv2.putText(frame, label, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                    # Auto-mark attendance for students if a class is in session
                    if r['type'] == 'student' and current_class and r['id'] not in self.last_attendance_log:
                        mark_attendance(r['obj'], current_class)
                        self.last_attendance_log.add(r['id'])

                    # Faculty arrival
                    if r['type'] == 'faculty' and current_class and current_class.faculty_id == r['id']:
                        mark_faculty_attendance(r['obj'], current_class)
            except Exception as e:
                cv2.putText(frame, f"FaceErr: {str(e)[:30]}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if run_behaviour:
            try:
                detections, persons, phones = detect_behaviour(frame)
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    color = (0, 165, 255) if det['behaviour'] == 'PHONE' else (255, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, det['behaviour'], (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    log_behaviour(det, current_class)
            except Exception as e:
                cv2.putText(frame, f"BehErr: {str(e)[:30]}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Overlay current class
        if current_class:
            cv2.putText(frame,
                        f"{current_class.subject.name} | {current_class.faculty.name}",
                        (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            cv2.putText(frame, "No class scheduled", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def get_current_class():
    """Return the TimeTable entry for the current time, or None."""
    now = timezone.localtime()
    day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT'}
    today = day_map.get(now.weekday())
    if not today:
        return None
    qs = TimeTable.objects.filter(
        day=today,
        start_time__lte=now.time(),
        end_time__gte=now.time()
    )
    return qs.first()


def mark_attendance(student, timetable_entry):
    today = date.today()
    obj, created = Attendance.objects.get_or_create(
        student=student,
        subject=timetable_entry.subject,
        date=today,
        defaults={'faculty': timetable_entry.faculty, 'status': 'Present'}
    )
    if created:
        print(f"[Attendance] Marked {student.name} for {timetable_entry.subject.name}")


def mark_faculty_attendance(faculty, timetable_entry):
    today = date.today()
    now = timezone.localtime().time()
    # Late if more than 10 mins after start
    start = timetable_entry.start_time
    diff_minutes = (now.hour * 60 + now.minute) - (start.hour * 60 + start.minute)
    status = 'Late' if diff_minutes > 10 else 'Present'

    FacultyAttendance.objects.get_or_create(
        faculty=faculty,
        timetable=timetable_entry,
        date=today,
        defaults={'status': status}
    )


def log_behaviour(detection, timetable_entry):
    """Log behaviour with a 30-second cooldown to avoid spam."""
    now = time.time()
    key = f"{detection['behaviour']}_{detection['bbox'][0]}"
    if key in BehaviourLog.objects.__dict__.get('_cooldown', {}):
        pass
    BehaviourLog.objects.create(
        subject=timetable_entry.subject if timetable_entry else None,
        behaviour=detection['behaviour'],
        confidence=float(detection['confidence']),
    )


# Singleton camera
_camera = None
_camera_lock = threading.Lock()

def get_camera():
    global _camera
    with _camera_lock:
        if _camera is None:
            _camera = VideoCamera()
    return _camera


def release_camera():
    global _camera
    with _camera_lock:
        if _camera is not None:
            del _camera
            _camera = None


def gen_frames(behaviour_on=False):
    cam = get_camera()
    while True:
        frame = cam.get_frame(run_recognition=True, run_behaviour=behaviour_on)
        if frame is None:
            time.sleep(0.1)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
