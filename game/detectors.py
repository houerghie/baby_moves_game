import mediapipe as mp
from math import acos, degrees
from .utils import DetectorResult, normDist, getLmk, faceShoulderScales, GestureState

# Optional speech recognition for sound-based levels
try:
    import speech_recognition as sr
except Exception:  # library or microphone may be unavailable
    sr = None

mpHolistic = mp.solutions.holistic

# ---------------- Finger counting ----------------

PIP_INDEX = {8: 6, 12: 10, 16: 14, 20: 18}  # tip -> pip

def _angle(a, b, c):
    """Angle ABC in degrees (XY only)."""
    if not (a and b and c): return 0.0
    v1x, v1y = a.x - b.x, a.y - b.y
    v2x, v2y = c.x - b.x, c.y - b.y
    dot = v1x*v2x + v1y*v2y
    n1 = (v1x*v1x + v1y*v1y) ** 0.5
    n2 = (v2x*v2x + v2y*v2y) ** 0.5
    if n1 == 0 or n2 == 0: return 0.0
    cosv = max(-1.0, min(1.0, dot/(n1*n2)))
    return degrees(acos(cosv))

def countExtendedFingers(handLandmarks, isLeftHand: bool) -> int:
    """Robust finger count with thumb angle + vertical tip test. Clamped to 0..5."""
    if not handLandmarks:
        return 0
    def L(i): return handLandmarks[i] if i < len(handLandmarks) else None

    # Thumb extended if MCP angle is straight-ish
    thumbTip, thumbIP, thumbMCP = L(4), L(3), L(2)
    wrist, thumbCMC = L(0), L(1)
    thumbAnchor = wrist if wrist else thumbCMC
    thumbAngle = _angle(thumbTip, thumbMCP, thumbAnchor) if (thumbTip and thumbMCP and thumbAnchor) else 0.0
    thumbUp = thumbAngle > 160.0

    up = 0
    for tip in [8, 12, 16, 20]:
        tipL, pipL = L(tip), L(PIP_INDEX[tip])
        if tipL and pipL and (tipL.y < pipL.y):
            up += 1

    count = up + (1 if thumbUp else 0)
    return max(0, min(5, count))

# ---------------- Friendly labels ----------------

FRIENDLY = {
    "HANDS_UP":   "Raise both hands 🙌",
    "CLAP":       "Clap your hands 👏",
    "WAVE_RIGHT": "Wave right hand 👋",
    "WAVE_LEFT":  "Wave left hand 👋",
    "JUMP":       "Jump! 🦘",
    "NOD":        "Nod your head (Yes) 👍",
    "SHAKE_HEAD": "Shake your head (No) 👎",
}

def friendlyLabel(move: str) -> str:
    if move.startswith("FINGERS_L_"):
        n = move.split("_")[-1]; return f"Show {n} fingers (LEFT) ✋"
    if move.startswith("FINGERS_R_"):
        n = move.split("_")[-1]; return f"Show {n} fingers (RIGHT) ✋"
    if move.startswith("FINGERS_BOTH_"):
        n = move.split("_")[-1]; return f"Show {n}+{n} fingers (BOTH) ✋✋"
    if move.startswith("COMBO["):
        inner = move[6:-1].split(";")[0]
        parts = [p.strip() for p in inner.split("+")]
        return "Combo: " + " → ".join(parts)
    if move.startswith("SAY_"):
        word = move.split("_", 1)[1].lower()
        return f'Say "{word}" 🗣️'
    return FRIENDLY.get(move, move)

# Back-compat alias for engine that calls friendly_label
def friendly_label(move: str) -> str:
    return friendlyLabel(move)

# ---------------- Detectors (scale-aware) ----------------

def handsUp(poseLandmarks, gestureState: GestureState, now: float, settings) -> DetectorResult:
    rightWrist = getLmk(poseLandmarks, mpHolistic.PoseLandmark.RIGHT_WRIST.value)
    leftWrist  = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_WRIST.value)
    rightShoulder = getLmk(poseLandmarks, mpHolistic.PoseLandmark.RIGHT_SHOULDER.value)
    leftShoulder  = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_SHOULDER.value)

    isAboveRight = rightWrist and rightShoulder and (rightWrist.y < rightShoulder.y - settings.hands_up_margin)
    isAboveLeft  = leftWrist  and leftShoulder  and (leftWrist.y  < leftShoulder.y  - settings.hands_up_margin)
    ok = isAboveRight and isAboveLeft

    if gestureState.holdCheck(ok, now, settings.detection_hold):
        return DetectorResult(True)

    reason = []
    if rightWrist and rightShoulder and not isAboveRight:
        reason.append("raise RIGHT wrist higher")
    if leftWrist and leftShoulder and not isAboveLeft:
        reason.append("raise LEFT wrist higher")
    return DetectorResult(False, " & ".join(reason) if reason else "Raise both wrists above shoulders")

def clap(poseLandmarks, gestureState: GestureState, now: float, settings) -> DetectorResult:
    """Adaptive threshold using shoulder width (robust to distance to camera)."""
    rightWrist = getLmk(poseLandmarks, mpHolistic.PoseLandmark.RIGHT_WRIST.value)
    leftWrist  = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_WRIST.value)

    eyeDist, shoulderWidth = faceShoulderScales(poseLandmarks)
    ref = shoulderWidth if shoulderWidth else (eyeDist * 3.0 if eyeDist else 0.3)
    dynamicThresh = max(0.35 * ref, 0.05)

    if rightWrist and leftWrist:
        wristDist = normDist(rightWrist, leftWrist)
        ok = wristDist < dynamicThresh
        if gestureState.holdCheck(ok, now, settings.detection_hold):
            return DetectorResult(True)
        return DetectorResult(False, f"Bring hands closer (dist {wristDist:.3f} < {dynamicThresh:.3f})")

    gestureState.resetHold()
    return DetectorResult(False, "Show both hands to the camera")

def waveSide(poseLandmarks, gestureState: GestureState, now: float, settings, left=False) -> DetectorResult:
    wristLmk = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_WRIST.value if left else mpHolistic.PoseLandmark.RIGHT_WRIST.value)
    shoulderLmk = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_SHOULDER.value if left else mpHolistic.PoseLandmark.RIGHT_SHOULDER.value)
    trail = gestureState.leftWristX if left else gestureState.rightWristX
    sideName = "LEFT" if left else "RIGHT"

    if not (wristLmk and shoulderLmk):
        gestureState.resetHold()
        return DetectorResult(False, f"Show {sideName} hand near shoulder height")

    if abs(wristLmk.y - shoulderLmk.y) < 0.1:
        trail.append(wristLmk.x)

    if len(trail) >= 3:
        deltaX = abs(trail[-1] - trail[0])
        ok = deltaX > settings.wave_vel
        if gestureState.holdCheck(ok, now, settings.detection_hold):
            return DetectorResult(True)
        return DetectorResult(False, f"Wave bigger (Δx {deltaX:.3f} > {settings.wave_vel:.3f})")

    gestureState.resetHold()
    return DetectorResult(False, f"Keep {sideName} hand near shoulder height and wave")

def jump(poseLandmarks, gestureState: GestureState, now: float, settings) -> DetectorResult:
    leftHip  = getLmk(poseLandmarks, mpHolistic.PoseLandmark.LEFT_HIP.value)
    rightHip = getLmk(poseLandmarks, mpHolistic.PoseLandmark.RIGHT_HIP.value)
    if not (leftHip and rightHip):
        gestureState.resetHold()
        return DetectorResult(False, "Show your hips to the camera")
    hipY = (leftHip.y + rightHip.y) / 2.0
    gestureState.hipY.append(hipY)
    if len(gestureState.hipY) < 4:
        return DetectorResult(False, "Keep steady, then jump")
    baseline = sum(gestureState.hipY) / len(gestureState.hipY)
    rise = baseline - hipY
    ok = rise > settings.jump_delta
    if gestureState.holdCheck(ok, now, holdSecs=0.12):
        return DetectorResult(True)
    return DetectorResult(False, f"Jump higher (rise {rise:.3f} > {settings.jump_delta:.3f})")

def nod(poseLandmarks, gestureState: GestureState, now: float, settings) -> DetectorResult:
    nose = getLmk(poseLandmarks, mpHolistic.PoseLandmark.NOSE.value)
    if not nose:
        gestureState.resetHold()
        return DetectorResult(False, "Face not detected")
    gestureState.noseY.append(nose.y)
    if len(gestureState.noseY) < 4:
        return DetectorResult(False, "Move head up/down")
    amplitude = max(gestureState.noseY) - min(gestureState.noseY)
    ok = amplitude > settings.nod_amp
    if gestureState.holdCheck(ok, now, holdSecs=0.12):
        return DetectorResult(True)
    return DetectorResult(False, f"Nod more (amp {amplitude:.3f} > {settings.nod_amp:.3f})")

def shakeHead(poseLandmarks, gestureState: GestureState, now: float, settings) -> DetectorResult:
    nose = getLmk(poseLandmarks, mpHolistic.PoseLandmark.NOSE.value)
    if not nose:
        gestureState.resetHold()
        return DetectorResult(False, "Face not detected")
    gestureState.noseX.append(nose.x)
    if len(gestureState.noseX) < 4:
        return DetectorResult(False, "Move head left/right")
    amplitude = max(gestureState.noseX) - min(gestureState.noseX)
    ok = amplitude > settings.shake_amp
    if gestureState.holdCheck(ok, now, holdSecs=0.12):
        return DetectorResult(True)
    return DetectorResult(False, f"Shake more (amp {amplitude:.3f} > {settings.shake_amp:.3f})")

# ---------------- Parametric detectors ----------------

def fingersLeft(expectedCount: int):
    def _fn(poseLandmarks, gestureState: GestureState, now: float, settings, left_hand=None, **_):
        count = countExtendedFingers(left_hand, True) if left_hand else 0
        ok = (count == expectedCount)
        if gestureState.holdCheck(ok, now, settings.detection_hold):
            return DetectorResult(True)
        return DetectorResult(False, f"Left hand shows {count}, need {expectedCount}")
    return _fn

def fingersRight(expectedCount: int):
    def _fn(poseLandmarks, gestureState: GestureState, now: float, settings, right_hand=None, **_):
        count = countExtendedFingers(right_hand, False) if right_hand else 0
        ok = (count == expectedCount)
        if gestureState.holdCheck(ok, now, settings.detection_hold):
            return DetectorResult(True)
        return DetectorResult(False, f"Right hand shows {count}, need {expectedCount}")
    return _fn

def fingersBoth(expectedCount: int):
    def _fn(poseLandmarks, gestureState: GestureState, now: float, settings, left_hand=None, right_hand=None, **_):
        leftCount  = countExtendedFingers(left_hand,  True) if left_hand  else 0
        rightCount = countExtendedFingers(right_hand, False) if right_hand else 0
        ok = (leftCount == expectedCount and rightCount == expectedCount)
        if gestureState.holdCheck(ok, now, settings.detection_hold):
            return DetectorResult(True)
        return DetectorResult(False, f"Hands show L:{leftCount} R:{rightCount}, need {expectedCount}+{expectedCount}")
    return _fn

def sayWord(expected: str):
    """Return a detector that succeeds when the expected word is spoken."""
    expected = expected.lower()

    def _fn(poseLandmarks, gestureState: GestureState, now: float, settings, **_):
        if sr is None:
            return DetectorResult(False, "Speech recognition unavailable")
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.1)
                audio = recognizer.listen(source, phrase_time_limit=2)
            said = recognizer.recognize_google(audio).lower()
        except Exception:
            said = ""
        ok = expected in said.split()
        if ok:
            return DetectorResult(True)
        return DetectorResult(False, f"Say '{expected}'")

    return _fn

# ---------------- Registry ----------------

def resolve_detector(move: str):
    if move == "HANDS_UP":   return handsUp, {"needs_hands": False}
    if move == "CLAP":       return clap, {"needs_hands": False}
    if move == "WAVE_RIGHT": return lambda p,g,n,s,**k: waveSide(p,g,n,s,left=False), {"needs_hands": False}
    if move == "WAVE_LEFT":  return lambda p,g,n,s,**k: waveSide(p,g,n,s,left=True),  {"needs_hands": False}
    if move == "JUMP":       return jump, {"needs_hands": False}
    if move == "NOD":        return nod, {"needs_hands": False}
    if move == "SHAKE_HEAD": return shakeHead, {"needs_hands": False}

    if move.startswith("FINGERS_L_"):
        n = int(move.split("_")[-1]); return fingersLeft(n), {"needs_hands": True}
    if move.startswith("FINGERS_R_"):
        n = int(move.split("_")[-1]); return fingersRight(n), {"needs_hands": True}
    if move.startswith("FINGERS_BOTH_"):
        n = int(move.split("_")[-1]); return fingersBoth(n), {"needs_hands": True}
    if move.startswith("SAY_"):
        word = move.split("_", 1)[1]
        return sayWord(word), {"needs_hands": False}

    return (lambda *a, **k: DetectorResult(False, "Unknown move")), {"needs_hands": False}
