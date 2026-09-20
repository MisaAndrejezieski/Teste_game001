from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "images"
WIDTH = 1100
HEIGHT = 620
GROUND_Y = 500
FPS = 60
WORLD_SPEED = 320
SPAWN_INTERVAL = 1.5
PLAYER_X = 180
DAMAGE_COOLDOWN = 0.9
MAX_LIVES = 3

NORA_ACTIONS = {
    "idle": "muse-dash-buro_ tela principal.gif",
    "run": "muse-dash-buro_anda_normal.gif",
    "jump": "muse-dash-buro_primeira_imagem_do_pulo.gif",
    "bump": "muse-dash-buro_primeira_imagem_do_esbarrao.gif",
    "defeat": "muse-dash-marija_morte.gif",
}

ENEMY_ACTIONS = {
    "run": "inim004.gif",
    "bump": "inimiga_esbarra_na_principal.gif",
}

SCENERY = [
    ("cenario001.jpg", 0.18),
    ("cenario002.jpg", 0.42),
    ("cenario003.png", 0.75),
]

# --- Escala por personagem ---
# 1.0 = tamanho original do GIF
# < 1.0 = menor, > 1.0 = maior
# Calibre olhando o resultado na tela
NORA_SCALE = 0.15
ENEMY_SCALE = 0.12

# --- Física do pulo ---
GRAVITY = 2200      # px/s² (quanto maior, mais rápido cai)
JUMP_SPEED = 900    # px/s (velocidade inicial do pulo)