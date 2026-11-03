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

def choose_guard_move(guard, player, guard_row, all_guards, depth=3):
    """
    One independent guard agent.
    MAX = guard chooses left/right/stay.
    MIN = human chooses the best cardinal move (or stay).
    Search alternates: guard, player, player ... within bounded depth.
    Alpha-beta pruning returns the same decision as Minimax.
    """
    nodes = 0
    other_guards = tuple(g for g in all_guards if g != guard)

    def player_successfully_crossed(p):
        # A guard loses this local encounter if the player has passed its line.
        return p[0] < guard_row if player[0] > guard_row else p[0] > guard_row

    def search(p, gcol, remaining, maximizing, alpha, beta, last_p=None, last_g=None):
        nonlocal nodes
        nodes += 1
        gpos = (guard_row, gcol)
        if _caught(p, gpos, last_p, last_g):
            return 100
        if any(p == other for other in other_guards):
            return 100
        if player_successfully_crossed(p):
            return -100
        if remaining <= 0:
            return evaluate(p, gpos, guard_row)

        if maximizing:
            value = -10**9
            for move in GUARD_ACTIONS:
                next_col = _clamp_col(gcol + move)
                # Guard can only move horizontally on its own row.
                candidate = (guard_row, next_col)
                if candidate in other_guards:
                    continue
                score = search(p, next_col, remaining - 1, False,
                               alpha, beta, p, gpos)
                value = max(value, score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        value = 10**9
        pr, pc = p
        for dr, dc in PLAYER_ACTIONS:
            nr, nc = pr + dr, pc + dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            np = (nr, nc)
            # If player moves into/crosses this guard, it is a terminal capture.
            if _caught(np, gpos, p, gpos):
                score = 100
            else:
                score = search(np, gcol, remaining - 1, True,
                               alpha, beta, p, gpos)
            value = min(value, score)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    best_col = guard[1]
    best_value = -10**9
    alpha, beta = -10**9, 10**9
    for move in GUARD_ACTIONS:
        candidate_col = _clamp_col(guard[1] + move)
        candidate_pos = (guard_row, candidate_col)
        if candidate_pos in other_guards:
            continue
        value = search(player, candidate_col, depth - 1, False,
                       alpha, beta, player, guard)
        if value > best_value:
            best_value = value
            best_col = candidate_col
        alpha = max(alpha, best_value)
        if alpha >= beta:
            break
    return best_col, nodes
