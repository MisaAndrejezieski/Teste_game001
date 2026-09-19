"""
Gera sprite sheet de 8 frames da personagem.
Baseado na referência: cabelo preto com coque, olho azul, vestido preto,
luvas longas, meia arrastão, botas longas.

Cada frame é uma variação do mesmo desenho base, mudando:
- posição dos braços
- altura dos ombros
- inclinação da cabeça
- altura do corpo (esticado/comprimido)
"""
import pygame

pygame.init()

SPRITE_W, SPRITE_H = 96, 128
NUM_FRAMES = 8
FOLHA = pygame.Surface((SPRITE_W * NUM_FRAMES, SPRITE_H), pygame.SRCALPHA)

# --- Paleta ---
CABELO_PRETO = (30, 28, 35, 255)
CABELO_LUZ = (70, 65, 80, 255)
CABELO_SOMBRA = (15, 13, 20, 255)
PELE = (245, 205, 180, 255)
PELE_SOMBRA = (210, 165, 140, 255)
PELE_LUZ = (255, 225, 205, 255)
OLHO_AZUL = (90, 150, 220, 255)
OLHO_BRANCO = (250, 250, 250, 255)
OLHO_PUPILA = (30, 30, 50, 255)
CICLO = (20, 15, 25, 255)
VESTIDO = (25, 22, 30, 255)
VESTIDO_LUZ = (55, 50, 65, 255)
VERMELHO = (180, 35, 45, 255)
VERMELHO_ESCURO = (110, 20, 30, 255)
MEIA = (35, 30, 40, 255)
MEIA_LUZ = (60, 55, 70, 255)
BOTA = (20, 18, 25, 255)
BOTA_LUZ = (45, 40, 55, 255)
CONTORNO = (10, 8, 15, 255)
GOLA = (40, 60, 100, 255)


def px(x, y, cor, frame):
    if 0 <= x < SPRITE_W and 0 <= y < SPRITE_H:
        FOLHA.set_at((frame * SPRITE_W + x, y), cor)


def rect(x0, y0, x1, y1, cor, frame):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor, frame)


def linha_h(y, x0, x1, cor, frame):
    for x in range(x0, x1 + 1):
        px(x, y, cor, frame)


def desenhar_personagem(frame, pose):
    """
    Desenha a personagem em uma pose específica.
    Cada pose muda posições de ombros, braços, cabeça e corpo.
    """
    CX = SPRITE_W // 2

    # --- Parâmetros por pose ---
    # altura_offset: quanto o corpo todo sobe/desce
    # ombro_delta: quanto os ombros sobem/descem
    # cabeca_delta: inclinação da cabeça (deslocamento x)
    # braco_esq_x / braco_dir_x: deslocamento horizontal dos braços
    # perna_delta: qual perna está à frente
    configs = {
        "idle_1":  {"altura": 0,  "ombro": 0, "cabeca": 0, "be": -1, "bd": 1, "perna": 0},
        "idle_2":  {"altura": 0,  "ombro": 1, "cabeca": 0, "be": -1, "bd": 1, "perna": 0},
        "passo_1": {"altura": 0,  "ombro": 0, "cabeca": 1, "be": 2,  "bd": -1, "perna": -1},
        "passo_2": {"altura": 0,  "ombro": 0, "cabeca": -1, "be": -2, "bd": 1, "perna": 1},
        "levitar_1": {"altura": -2, "ombro": -1, "cabeca": 0, "be": 1, "bd": -1, "perna": 0},
        "levitar_2": {"altura": -1, "ombro": -2, "cabeca": 0, "be": -1, "bd": 1, "perna": 0},
        "levantar": {"altura": -3, "ombro": -1, "cabeca": 0, "be": 0, "bd": 0, "perna": 0},
        "cair":     {"altura": 1,  "ombro": 2, "cabeca": 0, "be": 0, "bd": 0, "perna": 0},
    }
    cfg = configs[pose]
    alt = cfg["altura"]
    ombro_d = cfg["ombro"]
    cab_d = cfg["cabeca"]
    be = cfg["be"]
    bd = cfg["bd"]
    perna_d = cfg["perna"]

    # ============================================================
    # GEOMETRIA (com offset por pose)
    # ============================================================
    COQUE_TOPO = 8 + alt
    CABECA_TOPO = 16 + alt
    CABECA_BASE = 38 + alt
    PESCOCO_Y = 42 + alt
    OMBRO_Y = 46 + alt + ombro_d
    PEITO_Y = 58 + alt + ombro_d
    CINTURA_Y = 72 + alt
    QUADRIL_Y = 82 + alt
    COXA_Y = 95 + alt
    JOELHO_Y = 105 + alt
    PE_Y = 124 + alt

    # --- Pernas ---
    # coxas (pele)
    for y in range(QUADRIL_Y + 6, COXA_Y + 4):
        t = (y - QUADRIL_Y - 6) / (COXA_Y + 4 - QUADRIL_Y - 6)
        larg = 5 - int(t * 1)
        if perna_d == -1:
            # perna esquerda à frente (mais visível)
            linha_h(y, CX - 4 - larg, CX - 4, PELE, frame)
            linha_h(y, CX + 4, CX + 4 + larg - 1, PELE, frame)
        elif perna_d == 1:
            # perna direita à frente
            linha_h(y, CX - 4 - larg + 1, CX - 4, PELE, frame)
            linha_h(y, CX + 4, CX + 4 + larg, PELE, frame)
        else:
            linha_h(y, CX - 4 - larg, CX - 4, PELE, frame)
            linha_h(y, CX + 4, CX + 4 + larg, PELE, frame)

    # meia arrastão
    for y in range(COXA_Y + 4, JOELHO_Y):
        t = (y - COXA_Y - 4) / (JOELHO_Y - COXA_Y - 4)
        larg = 4 - int(t * 1)
        linha_h(y, CX - 4 - larg, CX - 4, MEIA, frame)
        if (y % 3) == 0:
            px(CX - 4 - larg + 1, y, MEIA_LUZ, frame)
        linha_h(y, CX + 4, CX + 4 + larg, MEIA, frame)
        if (y % 3) == 0:
            px(CX + 4 + larg - 1, y, MEIA_LUZ, frame)

    # botas
    for y in range(JOELHO_Y, PE_Y):
        t = (y - JOELHO_Y) / (PE_Y - JOELHO_Y)
        larg = 4 + int(t * 1)
        linha_h(y, CX - 4 - larg, CX - 3, BOTA, frame)
        px(CX - 4 - larg, y, CONTORNO, frame)
        linha_h(y, CX + 3, CX + 4 + larg, BOTA, frame)
        px(CX + 4 + larg, y, CONTORNO, frame)

    linha_h(PE_Y - 1, CX - 8, CX - 2, BOTA, frame)
    linha_h(PE_Y - 1, CX + 2, CX + 8, BOTA, frame)
    linha_h(PE_Y, CX - 8, CX - 2, CONTORNO, frame)
    linha_h(PE_Y, CX + 2, CX + 8, CONTORNO, frame)

    # --- Quadril ---
    for y in range(CINTURA_Y, QUADRIL_Y + 6):
        t = (y - CINTURA_Y) / (QUADRIL_Y + 6 - CINTURA_Y)
        meia = 10 + int(t * 3)
        linha_h(y, CX - meia, CX + meia, PELE, frame)
        px(CX - meia, y, PELE_SOMBRA, frame)
        px(CX + meia, y, PELE_SOMBRA, frame)

    # --- Vestido ---
    for y in range(OMBRO_Y + 4, QUADRIL_Y):
        t = (y - OMBRO_Y - 4) / (QUADRIL_Y - OMBRO_Y - 4)
        if t < 0.4:
            meia = 9 + int(t * 2)
        elif t < 0.6:
            meia = 8
        else:
            meia = 8 + int((t - 0.6) * 4 * 8)
        linha_h(y, CX - meia, CX + meia, VESTIDO, frame)
        px(CX - meia, y, CONTORNO, frame)
        px(CX + meia, y, CONTORNO, frame)

    for y in range(OMBRO_Y + 6, CINTURA_Y):
        px(CX - 1, y, VESTIDO_LUZ, frame)

    # detalhes vermelhos
    for y in [60 + alt + ombro_d, 64 + alt + ombro_d, 68 + alt + ombro_d]:
        px(CX - 1, y, VERMELHO, frame)
        px(CX, y, VERMELHO_ESCURO, frame)
        px(CX + 1, y, VERMELHO, frame)

    # decote
    for y in range(OMBRO_Y + 4, PEITO_Y):
        t = (y - OMBRO_Y - 4) / (PEITO_Y - OMBRO_Y - 4)
        meia = 3 + int(t * 3)
        linha_h(y, CX - meia, CX + meia, PELE, frame)
        px(CX - meia, y, PELE_SOMBRA, frame)
        px(CX + meia, y, PELE_SOMBRA, frame)

    # gola
    for y in range(PESCOCO_Y, PESCOCO_Y + 3):
        linha_h(y, CX - 3, CX + 3, GOLA, frame)

    # --- Braços ---
    for y in range(OMBRO_Y + 2, CINTURA_Y + 2):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y - OMBRO_Y)
        # braço esquerdo
        x_e = CX - 11 - int(t * 2) + be
        px(x_e, y, VESTIDO, frame)
        px(x_e + 1, y, VESTIDO, frame)
        px(x_e - 1, y, CONTORNO, frame)
        # braço direito
        x_d = CX + 11 + int(t * 2) + bd
        px(x_d, y, VESTIDO, frame)
        px(x_d - 1, y, VESTIDO, frame)
        px(x_d + 1, y, CONTORNO, frame)

    # mãos
    rect(CX - 13 + be, CINTURA_Y - 2, CX - 11 + be, CINTURA_Y + 1, PELE, frame)
    rect(CX + 11 + bd, CINTURA_Y + 2, CX + 13 + bd, CINTURA_Y + 5, PELE, frame)

    # --- Cabeça ---
    for y in range(CABECA_TOPO, CABECA_BASE):
        t = (y - CABECA_TOPO) / (CABECA_BASE - CABECA_TOPO)
        if t < 0.5:
            meia = 3 + int(t * 2 * 9)
        else:
            meia = 12 - int((t - 0.5) * 2 * 7)
        c = cab_d  # deslocamento horizontal da cabeça
        px(CX - meia - 1 + c, y, CONTORNO, frame)
        px(CX + meia + 1 + c, y, CONTORNO, frame)
        linha_h(y, CX - meia + c, CX + meia + c, PELE, frame)
        px(CX - meia + c, y, PELE_SOMBRA, frame)
        px(CX + meia + c, y, PELE_SOMBRA, frame)
        if y < CABECA_TOPO + 6:
            px(CX - 1 + c, y, PELE_LUZ, frame)

    # pescoço
    rect(CX - 3, CABECA_BASE, CX + 3, PESCOCO_Y + 2, PELE, frame)

    # --- Rosto ---
    olho_y = CABECA_TOPO + 12
    c = cab_d
    # olho esquerdo
    rect(CX - 8 + c, olho_y - 1, CX - 4 + c, olho_y + 2, OLHO_BRANCO, frame)
    rect(CX - 7 + c, olho_y, CX - 5 + c, olho_y + 1, OLHO_AZUL, frame)
    px(CX - 6 + c, olho_y + 1, OLHO_PUPILA, frame)
    px(CX - 7 + c, olho_y, OLHO_BRANCO, frame)
    linha_h(olho_y - 2, CX - 8 + c, CX - 4 + c, CICLO, frame)
    # olho direito
    rect(CX + 4 + c, olho_y - 1, CX + 8 + c, olho_y + 2, OLHO_BRANCO, frame)
    rect(CX + 5 + c, olho_y, CX + 7 + c, olho_y + 1, OLHO_AZUL, frame)
    px(CX + 6 + c, olho_y + 1, OLHO_PUPILA, frame)
    px(CX + 7 + c, olho_y, OLHO_BRANCO, frame)
    linha_h(olho_y - 2, CX + 4 + c, CX + 8 + c, CICLO, frame)
    # sobrancelhas
    linha_h(olho_y - 4, CX - 8 + c, CX - 4 + c, CABELO_PRETO, frame)
    linha_h(olho_y - 4, CX + 4 + c, CX + 8 + c, CABELO_PRETO, frame)
    # boca
    px(CX - 1 + c, olho_y + 7, (180, 80, 90, 255), frame)
    px(CX + c, olho_y + 7, (180, 80, 90, 255), frame)
    px(CX + 1 + c, olho_y + 7, (180, 80, 90, 255), frame)

    # --- Cabelo ---
    for y in range(CABECA_TOPO - 4, CABECA_TOPO + 8):
        t = (y - CABECA_TOPO + 4) / 12
        if t < 0.4:
            meia = 4 + int(t * 2.5 * 9)
        else:
            meia = 13
        linha_h(y, CX - meia + c, CX + meia + c, CABELO_PRETO, frame)

    for y in range(CABECA_TOPO + 4, CABECA_TOPO + 10):
        t = (y - CABECA_TOPO - 4) / 6
        meia = 12 - int(t * 2)
        for x in range(CX - meia + c, CX + meia + c + 1):
            if (x + y) % 3 != 0:
                px(x, y, CABELO_PRETO, frame)

    # mechas laterais
    for y in range(CABECA_TOPO + 6, OMBRO_Y + 4):
        t = (y - CABECA_TOPO - 6) / (OMBRO_Y + 4 - CABECA_TOPO - 6)
        x_e = CX - 13 - int(t * 2) + c
        px(x_e, y, CABELO_PRETO, frame)
        px(x_e + 1, y, CABELO_PRETO, frame)
        x_d = CX + 13 + int(t * 2) + c
        px(x_d, y, CABELO_PRETO, frame)
        px(x_d - 1, y, CABELO_PRETO, frame)

    # coque
    for y in range(COQUE_TOPO - 2, COQUE_TOPO + 10):
        t = (y - COQUE_TOPO + 2) / 12
        if t < 0.5:
            meia = 4 + int(t * 2 * 5)
        else:
            meia = 9 - int((t - 0.5) * 2 * 5)
        if meia < 1:
            continue
        linha_h(y, CX - meia + c, CX + meia + c, CABELO_PRETO, frame)

    # detalhe vermelho no coque
    for dx in range(-2, 3):
        px(CX + dx + c, COQUE_TOPO + 2, VERMELHO if dx != 0 else VERMELHO_ESCURO, frame)

    # luz no cabelo
    for dx in [-3, -2, -1]:
        px(CX + dx + c, CABECA_TOPO - 2, CABELO_LUZ, frame)


# --- Gera os 8 frames ---
poses = ["idle_1", "idle_2", "passo_1", "passo_2",
         "levitar_1", "levitar_2", "levantar", "cair"]
for i, pose in enumerate(poses):
    desenhar_personagem(i, pose)

pygame.image.save(FOLHA, "personagem.png")
print(f"Sprite sheet salvo: personagem.png ({SPRITE_W * NUM_FRAMES}x{SPRITE_H}, {NUM_FRAMES} frames)")
pygame.quit()