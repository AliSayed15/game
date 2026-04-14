# ============================================================
#   🐍 لعبة الثعبان - Snake Game
#   تشتغل في Jupyter Notebook باستخدام pygame
# ============================================================

# ── الخطوة 1: تثبيت المكتبة (شغّل الخلية دي أول مرة بس) ──
# !pip install pygame


# ── الخطوة 2: الكود الكامل للعبة ──

import pygame
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum, auto


# ── الثوابت ──────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 600, 600
CELL_SIZE          = 20
COLS               = WINDOW_W // CELL_SIZE
ROWS               = WINDOW_H // CELL_SIZE
FPS_START          = 8          # سرعة البداية
FPS_MAX            = 20         # أقصى سرعة

# الألوان
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = ( 39, 174,  96)
DARK_GREEN = ( 27, 120,  66)
RED        = (231,  76,  60)
GRAY       = ( 44,  62,  80)
YELLOW     = (241, 196,  15)
BG_COLOR   = ( 18,  18,  18)
GRID_COLOR = ( 28,  28,  28)


class Direction(Enum):
    UP    = auto()
    DOWN  = auto()
    LEFT  = auto()
    RIGHT = auto()

# الاتجاهات المعاكسة (عشان ما نعكسش الثعبان على نفسه)
OPPOSITES = {
    Direction.UP:    Direction.DOWN,
    Direction.DOWN:  Direction.UP,
    Direction.LEFT:  Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


@dataclass
class Snake:
    body: List[Tuple[int, int]] = field(default_factory=list)
    direction: Direction        = Direction.RIGHT
    grew: bool                  = False

    def setup(self):
        """وضع الثعبان في منتصف الشاشة عند البداية."""
        cx, cy = COLS // 2, ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = Direction.RIGHT
        self.grew = False

    @property
    def head(self) -> Tuple[int, int]:
        return self.body[0]

    def change_direction(self, new_dir: Direction):
        """تغيير الاتجاه مع منع الانعكاس."""
        if new_dir != OPPOSITES[self.direction]:
            self.direction = new_dir

    def move(self):
        """تحريك الثعبان خطوة واحدة."""
        x, y = self.head
        moves = {
            Direction.UP:    (x,     y - 1),
            Direction.DOWN:  (x,     y + 1),
            Direction.LEFT:  (x - 1, y    ),
            Direction.RIGHT: (x + 1, y    ),
        }
        new_head = moves[self.direction]
        self.body.insert(0, new_head)
        if not self.grew:
            self.body.pop()
        self.grew = False

    def grow(self):
        """يخلي الثعبان يكبر في الخطوة الجاية."""
        self.grew = True

    def is_dead(self) -> bool:
        """تحقق من اصطدام بالحيطة أو بالجسم."""
        x, y = self.head
        hit_wall = not (0 <= x < COLS and 0 <= y < ROWS)
        hit_self = self.head in self.body[1:]
        return hit_wall or hit_self


@dataclass
class Food:
    pos: Tuple[int, int] = (0, 0)

    def spawn(self, snake_body: List[Tuple[int, int]]):
        """إنشاء أكل في مكان عشوائي بعيد عن الثعبان."""
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in snake_body:
                self.pos = pos
                return


class SnakeGame:
    """الكلاس الرئيسي اللي بيدير اللعبة كاملة."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("🐍 Snake Game")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock  = pygame.time.Clock()
        self.font_big   = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.font_tiny  = pygame.font.SysFont("Arial", 18)
        self.snake = Snake()
        self.food  = Food()
        self.reset()

    def reset(self):
        """إعادة ضبط اللعبة من الأول."""
        self.snake.setup()
        self.food.spawn(self.snake.body)
        self.score    = 0
        self.fps      = FPS_START
        self.running  = True
        self.game_over = False

    # ── الرسم ─────────────────────────────────────────────────

    def _draw_grid(self):
        for x in range(0, WINDOW_W, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_H))
        for y in range(0, WINDOW_H, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_W, y))

    def _draw_snake(self):
        for i, (x, y) in enumerate(self.snake.body):
            rect = pygame.Rect(x * CELL_SIZE + 1, y * CELL_SIZE + 1,
                               CELL_SIZE - 2, CELL_SIZE - 2)
            color = GREEN if i == 0 else DARK_GREEN  # الرأس أفتح
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def _draw_food(self):
        fx, fy = self.food.pos
        cx = fx * CELL_SIZE + CELL_SIZE // 2
        cy = fy * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, RED, (cx, cy), CELL_SIZE // 2 - 2)

    def _draw_hud(self):
        score_surf = self.font_small.render(f"النقاط: {self.score}", True, WHITE)
        speed_surf = self.font_tiny.render(f"السرعة: {self.fps}", True, GRAY)
        self.screen.blit(score_surf, (10, 10))
        self.screen.blit(speed_surf, (10, 38))

    def _draw_game_over(self):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("Game Over!", True, RED)
        score = self.font_small.render(f"نقاطك: {self.score}", True, WHITE)
        retry = self.font_small.render("اضغط R للعب تاني  |  Q للخروج", True, YELLOW)

        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 60)))
        self.screen.blit(score, score.get_rect(center=(WINDOW_W//2, WINDOW_H//2)))
        self.screen.blit(retry, retry.get_rect(center=(WINDOW_W//2, WINDOW_H//2 + 50)))

    def _draw_start_screen(self):
        self.screen.fill(BG_COLOR)
        title = self.font_big.render("🐍 Snake", True, GREEN)
        msg   = self.font_small.render("اضغط أي زرار تبدأ", True, WHITE)
        ctrl  = self.font_tiny.render("↑ ↓ ← →  للتحكم  |  Q للخروج", True, GRAY)
        self.screen.blit(title, title.get_rect(center=(WINDOW_W//2, WINDOW_H//2 - 60)))
        self.screen.blit(msg,   msg.get_rect(center=(WINDOW_W//2, WINDOW_H//2)))
        self.screen.blit(ctrl,  ctrl.get_rect(center=(WINDOW_W//2, WINDOW_H//2 + 40)))

    # ── الإدخال ───────────────────────────────────────────────

    def _handle_events(self) -> str:
        """معالجة ضغطات الكيبورد. ترجع 'quit' أو 'restart' أو ''."""
        key_map = {
            pygame.K_UP:    Direction.UP,
            pygame.K_DOWN:  Direction.DOWN,
            pygame.K_LEFT:  Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return "quit"
                if event.key == pygame.K_r and self.game_over:
                    return "restart"
                if event.key in key_map and not self.game_over:
                    self.snake.change_direction(key_map[event.key])
        return ""

    # ── المنطق ────────────────────────────────────────────────

    def _update(self):
        self.snake.move()
        if self.snake.is_dead():
            self.game_over = True
            return
        if self.snake.head == self.food.pos:
            self.snake.grow()
            self.food.spawn(self.snake.body)
            self.score += 10
            # زيادة السرعة كل 5 نقاط أكل
            self.fps = min(FPS_START + (self.score // 50), FPS_MAX)

    # ── الحلقة الرئيسية ───────────────────────────────────────

    def run(self):
        """تشغيل اللعبة - ما تتوقفش إلا لما تضغط Q."""
        # شاشة البداية
        waiting = True
        while waiting:
            self._draw_start_screen()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit(); return
                    waiting = False

        # الحلقة الرئيسية
        while self.running:
            action = self._handle_events()
            if action == "quit":
                break
            if action == "restart":
                self.reset()

            if not self.game_over:
                self._update()

            # الرسم
            self.screen.fill(BG_COLOR)
            self._draw_grid()
            self._draw_food()
            self._draw_snake()
            self._draw_hud()
            if self.game_over:
                self._draw_game_over()

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        print(f"✅ اللعبة خلصت! نقاطك: {self.score}")


# ── التشغيل ───────────────────────────────────────────────────
if __name__ == "__main__":
    game = SnakeGame()
    game.run()