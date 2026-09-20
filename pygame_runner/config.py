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

WORLD_SPEED = 320           # px/s — velocidade base do mundo
SPAWN_INTERVAL = 1.5        # segundos entre spawns de inimigos
PLAYER_X = 180              # posição X fixa da Nora
DAMAGE_COOLDOWN = 0.9       # segundos de invulnerabilidade após tomar dano
MAX_LIVES = 3

GRAVITY = 2200              # px/s² — quanto maior, mais rápido cai
JUMP_SPEED = 900            # px/s — velocidade inicial do pulo


# =============================================================
# ESCALA DOS PERSONAGENS
# =============================================================
# 1.0 = tamanho original do GIF
# < 1.0 = menor, > 1.0 = maior

NORA_SCALE = 0.15
ENEMY_SCALE = 0.12


# =============================================================
# ANIMAÇÕES DA NORA (player)
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
    "run":  "inim004.gif",
    "bump": "inimiga_esbarra_na_principal.gif",
}


# =============================================================
# CENÁRIO (paralaxe com 3 camadas do cenário 004)
# =============================================================
# Lista de (arquivo, velocidade_relativa)
# Ordem: do mais distante (lento) para o mais próximo (rápido)
#
# A velocidade efetiva de cada camada é:
#   WORLD_SPEED * velocidade_relativa

SCENERY = [
    ("cenario004.jpg", 0.15),   # camada distante (mais lenta)
    ("cenario004.jpg", 0.45),   # camada intermediária
    ("cenario004.jpg", 0.85),   # camada próxima (mais rápida)
]