import pygame
from .settings import load_settings, Settings
from .menu import show_main_menu
from .engine import run_levels, run_endless
from .settings_ui import show_settings_ui
from .scoreboard import show_scoreboard
from .camera import VisionPipeline

def run_app():
    pygame.init()
    settings: Settings = load_settings("settings.json")
    pygame.display.set_caption("Baby Moves")

    # Persistent camera/holistic pipeline (only load once)
    pipeline = VisionPipeline(settings.cam_w, settings.cam_h)

    try:
        running = True
        while running:
            choice = show_main_menu(settings)
            if choice == "LEVELS":
                run_levels(settings, levels_path="levels.json", pipeline=pipeline)
            elif choice == "ENDLESS":
                run_endless(settings, duration_secs=60, pipeline=pipeline)
            elif choice == "SCOREBOARD":
                show_scoreboard(settings)
            elif choice == "SETTINGS":
                settings = show_settings_ui(settings, path="settings.json")
            elif choice in ("QUIT", None):
                running = False
    finally:
        pipeline.close()
        pygame.quit()
