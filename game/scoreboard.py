import json
import os
import pygame
from .ui import draw_text

SCORES_PATH = "scores.json"
MAX_ENTRIES_PER_MODE = 10

def load_scores():
    if not os.path.exists(SCORES_PATH):
        return {"ENDLESS": [], "LEVELS": []}
    with open(SCORES_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return { "ENDLESS": data.get("ENDLESS", []), "LEVELS": data.get("LEVELS", []) }
        except Exception:
            return {"ENDLESS": [], "LEVELS": []}

def save_score(name: str, score: int, mode: str):
    data = load_scores()
    arr = data.get(mode, [])
    arr.append({"name": name[:20], "score": int(score)})
    arr.sort(key=lambda x: x["score"], reverse=True)
    data[mode] = arr[:MAX_ENTRIES_PER_MODE]
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ask_name(screen, settings) -> str | None:
    name = ""
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
                if event.key == pygame.K_RETURN: return name.strip() or "Player"
                if event.key == pygame.K_BACKSPACE: name = name[:-1]
                else:
                    ch = event.unicode
                    if ch.isprintable() and len(name) < 20:
                        name += ch

        screen.fill((20, 18, 40))
        draw_text(screen, "New High Score!", 160, settings.scr_w, size=42, color=(255,230,120))
        draw_text(screen, "Type your name and press Enter", 210, settings.scr_w, size=24, color=(200,200,200))
        draw_text(screen, name + "▌", 260, settings.scr_w, size=36, color=(140,220,255))
        pygame.display.flip()
        clock.tick(60)

def show_scoreboard(settings):
    screen = pygame.display.set_mode((settings.scr_w, settings.scr_h))
    pygame.display.set_caption("Scoreboard")
    clock = pygame.time.Clock()
    data = load_scores()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return

        screen.fill((10, 12, 20))
        draw_text(screen, "SCOREBOARD", 60, settings.scr_w, size=48, color=(255,230,120))

        draw_text(screen, "ENDLESS", 140, settings.scr_w, size=28, color=(180,220,255))
        y = 175
        for i, row in enumerate(data.get("ENDLESS", [])):
            draw_text(screen, f"{i+1:2d}. {row['name']:<12} — {row['score']}", y, settings.scr_w, size=24, color=(230,230,230))
            y += 28

        draw_text(screen, "LEVELS", y + 20, settings.scr_w, size=28, color=(180,220,255))
        y += 55
        for i, row in enumerate(data.get("LEVELS", [])):
            draw_text(screen, f"{i+1:2d}. {row['name']:<12} — {row['score']}", y, settings.scr_w, size=24, color=(230,230,230))
            y += 28

        draw_text(screen, "Press Esc/Enter to return", settings.scr_h - 42, settings.scr_w, size=20, color=(200,200,200))
        pygame.display.flip()
        clock.tick(60)
