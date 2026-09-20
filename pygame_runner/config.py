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
    "run":  "inim004.gif",
    "bump": "inimiga_esbarra_na_principal.gif",
}


# =============================================================
# CENÁRIO — PARALAXE REAL A PARTIR DE UMA ÚNICA IMAGEM
# =============================================================
# O cenario004.jpg é CORTADO em 3 faixas horizontais.
# Cada faixa vira uma "camada" independente, rolando em
# velocidade própria. Isso cria paralaxe de verdade com
# uma imagem só.
#
# Estrutura de cada tupla:
#   (arquivo, y_inicio_%, y_fim_%, velocidade_relativa)
#
# y_inicio_% e y_fim_% são em FRAÇÃO da altura da imagem (0.0 a 1.0)
# Ex:
#   (0.00, 0.40) → do topo até 40% da altura
#   (0.40, 0.75) → de 40% até 75% da altura
#   (0.75, 1.00) → de 75% até o fim

SCENERY = [
    # Céu + montanhas distantes — rola devagar (parece longe)
    ("cenario004.jpg", 0.00, 0.40, 0.15),

    # Árvores, casas, torii — rola em velocidade média
    ("cenario004.jpg", 0.40, 0.75, 0.45),

    # Chão, grama, pedras — rola rápido (parece perto)
    ("cenario004.jpg", 0.75, 1.00, 1.00),
]