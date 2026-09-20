from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "images"

WIDTH = 1100
HEIGHT = 620
FPS = 60
GROUND_Y = 560

WORLD_SPEED = 320
ENEMY_SPEED = 520
SPAWN_INTERVAL = 1.5
PLAYER_X = 180
DAMAGE_COOLDOWN = 0.9
MAX_LIVES = 3

GRAVITY = 2200
JUMP_SPEED = 900

# Multiplicadores aplicados à velocidade base (via menu)
SPEED_MIN = 0.5
SPEED_MAX = 2.5
SPEED_STEP = 0.25

# Total de inimigas que podem aparecer na partida
ENEMY_COUNT_MIN = 2
ENEMY_COUNT_MAX = 50


# =============================================================
# ANIMAÇÕES DA NORA — escala individual por ação
# =============================================================
# Cada entrada: filename, scale
# Ajuste o "scale" de cada linha pra calibrar o tamanho daquele
# GIF específico. 1.0 = tamanho original, 0.30 = 30% do original.

NORA_ACTIONS = {
    "idle":   ("muse-dash-buro_ tela principal.gif",              0.30),
    "run":    ("muse-dash-buro_anda_normal.gif",                  0.30),
    "jump":   ("muse-dash-buro_primeira_imagem_do_pulo.gif",      0.30),
    "bump":   ("muse-dash-buro_primeira_imagem_do_esbarrao.gif",  0.30),
    "defeat": ("muse-dash-marija_morte.gif",                      0.30),
}


# =============================================================
# ANIMAÇÕES DA INIMIGA — escala individual por ação
# =============================================================

ENEMY_ACTIONS = {
    "run":  ("inimiga_caminha.gif",                  0.16),
    "bump": ("inimiga_esbarra_na_principal.gif",     0.16),
}


BACKGROUND = "cenario004.jpg"