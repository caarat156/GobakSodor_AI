========================================================================
PANDUAN MENJALANKAN SOURCE CODE - MINI PROJECT ARTIFICIAL INTELLIGENCE
Permainan Tradisional Gobak Sodor AI (Minimax + Alpha-Beta Pruning)
========================================================================

1. LIBRARY YANG DIGUNAKAN
------------------------------------------------------------------------
- Python (versi 3.10 / 3.11 / 3.12 / 3.13)
- Pygame (versi 2.5.2 atau 2.6.1)
- Library bawaan Python (Standard Library):
  * time
  * random
  * sys
  * functools (lru_cache)


2. IDE YANG DIGUNAKAN
------------------------------------------------------------------------
- Visual Studio Code (VS Code) versi 1.90+ (atau versi terbaru)
  * Extension: Python (by Microsoft)


3. LANGKAH-LANGKAH MENJALANKAN SOURCE CODE
------------------------------------------------------------------------
Langkah 1: Buka Folder Project
- Buka Visual Studio Code / terminal, lalu buka folder root project ini.

Langkah 2: (Opsional / Disarankan) Buat dan Aktifkan Virtual Environment
- Windows:
    python -m venv .venv
    .venv\Scripts\activate
- macOS / Linux:
    python3 -m venv .venv
    source .venv/bin/activate

Langkah 3: Install Library Dependensi
- Jalankan perintah berikut di terminal:
    pip install -r requirements.txt
  (atau langsung jalankan: pip install pygame)

Langkah 4: Jalankan Program Game
- Jalankan perintah:
    python main.py
  (atau python3 main.py pada macOS/Linux)

Langkah 5: Kontrol Permainan
- W / A / S / D atau Tombol Panah : Bergerak (Atas, Kiri, Bawah, Kanan)
- Spasi (SPACE)                   : Diam / Tunggu 1 giliran
- ESC                             : Kembali ke menu / Keluar
========================================================================

