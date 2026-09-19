"""
Sprite sheet em PERFIL da personagem.
Corpo inclinado, pernas em passada, cabelo em movimento.
Corrige o problema da cabeça flutuante (pescoço visível).
"""
import pygame

pygame.init()

SPRITE_W, SPRITE_H = 96, 128
NUM_FRAMES = 8
FOLHA = pygame.Surface((SPRITE_W * NUM_FRAMES, SPRITE_H), pygame.SRCALPHA)

# --- Paleta ---
CABELO = (30, 28, 35, 255)
CABELO_LUZ = (70, 65, 80, 255)
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
    Personagem de perfil.
    CX = centro do sprite.
    A personagem está sempre voltada pra DIREITA.
    """
    CX = SPRITE_W // 2

    # Parâmetros por pose
    # inclinacao: deslocamento do tronco (negativo = inclina pra frente)
    # passada: qual perna está à frente (-1, 0, 1)
    # balanco_braco: qual braço está à frente (-1, 0, 1)
    # altura: offset vertical geral
    # cabelo_extra: comprimento extra do cabelo pra trás
    configs = {
        "idle_1":    {"inclinacao": 0,  "passada": 0,  "braco": 0,  "altura": 0,  "cabelo": 0},
        "idle_2":    {"inclinacao": 0,  "passada": 0,  "braco": 0,  "altura": -1, "cabelo": 0},
        "passo_1":   {"inclinacao": -2, "passada": -1, "braco": 1,  "altura": 0,  "cabelo": 3},
        "passo_2":   {"inclinacao": -2, "passada": 1,  "braco": -1, "altura": 0,  "cabelo": 3},
        "levitar_1": {"inclinacao": -1, "passada": -1, "braco": 1,  "altura": -2, "cabelo": 4},
        "levitar_2": {"inclinacao": -1, "passada": 1,  "braco": -1, "altura": -1, "cabelo": 4},
        "levantar": {"inclinacao": 0,  "passada": 0,  "braco": 0,  "altura": -3, "cabelo": 6},
        "cair":     {"inclinacao": -3, "passada": -1, "braco": 1,  "altura": 1,  "cabelo": 5},
    }
    cfg = configs[pose]
    inc = cfg["inclinacao"]
    passada = cfg["passada"]
    braco_frente = cfg["braco"]
    alt = cfg["altura"]
    cabelo_extra = cfg["cabelo"]

    # --- Coordenadas verticais (baseadas em perfil) ---
    TOPO_CABECA = 12 + alt
    BASE_CABECA = 34 + alt
    PESCOCO_Y = 34 + alt
    PESCOCO_BASE = 40 + alt
    OMBRO_Y = 40 + alt
    PEITO_Y = 54 + alt
    CINTURA_Y = 68 + alt
    QUADRIL_Y = 78 + alt
    COXA_Y = 90 + alt
    JOELHO_Y = 102 + alt
    PE_Y = 122 + alt

    # offset horizontal do tronco (inclinação)
    ox = inc

    # ============================================================
    # PERNAS (em perfil, alternadas)
    # ============================================================
    # perna de trás (mais escura)
    if passada == -1:
        # perna esquerda atrás
        perna_tras_x = CX - 6 + ox
        perna_frente_x = CX + 2 + ox
    elif passada == 1:
        # perna direita atrás
        perna_tras_x = CX - 6 + ox
        perna_frente_x = CX + 2 + ox
    else:
        perna_tras_x = CX - 5 + ox
        perna_frente_x = CX + 2 + ox

    # perna de trás
    for y in range(QUADRIL_Y, PE_Y):
        t = (y - QUADRIL_Y) / (PE_Y - QUADRIL_Y)
        if t < 0.5:
            larg = 4
        else:
            larg = 4 + int((t - 0.5) * 2)
        # meia arrastão em cima, bota embaixo
        if y < COXA_Y + 4:
            cor_perna = PELE
        elif y < JOELHO_Y:
            cor_perna = MEIA
        else:
            cor_perna = BOTA
        linha_h(y, perna_tras_x - larg, perna_tras_x, cor_perna, frame)

    # pé de trás
    linha_h(PE_Y - 1, perna_tras_x - 6, perna_tras_x + 1, BOTA, frame)
    linha_h(PE_Y, perna_tras_x - 6, perna_tras_x + 1, CONTORNO, frame)

    # perna da frente (mais clara)
    for y in range(QUADRIL_Y, PE_Y):
        t = (y - QUADRIL_Y) / (PE_Y - QUADRIL_Y)
        if t < 0.5:
            larg = 5
        else:
            larg = 5 + int((t - 0.5) * 2)
        if y < COXA_Y + 4:
            cor_perna = PELE
        elif y < JOELHO_Y:
            cor_perna = MEIA
            if (y % 3) == 0:
                px(perna_frente_x - larg + 1, y, MEIA_LUZ, frame)
        else:
            cor_perna = BOTA
        linha_h(y, perna_frente_x, perna_frente_x + larg, cor_perna, frame)
        # contorno
        if y >= JOELHO_Y:
            px(perna_frente_x + larg, y, CONTORNO, frame)

    # pé da frente
    linha_h(PE_Y - 1, perna_frente_x, perna_frente_x + 6, BOTA, frame)
    linha_h(PE_Y, perna_frente_x, perna_frente_x + 6, CONTORNO, frame)

    # ============================================================
    # QUADRIL
    # ============================================================
    for y in range(CINTURA_Y, QUADRIL_Y + 2):
        t = (y - CINTURA_Y) / (QUADRIL_Y + 2 - CINTURA_Y)
        meia_esq = 4 + int(t * 2)
        meia_dir = 5 + int(t * 2)
        linha_h(y, CX - meia_esq + ox, CX + meia_dir + ox, VESTIDO, frame)

    # ============================================================
    # VESTIDO (perfil: mais estreito do que frontal)
    # ============================================================
    for y in range(OMBRO_Y + 2, CINTURA_Y):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y - OMBRO_Y - 2)
        meia = 6 + int(t * 2)
        linha_h(y, CX - meia + ox, CX + meia + ox, VESTIDO, frame)
        px(CX - meia + ox, y, CONTORNO, frame)
        px(CX + meia + ox, y, CONTORNO, frame)
        # luz no peito
        if y > OMBRO_Y + 4 and y < CINTURA_Y - 4:
            px(CX + 2 + ox, y, VESTIDO_LUZ, frame)

    # detalhes vermelhos verticais (na lateral do vestido)
    for y in range(OMBRO_Y + 8, CINTURA_Y - 4):
        if (y % 4) == 0:
            px(CX + 3 + ox, y, VERMELHO, frame)

    # ============================================================
    # PESCOÇO (agora visível, conecta cabeça ao corpo)
    # ============================================================
    # retângulo de pele entre o queixo e os ombros
    for y in range(PESCOCO_Y, PESCOCO_BASE + 1):
        linha_h(y, CX - 2 + ox, CX + 2 + ox, PELE, frame)
        # sombra do lado esquerdo
        px(CX - 2 + ox, y, PELE_SOMBRA, frame)
    # sombra embaixo do queixo (dá volume)
    linha_h(PESCOCO_Y, CX - 3 + ox, CX + 3 + ox, PELE_SOMBRA, frame)

    # gola
    for y in range(PESCOCO_BASE - 1, PESCOCO_BASE + 2):
        linha_h(y, CX - 3 + ox, CX + 3 + ox, GOLA, frame)

    # ============================================================
    # CABEÇA (perfil, virada pra direita)
    # ============================================================
    # perfil: crânio com testa, nariz e queixo do lado direito
    for y in range(TOPO_CABECA, BASE_CABECA):
        t = (y - TOPO_CABECA) / (BASE_CABECA - TOPO_CABECA)
        if t < 0.3:
            # topo do crânio
            meia_esq = 5 + int(t * 2 * 5)
            meia_dir = 6 + int(t * 2 * 5)
        elif t < 0.7:
            # meio do rosto
            meia_esq = 7
            meia_dir = 8
        else:
            # queixo: estreita
            meia_esq = 7 - int((t - 0.7) * 3 * 2)
            meia_dir = 8 - int((t - 0.7) * 3 * 3)
        linha_h(y, CX - meia_esq + ox, CX + meia_dir + ox, PELE, frame)
        # contorno
        px(CX - meia_esq - 1 + ox, y, CONTORNO, frame)
        px(CX + meia_dir + 1 + ox, y, CONTORNO, frame)
        # sombra na parte de trás da cabeça
        px(CX - meia_esq + ox, y, PELE_SOMBRA, frame)
        # nariz (pequeno, na direita)
        if t > 0.4 and t < 0.55:
            px(CX + meia_dir + 2 + ox, y, PELE, frame)
            px(CX + meia_dir + 2 + ox, y, PELE_SOMBRA, frame)

    # ============================================================
    # ROSTO (perfil)
    # ============================================================
    olho_y = TOPO_CABECA + 11
    # olho (um só, porque é perfil)
    rect(CX + 2 + ox, olho_y - 1, CX + 5 + ox, olho_y + 1, OLHO_BRANCO, frame)
    rect(CX + 3 + ox, olho_y, CX + 4 + ox, olho_y, OLHO_AZUL, frame)
    px(CX + 4 + ox, olho_y, OLHO_PUPILA, frame)
    px(CX + 3 + ox, olho_y - 1, OLHO_BRANCO, frame)
    # cílios
    linha_h(olho_y - 2, CX + 2 + ox, CX + 5 + ox, CICLO, frame)
    # sobrancelha
    linha_h(olho_y - 4, CX + 2 + ox, CX + 5 + ox, CABELO, frame)
    # boca
    px(CX + 6 + ox, olho_y + 5, (180, 80, 90, 255), frame)
    px(CX + 7 + ox, olho_y + 5, (180, 80, 90, 255), frame)

    # ============================================================
    # CABELO (em perfil, com movimento pra trás)
    # ============================================================
    # topo do cabelo
    for y in range(TOPO_CABECA - 4, TOPO_CABECA + 6):
        t = (y - TOPO_CABECA + 4) / 10
        if t < 0.5:
            meia = 4 + int(t * 2 * 8)
        else:
            meia = 12
        linha_h(y, CX - meia + ox, CX + meia + ox, CABELO, frame)

    # franja cobre parte da testa
    for y in range(TOPO_CABECA + 2, TOPO_CABECA + 8):
        t = (y - TOPO_CABECA - 2) / 6
        meia = 11 - int(t * 3)
        for x in range(CX - meia + ox, CX + meia + ox):
            if (x + y) % 3 != 0:
                px(x, y, CABELO, frame)

    # cabelo comprido caindo pra trás (do lado esquerdo, perfil)
    for y in range(TOPO_CABECA + 4, OMBRO_Y + 8 + cabelo_extra):
        t = (y - TOPO_CABECA - 4) / (OMBRO_Y + 8 + cabelo_extra - TOPO_CABECA - 4)
        # cresce pra trás conforme desce
        x_tras = CX - 8 - int(t * 8) + ox
        px(x_tras, y, CABELO, frame)
        px(x_tras - 1, y, CABELO, frame)
        px(x_tras - 2, y, CABELO, frame)
        # luz no cabelo
        if (y % 5) == 0:
            px(x_tras + 1, y, CABELO_LUZ, frame)

    # coque no topo
    for y in range(TOPO_CABECA - 8, TOPO_CABECA - 1):
        t = (y - (TOPO_CABECA - 8)) / 7
        if t < 0.5:
            meia = 3 + int(t * 2 * 5)
        else:
            meia = 8 - int((t - 0.5) * 2 * 5)
        if meia < 1:
            continue
        linha_h(y, CX - meia + ox, CX + meia + ox, CABELO, frame)

    # detalhe vermelho no coque
    for dx in range(-2, 3):
        px(CX + dx + ox, TOPO_CABECA - 6, VERMELHO if dx != 0 else VERMELHO_ESCURO, frame)

    # luz no topo do cabelo
    for dx in [-3, -2, -1]:
        px(CX + dx + ox, TOPO_CABECA - 2, CABELO_LUZ, frame)

    # ============================================================
    # BRAÇOS (perfil, um à frente, um atrás)
    # ============================================================
    # braço de trás
    x_braco_tras = CX - 8 + ox
    for y in range(OMBRO_Y + 2, CINTURA_Y + 4):
        px(x_braco_tras, y, VESTIDO, frame)
        px(x_braco_tras - 1, y, CONTORNO, frame)
    # mão de trás
    rect(x_braco_tras - 1, CINTURA_Y + 4, x_braco_tras + 1, CINTURA_Y + 7, PELE, frame)

    # braço da frente (balança)
    x_braco_frente = CX + 7 + ox + (2 if braco_frente == 1 else -2 if braco_frente == -1 else 0)
    for y in range(OMBRO_Y + 2, CINTURA_Y + 4):
        px(x_braco_frente, y, VESTIDO, frame)
        px(x_braco_frente + 1, y, VESTIDO, frame)
        px(x_braco_frente + 2, y, CONTORNO, frame)
    # mão da frente
    rect(x_braco_frente + 1, CINTURA_Y + 4, x_braco_frente + 3, CINTURA_Y + 7, PELE, frame)


poses = ["idle_1", "idle_2", "passo_1", "passo_2",
         "levitar_1", "levitar_2", "levantar", "cair"]
for i, pose in enumerate(poses):
    desenhar_personagem(i, pose)

pygame.image.save(FOLHA, "personagem.png")
print(f"Sprite sheet salvo: personagem.png ({SPRITE_W * NUM_FRAMES}x{SPRITE_H}, {NUM_FRAMES} frames)")
pygame.quit()