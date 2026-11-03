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

    def time_left(self):
        return self.duration - (time.perf_counter() - self.started_at)

    def check_timeout(self):
        if not self.finished and self.time_left() <= 0:
            self.finished = True
            self.won = all(self.collected)
            self.status = "Waktu habis."

    def player_turn(self, delta):
        if self.finished:
            return
        dr, dc = delta
        r, c = self.player
        nr, nc = r + dr, c + dc
        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            self.status = "Tidak bisa bergerak keluar dari lapangan."
            return
        if abs(dr) + abs(dc) > 1:
            return

        old = self.player
        self.player = (nr, nc)
        self._collect_items()
        if self._caught_by_any_guard(old, self.player):
            self._reset_to_start("Tertangkap! Kamu kembali ke titik A.")
            return

        self.player_steps += 1
        self.status = "Langkah pemain."
        # A guard phase occurs after every two player actions.
        if self.player_steps >= 2:
            self.player_steps = 0
            was_caught = self._move_guards(old_player=old)
            self._collect_items()
            if was_caught or self._caught_by_any_guard(old, self.player):
                self._reset_to_start("Tertangkap penjaga! Kembali ke titik A.")
                return

        if self.player == (0, self.player[1]):
             if self.player[0] == 0 and not self.reached_finish_this_trip:
                self.score += 2
                self.reached_finish_this_trip = True
                self.status = "Sampai di garis B: +2 poin."

        # Kembali ke garis A (baris 10), kolom mana pun: +3 poin
        if self.player[0] == 10 and self.reached_finish_this_trip:
            self.score += 3
            self.reached_finish_this_trip = False
            self.status = "Kembali ke garis A: +3 poin."

        if all(self.collected):
            self.finished = True
            self.won = True
            self.status = "MENANG! Kedua item wajib berhasil dikumpulkan."
        self.check_timeout()

    def _collect_items(self):
        for i, item in enumerate(self.mandatory_items):
            if not self.collected[i] and self.player == item:
                self.collected[i] = True
                self.status = f"Item wajib {i + 1} berhasil diambil!"
        if not self.bonus_collected and self.player == self.bonus_item:
            self.bonus_collected = True
            self.score += 3
            self.status = "Item bonus didapatkan: +3 poin."

    def _caught_by_any_guard(self, old_player, new_player):
        for guard in self.guards:
            # Same cell or crossing positions in one move.
            if new_player == guard or (old_player == guard and new_player == old_player):
                return True
        return False

    def _reset_to_start(self, message):
        self.player = (10, 3)
        self.player_steps = 0
        self.reached_finish_this_trip = False
        self.status = message
        # Items already collected remain collected, as specified in the proposal.

    def _move_guards(self, old_player):
        start = time.perf_counter()
        updated = []
        old_guards = list(self.guards)
        for index, guard in enumerate(self.guards):
            new_col, nodes = choose_guard_move(
                guard=guard,
                player=self.player,
                guard_row=self.guard_rows[index],
                all_guards=self.guards,
                depth=3
            )
            self.total_nodes += nodes
            updated.append((guard[0], new_col))
        self.guards = updated
        self.last_ai_ms = (time.perf_counter() - start) * 1000
        # Detect a swap: player and guard cross positions during the same phase.
        for old_guard, new_guard in zip(old_guards, updated):
            if old_guard == self.player and new_guard == old_player:
                return True
            if new_guard == self.player:
                return True
        return False