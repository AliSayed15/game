# ============================================================
#   XO Game - vs AI (Minimax Algorithm)
#   pip install pygame
# ============================================================

import pygame
import sys
import random
import math
from enum import Enum, auto
from typing import Optional, List, Tuple


# ── Constants ────────────────────────────────────────────────
WINDOW_SIZE   = 540
GRID_SIZE     = 3
CELL_SIZE     = WINDOW_SIZE // GRID_SIZE
LINE_WIDTH    = 6
PIECE_WIDTH   = 10
RADIUS        = CELL_SIZE // 3
AI_THINK_MS   = 500

BG_COLOR      = ( 15,  15,  20)
LINE_COLOR    = ( 50,  50,  65)
X_COLOR       = (231,  76,  60)
O_COLOR       = ( 52, 152, 219)
WIN_COLOR     = (241, 196,  15)
TEXT_COLOR    = (236, 240, 241)
MUTED_COLOR   = (127, 140, 141)
PANEL_COLOR   = ( 25,  25,  35)
BTN_COLOR     = ( 44,  62,  80)
BTN_HOVER     = ( 52,  73,  94)
EASY_COLOR    = ( 39, 174,  96)
MED_COLOR     = (230, 126,  34)
HARD_COLOR    = (192,  57,  43)


class Difficulty(Enum):
    EASY   = auto()
    MEDIUM = auto()
    HARD   = auto()


class GameState(Enum):
    MENU       = auto()
    PLAYING    = auto()
    AI_THINK   = auto()
    GAME_OVER  = auto()


# ── Board Logic ──────────────────────────────────────────────

class Board:
    EMPTY  = 0
    HUMAN  = 1
    AI     = -1

    def __init__(self):
        self.cells: List[List[int]] = [[self.EMPTY]*3 for _ in range(3)]

    def reset(self):
        self.cells = [[self.EMPTY]*3 for _ in range(3)]

    def make_move(self, row: int, col: int, player: int) -> bool:
        if self.cells[row][col] == self.EMPTY:
            self.cells[row][col] = player
            return True
        return False

    def undo_move(self, row: int, col: int):
        self.cells[row][col] = self.EMPTY

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        return [(r, c) for r in range(3) for c in range(3)
                if self.cells[r][c] == self.EMPTY]

    def check_winner(self) -> Optional[int]:
        b = self.cells
        lines = [
            [b[0][0], b[0][1], b[0][2]],
            [b[1][0], b[1][1], b[1][2]],
            [b[2][0], b[2][1], b[2][2]],
            [b[0][0], b[1][0], b[2][0]],
            [b[0][1], b[1][1], b[2][1]],
            [b[0][2], b[1][2], b[2][2]],
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]],
        ]
        for line in lines:
            if line[0] != self.EMPTY and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def get_winning_line(self) -> Optional[Tuple[Tuple, Tuple]]:
        b = self.cells
        checks = [
            ((0,0),(0,1),(0,2)), ((1,0),(1,1),(1,2)), ((2,0),(2,1),(2,2)),
            ((0,0),(1,0),(2,0)), ((0,1),(1,1),(2,1)), ((0,2),(1,2),(2,2)),
            ((0,0),(1,1),(2,2)), ((0,2),(1,1),(2,0)),
        ]
        for (r1,c1),(r2,c2),(r3,c3) in checks:
            if (b[r1][c1] != self.EMPTY and
                    b[r1][c1] == b[r2][c2] == b[r3][c3]):
                start = (c1*CELL_SIZE + CELL_SIZE//2, r1*CELL_SIZE + CELL_SIZE//2)
                end   = (c3*CELL_SIZE + CELL_SIZE//2, r3*CELL_SIZE + CELL_SIZE//2)
                return (start, end)
        return None

    def is_full(self) -> bool:
        return all(self.cells[r][c] != self.EMPTY
                   for r in range(3) for c in range(3))


# ── AI (Minimax + Alpha-Beta) ─────────────────────────────────

class AI:
    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty

    def get_move(self, board: Board) -> Tuple[int, int]:
        empty = board.get_empty_cells()
        if not empty:
            return (-1, -1)
        if self.difficulty == Difficulty.EASY:
            return random.choice(empty)
        if self.difficulty == Difficulty.MEDIUM:
            if random.random() < 0.4:
                return random.choice(empty)
        return self._minimax_best(board)

    def _minimax_best(self, board: Board) -> Tuple[int, int]:
        best_score = -math.inf
        best_move  = board.get_empty_cells()[0]
        for (r, c) in board.get_empty_cells():
            board.make_move(r, c, Board.AI)
            score = self._minimax(board, 0, False, -math.inf, math.inf)
            board.undo_move(r, c)
            if score > best_score:
                best_score = score
                best_move  = (r, c)
        return best_move

    def _minimax(self, board: Board, depth: int,
                 is_max: bool, alpha: float, beta: float) -> float:
        winner = board.check_winner()
        if winner == Board.AI:    return 10 - depth
        if winner == Board.HUMAN: return depth - 10
        if board.is_full():       return 0
        if is_max:
            best = -math.inf
            for (r, c) in board.get_empty_cells():
                board.make_move(r, c, Board.AI)
                best = max(best, self._minimax(board, depth+1, False, alpha, beta))
                board.undo_move(r, c)
                alpha = max(alpha, best)
                if beta <= alpha: break
            return best
        else:
            best = math.inf
            for (r, c) in board.get_empty_cells():
                board.make_move(r, c, Board.HUMAN)
                best = min(best, self._minimax(board, depth+1, True, alpha, beta))
                board.undo_move(r, c)
                beta = min(beta, best)
                if beta <= alpha: break
            return best


# ── Renderer ─────────────────────────────────────────────────

class Renderer:
    PANEL_H = 160

    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.font_xl = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_lg = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 22)
        self.font_sm = pygame.font.SysFont("Arial", 17)

    def _cx(self, surf: pygame.Surface) -> int:
        return (WINDOW_SIZE - surf.get_width()) // 2

    def draw_menu(self, hovered: Optional[str]):
        self.screen.fill(BG_COLOR)

        title = self.font_xl.render("X  O", True, TEXT_COLOR)
        self.screen.blit(title, (self._cx(title), 55))

        sub = self.font_md.render("Play Against the AI", True, MUTED_COLOR)
        self.screen.blit(sub, (self._cx(sub), 125))

        levels = [
            ("EASY",   "easy",   EASY_COLOR, 210),
            ("MEDIUM", "medium", MED_COLOR,  300),
            ("HARD",   "hard",   HARD_COLOR, 390),
        ]
        for label, key, color, y in levels:
            rect = pygame.Rect(WINDOW_SIZE//2 - 130, y, 260, 60)
            hover = hovered == key
            pygame.draw.rect(self.screen, BTN_HOVER if hover else BTN_COLOR,
                             rect, border_radius=12)
            pygame.draw.rect(self.screen, color, rect, width=3, border_radius=12)
            txt = self.font_lg.render(label, True, color)
            self.screen.blit(txt, (rect.centerx - txt.get_width()//2,
                                   rect.centery - txt.get_height()//2))

        hint = self.font_sm.render("Choose difficulty to start", True, MUTED_COLOR)
        self.screen.blit(hint, (self._cx(hint), 480))

    def get_menu_btn(self, pos) -> Optional[str]:
        for key, y in [("easy", 210), ("medium", 300), ("hard", 390)]:
            if pygame.Rect(WINDOW_SIZE//2 - 130, y, 260, 60).collidepoint(pos):
                return key
        return None

    def draw_game(self, board: Board, state: GameState,
                  winner: Optional[int], difficulty: Difficulty,
                  score: dict, thinking: bool):

        self.screen.fill(BG_COLOR, (0, 0, WINDOW_SIZE, WINDOW_SIZE))
        pygame.draw.rect(self.screen, PANEL_COLOR,
                         (0, WINDOW_SIZE, WINDOW_SIZE, self.PANEL_H))
        pygame.draw.line(self.screen, LINE_COLOR,
                         (0, WINDOW_SIZE), (WINDOW_SIZE, WINDOW_SIZE), 2)

        self._draw_grid()
        self._draw_pieces(board)

        if winner is not None:
            line = board.get_winning_line()
            if line:
                pygame.draw.line(self.screen, WIN_COLOR,
                                 line[0], line[1], LINE_WIDTH + 4)

        self._draw_panel(difficulty, score, state, winner, thinking)

    def _draw_grid(self):
        for i in range(1, GRID_SIZE):
            pygame.draw.line(self.screen, LINE_COLOR,
                             (i*CELL_SIZE, 20), (i*CELL_SIZE, WINDOW_SIZE-20), LINE_WIDTH)
            pygame.draw.line(self.screen, LINE_COLOR,
                             (20, i*CELL_SIZE), (WINDOW_SIZE-20, i*CELL_SIZE), LINE_WIDTH)

    def _draw_pieces(self, board: Board):
        for r in range(3):
            for c in range(3):
                val = board.cells[r][c]
                cx  = c * CELL_SIZE + CELL_SIZE // 2
                cy  = r * CELL_SIZE + CELL_SIZE // 2
                if val == Board.HUMAN:
                    off = RADIUS - 15
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx-off, cy-off), (cx+off, cy+off), PIECE_WIDTH)
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx+off, cy-off), (cx-off, cy+off), PIECE_WIDTH)
                elif val == Board.AI:
                    pygame.draw.circle(self.screen, O_COLOR,
                                       (cx, cy), RADIUS, PIECE_WIDTH)

    def _draw_panel(self, difficulty: Difficulty, score: dict,
                    state: GameState, winner: Optional[int], thinking: bool):
        Y = WINDOW_SIZE
        diff_info = {
            Difficulty.EASY:   ("EASY",   EASY_COLOR),
            Difficulty.MEDIUM: ("MEDIUM", MED_COLOR),
            Difficulty.HARD:   ("HARD",   HARD_COLOR),
        }
        diff_name, diff_color = diff_info[difficulty]

        lvl = self.font_sm.render(f"Level: {diff_name}", True, diff_color)
        self.screen.blit(lvl, (20, Y + 14))

        sc = self.font_sm.render(
            f"You: {score['human']}   Draw: {score['draw']}   AI: {score['ai']}",
            True, MUTED_COLOR)
        self.screen.blit(sc, (20, Y + 36))

        if thinking:
            msg, color = "AI is thinking...  o_O", O_COLOR
        elif state == GameState.GAME_OVER:
            if winner == Board.HUMAN:
                msg, color = "You Win!  \\(^o^)/", EASY_COLOR
            elif winner == Board.AI:
                msg, color = "AI Wins!  (>_<)", HARD_COLOR
            else:
                msg, color = "Draw!  (-_-)", MED_COLOR
        else:
            msg, color = "Your turn! Click a cell.", TEXT_COLOR

        msg_surf = self.font_lg.render(msg, True, color)
        self.screen.blit(msg_surf, (self._cx(msg_surf), Y + 65))

        self._draw_bottom_btns()

    def _draw_bottom_btns(self):
        mouse = pygame.mouse.get_pos()
        Y = WINDOW_SIZE
        btn_r = pygame.Rect(WINDOW_SIZE//2 + 10,  Y + 110, 155, 38)
        btn_m = pygame.Rect(WINDOW_SIZE//2 - 170, Y + 110, 155, 38)
        for btn, label in [(btn_r, "New Game  [R]"), (btn_m, "[M]  Menu")]:
            hover = btn.collidepoint(mouse)
            pygame.draw.rect(self.screen, BTN_HOVER if hover else BTN_COLOR,
                             btn, border_radius=8)
            pygame.draw.rect(self.screen, LINE_COLOR, btn, width=1, border_radius=8)
            t = self.font_sm.render(label, True, TEXT_COLOR)
            self.screen.blit(t, (btn.centerx - t.get_width()//2,
                                 btn.centery - t.get_height()//2))

    def get_game_btn(self, pos) -> Optional[str]:
        Y = WINDOW_SIZE
        if pygame.Rect(WINDOW_SIZE//2 + 10,  Y + 110, 155, 38).collidepoint(pos): return "restart"
        if pygame.Rect(WINDOW_SIZE//2 - 170, Y + 110, 155, 38).collidepoint(pos): return "menu"
        return None


# ── Main Game Controller ──────────────────────────────────────

class XOGame:
    PANEL_H = 160

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("XO  -  vs AI")
        self.screen    = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + self.PANEL_H))
        self.clock     = pygame.time.Clock()
        self.renderer  = Renderer(self.screen)
        self.board     = Board()
        self.ai        = AI(Difficulty.HARD)
        self.state     = GameState.MENU
        self.difficulty     = Difficulty.HARD
        self.winner: Optional[int] = None
        self.score          = {"human": 0, "ai": 0, "draw": 0}
        self.ai_think_timer = 0
        self.hovered_btn: Optional[str] = None

    def _start_game(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.ai = AI(difficulty)
        self.board.reset()
        self.winner = None
        self.state  = GameState.PLAYING

    def _restart(self):
        self.board.reset()
        self.winner = None
        self.state  = GameState.PLAYING

    def _handle_menu_events(self):
        mouse = pygame.mouse.get_pos()
        self.hovered_btn = self.renderer.get_menu_btn(mouse)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn = self.renderer.get_menu_btn(event.pos)
                if btn == "easy":   self._start_game(Difficulty.EASY)
                elif btn == "medium": self._start_game(Difficulty.MEDIUM)
                elif btn == "hard":   self._start_game(Difficulty.HARD)

    def _handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self._restart(); return
                if event.key == pygame.K_m:
                    self.state = GameState.MENU; return
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn = self.renderer.get_game_btn(event.pos)
                if btn == "restart": self._restart(); return
                if btn == "menu":    self.state = GameState.MENU; return
                if self.state == GameState.PLAYING:
                    mx, my = event.pos
                    if my < WINDOW_SIZE:
                        col = mx // CELL_SIZE
                        row = my // CELL_SIZE
                        if self.board.make_move(row, col, Board.HUMAN):
                            winner = self.board.check_winner()
                            if winner or self.board.is_full():
                                self._end_game(winner)
                            else:
                                self.state = GameState.AI_THINK
                                self.ai_think_timer = pygame.time.get_ticks()

    def _update_ai(self):
        if self.state != GameState.AI_THINK:
            return
        if pygame.time.get_ticks() - self.ai_think_timer >= AI_THINK_MS:
            move = self.ai.get_move(self.board)
            if move != (-1, -1):
                self.board.make_move(move[0], move[1], Board.AI)
            winner = self.board.check_winner()
            if winner or self.board.is_full():
                self._end_game(winner)
            else:
                self.state = GameState.PLAYING

    def _end_game(self, winner: Optional[int]):
        self.winner = winner
        self.state  = GameState.GAME_OVER
        if winner == Board.HUMAN: self.score["human"] += 1
        elif winner == Board.AI:  self.score["ai"]    += 1
        else:                     self.score["draw"]  += 1

    def run(self):
        while True:
            if self.state == GameState.MENU:
                self._handle_menu_events()
                self.renderer.draw_menu(self.hovered_btn)
            else:
                self._handle_game_events()
                self._update_ai()
                thinking = (self.state == GameState.AI_THINK)
                self.renderer.draw_game(
                    self.board, self.state, self.winner,
                    self.difficulty, self.score, thinking
                )
            pygame.display.flip()
            self.clock.tick(60)


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    game = XOGame()
    game.run()     