"""
Behaviour detection — detects phone usage and sleeping using YOLOv8 + simple heuristics.
On first run, YOLOv8 will auto-download yolov8n.pt (~6 MB).
"""
import cv2
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO('yolov8n.pt')  # COCO pretrained — has 'cell phone' & 'person' classes
    return _model


# COCO class IDs
PERSON_CLASS = 0
CELL_PHONE_CLASS = 67


def detect_behaviour(frame):
    """
    Returns list of dicts:
    {behaviour: 'PHONE'|'SLEEP'|'ATTENTIVE', confidence, bbox}
    """
    model = get_model()
    results = model(frame, verbose=False, classes=[PERSON_CLASS, CELL_PHONE_CLASS])

    detections = []
    persons = []
    phones = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            if cls == PERSON_CLASS:
                persons.append({'bbox': xyxy, 'conf': conf})
            elif cls == CELL_PHONE_CLASS:
                phones.append({'bbox': xyxy, 'conf': conf})

    # Phone usage: phone bbox overlaps with person bbox
    for phone in phones:
        for person in persons:
            if _bbox_overlap(phone['bbox'], person['bbox']):
                detections.append({
                    'behaviour': 'PHONE',
                    'confidence': phone['conf'],
                    'bbox': person['bbox'],
                })
                break

    # Sleeping heuristic: person bbox where height < width * 1.2 (slumped/horizontal)
    for person in persons:
        x1, y1, x2, y2 = person['bbox']
        w, h = x2 - x1, y2 - y1
        if h > 0 and w > 0 and (h / w) < 1.2:
            detections.append({
                'behaviour': 'SLEEP',
                'confidence': person['conf'],
                'bbox': person['bbox'],
            })

    return detections, persons, phones


def _bbox_overlap(b1, b2):
    x1 = max(b1[0], b2[0]); y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2]); y2 = min(b1[3], b2[3])
    return x2 > x1 and y2 > y1
