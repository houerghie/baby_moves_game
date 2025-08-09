import cv2
import mediapipe as mp

class VisionPipeline:
    """Persistent camera + MediaPipe Holistic pipeline."""
    def __init__(self, cam_w: int, cam_h: int):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

        self.mpHolistic = mp.solutions.holistic
        self.holistic = self.mpHolistic.Holistic(
            static_image_mode=False,
            model_complexity=0,
            enable_segmentation=False,
            refine_face_landmarks=False
        )

    def read(self):
        """Return (ok, frame_bgr)."""
        ok, frame = self.cap.read()
        return ok, frame

    def process(self, frame_bgr):
        """Run holistic on an RGB frame and return results."""
        import cv2
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return self.holistic.process(rgb)

    def close(self):
        try:
            self.cap.release()
        except Exception:
            pass
        try:
            self.holistic.close()
        except Exception:
            pass
