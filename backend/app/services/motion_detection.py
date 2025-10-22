import cv2
import numpy as np
from typing import Optional, List, Tuple
import threading
import time


class MotionDetector:
    """Motion detection service using OpenCV."""

    def __init__(self, sensitivity: int = 50, min_area: int = 500):
        """
        Initialize motion detector.

        Args:
            sensitivity: Motion sensitivity (0-100), higher is more sensitive
            min_area: Minimum area of motion to trigger detection
        """
        self.sensitivity = sensitivity
        self.min_area = min_area
        self.prev_frame = None
        self.threshold = int((100 - sensitivity) * 2.55)  # Convert 0-100 to 255-0

    def detect_motion(self, frame: np.ndarray, regions: Optional[List[dict]] = None) -> Tuple[bool, List[dict]]:
        """
        Detect motion in frame.

        Args:
            frame: Current video frame
            regions: Optional list of regions to check for motion

        Returns:
            Tuple of (motion_detected, detected_regions)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # First frame, initialize
        if self.prev_frame is None:
            self.prev_frame = gray
            return False, []

        # Compute difference
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]

        # Dilate threshold image
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        detected_regions = []

        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue

            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)

            # Check if motion is in specified regions
            if regions:
                in_region = False
                for region in regions:
                    if (x >= region['x'] and y >= region['y'] and
                        x + w <= region['x'] + region['width'] and
                        y + h <= region['y'] + region['height']):
                        in_region = True
                        break

                if in_region:
                    detected_regions.append({'x': x, 'y': y, 'width': w, 'height': h})
            else:
                detected_regions.append({'x': x, 'y': y, 'width': w, 'height': h})

        # Update previous frame
        self.prev_frame = gray

        return motion_detected and (not regions or len(detected_regions) > 0), detected_regions


class MotionDetectionService:
    """Service for managing motion detection on camera streams."""

    active_detectors: dict = {}

    @classmethod
    def start_detection(cls, camera_id: int, stream_url: str, sensitivity: int = 50,
                       callback=None, regions: Optional[List[dict]] = None):
        """Start motion detection on a camera stream."""
        if camera_id in cls.active_detectors:
            cls.stop_detection(camera_id)

        detector = MotionDetector(sensitivity=sensitivity)

        def detection_loop():
            cap = cv2.VideoCapture(stream_url)
            while camera_id in cls.active_detectors:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(1)
                    continue

                motion_detected, detected_regions = detector.detect_motion(frame, regions)

                if motion_detected and callback:
                    callback(camera_id, detected_regions)

                time.sleep(0.1)  # Check 10 times per second

            cap.release()

        thread = threading.Thread(target=detection_loop, daemon=True)
        cls.active_detectors[camera_id] = thread
        thread.start()

    @classmethod
    def stop_detection(cls, camera_id: int):
        """Stop motion detection on a camera."""
        if camera_id in cls.active_detectors:
            del cls.active_detectors[camera_id]

    @classmethod
    def is_detection_active(cls, camera_id: int) -> bool:
        """Check if motion detection is active for a camera."""
        return camera_id in cls.active_detectors
