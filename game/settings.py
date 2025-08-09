import json
from dataclasses import dataclass

@dataclass
class Settings:
    cam_w: int
    cam_h: int
    scr_w: int
    scr_h: int
    fps_cap: int
    debug_draw: bool

    clap_dist: float
    peekaboo_eye_dist: float
    hands_up_margin: float
    wave_vel: float
    wave_window: int
    detection_hold: float

    hip_window: int
    jump_delta: float

    head_window: int
    nod_amp: float
    shake_amp: float

def load_settings(path: str) -> "Settings":
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return Settings(
        cam_w=cfg["camera"]["width"],
        cam_h=cfg["camera"]["height"],
        scr_w=cfg["screen"]["width"],
        scr_h=cfg["screen"]["height"],
        fps_cap=cfg["screen"]["fps_cap"],
        debug_draw=cfg["debug"]["draw"],
        clap_dist=cfg["gestures"]["clap_dist"],
        peekaboo_eye_dist=cfg["gestures"]["peekaboo_eye_dist"],
        hands_up_margin=cfg["gestures"]["hands_up_margin"],
        wave_vel=cfg["gestures"]["wave_vel"],
        wave_window=cfg["gestures"]["wave_window"],
        detection_hold=cfg["gestures"]["detection_hold"],
        hip_window=cfg["jump"]["hip_window"],
        jump_delta=cfg["jump"]["jump_delta"],
        head_window=cfg["head"]["head_window"],
        nod_amp=cfg["head"]["nod_amp"],
        shake_amp=cfg["head"]["shake_amp"],
    )
