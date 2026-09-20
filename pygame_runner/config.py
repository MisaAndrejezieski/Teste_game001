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

NORA_SCALE = 0.30
ENEMY_SCALE = 0.16

# Multiplicadores aplicados à velocidade base (via menu)
SPEED_MIN = 0.5
SPEED_MAX = 2.5
SPEED_STEP = 0.25

# Total de inimigas que podem aparecer na partida
ENEMY_COUNT_MIN = 2
ENEMY_COUNT_MAX = 50

NORA_ACTIONS = {
    "idle":   "muse-dash-buro_ tela principal.gif",
    "run":    "muse-dash-buro_anda_normal.gif",
    "jump":   "muse-dash-buro_primeira_imagem_do_pulo.gif",
    "bump":   "muse-dash-buro_primeira_imagem_do_esbarrao.gif",
    "defeat": "muse-dash-marija_morte.gif",
}

ENEMY_ACTIONS = {
    "run":  "inimiga_caminha.gif",
    "bump": "inimiga_esbarra_na_principal.gif",
}

BACKGROUND = "cenario004.jpg"