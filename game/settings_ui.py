import json
import pygame
from .ui import draw_text, Slider, Toggle, Button
from .settings import Settings

def settings_to_dict(s: Settings) -> dict:
    return {
        "camera": {"width": s.cam_w, "height": s.cam_h},
        "screen": {"width": s.scr_w, "height": s.scr_h, "fps_cap": s.fps_cap},
        "debug":  {"draw": bool(s.debug_draw)},
        "gestures": {
            "clap_dist": s.clap_dist,
            "peekaboo_eye_dist": s.peekaboo_eye_dist,
            "hands_up_margin": s.hands_up_margin,
            "wave_vel": s.wave_vel,
            "wave_window": s.wave_window,
            "detection_hold": s.detection_hold
        },
        "jump": {"hip_window": s.hip_window, "jump_delta": s.jump_delta},
        "head": {"head_window": s.head_window, "nod_amp": s.nod_amp, "shake_amp": s.shake_amp}
    }

def dict_to_settings(d: dict) -> Settings:
    from .settings import Settings
    return Settings(
        cam_w=d["camera"]["width"], cam_h=d["camera"]["height"],
        scr_w=d["screen"]["width"], scr_h=d["screen"]["height"], fps_cap=d["screen"]["fps_cap"],
        debug_draw=bool(d["debug"]["draw"]),
        clap_dist=d["gestures"]["clap_dist"], peekaboo_eye_dist=d["gestures"]["peekaboo_eye_dist"],
        hands_up_margin=d["gestures"]["hands_up_margin"], wave_vel=d["gestures"]["wave_vel"],
        wave_window=d["gestures"]["wave_window"], detection_hold=d["gestures"]["detection_hold"],
        hip_window=d["jump"]["hip_window"], jump_delta=d["jump"]["jump_delta"],
        head_window=d["head"]["head_window"], nod_amp=d["head"]["nod_amp"], shake_amp=d["head"]["shake_amp"]
    )

def show_settings_ui(settings: Settings, path: str) -> Settings:
    cfg = settings_to_dict(settings)

    screen = pygame.display.set_mode((settings.scr_w, settings.scr_h))
    pygame.display.set_caption("Settings")
    clock = pygame.time.Clock()

    # Sliders & toggles layout
    x0 = 120; y0 = 120; gap = 54; w = settings.scr_w - x0*2
    widgets = []

    def add_slider(label, get_path, step, lo, hi):
        nonlocal y0
        obj = cfg
        keys = get_path.split(".")
        for k in keys[:-1]: obj = obj[k]
        leaf = keys[-1]
        slider = Slider(x0, y0, w, obj[leaf], lo, hi, step=step, label=label)
        widgets.append(("slider", get_path, slider))
        y0 += gap

    def add_toggle(label, get_path):
        nonlocal y0
        obj = cfg
        keys = get_path.split(".")
        for k in keys[:-1]: obj = obj[k]
        leaf = keys[-1]
        toggle = Toggle(x0, y0, value=bool(obj[leaf]), label=label)
        widgets.append(("toggle", get_path, toggle))
        y0 += gap

    # Build form
    add_slider("Camera Width",  "camera.width",   20, 160, 1920)
    add_slider("Camera Height", "camera.height",  20, 120, 1080)
    add_slider("Screen Width",  "screen.width",   20, 800,  2560)
    add_slider("Screen Height", "screen.height",  20, 600,  1440)
    add_slider("FPS Cap",       "screen.fps_cap", 1,  15,   120)
    add_toggle("Debug Draw",    "debug.draw")

    y0 += 10
    add_slider("Clap Distance",        "gestures.clap_dist",        0.005, 0.02, 0.2)
    add_slider("Peekaboo Eye Dist",    "gestures.peekaboo_eye_dist",0.005, 0.03, 0.2)
    add_slider("Hands-Up Margin",      "gestures.hands_up_margin",  0.005, 0.01, 0.15)
    add_slider("Wave Velocity",        "gestures.wave_vel",         0.005, 0.04, 0.5)
    add_slider("Wave Window",          "gestures.wave_window",      1,     3,    30)
    add_slider("Detection Hold (s)",   "gestures.detection_hold",   0.05,  0.10, 1.00)

    y0 += 10
    add_slider("Hip Window",     "jump.hip_window", 1, 4, 40)
    add_slider("Jump Delta",     "jump.jump_delta", 0.005, 0.02, 0.2)

    y0 += 10
    add_slider("Head Window", "head.head_window", 1, 4, 40)
    add_slider("Nod Amplitude", "head.nod_amp", 0.005, 0.02, 0.2)
    add_slider("Shake Amplitude", "head.shake_amp", 0.005, 0.02, 0.2)

    # Save/Cancel buttons
    btn_w, btn_h = 180, 50
    btn_save = Button((screen.get_width()//2 - btn_w - 20, screen.get_height() - 80, btn_w, btn_h), "Save")
    btn_cancel = Button((screen.get_width()//2 + 20,       screen.get_height() - 80, btn_w, btn_h), "Cancel")

    chosen = None
    def save_and_exit():
        nonlocal chosen
        for kind, pathkey, widget in widgets:
            obj = cfg
            keys = pathkey.split(".")
            for k in keys[:-1]: obj = obj[k]
            leaf = keys[-1]
            if kind == "slider":
                orig = obj.get(leaf)
                val = widget.value
                obj[leaf] = int(val) if isinstance(orig, int) or pathkey.endswith("window") or pathkey.endswith("fps_cap") else float(val)
            else:
                obj[leaf] = bool(widget.value)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        chosen = "SAVE"

    def cancel_and_exit():
        nonlocal chosen
        chosen = "CANCEL"

    btn_save.on_click = save_and_exit
    btn_cancel.on_click = cancel_and_exit

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return settings
            for kind, pathkey, widget in widgets:
                widget.handle_event(event)
            btn_save.handle_event(event, hovered=btn_save.rect.collidepoint(mouse_pos))
            btn_cancel.handle_event(event, hovered=btn_cancel.rect.collidepoint(mouse_pos))

        if chosen == "SAVE":
            from .settings_ui import dict_to_settings
            return dict_to_settings(cfg)
        if chosen == "CANCEL":
            return settings

        screen.fill((12, 14, 22))
        draw_text(screen, "Settings", 32, screen.get_width(), size=40, color=(255,230,120))
        draw_text(screen, "(Drag sliders • Click toggles • Save/Cancel)", 72, screen.get_width(), size=20, color=(200,200,200))

        for _, _, widget in widgets:
            widget.draw(screen)

        btn_save.draw(screen, hovered=btn_save.rect.collidepoint(mouse_pos))
        btn_cancel.draw(screen, hovered=btn_cancel.rect.collidepoint(mouse_pos))

        pygame.display.flip()
        clock.tick(60)
