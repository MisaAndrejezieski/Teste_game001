"""
Gera a personagem baseada na referência:
- Cabelo preto com coque no topo
- Olho azul
- Vestido preto justo com detalhes vermelhos
- Luvas longas pretas
- Meia-calça arrastão
- Botas longas pretas
Resolução: 96x128
"""
import pygame

pygame.init()

W, H = 96, 128
SUP = pygame.Surface((W, H), pygame.SRCALPHA)

# ============================================================
# PALETA (extraída da referência)
# ============================================================
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


def px(x, y, cor):
    if 0 <= x < W and 0 <= y < H:
        SUP.set_at((x, y), cor)


def rect(x0, y0, x1, y1, cor):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor)


def linha_h(y, x0, x1, cor):
    for x in range(x0, x1 + 1):
        px(x, y, cor)


# ============================================================
# GEOMETRIA (baseada nas proporções da referência)
# ============================================================
CX = W // 2  # 48

# Pontos verticais (topo -> base)
COQUE_TOPO = 8
CABECA_TOPO = 16
CABECA_BASE = 38
PESCOCO_Y = 42
OMBRO_Y = 46
PEITO_Y = 58
CINTURA_Y = 72
QUADRIL_Y = 82
COXA_Y = 95
JOELHO_Y = 105
PE_Y = 124


def desenhar_pernas():
    """Pernas com meia arrastão e botas longas."""
    # Coxas (pele visível entre saia e meia)
    for y in range(QUADRIL_Y + 6, COXA_Y + 4):
        t = (y - QUADRIL_Y - 6) / (COXA_Y + 4 - QUADRIL_Y - 6)
        # perna esquerda
        larg_esq = 5 - int(t * 1)
        linha_h(y, CX - 4 - larg_esq, CX - 4, PELE)
        px(CX - 4 - larg_esq, y, PELE_SOMBRA)
        # perna direita
        larg_dir = 5 - int(t * 1)
        linha_h(y, CX + 4, CX + 4 + larg_dir, PELE)
        px(CX + 4 + larg_dir, y, PELE_SOMBRA)

    # Meia-calça arrastão (do meio da coxa até o joelho)
    for y in range(COXA_Y + 4, JOELHO_Y):
        t = (y - COXA_Y - 4) / (JOELHO_Y - COXA_Y - 4)
        larg = 4 - int(t * 1)
        # esquerda
        linha_h(y, CX - 4 - larg, CX - 4, MEIA)
        # padrão arrastão: risquinhos
        if (y % 3) == 0:
            px(CX - 4 - larg + 1, y, MEIA_LUZ)
            px(CX - 4 - 1, y, MEIA_LUZ)
        # direita
        linha_h(y, CX + 4, CX + 4 + larg, MEIA)
        if (y % 3) == 0:
            px(CX + 4 + 1, y, MEIA_LUZ)
            px(CX + 4 + larg - 1, y, MEIA_LUZ)

    # Botas longas (do joelho até o pé)
    for y in range(JOELHO_Y, PE_Y):
        t = (y - JOELHO_Y) / (PE_Y - JOELHO_Y)
        larg = 4 + int(t * 1)
        # esquerda
        linha_h(y, CX - 4 - larg, CX - 4 + 1, BOTA)
        px(CX - 4 - larg, y, CONTORNO)
        if (y % 4) == 0:
            px(CX - 4 - larg + 2, y, BOTA_LUZ)
        # direita
        linha_h(y, CX + 4 - 1, CX + 4 + larg, BOTA)
        px(CX + 4 + larg, y, CONTORNO)
        if (y % 4) == 0:
            px(CX + 4 + larg - 2, y, BOTA_LUZ)

    # Pés (bico da bota)
    linha_h(PE_Y - 1, CX - 8, CX - 2, BOTA)
    linha_h(PE_Y - 1, CX + 2, CX + 8, BOTA)
    linha_h(PE_Y, CX - 8, CX - 2, CONTORNO)
    linha_h(PE_Y, CX + 2, CX + 8, CONTORNO)


def desenhar_corpo():
    """Tronco, quadril, vestido."""
    # Quadril (embaixo do vestido)
    for y in range(CINTURA_Y, QUADRIL_Y + 6):
        t = (y - CINTURA_Y) / (QUADRIL_Y + 6 - CINTURA_Y)
        meia = 10 + int(t * 3)
        linha_h(y, CX - meia, CX + meia, PELE)
        px(CX - meia, y, PELE_SOMBRA)
        px(CX + meia, y, PELE_SOMBRA)

    # Vestido (do ombro até o quadril)
    for y in range(OMBRO_Y + 4, QUADRIL_Y):
        t = (y - OMBRO_Y - 4) / (QUADRIL_Y - OMBRO_Y - 4)
        if t < 0.4:
            # parte de cima: mais estreita (busto)
            meia = 9 + int(t * 2)
        elif t < 0.6:
            # cintura: mais fina
            meia = 8
        else:
            # quadril: mais larga
            meia = 8 + int((t - 0.6) * 4 * 8)
        linha_h(y, CX - meia, CX + meia, VESTIDO)
        px(CX - meia, y, CONTORNO)
        px(CX + meia, y, CONTORNO)

    # Luz central do vestido
    for y in range(OMBRO_Y + 6, CINTURA_Y):
        px(CX - 1, y, VESTIDO_LUZ)

    # Detalhes vermelhos (os "botões" centrais)
    for y in [60, 64, 68]:
        px(CX - 1, y, VERMELHO)
        px(CX, y, VERMELHO_ESCURO)
        px(CX + 1, y, VERMELHO)

    # Decote: pele visível na parte de cima
    for y in range(OMBRO_Y + 4, PEITO_Y):
        t = (y - OMBRO_Y - 4) / (PEITO_Y - OMBRO_Y - 4)
        meia = 3 + int(t * 3)
        linha_h(y, CX - meia, CX + meia, PELE)
        px(CX - meia, y, PELE_SOMBRA)
        px(CX + meia, y, PELE_SOMBRA)

    # Gola/coleira azul-escura
    for y in range(PESCOCO_Y, PESCOCO_Y + 3):
        linha_h(y, CX - 3, CX + 3, (40, 60, 100, 255))


def desenhar_bracos():
    """Braços com luvas longas pretas."""
    # Braço esquerdo (caído, mão na cintura)
    for y in range(OMBRO_Y + 2, CINTURA_Y + 2):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y - OMBRO_Y)
        x = CX - 11 - int(t * 2)
        px(x, y, VESTIDO)
        px(x + 1, y, VESTIDO)
        px(x - 1, y, VESTIDO)
        px(x - 1, y, CONTORNO)

    # Mão esquerda (na cintura)
    rect(CX - 13, CINTURA_Y - 2, CX - 11, CINTURA_Y + 1, PELE)
    px(CX - 14, CINTURA_Y, CONTORNO)

    # Braço direito (caído, com luva)
    for y in range(OMBRO_Y + 2, CINTURA_Y + 4):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y + 4 - OMBRO_Y - 2)
        x = CX + 11 + int(t * 2)
        px(x, y, VESTIDO)
        px(x - 1, y, VESTIDO)
        px(x + 1, y, VESTIDO)
        px(x + 1, y, CONTORNO)

    # Mão direita (na lateral)
    rect(CX + 11, CINTURA_Y + 2, CX + 13, CINTURA_Y + 5, PELE)
    px(CX + 14, CINTURA_Y + 3, CONTORNO)


def desenhar_cabeca():
    """Cabeça com contorno, queixo, orelhas."""
    # Contorno + preenchimento
    for y in range(CABECA_TOPO, CABECA_BASE):
        t = (y - CABECA_TOPO) / (CABECA_BASE - CABECA_TOPO)
        if t < 0.5:
            meia = 3 + int(t * 2 * 9)
        else:
            meia = 12 - int((t - 0.5) * 2 * 7)
        # contorno
        px(CX - meia - 1, y, CONTORNO)
        px(CX + meia + 1, y, CONTORNO)
        # pele
        linha_h(y, CX - meia, CX + meia, PELE)
        # sombra nas laterais
        px(CX - meia, y, PELE_SOMBRA)
        px(CX + meia, y, PELE_SOMBRA)
        # luz na testa
        if y < CABECA_TOPO + 6:
            px(CX - 1, y, PELE_LUZ)
            px(CX, y, PELE_LUZ)

    # Pescoço
    rect(CX - 3, CABECA_BASE, CX + 3, PESCOCO_Y + 2, PELE)
    px(CX - 3, CABECA_BASE, PELE_SOMBRA)
    px(CX + 3, CABECA_BASE, PELE_SOMBRA)


def desenhar_rosto():
    """Olhos azuis, sobrancelhas, boca."""
    olho_y = CABECA_TOPO + 12

    # Olho esquerdo
    rect(CX - 8, olho_y - 1, CX - 4, olho_y + 2, OLHO_BRANCO)
    rect(CX - 7, olho_y, CX - 5, olho_y + 1, OLHO_AZUL)
    px(CX - 6, olho_y + 1, OLHO_PUPILA)
    px(CX - 7, olho_y, OLHO_BRANCO)
    # cílios
    linha_h(olho_y - 2, CX - 8, CX - 4, CICLO)

    # Olho direito
    rect(CX + 4, olho_y - 1, CX + 8, olho_y + 2, OLHO_BRANCO)
    rect(CX + 5, olho_y, CX + 7, olho_y + 1, OLHO_AZUL)
    px(CX + 6, olho_y + 1, OLHO_PUPILA)
    px(CX + 7, olho_y, OLHO_BRANCO)
    linha_h(olho_y - 2, CX + 4, CX + 8, CICLO)

    # Sobrancelhas
    linha_h(olho_y - 4, CX - 8, CX - 4, CABELO_PRETO)
    linha_h(olho_y - 4, CX + 4, CX + 8, CABELO_PRETO)

    # Boca pequena
    px(CX - 1, olho_y + 7, (180, 80, 90, 255))
    px(CX, olho_y + 7, (180, 80, 90, 255))
    px(CX + 1, olho_y + 7, (180, 80, 90, 255))


def desenhar_cabelo():
    """Cabelo preto com franja e coque no topo."""
    # Topo da cabeça (cabelo)
    for y in range(CABECA_TOPO - 4, CABECA_TOPO + 8):
        t = (y - CABECA_TOPO + 4) / 12
        if t < 0.4:
            meia = 4 + int(t * 2.5 * 9)
        else:
            meia = 13
        linha_h(y, CX - meia, CX + meia, CABELO_PRETO)

    # Franja (cobre parte da testa)
    for y in range(CABECA_TOPO + 4, CABECA_TOPO + 10):
        t = (y - CABECA_TOPO - 4) / 6
        meia = 12 - int(t * 2)
        # desenha a franja com "bicos"
        for x in range(CX - meia, CX + meia + 1):
            if (x + y) % 3 != 0:  # deixa alguns pixels de fora pra dar textura
                px(x, y, CABELO_PRETO)

    # Mechas laterais (caindo ao lado do rosto)
    for y in range(CABECA_TOPO + 6, OMBRO_Y + 4):
        t = (y - CABECA_TOPO - 6) / (OMBRO_Y + 4 - CABECA_TOPO - 6)
        x_esq = CX - 13 - int(t * 2)
        px(x_esq, y, CABELO_PRETO)
        px(x_esq + 1, y, CABELO_PRETO)
        px(x_esq, y, CABELO_SOMBRA)
        x_dir = CX + 13 + int(t * 2)
        px(x_dir, y, CABELO_PRETO)
        px(x_dir - 1, y, CABELO_PRETO)
        px(x_dir, y, CABELO_SOMBRA)

    # Coque no topo (estilo "coque samurai" da referência)
    for y in range(COQUE_TOPO - 2, COQUE_TOPO + 10):
        t = (y - COQUE_TOPO + 2) / 12
        if t < 0.5:
            meia = 4 + int(t * 2 * 5)
        else:
            meia = 9 - int((t - 0.5) * 2 * 5)
        if meia < 1:
            continue
        linha_h(y, CX - meia, CX + meia, CABELO_PRETO)
        px(CX - meia, y, CABELO_SOMBRA)
        px(CX + meia, y, CABELO_SOMBRA)

    # Detalhe vermelho no coque
    px(CX - 2, COQUE_TOPO + 2, VERMELHO)
    px(CX - 1, COQUE_TOPO + 2, VERMELHO)
    px(CX, COQUE_TOPO + 2, VERMELHO_ESCURO)
    px(CX + 1, COQUE_TOPO + 2, VERMELHO)
    px(CX + 2, COQUE_TOPO + 2, VERMELHO)

    # Luz no cabelo
    px(CX - 3, CABECA_TOPO - 2, CABELO_LUZ)
    px(CX - 2, CABECA_TOPO - 2, CABELO_LUZ)
    px(CX - 1, CABECA_TOPO - 2, CABELO_LUZ)


# ============================================================
# EXECUTA O DESENHO (ordem importa)
# ============================================================
desenhar_pernas()      # pernas primeiro (ficam atrás)
desenhar_corpo()       # tronco e quadril
desenhar_bracos()      # braços
desenhar_cabeca()      # cabeça
desenhar_rosto()       # olhos, boca
desenhar_cabelo()      # cabelo por cima

# Salva
pygame.image.save(SUP, "personagem.png")
print(f"Personagem gerada: personagem.png ({W}x{H})")
pygame.quit()