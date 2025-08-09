import math
from collections import deque
from dataclasses import dataclass
from typing import Optional

@dataclass
class DetectorResult:
    ok: bool
    reason: str = ""   # empty if ok

def normDist(a, b) -> float:
    """3D distance between two MediaPipe landmarks (normalized coords)."""
    if a is None or b is None:
        return 999.0
    dx, dy = a.x - b.x, a.y - b.y
    dz = (getattr(a, "z", 0.0) or 0.0) - (getattr(b, "z", 0.0) or 0.0)
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def getLmk(landmarks, index):
    """Safe landmark getter; returns None if missing."""
    if landmarks and index < len(landmarks):
        return landmarks[index]
    return None

def faceShoulderScales(pose):
    """Return (interEyeDistance, shoulderWidth) in normalized coords, or (None, None)."""
    import mediapipe as mp
    mpHolistic = mp.solutions.holistic
    leftEye  = getLmk(pose, mpHolistic.PoseLandmark.LEFT_EYE.value)
    rightEye = getLmk(pose, mpHolistic.PoseLandmark.RIGHT_EYE.value)
    leftShoulder  = getLmk(pose, mpHolistic.PoseLandmark.LEFT_SHOULDER.value)
    rightShoulder = getLmk(pose, mpHolistic.PoseLandmark.RIGHT_SHOULDER.value)
    eyeDist = normDist(leftEye, rightEye) if leftEye and rightEye else None
    shoulderWidth = normDist(leftShoulder, rightShoulder) if leftShoulder and rightShoulder else None
    return eyeDist, shoulderWidth

class GestureState:
    """Holds short histories and timing state."""
    def __init__(self, wave_window: int, hip_window: int, head_window: int):
        # switched to camelCase, but keep snake_case aliases for compatibility
        self.rightWristX = deque(maxlen=wave_window)
        self.leftWristX  = deque(maxlen=wave_window)
        self.holdSince: Optional[float] = None

        self.hipY = deque(maxlen=hip_window)
        self.noseY = deque(maxlen=head_window)
        self.noseX = deque(maxlen=head_window)

        # combo
        self.comboKey: Optional[str] = None
        self.comboIndex: int = 0
        self.comboDeadline: Optional[float] = None
        self.comboMoves = []

    # New camelCase methods
    def holdCheck(self, condition: bool, now: float, holdSecs: float) -> bool:
        if condition:
            if self.holdSince is None:
                self.holdSince = now
            return (now - self.holdSince) >= holdSecs
        self.holdSince = None
        return False

    def resetHold(self):
        self.holdSince = None

    def resetCombo(self):
        self.comboKey = None
        self.comboIndex = 0
        self.comboDeadline = None
        self.comboMoves = []

    # Back-compat snake_case aliases
    def hold_check(self, condition: bool, now: float, hold_secs: float) -> bool:
        return self.holdCheck(condition, now, hold_secs)

    def reset_hold(self):
        self.resetHold()

    def reset_combo(self):
        self.resetCombo()
