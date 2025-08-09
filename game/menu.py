import pygame
from .ui import Button, draw_text

MENU_ITEMS = ["LEVELS", "ENDLESS", "SCOREBOARD", "SETTINGS", "QUIT"]

def show_main_menu(settings) -> str | None:
    screen = pygame.display.set_mode((settings.scr_w, settings.scr_h))
    pygame.display.set_caption("Baby Moves – Menu")
    clock = pygame.time.Clock()

    # Build buttons
    buttons = []
    w, h = 320, 56
    x = settings.scr_w//2 - w//2
    y = 220
    for item in MENU_ITEMS:
        buttons.append(Button((x, y, w, h), item))
        y += 72

    chosen = None

    def choose(label):
        nonlocal chosen
        chosen = label

    # Wire click callbacks
    for b, label in zip(buttons, MENU_ITEMS):
        b.on_click = lambda l=label: choose(l)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        hovered = [b.rect.collidepoint(mouse_pos) for b in buttons]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    idx = next((i for i, h in enumerate(hovered) if h), 0)
                    buttons[idx].on_click()
            if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                for i, b in enumerate(buttons):
                    b.handle_event(event, hovered[i])

        if chosen:
            return chosen

        # Draw
        screen.fill((10, 12, 20))
        draw_text(screen, "BABY MOVES", 90, settings.scr_w, size=56, color=(255,230,120))
        draw_text(screen, "Click a button or press Enter", 150, settings.scr_w, size=22, color=(200,200,200))

        for i, b in enumerate(buttons):
            b.draw(screen, hovered=hovered[i])

        pygame.display.flip()
        clock.tick(60)
