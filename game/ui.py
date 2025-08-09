import pygame

# ---------- Primitive UI Widgets ----------

class Button:
    def __init__(self, rect, text, on_click=None, font_size=32):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.font_size = font_size

    def draw(self, screen, hovered=False, disabled=False):
        base = (38, 46, 66)
        hover = (55, 70, 100)
        disable = (30, 30, 30)
        color = disable if disabled else (hover if hovered else base)
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (80, 90, 120), self.rect, width=2, border_radius=12)
        draw_text(screen, self.text, self.rect.centery - self.font_size//2, screen.get_width(),
                  size=self.font_size, center=True, color=(255,255,255),
                  center_x=self.rect.centerx)

    def handle_event(self, event, hovered=False):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and hovered:
            if self.on_click: self.on_click()

class Slider:
    def __init__(self, x, y, width, value, min_v, max_v, step=1.0, label=""):
        self.rect = pygame.Rect(x, y, width, 24)
        self.track_rect = pygame.Rect(x, y+8, width, 8)
        self.value, self.min_v, self.max_v, self.step = value, min_v, max_v, step
        self.label = label
        self.dragging = False

    def draw(self, screen):
        # label
        draw_text(screen, f"{self.label}: {self.value}", self.rect.y - 26, screen.get_width(),
                  size=22, center=False, color=(220,220,220), x=self.rect.x)
        # track
        pygame.draw.rect(screen, (70, 80, 110), self.track_rect, border_radius=6)
        # knob pos
        t = 0 if self.max_v == self.min_v else (self.value - self.min_v) / (self.max_v - self.min_v)
        cx = self.track_rect.x + int(t * self.track_rect.w)
        knob = pygame.Rect(0, 0, 18, 18) 
        knob.center = (cx, self.track_rect.centery)
        pygame.draw.circle(screen, (180, 220, 255), knob.center, 10)

    def clamp(self, v):
        v = max(self.min_v, min(self.max_v, v))
        if isinstance(self.step, int):
            return int(round(v / self.step) * self.step)
        return round(v / self.step) * self.step

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.track_rect.collidepoint(event.pos):
            self.dragging = True; self._update_from_mouse(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_mouse(event.pos[0])

    def _update_from_mouse(self, mx):
        t = (mx - self.track_rect.x) / max(1, self.track_rect.w)
        v = self.min_v + t * (self.max_v - self.min_v)
        self.value = self.clamp(v)

class Toggle:
    def __init__(self, x, y, value=False, label=""):
        self.rect = pygame.Rect(x, y, 52, 28)
        self.value = bool(value)
        self.label = label

    def draw(self, screen):
        draw_text(screen, f"{self.label}: {'ON' if self.value else 'OFF'}",
                  self.rect.y - 26, screen.get_width(), size=22, center=False,
                  color=(220,220,220), x=self.rect.x)
        bg = (80,180,120) if self.value else (90, 90, 110)
        pygame.draw.rect(screen, bg, self.rect, border_radius=14)
        knob = pygame.Rect(0,0,24,24)
        knob.center = (self.rect.right-14, self.rect.centery) if self.value else (self.rect.left+14, self.rect.centery)
        pygame.draw.circle(screen, (240,240,240), knob.center, 12)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            self.value = not self.value

# ---------- Text helper ----------

def draw_text(screen, text, y, scr_w, size=36, center=True, color=(255,255,255), center_x=None, x=None):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center_x is not None:
        rect.centerx = center_x
    elif center:
        rect.centerx = scr_w // 2
    else:
        rect.x = x if x is not None else 0
    rect.top = y
    screen.blit(surf, rect)

def end_screen(screen, score, scr_w, scr_h):
    import pygame
    waiting = True
    start = pygame.time.get_ticks()
    while waiting and (pygame.time.get_ticks() - start) < 6000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
        screen.fill((20, 18, 40))
        draw_text(screen, "🎉 All levels complete!", 180, scr_w, size=46)
        draw_text(screen, f"Final Score: {score}", 240, scr_w, size=38, color=(180, 230, 255))
        draw_text(screen, "Thanks for playing 👶", 300, scr_w, size=32)
        pygame.display.flip()
        pygame.time.delay(20)
