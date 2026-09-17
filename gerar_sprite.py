"""
Gera sprite sheet da personagem com vestido esvoaçante.
8 frames x 48x64 px = 384x64 px.
"""
import pygame

pygame.init()

SPRITE_W, SPRITE_H = 48, 64
NUM_FRAMES = 8
FOLHA = pygame.Surface((SPRITE_W * NUM_FRAMES, SPRITE_H), pygame.SRCALPHA)

# --- Paleta ---
CABELO = (28, 22, 38, 255)
CABELO_LUZ = (60, 48, 78, 255)
PELE = (240, 205, 180, 255)
PELE_SOMBRA = (200, 165, 145, 255)
VESTIDO = (205, 45, 55, 255)
VESTIDO_ESCURO = (120, 20, 35, 255)
VESTIDO_LUZ = (245, 85, 90, 255)
VESTIDO_SOMBRA = (80, 12, 22, 255)
DOURADO = (235, 195, 100, 255)
DOURADO_ESCURO = (170, 130, 60, 255)
OLHO = (255, 230, 140, 255)
PE = (45, 35, 40, 255)


def px(x, y, cor, frame):
    if 0 <= x < SPRITE_W and 0 <= y < SPRITE_H:
        FOLHA.set_at((frame * SPRITE_W + x, y), cor)


def rect(x0, y0, x1, y1, cor, frame):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor, frame)


def desenhar_saia(frame, cx, cintura_y, pe_y, abertura, balanco_x, curvatura,
                   largura_base=6):
    """
    Desenha a saia como uma série de linhas horizontais.
    - abertura: quão aberta a saia está (largura extra no fundo)
    - balanco_x: deslocamento horizontal (esvoaçar lateral)
    - curvatura: quanto a saia curva pra um lado (positivo = direita)
    """
    altura_saia = pe_y - 2 - cintura_y
    pontos_borda = []

    for i, y in enumerate(range(cintura_y, pe_y - 2)):
        t = i / max(1, altura_saia)

        meia_largura = largura_base + abertura * t
        desloc = balanco_x * t + curvatura * (t * t)
        cx_linha = cx + desloc

        # Camada de trás (silhueta escura, um pouco mais larga)
        rect(int(cx_linha - meia_largura - 1), y,
             int(cx_linha + meia_largura + 1), y,
             VESTIDO_ESCURO, frame)

        pontos_borda.append((cx_linha, y, meia_largura))

    # Camada da frente (vermelho vivo)
    for (cx_linha, y, meia_largura) in pontos_borda:
        m = meia_largura * 0.85
        rect(int(cx_linha - m), y, int(cx_linha + m), y, VESTIDO, frame)

    # Sombra interna (lado direito)
    for (cx_linha, y, meia_largura) in pontos_borda:
        m = meia_largura * 0.85
        px(int(cx_linha + m - 1), y, VESTIDO_SOMBRA, frame)
        px(int(cx_linha + m - 2), y, VESTIDO_SOMBRA, frame)

    # Luz interna (lado esquerdo)
    for (cx_linha, y, meia_largura) in pontos_borda:
        m = meia_largura * 0.85
        px(int(cx_linha - m + 1), y, VESTIDO_LUZ, frame)

    # Borda dourada no fundo da saia
    for (cx_linha, y, meia_largura) in pontos_borda[-3:]:
        m = meia_largura
        for xx in range(int(cx_linha - m), int(cx_linha + m) + 1):
            px(xx, y, DOURADO, frame)
        px(int(cx_linha - m), y, DOURADO_ESCURO, frame)
        px(int(cx_linha + m), y, DOURADO_ESCURO, frame)


def desenhar_personagem(frame, pose):
    cx = SPRITE_W // 2
    cabeca_cy = 16
    ombro_y = 26
    cintura_y = 38
    pe_y = 62

    configs = {
        "idle":         {"abertura": 8,  "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": 0},
        "passo_esq":    {"abertura": 10, "balanco_x": -2, "curvatura": -1, "balanco_corpo": -1, "altura_pe": -1},
        "passo_dir":    {"abertura": 10, "balanco_x": 2,  "curvatura": 1,  "balanco_corpo": 1,  "altura_pe": -1},
        "levitar_sub":  {"abertura": 16, "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": -3},
        "levitar_apex": {"abertura": 22, "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": -4},
        "levitar_desc": {"abertura": 14, "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": -3},
        "pousar_imp":   {"abertura": 20, "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": 1},
        "pousar_vol":   {"abertura": 11, "balanco_x": 0,  "curvatura": 0,  "balanco_corpo": 0,  "altura_pe": 0},
    }
    cfg = configs[pose]
    abertura = cfg["abertura"]
    balanco_x = cfg["balanco_x"]
    curvatura = cfg["curvatura"]
    bal = cfg["balanco_corpo"]
    alt_pe = cfg["altura_pe"]

    # --- Pés ---
    rect(cx - 4 + bal, pe_y + alt_pe - 2, cx - 2 + bal, pe_y + alt_pe, PE, frame)
    rect(cx + 1 + bal, pe_y + alt_pe - 2, cx + 3 + bal, pe_y + alt_pe, PE, frame)

    # --- Saia ---
    desenhar_saia(frame, cx + bal, cintura_y, pe_y + alt_pe,
                  abertura, balanco_x, curvatura, largura_base=6)

    # --- Tronco ---
    for y in range(ombro_y, cintura_y):
        rect(cx - 5 + bal, y, cx + 5 + bal, y, VESTIDO, frame)
    for y in range(ombro_y + 1, cintura_y):
        px(cx - 4 + bal, y, VESTIDO_LUZ, frame)
        px(cx + 4 + bal, y, VESTIDO_SOMBRA, frame)

    # --- Cinto dourado ---
    rect(cx - 6 + bal, cintura_y - 1, cx + 6 + bal, cintura_y, DOURADO, frame)

    # --- Pescoço ---
    rect(cx - 1 + bal, ombro_y - 4, cx + 1 + bal, ombro_y, PELE, frame)

    # --- Cabeça ---
    rect(cx - 4 + bal, cabeca_cy - 5, cx + 4 + bal, cabeca_cy + 5, PELE, frame)
    px(cx - 5 + bal, cabeca_cy - 3, PELE, frame)
    px(cx - 5 + bal, cabeca_cy - 2, PELE, frame)
    px(cx - 5 + bal, cabeca_cy - 1, PELE, frame)
    px(cx + 5 + bal, cabeca_cy - 3, PELE, frame)
    px(cx + 5 + bal, cabeca_cy - 2, PELE, frame)
    px(cx + 5 + bal, cabeca_cy - 1, PELE, frame)

    # --- Cabelo (topo) ---
    rect(cx - 5 + bal, cabeca_cy - 7, cx + 5 + bal, cabeca_cy - 4, CABELO, frame)
    rect(cx - 6 + bal, cabeca_cy - 5, cx - 6 + bal, cabeca_cy + 2, CABELO, frame)
    rect(cx + 6 + bal, cabeca_cy - 5, cx + 6 + bal, cabeca_cy + 2, CABELO, frame)
    rect(cx - 4 + bal, cabeca_cy - 6, cx + 2 + bal, cabeca_cy - 5, CABELO, frame)
    px(cx - 2 + bal, cabeca_cy - 6, CABELO_LUZ, frame)
    px(cx - 1 + bal, cabeca_cy - 6, CABELO_LUZ, frame)

    # --- Cabelo comprido ---
    if pose.startswith("levitar"):
        cabelo_extra = 6
    elif pose.startswith("pousar"):
        cabelo_extra = 8
    else:
        cabelo_extra = 6

    rect(cx - 6 + bal, cabeca_cy + 2, cx - 4 + bal, cabeca_cy + cabelo_extra, CABELO, frame)
    rect(cx + 4 + bal, cabeca_cy + 2, cx + 6 + bal, cabeca_cy + cabelo_extra, CABELO, frame)

    # --- Olho ---
    px(cx + 2 + bal, cabeca_cy, OLHO, frame)
    px(cx + 3 + bal, cabeca_cy, OLHO, frame)

    # --- Braços ---
    for y in range(ombro_y + 1, cintura_y - 2):
        px(cx - 6 + bal, y, VESTIDO_ESCURO, frame)
        px(cx - 7 + bal, y, VESTIDO_ESCURO, frame)
        px(cx + 6 + bal, y, VESTIDO, frame)
        px(cx + 7 + bal, y, VESTIDO, frame)
    px(cx + 7 + bal, cintura_y - 2, DOURADO, frame)
    px(cx + 8 + bal, cintura_y - 2, DOURADO, frame)


poses = [
    "idle", "passo_esq", "passo_dir",
    "levitar_sub", "levitar_apex", "levitar_desc",
    "pousar_imp", "pousar_vol",
]
for i, pose in enumerate(poses):
    desenhar_personagem(i, pose)

pygame.image.save(FOLHA, "personagem.png")
print(f"Sprite salvo: personagem.png ({SPRITE_W * NUM_FRAMES}x{SPRITE_H}, {NUM_FRAMES} frames)")
pygame.quit()