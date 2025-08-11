import json, random, time, cv2, pygame, mediapipe as mp
import numpy as np
from .settings import Settings
from .utils import GestureState
from .ui import draw_text, end_screen
from . import detectors as D
from .combos import make_combo_detector
from .scoreboard import save_score, ask_name

mpHolistic = mp.solutions.holistic
mpDrawing = mp.solutions.drawing_utils
mpStyles = mp.solutions.drawing_styles

POOL_MOVES = [
    "HANDS_UP","CLAP","WAVE_RIGHT","WAVE_LEFT","JUMP","NOD","SHAKE_HEAD",
    "FINGERS_L_2","FINGERS_R_5","FINGERS_BOTH_3",
    "SAY_MAMA","SAY_DADA"
]

def load_levels(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [
            {"name": "Warmup", "moves": ["HANDS_UP", "CLAP", "WAVE_RIGHT"]},
            {"name": "Body",   "moves": ["NOD", "SHAKE_HEAD", "JUMP"]},
            {"name": "Hands",  "moves": ["FINGERS_L_2", "FINGERS_R_5", "FINGERS_BOTH_3"]},
            {"name": "Combo",  "moves": ["COMBO[HANDS_UP+CLAP+JUMP;T=7]"]}
        ]

def resolve_any(move: str):
    if move.startswith("COMBO[") and move.endswith("]"):
        return make_combo_detector(move, D.resolve_detector), {"is_combo": True, "needs_hands": True}
    return D.resolve_detector(move)

def _skeleton_surface(results, width=220, height=160):
    """Render only the pose skeleton onto a small surface (numpy image)."""
    canvas = np.zeros((height, width, 3), dtype=np.uint8)  # black
    if results and results.pose_landmarks:
        # draw landmarks using normalized coords scaled to this canvas size
        mpDrawing.draw_landmarks(
            canvas,
            results.pose_landmarks,
            mpHolistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mpStyles.get_default_pose_landmarks_style()
        )
    return canvas

def _tick_pipeline(pipeline):
    ok, frame = pipeline.read()
    if not ok:
        return None, None, None, None
    results = pipeline.process(frame)
    pose = results.pose_landmarks.landmark if results and results.pose_landmarks else None
    left_hand  = results.left_hand_landmarks.landmark if results and results.left_hand_landmarks else None
    right_hand = results.right_hand_landmarks.landmark if results and results.right_hand_landmarks else None
    return results, pose, left_hand, right_hand

def run_levels(settings: Settings, levels_path: str, pipeline):
    pygame.display.set_caption("Baby Moves – Levels")
    screen = pygame.display.set_mode((settings.scr_w, settings.scr_h))
    clock = pygame.time.Clock()
    levels = load_levels(levels_path)

    gs = GestureState(settings.wave_window, settings.hip_window, settings.head_window)
    level_idx, move_idx, score = 0, 0, 0
    feedback, feedback_t = "", 0.0
    running = True

    while running:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_SPACE:
                    feedback = "Skipped."; feedback_t = now
                    gs.reset_hold() 
                    gs.reset_combo() 
                    move_idx += 1

        results, pose, lh, rh = _tick_pipeline(pipeline)
        if results is None:
            continue  # keep trying

        current_level = levels[level_idx]
        target = current_level["moves"][move_idx] if move_idx < len(current_level["moves"]) else None

        if target and pose:
            det, meta = resolve_any(target)
            result = det(pose, gs, now, settings, left_hand=lh, right_hand=rh)                      if (meta.get("needs_hands") or meta.get("is_combo")) else det(pose, gs, now, settings)

            if result.ok:
                score += 1
                feedback, feedback_t = f"Great! {D.friendly_label(target)}", now
                gs.reset_hold(); gs.reset_combo(); move_idx += 1
            else:
                feedback, feedback_t = (result.reason or f"Try: {D.friendly_label(target)}"), now

        if move_idx >= len(current_level["moves"]):
            level_idx += 1; move_idx = 0; gs.reset_combo()
            if level_idx >= len(levels):
                end_screen(screen, score, settings.scr_w, settings.scr_h)
                name = ask_name(screen, settings)
                if name: save_score(name, score, "LEVELS")
                break
            else:
                feedback, feedback_t = f"Level up! → {levels[level_idx]['name']}", now

        # ---- UI ----
        screen.fill((15,20,30))
        draw_text(screen, f"Level: {levels[level_idx]['name']}", 16, settings.scr_w, size=32)
        draw_text(screen, f"Score: {score}", 60, settings.scr_w, size=28)
        draw_text(screen, "SPACE = skip • ESC = quit", settings.scr_h - 44, settings.scr_w, size=22, color=(200,200,200))

        if target:
            draw_text(screen, "Do this:", 110, settings.scr_w, size=28)
            draw_text(screen, D.friendly_label(target), 150, settings.scr_w, size=44, color=(255,230,120))
        if feedback and (time.time()-feedback_t) < 1.3:
            draw_text(screen, feedback, 210, settings.scr_w, size=26, color=(140,220,255))

        # Draw skeleton only (top-right)
        skel = _skeleton_surface(results, width=220, height=160)
        skel = cv2.cvtColor(skel, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(skel.swapaxes(0,1))
        margin = 16
        screen.blit(surf, (settings.scr_w - surf.get_width() - margin, margin))

        pygame.display.flip()
        clock.tick(settings.fps_cap)

def run_endless(settings: Settings, duration_secs: int = 60, pipeline=None):
    pygame.display.set_caption("Baby Moves – Endless")
    screen = pygame.display.set_mode((settings.scr_w, settings.scr_h))
    clock = pygame.time.Clock()

    gs = GestureState(settings.wave_window, settings.hip_window, settings.head_window)
    score = 0
    target = random.choice(POOL_MOVES)
    feedback, feedback_t = "Get ready!", time.time()
    end_time = time.time() + duration_secs

    running = True
    while running:
        now = time.time()
        time_left = max(0, int(end_time - now))
        if time_left <= 0:
            name = ask_name(screen, settings)
            if name: save_score(name, score, "ENDLESS")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        results, pose, lh, rh = _tick_pipeline(pipeline)
        if results is None:
            continue

        if target and pose:
            det, meta = resolve_any(target)
            result = det(pose, gs, now, settings, left_hand=lh, right_hand=rh)                      if (meta.get("needs_hands") or meta.get("is_combo")) else det(pose, gs, now, settings)
            if result.ok:
                score += 1
                target = random.choice(POOL_MOVES)
                feedback, feedback_t = f"Nice! +1 → {D.friendly_label(target)}", now
                gs.reset_hold(); gs.reset_combo()
            else:
                feedback, feedback_t = (result.reason or f"Do: {D.friendly_label(target)}"), now

        # ---- UI ----
        screen.fill((15,20,30))
        draw_text(screen, f"ENDLESS — Time: {time_left}s", 16, settings.scr_w, size=32)
        draw_text(screen, f"Score: {score}", 60, settings.scr_w, size=28)
        draw_text(screen, "ESC = quit", settings.scr_h - 44, settings.scr_w, size=22, color=(200,200,200))
        draw_text(screen, "Do this:", 110, settings.scr_w, size=28)
        draw_text(screen, D.friendly_label(target), 150, settings.scr_w, size=44, color=(255,230,120))
        if feedback and (time.time()-feedback_t) < 1.2:
            draw_text(screen, feedback, 210, settings.scr_w, size=26, color=(140,220,255))

        # Skeleton only (top-right)
        skel = _skeleton_surface(results, width=220, height=160)
        skel = cv2.cvtColor(skel, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(skel.swapaxes(0,1))
        margin = 16
        screen.blit(surf, (settings.scr_w - surf.get_width() - margin, margin))

        pygame.display.flip()
        clock.tick(settings.fps_cap)
