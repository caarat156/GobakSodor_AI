"""
Gobak Sodor AI — Minimax + Alpha-Beta Pruning
Antarmuka Pengguna (UI) Lapangan & Karakter Pygame
"""
import sys
import pygame
from game import GobakSodorGame, COLS, ROWS

pygame.init()

# ---------------------------------------------------------------------------
# Konfigurasi Dimensi Tampilan (Frame yang diperbesar)
# ---------------------------------------------------------------------------
CELL = 60                           # Ukuran setiap sel (diperbesar agar lega)
MARGIN_X = 40                       # Margin kiri dan kanan
WIDTH = MARGIN_X * 2 + COLS * CELL  # 40*2 + 7*60 = 500 px
HUD_H = 110                         # Tinggi area HUD atas
BOARD_H = ROWS * CELL               # 11 * 60 = 660 px
FOOTER_H = 60                       # Tinggi info status bawah
HEIGHT = HUD_H + BOARD_H + FOOTER_H # 110 + 660 + 60 = 830 px
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gobak Sodor AI — Minimax + Alpha-Beta Pruning")
clock = pygame.time.Clock()


# ---------------------------------------------------------------------------
# Palet Warna UI
# ---------------------------------------------------------------------------
BG = (22, 28, 38)
GRID = (70, 83, 100)
WHITE = (240, 244, 248)
MUTED = (185, 195, 207)
SAFE_COLOR = (32, 54, 58)           # Sel aman: hijau gelap/slate
GUARD_LINE_COLOR = (52, 43, 48)     # Garis jaga: merah bata gelap
START_COLOR = (34, 83, 62)          # Titik A / Start: hijau emerald
END_COLOR = (65, 57, 94)            # Titik B / Finish: ungu royal
PLAYER_COLOR = (65, 190, 255)       # Pemain: biru terang
GUARD_COLORS = [
    (245, 95, 95),                  # G1: koral merah
    (255, 174, 66),                 # G2: kuning jingga
    (181, 118, 255),                # G3: ungu pastel
]
ITEM_COLOR = (255, 220, 70)         # Item wajib: emas cerah
BONUS_COLOR = (82, 230, 154)        # Item bonus: hijau mint
BADGE_BG = (57, 76, 95)


# ---------------------------------------------------------------------------
# Manajemen Font
# ---------------------------------------------------------------------------
def get_font(name, size, bold=False):
    """Fallback aman jika folder font sistem macOS dibatasi izin aksesnya."""
    try:
        return pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        return f


FONT = get_font("arial", 20)
HUD_FONT = get_font("arial", 18, bold=True)
SMALL = get_font("arial", 15)
TINY = get_font("arial", 13, bold=True)
TITLE = get_font("arial", 42, bold=True)
BIG = get_font("arial", 54, bold=True)


def draw_text(surface, msg, font, color, center):
    img = font.render(str(msg), True, color)
    surface.blit(img, img.get_rect(center=center))


def cell_center(pos):
    """Konversi koordinat (r, c) ke koordinat pixel layar (cx, cy)."""
    r, c = pos
    cx = MARGIN_X + c * CELL + CELL // 2
    cy = HUD_H + r * CELL + CELL // 2
    return cx, cy


def draw_character(surface, pos, color, label, is_player=False):
    """
    Menggambar bentuk visual karakter pemain & agen AI penjaga.
    Desain karakter sprite memiliki kepala, mata, badan, dan label identitas.
    """
    cx, cy = cell_center(pos)

    # Kepala & Badan
    pygame.draw.circle(surface, color, (cx, cy - 7), 13)
    pygame.draw.ellipse(surface, color, (cx - 16, cy + 4, 32, 24))

    # Mata
    pygame.draw.circle(surface, WHITE, (cx - 4, cy - 8), 2)
    pygame.draw.circle(surface, WHITE, (cx + 4, cy - 8), 2)

    if is_player:
        # Label "KAMU" di bawah badan pemain
        draw_text(surface, label, TINY, WHITE, (cx, cy + 35))
    else:
        # Label "G1", "G2", "G3" di dalam badan penjaga
        draw_text(surface, label, TINY, (25, 25, 30), (cx, cy + 16))


def draw_game(game):
    screen.fill(BG)
    remaining = max(0, int(game.time_left()))

    # --- HUD ATAS ---
    draw_text(screen, f"SKOR: {game.score}", HUD_FONT, WHITE, (MARGIN_X + 60, 24))
    draw_text(screen, f"WAKTU: {remaining // 60:02d}:{remaining % 60:02d}", HUD_FONT, WHITE, (WIDTH - MARGIN_X - 60, 24))

    # Indikator item wajib
    item_status = " ".join("[V]" if v else "[ ]" for v in game.collected)
    draw_text(screen, f"ITEM WAJIB: {item_status}", HUD_FONT, ITEM_COLOR, (WIDTH // 2, 50))

    # Petunjuk dinamis
    if all(game.collected):
        draw_text(screen, ">> KEMBALI KE A UNTUK MENANG! <<", FONT, BONUS_COLOR, (WIDTH // 2, 76))
    else:
        draw_text(screen, "Ambil 2 item wajib, lalu kembali ke A", SMALL, BONUS_COLOR, (WIDTH // 2, 76))

    draw_text(screen, "WASD/Panah: gerak  |  SPACE: diam  |  ESC: menu", SMALL, MUTED, (WIDTH // 2, 97))

    # --- AREA LAPANGAN ---
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(MARGIN_X + c * CELL, HUD_H + r * CELL, CELL, CELL)
            if r == ROWS - 1:
                fill = START_COLOR
            elif r == 0:
                fill = END_COLOR
            elif r in game.guard_rows:
                fill = GUARD_LINE_COLOR
            else:
                fill = SAFE_COLOR
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, GRID, rect, 1)

    # Label Titik B dan Titik A pada lapangan
    draw_text(screen, "B / FINISH", SMALL, WHITE, (WIDTH // 2, HUD_H + 16))
    if all(game.collected):
        draw_text(screen, "A / KEMBALI KE SINI!", SMALL, ITEM_COLOR, (WIDTH // 2, HUD_H + (ROWS - 1) * CELL + CELL - 16))
    else:
        draw_text(screen, "A / START", SMALL, WHITE, (WIDTH // 2, HUD_H + (ROWS - 1) * CELL + CELL - 16))

    # Label penanda garis jaga 1, 2, 3 di sisi kiri
    for idx, g_row in enumerate(game.guard_rows):
        y_pos = HUD_H + g_row * CELL + 10
        draw_text(screen, f"Garis {idx + 1}", TINY, MUTED, (MARGIN_X + 28, y_pos))

    # --- BENTUK ITEM WAJIB ---
    for i, item_pos in enumerate(game.mandatory_items):
        if not game.collected[i]:
            cx, cy = cell_center(item_pos)
            pygame.draw.circle(screen, ITEM_COLOR, (cx, cy), 16)
            draw_text(screen, str(i + 1), TINY, (30, 30, 30), (cx, cy))

    # --- BENTUK ITEM BONUS ---
    if not game.bonus_collected:
        cx, cy = cell_center(game.bonus_item)
        pygame.draw.polygon(screen, BONUS_COLOR, [
            (cx, cy - 18), (cx + 18, cy), (cx, cy + 18), (cx - 18, cy)
        ])
        draw_text(screen, "+3", TINY, (15, 30, 25), (cx, cy))

    # --- BENTUK AGEN PENJAGA (AI) ---
    for i, guard_pos in enumerate(game.guards):
        draw_character(screen, guard_pos, GUARD_COLORS[i], f"G{i + 1}")

    # --- BENTUK PEMAIN ---
    draw_character(screen, game.player, PLAYER_COLOR, "KAMU", is_player=True)

    # --- FOOTER STATUS & METRIK AI ---
    footer_y = HUD_H + BOARD_H + 20
    draw_text(screen, game.status, SMALL, WHITE, (WIDTH // 2, footer_y))
    ai_info = f"Node AI: {game.total_nodes}   |   Waktu keputusan: {game.last_ai_ms:.2f} ms"
    draw_text(screen, ai_info, TINY, MUTED, (WIDTH // 2, footer_y + 24))

    pygame.display.flip()