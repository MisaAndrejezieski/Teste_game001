from pathlib import Path

# =============================================================
# CAMINHOS
# =============================================================

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "images"


# =============================================================
# TELA
# =============================================================

WIDTH = 1100
HEIGHT = 620
FPS = 60
GROUND_Y = 500


# =============================================================
# MUNDO / FÍSICA
# =============================================================

WORLD_SPEED = 320
SPAWN_INTERVAL = 1.5
PLAYER_X = 180
DAMAGE_COOLDOWN = 0.9
MAX_LIVES = 3

GRAVITY = 2200
JUMP_SPEED = 900


# =============================================================
# ESCALA DOS PERSONAGENS
# =============================================================

NORA_SCALE = 0.15
ENEMY_SCALE = 0.12


# =============================================================
# ANIMAÇÕES DA NORA
# =============================================================

NORA_ACTIONS = {
    "idle":   "muse-dash-buro_ tela principal.gif",
    "run":    "muse-dash-buro_anda_normal.gif",
    "jump":   "muse-dash-buro_primeira_imagem_do_pulo.gif",
    "bump":   "muse-dash-buro_primeira_imagem_do_esbarrao.gif",
    "defeat": "muse-dash-marija_morte.gif",
}


# =============================================================
# ANIMAÇÕES DA INIMIGA
# =============================================================

ENEMY_ACTIONS = {
    "run":  "inimiga_caminha.gif",
    "bump": "inimiga_esbarra_na_principal.gif",
}


# =============================================================
# CENÁRIO
# =============================================================
# Cenário único rolando horizontalmente, em loop infinito.

BACKGROUND = "cenario004.jpg"