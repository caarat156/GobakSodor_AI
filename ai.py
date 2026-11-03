from functools import lru_cache

COLS, ROWS = 7, 11
PLAYER_ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1), (0, 0))
GUARD_ACTIONS = (-1, 0, 1)

def _clamp_col(col):
    return max(0, min(COLS - 1, col))

def _caught(player, guard_pos, old_player=None, old_guard=None):
    if player == guard_pos:
        return True
    if old_player is not None and old_guard is not None:
        if player == old_guard and guard_pos == old_player:
            return True
    return False

def evaluate(player, guard, guard_row):
    """Proposal evaluation: -10*D_horiz -5*D_vert +15*C_intercept."""
    pr, pc = player
    gr, gc = guard
    d_horiz = abs(gc - pc)
    d_vert = abs(guard_row - pr)
    # Interception potential: player is approaching the guard's row
    # and the guard occupies the player's current column.
    intercept = 1 if gc == pc and d_vert <= 2 else 0
    return -10 * d_horiz - 5 * d_vert + 15 * intercept