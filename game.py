import random
import time
from ai import choose_guard_move

COLS, ROWS = 7, 11
CELL, MARGIN = 54, 28
WIDTH = MARGIN * 2 + COLS * CELL
HEIGHT = 62 + ROWS * CELL + 92

COLORS = {
    "background": (24, 31, 43), "text": (238, 242, 247), "muted": (166, 178, 194),
    "grid": (66, 78, 94), "safe": (220, 231, 218), "guard_line": (239, 218, 193),
    "start": (186, 218, 245), "finish": (186, 218, 245),
    "guard_label": (100, 67, 43), "guard": (205, 70, 75), "player": (48, 111, 190),
    "item": (246, 194, 66), "bonus": (100, 190, 130)
}

class GobakSodorGame:
    def __init__(self):
        self.player = (10, 3)
        # Three horizontal guard lines. Each agent remains on its assigned row.
        self.guard_rows = (2, 5, 8)
        self.guards = [(2, 3), (5, 3), (8, 3)]
        # Mandatory item at row 5 and row 0; bonus at row 7.
        self.mandatory_items = [(5, random.randrange(COLS)), (0, random.randrange(COLS))]
        self.bonus_item = (7, random.randrange(COLS))
        self.collected = [False, False]
        self.bonus_collected = False
        self.score = 0
        self.player_steps = 0
        self.started_at = time.perf_counter()
        self.duration = 120
        self.finished = False
        self.won = False
        self.status = "Lewati garis penjagaan dan kumpulkan kedua item wajib."
        self.total_nodes = 0
        self.last_ai_ms = 0.0
        self.reached_finish_this_trip = False