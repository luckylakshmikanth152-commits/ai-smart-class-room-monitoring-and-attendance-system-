"""
Face recognition engine.
Loads all student/faculty face encodings from DB into memory and matches against webcam frames.
"""
import face_recognition
import numpy as np
import pickle
import cv2
from .models import Student, Faculty


class FaceEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load_encodings(self):
        """Load all known faces from DB."""
        self.student_encodings = []
        self.student_ids = []
        self.faculty_encodings = []
        self.faculty_ids = []

        for s in Student.objects.exclude(face_encoding=None):
            try:
                enc = pickle.loads(s.face_encoding)
                self.student_encodings.append(enc)
                self.student_ids.append(s.id)
            except Exception:
                pass

        for f in Faculty.objects.exclude(face_encoding=None):
            try:
                enc = pickle.loads(f.face_encoding)
                self.faculty_encodings.append(enc)
                self.faculty_ids.append(f.id)
            except Exception:
                pass

        self._loaded = True
        print(f"[FaceEngine] Loaded {len(self.student_encodings)} students, "
              f"{len(self.faculty_encodings)} faculty")

    def recognize_frame(self, frame, tolerance=0.5):
        """
        Returns list of dicts: {type, id, name, location}
        location = (top, right, bottom, left)
        """
        if not self._loaded:
            self.load_encodings()

        # Resize for speed
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        results = []
        for enc, loc in zip(face_encodings, face_locations):
            top, right, bottom, left = [v * 4 for v in loc]
            person = self._match(enc, tolerance)
            if person:
                person['location'] = (top, right, bottom, left)
                results.append(person)
            else:
                results.append({
                    'type': 'unknown', 'id': None, 'name': 'Unknown',
                    'location': (top, right, bottom, left)
                })
        return results

    def _match(self, encoding, tolerance):
        # Try students first
        if self.student_encodings:
            distances = face_recognition.face_distance(self.student_encodings, encoding)
            best = np.argmin(distances)
            if distances[best] <= tolerance:
                from .models import Student
                s = Student.objects.get(id=self.student_ids[best])
                return {'type': 'student', 'id': s.id, 'name': s.name, 'obj': s}

        # Then faculty
        if self.faculty_encodings:
            distances = face_recognition.face_distance(self.faculty_encodings, encoding)
            best = np.argmin(distances)
            if distances[best] <= tolerance:
                from .models import Faculty
                f = Faculty.objects.get(id=self.faculty_ids[best])
                return {'type': 'faculty', 'id': f.id, 'name': f.name, 'obj': f}
        return None


def encode_face_from_image(image_path):
    """Generate encoding from an uploaded image. Returns pickled bytes or None."""
    image = face_recognition.load_image_file(image_path)
    encs = face_recognition.face_encodings(image)
    if encs:
        return pickle.dumps(encs[0])
    return None
