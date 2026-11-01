"""
Gobak Sodor AI — Minimax + Alpha-Beta Pruning
Kontrol: W/A/S/D atau tombol panah. ENTER untuk mulai/lanjut, ESC untuk kembali/keluar.
Ubah PAKAI_SPRITE di config.py untuk mengganti tampilan karakter.
"""
import random
import time
import pygame
from config import PAKAI_SPRITE

pygame.init()

CELL = 42
COLS, ROWS = 7, 11
WIDTH = COLS * CELL
HUD_H = 112
HEIGHT = ROWS * CELL + HUD_H
FPS = 60
GAME_SECONDS = 120

BG = (22, 28, 38)
GRID = (70, 83, 100)
WHITE = (240, 244, 248)
MUTED = (185, 195, 207)
PLAYER_COLOR = (65, 190, 255)
GUARD_COLORS = [(245, 95, 95), (255, 174, 66), (181, 118, 255)]
ITEM_COLOR = (255, 220, 70)
BONUS_COLOR = (82, 230, 154)
SAFE_COLOR = (32, 54, 58)
START_COLOR = (34, 83, 62)
END_COLOR = (65, 57, 94)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gobak Sodor AI")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 21)
SMALL = pygame.font.SysFont("arial", 15)
TITLE = pygame.font.SysFont("arial", 48, bold=True)
BIG = pygame.font.SysFont("arial", 58, bold=True)

# Baris penjagaan untuk tiga agen independen
GUARD_ROWS = [1, 2, 3]
DEPTH_LIMIT = 4

def text(surface, msg, font, color, center):
    img = font.render(msg, True, color)
    surface.blit(img, img.get_rect(center=center))

def cell_center(pos):
    x, y = pos
    return x * CELL + CELL // 2, HUD_H + y * CELL + CELL // 2

def draw_character(surface, pos, color, label, is_player=False):
    cx, cy = cell_center(pos)
    radius = 16
    if PAKAI_SPRITE:
        # Sprite sederhana berbentuk karakter, dibuat langsung dengan pygame.
        pygame.draw.circle(surface, color, (cx, cy - 5), 10)
        pygame.draw.ellipse(surface, color, (cx - 12, cy + 4, 24, 19))
        pygame.draw.circle(surface, WHITE, (cx - 3, cy - 6), 2)
        pygame.draw.circle(surface, WHITE, (cx + 3, cy - 6), 2)
    else:
        pygame.draw.rect(surface, color, (cx - radius, cy - radius, radius * 2, radius * 2), border_radius=5)
    label_img = SMALL.render(label, True, WHITE)
    surface.blit(label_img, label_img.get_rect(center=(cx, cy + 27)))

def random_item(exclude):
    choices = [(x, y) for y in range(ROWS) for x in range(COLS) if (x, y) not in exclude]
    return random.choice(choices)

def new_game():
    player = (3, 10)
    guards = [(random.randrange(COLS), y) for y in GUARD_ROWS]
    # Item wajib satu di baris 5 dan satu di baris 0, bonus di baris 7.
    required1 = (random.randrange(COLS), 5)
    required2 = (random.randrange(COLS), 0)
    while required2 == required1:
        required2 = (random.randrange(COLS), 0)
    bonus = (random.randrange(COLS), 7)
    return {
        "player": player,
        "guards": guards,
        "required": [required1, required2],
        "collected": [False, False],
        "bonus": bonus,
        "bonus_taken": False,
        "score": 0,
        "player_steps": 0,
        "time_start": time.time(),
        "status": "playing",
        "message": "",
    }

def caught(player, old_player, guards, old_guards):
    for i, g in enumerate(guards):
        old_g = old_guards[i]
        if player == g or (player == old_g and old_player == g):
            return True
    return False

def legal_player_moves(pos):
    x, y = pos
    result = []
    for dx, dy in [(0,-1), (0,1), (-1,0), (1,0), (0,0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            result.append((nx, ny))
    return result

def guard_moves(pos):
    x, y = pos
    return [(nx, y) for nx in (x-1, x, x+1) if 0 <= nx < COLS]

def evaluate_guard(guard_pos, player_pos, guard_row):
    # Sesuai proposal: bobot jarak horizontal, jarak vertikal ke garis,
    # dan indikator potensi pencegatan.
    dhoriz = abs(guard_pos[0] - player_pos[0])
    dvert = abs(guard_row - player_pos[1])
    intercept = 1 if guard_pos[0] == player_pos[0] else 0
    return -10 * dhoriz - 5 * dvert + 15 * intercept

def minimax_ab(guard_pos, player_pos, guard_row, depth, alpha, beta, maximizing):
    if player_pos == guard_pos:
        return 100 if maximizing else -100
    if depth == 0:
        return evaluate_guard(guard_pos, player_pos, guard_row)
    if maximizing:  # giliran penjaga (MAX)
        best = -10**9
        for move in guard_moves(guard_pos):
            value = minimax_ab(move, player_pos, guard_row, depth - 1, alpha, beta, False)
            best = max(best, value)
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best
    else:  # giliran pemain (MIN)
        best = 10**9
        for move in legal_player_moves(player_pos):
            value = minimax_ab(guard_pos, move, guard_row, depth - 1, alpha, beta, True)
            best = min(best, value)
            beta = min(beta, best)
            if alpha >= beta:
                break
        return best

def choose_guard_move(guard_pos, player_pos, guard_row):
    best_move, best_value = guard_pos, -10**9
    for move in guard_moves(guard_pos):
        value = minimax_ab(move, player_pos, guard_row, DEPTH_LIMIT - 1, -10**9, 10**9, False)
        if value > best_value:
            best_move, best_value = move, value
    return best_move

def move_guards(game):
    old_guards = game["guards"][:]
    # Posisi pemain tidak berubah selama fase penjaga; simpan posisi tersebut
    # untuk pemeriksaan tabrakan pada kotak yang sama maupun pertukaran posisi.
    player_before_guard_turn = game["player"]
    for i, guard in enumerate(game["guards"]):
        game["guards"][i] = choose_guard_move(guard, game["player"], GUARD_ROWS[i])
    if caught(game["player"], player_before_guard_turn, game["guards"], old_guards):
        # Jika tertangkap, pemain kembali ke titik A; item yang sudah didapat tetap tersimpan.
        game["player"] = (3, 10)
        game["score"] = max(0, game["score"] - 1)
        game["message"] = "TERTANGKAP! Kembali ke titik A (-1 poin)"

def collect_items(game):
    p = game["player"]
    for i, item in enumerate(game["required"]):
        if not game["collected"][i] and p == item:
            game["collected"][i] = True
            game["score"] += 1
            game["message"] = "Item wajib didapat! (+1)"
    if not game["bonus_taken"] and p == game["bonus"]:
        game["bonus_taken"] = True
        game["score"] += 3
        game["message"] = "Item bonus didapat! (+3)"
    if p == (3, 0):
        game["score"] += 2
        game["message"] = "Sampai di titik B! (+2)"
    if p == (3, 10) and game["player_steps"] > 0:
        # Poin kembali ke A diberikan saat semua item wajib sudah didapat.
        if all(game["collected"]):
            game["score"] += 3
            game["message"] = "Kembali ke titik A! (+3)"
    if all(game["collected"]):
        game["status"] = "win"

def draw_game(game):
    screen.fill(BG)
    # HUD
    elapsed = time.time() - game["time_start"]
    remaining = max(0, int(GAME_SECONDS - elapsed))
    hud_font = pygame.font.SysFont("arial", 17)
    # Baris 1: skor dan timer; baris 2: status item; baris 3: kontrol.
    text(screen, f"SKOR: {game['score']}", hud_font, WHITE, (70, 22))
    text(screen, f"WAKTU: {remaining//60:02d}:{remaining%60:02d}", hud_font, WHITE, (WIDTH-82, 22))
    text(screen, "ITEM WAJIB: " + " ".join("✓" if v else "□" for v in game["collected"]), hud_font, ITEM_COLOR, (WIDTH//2, 52))
    text(screen, "WASD / Panah: gerak  |  ESC: menu", SMALL, MUTED, (WIDTH//2, 82))
    # Grid and zones
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*CELL, HUD_H+y*CELL, CELL, CELL)
            fill = (BG)
            if y == 10: fill = START_COLOR
            elif y == 0: fill = END_COLOR
            elif y in GUARD_ROWS: fill = (52, 43, 48)
            elif y in (4, 6, 9): fill = SAFE_COLOR
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, GRID, rect, 1)
    text(screen, "B / FINISH", SMALL, WHITE, (WIDTH//2, HUD_H+15))
    text(screen, "A / START", SMALL, WHITE, (WIDTH//2, HUD_H+(ROWS-1)*CELL+CELL-13))
    # Items
    for i, item in enumerate(game["required"]):
        if not game["collected"][i]:
            cx, cy = cell_center(item)
            pygame.draw.circle(screen, ITEM_COLOR, (cx, cy), 13)
            text(screen, str(i+1), SMALL, (30, 30, 30), (cx, cy))
    if not game["bonus_taken"]:
        cx, cy = cell_center(game["bonus"])
        pygame.draw.polygon(screen, BONUS_COLOR, [(cx,cy-14),(cx+14,cy),(cx,cy+14),(cx-14,cy)])
        text(screen, "+3", SMALL, (15, 30, 25), (cx, cy))
    # Characters
    for i, guard in enumerate(game["guards"]):
        draw_character(screen, guard, GUARD_COLORS[i], f"G{i+1}")
    draw_character(screen, game["player"], PLAYER_COLOR, "KAMU", True)
    if game["message"]:
        text(screen, game["message"], SMALL, WHITE, (WIDTH//2, HEIGHT-12))
    pygame.display.flip()
    return remaining

def centered_lines(lines, y, font, color=WHITE, gap=38):
    for line in lines:
        text(screen, line, font, color, (WIDTH//2, y))
        y += gap

def menu_screen():
    while True:
        screen.fill(BG)
        text(screen, "GOBAK SODOR", TITLE, WHITE, (WIDTH//2, HEIGHT//2-100))
        text(screen, "MINIMAX + ALPHA-BETA PRUNING", FONT, BONUS_COLOR, (WIDTH//2, HEIGHT//2-50))
        centered_lines(["Tekan ENTER untuk mulai", "Tekan H untuk melihat petunjuk", "ESC untuk keluar"], HEIGHT//2+20, FONT, MUTED, 38)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "start"
                if event.key == pygame.K_h:
                    instruction_screen()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); raise SystemExit
        clock.tick(FPS)

def instruction_screen():
    # Semua teks dibungkus sesuai lebar jendela agar tidak terpotong.
    title_font = pygame.font.SysFont("arial", 29, bold=True)
    body_font = pygame.font.SysFont("arial", 17)
    hint_font = pygame.font.SysFont("arial", 15)
    key_font = pygame.font.SysFont("arial", 20, bold=True)
    margin = 22
    max_text_width = WIDTH - margin * 2

    instructions = [
        "1. Kumpulkan 2 item wajib: satu di baris 5 dan satu di baris 0.",
        "2. Ambil item bonus di baris 7 untuk mendapat +3 poin.",
        "3. Gerak satu kotak dengan W/A/S/D atau tombol panah.",
        "4. Setelah 2 langkah pemain, 3 penjaga AI bergerak.",
        "5. Jika tertangkap, kembali ke A; item yang didapat tetap tersimpan.",
        "6. Selesaikan misi sebelum 2 menit untuk MENANG.",
    ]

    def wrap_text(message, font, max_width):
        words = message.split()
        rows, current = [], ""
        for word in words:
            candidate = word if not current else current + " " + word
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    rows.append(current)
                current = word
        if current:
            rows.append(current)
        return rows

    while True:
        screen.fill(BG)
        text(screen, "PETUNJUK PERMAINAN", title_font, WHITE, (WIDTH//2, 48))
        text(screen, "Cara bermain Gobak Sodor AI", hint_font, BONUS_COLOR, (WIDTH//2, 78))

        y = 112
        line_gap = 22
        item_gap = 9
        for instruction in instructions:
            wrapped = wrap_text(instruction, body_font, max_text_width)
            for row in wrapped:
                text(screen, row, body_font, MUTED, (WIDTH//2, y))
                y += line_gap
            y += item_gap

        # Ilustrasi tombol WASD dengan ukuran yang proporsional.
        key_size = 34
        key_gap = 7
        keys_y = HEIGHT - 100
        positions = [
            ("W", WIDTH//2, keys_y),
            ("A", WIDTH//2 - key_size - key_gap, keys_y + key_size + 5),
            ("S", WIDTH//2, keys_y + key_size + 5),
            ("D", WIDTH//2 + key_size + key_gap, keys_y + key_size + 5),
        ]
        for key, cx, cy in positions:
            rect = pygame.Rect(cx-key_size//2, cy-key_size//2, key_size, key_size)
            pygame.draw.rect(screen, (57, 76, 95), rect, border_radius=5)
            text(screen, key, key_font, WHITE, (cx, cy))

        text(screen, "ENTER = mulai permainan", hint_font, WHITE, (WIDTH//2, HEIGHT-28))
        text(screen, "ESC = kembali ke menu", hint_font, MUTED, (WIDTH//2, HEIGHT-10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    return
        clock.tick(FPS)

def result_screen(game):
    won = game["status"] == "win"
    headline = "MENANG!" if won else "KALAH!"
    subtitle = "Misi item wajib berhasil diselesaikan." if won else "Waktu habis sebelum semua item wajib didapat."
    while True:
        screen.fill(BG)
        text(screen, headline, BIG, BONUS_COLOR if won else (255, 100, 100), (WIDTH//2, HEIGHT//2-100))
        text(screen, subtitle, FONT, WHITE, (WIDTH//2, HEIGHT//2-48))
        text(screen, f"SKOR AKHIR: {game['score']}", TITLE, ITEM_COLOR, (WIDTH//2, HEIGHT//2+5))
        text(screen, f"Item wajib: {sum(game['collected'])}/2    |    Bonus: {'didapat' if game['bonus_taken'] else 'belum didapat'}", FONT, MUTED, (WIDTH//2, HEIGHT//2+60))
        centered_lines(["ENTER = main lagi", "ESC = menu utama"], HEIGHT//2+125, FONT, WHITE, 36)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        clock.tick(FPS)

def play_game():
    game = new_game()
    keymap = {
        pygame.K_w: (0,-1), pygame.K_UP: (0,-1),
        pygame.K_s: (0,1), pygame.K_DOWN: (0,1),
        pygame.K_a: (-1,0), pygame.K_LEFT: (-1,0),
        pygame.K_d: (1,0), pygame.K_RIGHT: (1,0),
    }
    while game["status"] == "playing":
        remaining = draw_game(game)
        if remaining <= 0:
            game["status"] = "lose"
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key in keymap:
                    dx, dy = keymap[event.key]
                    old_player = game["player"]
                    nx, ny = old_player[0]+dx, old_player[1]+dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS:
                        old_guards = game["guards"][:]
                        game["player"] = (nx, ny)
                        game["player_steps"] += 1
                        game["message"] = ""
                        collect_items(game)
                        if caught(game["player"], old_player, game["guards"], old_guards):
                            game["player"] = (3,10)
                            game["message"] = "TERTANGKAP! Kembali ke titik A"
                        if game["status"] == "playing" and game["player_steps"] >= 2:
                            move_guards(game)
                            game["player_steps"] = 0
                            collect_items(game)
        clock.tick(FPS)
    if game["status"] == "playing":
        game["status"] = "lose"
    return result_screen(game)

def main():
    while True:
        choice = menu_screen()
        if choice == "start":
            instruction_screen()
            while True:
                result = play_game()
                if result == "menu":
                    break
                if result == "restart":
                    continue
                break

if __name__ == "__main__":
    main()
