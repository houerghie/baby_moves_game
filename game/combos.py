import re
from .utils import DetectorResult

COMBO_RE = re.compile(r"^COMBO\[(?P<body>.+?)\]$")

def parse_combo(expr: str):
    """COMBO[HANDS_UP+CLAP+JUMP;T=7] -> (moves, 7.0)"""
    m = COMBO_RE.match(expr)
    if not m: return [], 10.0
    body = m.group("body")
    parts = body.split(";")
    seq = parts[0]
    t = 10.0
    if len(parts) > 1 and parts[1].strip().upper().startswith("T="):
        try:
            t = float(parts[1].split("=")[1])
        except Exception:
            t = 10.0
    moves = [p.strip() for p in seq.split("+") if p.strip()]
    return moves, t

def make_combo_detector(expr: str, resolver):
    """Factory for a combo detector using `resolver(move)`."""
    sub_moves, time_limit = parse_combo(expr)

    def _combo(pose, gs, now, settings, left_hand=None, right_hand=None, **_):
        key = expr
        if gs.comboKey != key:
            gs.comboKey = key
            gs.combo_moves = sub_moves
            gs.combo_index = 0
            gs.combo_deadline = now + time_limit
            gs.reset_hold()

        if gs.combo_deadline and now > gs.combo_deadline:
            gs.combo_index = 0
            gs.combo_deadline = now + time_limit
            gs.reset_hold()
            return DetectorResult(False, "Combo timed out — start again")

        if gs.combo_index >= len(gs.combo_moves):
            return DetectorResult(True)

        current = gs.combo_moves[gs.combo_index]
        det, meta = resolver(current)

        res = det(pose, gs, now, settings, left_hand=left_hand, right_hand=right_hand)               if meta.get("needs_hands") else det(pose, gs, now, settings)

        if res.ok:
            gs.combo_index += 1
            gs.reset_hold()
            gs.combo_deadline = now + max(1.5, time_limit * 0.4)
            if gs.combo_index < len(gs.combo_moves):
                return DetectorResult(False, f"Good! Next: {gs.combo_moves[gs.combo_index]}")
            return DetectorResult(True)

        return DetectorResult(False, f"{current}: {res.reason}" if res.reason else f"Do: {current}")

    return _combo
