import pygame
import random
import sys
import os
pygame.init()
WIDTH, HEIGHT = 450, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpeedJamp")
CLOCK = pygame.time.Clock()
FPS = 55
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
BLUE = (0, 162, 232)
RED = (237, 28, 36)
YELLOW = (255, 242, 0)
FONT_COLOR = (50, 50, 50)
GRAVITY = 0.4
BOUNCE_VELOCITY = -11
JETPACK_VELOCITY = -20
FONT = pygame.font.SysFont("Arial", 24, bold=True)
FONT_BIG = pygame.font.SysFont("Arial", 32, bold=True)
PLAYER_COLORS = [(255, 127, 39), (0, 100, 255), (255, 0, 0)]
PLAYER_NAMES = ["Оранжевый", "Синий", "Красный"]
current_color_index = 0
def load_background(path):
    try:
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            return img
    except:
        pass
    return None
BACKGROUND = load_background("png/bg.png")
if not BACKGROUND:
    BACKGROUND = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(255 - (y / HEIGHT) * 200)
        r = max(0, min(255, color_value))
        g = max(0, min(255, color_value - 50))
        b = 255
        color = (r, g, b)
        pygame.draw.line(BACKGROUND, color, (0, y), (WIDTH, y))
def change_background(score):
    if score >= 15000:
        new_bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            progress = y / HEIGHT
            r = int(255 * (1 - progress * 0.7))
            g = int(100 * (1 - progress * 0.5))
            b = int(50 + 150 * progress)
            color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
            pygame.draw.line(new_bg, color, (0, y), (WIDTH, y))
        return new_bg
    else:
        normal_bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color_value = int(255 - (y / HEIGHT) * 200)
            r = max(0, min(255, color_value))
            g = max(0, min(255, color_value - 50))
            b = 255
            color = (r, g, b)
            pygame.draw.line(normal_bg, color, (0, y), (WIDTH, y))
        return normal_bg
def check_secret_code(keys, score):
    if score >= 5000:
        if keys[pygame.K_6] and keys[pygame.K_7]:
            return True
    return False
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 150
        self.vx = 0
        self.vy = 0
        self.speed = 7
        self.score = 0
        self.jetpack_timer = 0
        self.color = PLAYER_COLORS[current_color_index]
    def update(self):
        if self.jetpack_timer > 0:
            self.vy = JETPACK_VELOCITY
            self.jetpack_timer -= 1
        else:
            self.vy += GRAVITY
        keys = pygame.key.get_pressed()
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
        self.x += self.vx
        self.y += self.vy
        if self.x > WIDTH:
            self.x = -self.width
        elif self.x < -self.width:
            self.x = WIDTH
    def draw(self):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        eye_offset = self.width - 10 if self.vx >= 0 else 2
        pygame.draw.rect(SCREEN, BLACK, (self.x + eye_offset, self.y + 8, 8, 8), border_radius=2)
class Platform:
    def __init__(self, x, y, p_type="normal"):
        self.width = 70
        self.height = 15
        self.x = x
        self.y = y
        self.type = p_type
        self.vx = random.choice([-2, 2]) if p_type == "moving" else 0
        self.has_item = random.random() < 0.07 if p_type == "normal" else False
        self.item_rect = pygame.Rect(self.x + self.width // 2 - 10, self.y - 15, 20, 15) if self.has_item else None
        self.break_timer = 0
        self.is_breaking = False
        self.break_delay = 30
    def update(self):
        if self.type == "moving":
            self.x += self.vx
            if self.x <= 0 or self.x + self.width >= WIDTH:
                self.vx *= -1
            if self.has_item and self.item_rect:
                self.item_rect.x = self.x + self.width // 2 - 10
        if self.type == "breaking" and self.is_breaking:
            self.break_timer += 1
            if self.break_timer >= self.break_delay:
                return False
        return True
    def start_breaking(self):
        if self.type == "breaking" and not self.is_breaking:
            self.is_breaking = True
            self.break_timer = 0
    def draw(self):
        if self.type == "moving":
            color = BLUE
        elif self.type == "breaking":
            if self.is_breaking:
                if self.break_timer % 20 < 10:
                    color = RED
                else:
                    color = (200, 50, 50)
            else:
                color = RED
        else:
            color = GREEN
        pygame.draw.rect(SCREEN, color, (self.x, self.y, self.width, self.height), border_radius=4)
        if self.has_item and self.item_rect:
            pygame.draw.rect(SCREEN, YELLOW, self.item_rect, border_radius=3)
def generate_platform_type(score):
    rand = random.random()
    if score < 5000:
        return "normal"
    elif score < 15000:
        return "moving" if rand < 0.3 else "normal"
    else:
        if rand < 0.30: return "moving"
        if rand < 0.45: return "breaking"
        return "normal"
def settings_menu():
    global current_color_index
    in_settings = True
    color_buttons = []
    for i, color in enumerate(PLAYER_COLORS):
        x = WIDTH // 2 - 100 + i * 80
        y = HEIGHT // 2 - 20
        btn = Button(x, y, 60, 40, PLAYER_NAMES[i][0], color, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
        color_buttons.append(btn)
    exit_btn = Button(WIDTH // 2 - 50, HEIGHT // 2 + 60, 100, 40, "Выход", RED, (200, 50, 50))
    while in_settings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for i, btn in enumerate(color_buttons):
                if btn.handle_event(event):
                    current_color_index = i
            if exit_btn.handle_event(event):
                in_settings = False
        SCREEN.fill((50, 50, 80))
        title = FONT_BIG.render("Скины:", True, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        for i, btn in enumerate(color_buttons):
            btn.draw(SCREEN)
            if current_color_index == i:
                pygame.draw.rect(SCREEN, YELLOW, btn.rect, 3, border_radius=10)
        exit_btn.draw(SCREEN)
        preview_rect = pygame.Rect(WIDTH // 2 - 15, 250, 30, 30)
        pygame.draw.rect(SCREEN, PLAYER_COLORS[current_color_index], preview_rect, border_radius=8)
        pygame.draw.rect(SCREEN, BLACK, preview_rect, 2, border_radius=8)
        name = FONT.render(PLAYER_NAMES[current_color_index], True, WHITE)
        SCREEN.blit(name, (WIDTH // 2 - name.get_width() // 2, 290))
        pygame.display.flip()
        CLOCK.tick(FPS)
def main():
    global current_color_index
    player = Player()
    platforms = [Platform(WIDTH // 2 - 35, HEIGHT - 50, "normal")]
    while len(platforms) < 10:
        px = random.randint(0, WIDTH - 70)
        py = platforms[-1].y - random.randint(60, 110)
        platforms.append(Platform(px, py, "normal"))
    high_score = 0
    game_over = False
    secret_activated = False
    bg_changed = False
    settings_btn = Button(WIDTH - 93, 10, 85, 30, "Скины", BLUE, (50, 50, 200))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.stdout.flush()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    main()
            if settings_btn.handle_event(event):
                settings_menu()
                player.color = PLAYER_COLORS[current_color_index]
        if not game_over:
            player.update()
            keys = pygame.key.get_pressed()
            if not secret_activated and check_secret_code(keys, player.score):
                player.score = 100000
                secret_activated = True
                print("🚀 РАКЕТА АКТИВИРОВАНА! +100000 очков!")
            if player.y < HEIGHT // 2:
                diff = HEIGHT // 2 - player.y
                player.y = HEIGHT // 2
                player.score += int(diff)
                for plat in platforms:
                    plat.y += diff
                    if plat.has_item and plat.item_rect:
                        plat.item_rect.y += diff
            platforms_to_remove = []
            for plat in platforms:
                if not plat.update():
                    platforms_to_remove.append(plat)
            for plat in platforms_to_remove:
                if plat in platforms:
                    platforms.remove(plat)
            platforms = [p for p in platforms if p.y < HEIGHT]
            while len(platforms) < 10:
                px = random.randint(0, WIDTH - 70)
                py = platforms[-1].y - random.randint(70, 120)
                p_type = generate_platform_type(player.score)
                platforms.append(Platform(px, py, p_type))
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for plat in platforms[:]:
                plat_rect = pygame.Rect(plat.x, plat.y, plat.width, plat.height)
                if plat.has_item and plat.item_rect and player_rect.colliderect(plat.item_rect):
                    player.jetpack_timer = 120
                    plat.has_item = False
                if player_rect.colliderect(plat_rect) and player.vy > 0 and (
                        player.y + player.height - player.vy <= plat.y + 4):
                    if plat.type == "breaking":
                        plat.start_breaking()
                        player.vy = BOUNCE_VELOCITY
                    else:
                        player.vy = BOUNCE_VELOCITY
            if player.score >= 15000 and not bg_changed:
                global BACKGROUND
                BACKGROUND = change_background(player.score)
                bg_changed = True
            if player.y > HEIGHT:
                high_score = max(high_score, player.score)
                game_over = True
                secret_activated = False
        SCREEN.blit(BACKGROUND, (0, 0))
        for plat in platforms:
            plat.draw()
        if not game_over:
            player.draw()
        settings_btn.draw(SCREEN)
        score_txt = FONT.render(f"Высота: {player.score}", True, FONT_COLOR)
        SCREEN.blit(score_txt, (15, 15))
        if game_over:
            over_txt = FONT.render("Игра окончена!", True, RED)
            retry_txt = FONT.render("Нажми пробел для рестарта!", True, BLACK)
            SCREEN.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, HEIGHT // 2 - 40))
            SCREEN.blit(retry_txt, (WIDTH // 2 - retry_txt.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.flip()
        CLOCK.tick(FPS)
if __name__ == "__main__":
    main()