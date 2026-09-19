"""
Gera uma personagem em pixel art, resolução 96x128.
Estilo: feminina, cabelo comprido, vestido vermelho com borda dourada.
Baseado nas referências enviadas.
"""
import pygame

pygame.init()

W, H = 96, 128
SUPERFICIE = pygame.Surface((W, H), pygame.SRCALPHA)

# ============================================================
# PALETA (mapeada das referências)
# ============================================================
# Cabelo ruivo com 3 tons
CABELO_ESCURO   = (90, 30, 20, 255)
CABELO_MEDIO    = (150, 60, 35, 255)
CABELO_CLARO    = (200, 100, 60, 255)
CABELO_LUZ      = (240, 160, 110, 255)

# Pele com 4 tons (base, sombra, luz, blush)
PELE_ESCURA     = (170, 120, 100, 255)
PELE_BASE       = (225, 175, 150, 255)
PELE_CLARA      = (245, 205, 180, 255)
PELE_BLUSH      = (240, 150, 140, 255)

# Olhos
OLHO_BRANCO     = (250, 250, 250, 255)
OLHO_IRIS       = (100, 60, 150, 255)  # roxo (inspirado na ref)
OLHO_PUPILA     = (30, 15, 40, 255)
OLHO_BRILHO     = (255, 255, 255, 255)
SOBRANCELHA     = (80, 35, 25, 255)
BOCA            = (180, 70, 70, 255)

# Roupa
TOP_BRANCO      = (240, 240, 245, 255)
TOP_SOMBRA      = (200, 200, 215, 255)
CORPETE_ESCURO  = (35, 25, 45, 255)
CORPETE_MEDIO   = (60, 45, 80, 255)
CORPETE_LUZ     = (95, 75, 120, 255)
SAIA_ESCURA     = (25, 20, 35, 255)
SAIA_MEDIA      = (50, 40, 65, 255)
FAIXA_AZUL      = (130, 100, 200, 255)
FAIXA_AZUL_LUZ  = (170, 140, 230, 255)
LUVA_ESCURA     = (40, 30, 55, 255)
LUVA_MEDIA      = (70, 55, 95, 255)

# Detalhes
DOURADO         = (240, 200, 100, 255)
DOURADO_ESCURO  = (170, 130, 60, 255)
BOTA_ESCURA     = (60, 20, 35, 255)
BOTA_MEDIA      = (110, 40, 55, 255)
CONTORNO        = (25, 15, 25, 255)


def px(x, y, cor):
    if 0 <= x < W and 0 <= y < H:
        SUPERFICIE.set_at((x, y), cor)


def rect(x0, y0, x1, y1, cor):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor)


def linha_h(y, x0, x1, cor):
    for x in range(x0, x1 + 1):
        px(x, y, cor)


def linha_v(x, y0, y1, cor):
    for y in range(y0, y1 + 1):
        px(x, y, cor)


# ============================================================
# GEOMETRIA BASE
# ============================================================
CX = W // 2  # centro horizontal = 48

# Pontos de referência vertical (topo para baixo)
TOPO_CABECA = 18
BASE_CABECA = 42
OMBRO_Y = 46
PEITO_Y = 60
CINTURA_Y = 76
QUADRIL_Y = 86
JOELHO_Y = 105
PE_Y = 122

# Larguras
LARGURA_CABECA = 13   # metade da largura
LARGURA_OMBRO = 15
LARGURA_CINTURA = 10
LARGURA_QUADRIL = 14


# ============================================================
# DESENHO
# ============================================================

def desenhar_cabelo_tras():
    """Cabelo comprido caindo pelas costas, atrás do corpo."""
    # Forma geral: "cortina" que sai do topo da cabeça e cai até a cintura
    for y in range(TOPO_CABECA - 2, CINTURA_Y + 5):
        if y < BASE_CABECA:
            # atrás da cabeça: largura cresce
            meia = LARGURA_CABECA + 4 + (y - TOPO_CABECA) // 3
        elif y < OMBRO_Y:
            meia = LARGURA_CABECA + 6
        elif y < CINTURA_Y:
            # cai pelas costas, afunilando
            t = (y - OMBRO_Y) / (CINTURA_Y - OMBRO_Y)
            meia = LARGURA_OMBRO + 2 - int(t * 3)
        else:
            t = (y - CINTURA_Y) / 5
            meia = (LARGURA_OMBRO - 1) - int(t * 4)
        # contorno escuro
        px(CX - meia - 1, y, CABELO_ESCURO)
        px(CX + meia + 1, y, CABELO_ESCURO)
        # preenchimento médio
        linha_h(y, CX - meia, CX + meia, CABELO_MEDIO)
        # sombra nas bordas
        px(CX - meia, y, CABELO_ESCURO)
        px(CX + meia, y, CABELO_ESCURO)


def desenhar_corpo_base():
    """Silhueta base do corpo (pele), antes das roupas."""
    # Pescoço
    rect(CX - 3, BASE_CABECA - 2, CX + 3, OMBRO_Y, PELE_BASE)
    px(CX - 3, BASE_CABECA - 2, PELE_ESCURA)

    # Ombros e braços
    for y in range(OMBRO_Y, CINTURA_Y):
        t = (y - OMBRO_Y) / (CINTURA_Y - OMBRO_Y)
        meia = int(LARGURA_OMBRO * (1 - t * 0.4))
        linha_h(y, CX - meia, CX + meia, PELE_BASE)

    # Cintura/quadril
    for y in range(CINTURA_Y, QUADRIL_Y):
        t = (y - CINTURA_Y) / (QUADRIL_Y - CINTURA_Y)
        meia = int(LARGURA_CINTURA + (LARGURA_QUADRIL - LARGURA_CINTURA) * t)
        linha_h(y, CX - meia, CX + meia, PELE_BASE)

    # Pernas
    for y in range(QUADRIL_Y, PE_Y):
        t = (y - QUADRIL_Y) / (PE_Y - QUADRIL_Y)
        # perna esquerda
        meia_perna = 5 - int(t * 1)
        # gap entre as pernas aumenta
        gap = 2 + int(t * 4)
        # perna esquerda
        linha_h(y, CX - gap - meia_perna, CX - gap, PELE_BASE)
        # perna direita
        linha_h(y, CX + gap, CX + gap + meia_perna, PELE_BASE)
        # sombra nas laterais
        px(CX - gap - meia_perna, y, PELE_ESCURA)
        px(CX + gap + meia_perna, y, PELE_ESCURA)


def desenhar_rosto():
    """Rosto: olhos, sobrancelhas, boca, blush."""
    olho_y = TOPO_CABECA + 14
    # Olho esquerdo (do ponto de vista do observador)
    rect(CX - 8, olho_y - 2, CX - 3, olho_y + 2, OLHO_BRANCO)
    rect(CX - 7, olho_y - 1, CX - 4, olho_y + 1, OLHO_IRIS)
    px(CX - 6, olho_y, OLHO_PUPILA)
    px(CX - 5, olho_y, OLHO_PUPILA)
    px(CX - 7, olho_y - 1, OLHO_BRILHO)
    # sobrancelha esquerda
    linha_h(olho_y - 4, CX - 8, CX - 3, SOBRANCELHA)
    # cílios
    px(CX - 8, olho_y + 2, CONTORNO)
    px(CX - 3, olho_y + 2, CONTORNO)

    # Olho direito
    rect(CX + 3, olho_y - 2, CX + 8, olho_y + 2, OLHO_BRANCO)
    rect(CX + 4, olho_y - 1, CX + 7, olho_y + 1, OLHO_IRIS)
    px(CX + 5, olho_y, OLHO_PUPILA)
    px(CX + 6, olho_y, OLHO_PUPILA)
    px(CX + 7, olho_y - 1, OLHO_BRILHO)
    # sobrancelha direita
    linha_h(olho_y - 4, CX + 3, CX + 8, SOBRANCELHA)
    px(CX + 3, olho_y + 2, CONTORNO)
    px(CX + 8, olho_y + 2, CONTORNO)

    # Blush nas bochechas
    px(CX - 10, olho_y + 4, PELE_BLUSH)
    px(CX - 9, olho_y + 4, PELE_BLUSH)
    px(CX + 9, olho_y + 4, PELE_BLUSH)
    px(CX + 10, olho_y + 4, PELE_BLUSH)

    # Boca pequena
    px(CX - 1, olho_y + 8, BOCA)
    px(CX, olho_y + 8, BOCA)
    px(CX + 1, olho_y + 8, BOCA)
    px(CX, olho_y + 9, BOCA)


def desenhar_cabeca():
    """Cabeça com contorno, testa, queixo."""
    # Testa e topo
    for y in range(TOPO_CABECA, BASE_CABECA):
        t = (y - TOPO_CABECA) / (BASE_CABECA - TOPO_CABECA)
        if t < 0.5:
            meia = 5 + int(t * 2 * 8)
        else:
            meia = 13 - int((t - 0.5) * 2 * 6)
        # contorno
        px(CX - meia - 1, y, CONTORNO)
        px(CX + meia + 1, y, CONTORNO)
        # preenchimento
        linha_h(y, CX - meia, CX + meia, PELE_CLARA)
        # sombra embaixo do cabelo (primeiras linhas)
        if y < TOPO_CABECA + 4:
            linha_h(y, CX - meia, CX + meia, PELE_BASE)
        # sombra nas laterais
        px(CX - meia, y, PELE_ESCURA)
        px(CX + meia, y, PELE_ESCURA)

    # Queixo
    for y in range(BASE_CABECA - 4, BASE_CABECA):
        t = (y - (BASE_CABECA - 4)) / 4
        meia = 7 - int(t * 4)
        linha_h(y, CX - meia, CX + meia, PELE_BASE)


def desenhar_cabelo_frente():
    """Franja e mechas frontais."""
    # Topo do cabelo
    for y in range(TOPO_CABECA - 4, TOPO_CABECA + 6):
        t = (y - (TOPO_CABECA - 4)) / 10
        if t < 0.3:
            meia = 4 + int(t * 4 * 9)
        else:
            meia = 13
        linha_h(y, CX - meia, CX + meia, CABELO_MEDIO)

    # Franja: cobre a testa com bicos
    for y in range(TOPO_CABECA + 4, TOPO_CABECA + 12):
        t = (y - (TOPO_CABECA + 4)) / 8
        meia = 13 - int(t * 2)
        linha_h(y, CX - meia, CX + meia, CABELO_MEDIO)

    # Bicos da franja (assimétricos, caem sobre a testa)
    for i, x_bico in enumerate([-10, -6, -2, 4, 8]):
        base_y = TOPO_CABECA + 8
        altura_bico = 4 + (i % 3)
        for y in range(base_y, base_y + altura_bico):
            px(CX + x_bico, y, CABELO_MEDIO)
            px(CX + x_bico + 1, y, CABELO_MEDIO)

    # Mechas laterais (caindo na frente dos ombros)
    for y in range(TOPO_CABECA + 8, OMBRO_Y + 8):
        t = (y - (TOPO_CABECA + 8)) / (OMBRO_Y + 8 - TOPO_CABECA - 8)
        # mecha esquerda
        x_esq = CX - 13 - int(t * 2)
        px(x_esq, y, CABELO_MEDIO)
        px(x_esq + 1, y, CABELO_MEDIO)
        px(x_esq - 1, y, CABELO_ESCURO)
        # mecha direita
        x_dir = CX + 13 + int(t * 2)
        px(x_dir, y, CABELO_MEDIO)
        px(x_dir - 1, y, CABELO_MEDIO)
        px(x_dir + 1, y, CABELO_ESCURO)

    # Luz no cabelo (brilho no topo)
    for i in range(4):
        px(CX - 4 + i, TOPO_CABECA - 2, CABELO_LUZ)
        px(CX - 4 + i, TOPO_CABECA - 1, CABELO_CLARO)
    px(CX - 5, TOPO_CABECA, CABELO_LUZ)
    px(CX + 3, TOPO_CABECA - 1, CABELO_CLARO)


def desenhar_roupa():
    """Top, corpete, cinto, saia."""
    # Top branco (peito)
    for y in range(OMBRO_Y + 4, PEITO_Y + 4):
        t = (y - OMBRO_Y - 4) / (PEITO_Y - OMBRO_Y)
        meia = int(LARGURA_OMBRO * (1 - t * 0.15))
        linha_h(y, CX - meia, CX + meia, TOP_BRANCO)
        # sombra embaixo
        px(CX - meia, y, TOP_SOMBRA)
        px(CX + meia, y, TOP_SOMBRA)
        # decote em V
        if y > OMBRO_Y + 6:
            v_y = y - OMBRO_Y - 6
            px(CX - 1, y, PELE_BASE)
            px(CX, y, PELE_BASE)
            px(CX + 1, y, PELE_BASE)
            if v_y > 2:
                px(CX - 2, y, PELE_BASE)
                px(CX + 2, y, PELE_BASE)

    # Corpete escuro (cintura)
    for y in range(PEITO_Y + 4, CINTURA_Y + 2):
        t = (y - PEITO_Y - 4) / (CINTURA_Y + 2 - PEITO_Y - 4)
        meia = int(LARGURA_OMBRO * (1 - t * 0.35))
        linha_h(y, CX - meia, CX + meia, CORPETE_ESCURO)
        # luz central
        px(CX - 2, y, CORPETE_MEDIO)
        px(CX - 1, y, CORPETE_LUZ)
        px(CX, y, CORPETE_LUZ)
        px(CX + 1, y, CORPETE_MEDIO)
        # sombra nas laterais
        px(CX - meia, y, CONTORNO)
        px(CX + meia, y, CONTORNO)

    # Faixa azul na cintura
    for y in range(CINTURA_Y + 2, CINTURA_Y + 6):
        meia = LARGURA_CINTURA + 1
        linha_h(y, CX - meia, CX + meia, FAIXA_AZUL)
        # luz no centro
        px(CX - 1, y, FAIXA_AZUL_LUZ)
        px(CX, y, FAIXA_AZUL_LUZ)
        px(CX + 1, y, FAIXA_AZUL_LUZ)

    # Saia longa preta (cobre quadril e desce)
    for y in range(CINTURA_Y + 6, PE_Y - 2):
        t = (y - CINTURA_Y - 6) / (PE_Y - 2 - CINTURA_Y - 6)
        # largura cresce conforme desce
        meia = int(LARGURA_CINTURA + 2 + t * 14)
        # gap entre as pernas aparece (fenda)
        fenda = int(t * 6)
        # desenhar saia como duas metades, com fenda no centro
        linha_h(y, CX - meia, CX - 2 - fenda, SAIA_ESCURA)
        linha_h(y, CX + 2 + fenda, CX + meia, SAIA_ESCURA)
        # sombra nas bordas
        px(CX - meia, y, CONTORNO)
        px(CX + meia, y, CONTORNO)
        # luz interna sutil
        px(CX - meia + 2, y, SAIA_MEDIA)
        px(CX + meia - 2, y, SAIA_MEDIA)

    # Borda dourada no fundo da saia
    for y in range(PE_Y - 4, PE_Y - 2):
        t = (y - CINTURA_Y - 6) / (PE_Y - 2 - CINTURA_Y - 6)
        meia = int(LARGURA_CINTURA + 2 + t * 14)
        fenda = int(t * 6)
        linha_h(y, CX - meia, CX - 2 - fenda, DOURADO)
        linha_h(y, CX + 2 + fenda, CX + meia, DOURADO)
        px(CX - meia, y, DOURADO_ESCURO)
        px(CX + meia, y, DOURADO_ESCURO)


def desenhar_bracos():
    """Braços com luvas longas."""
    # Braço esquerdo (caído ao lado)
    for y in range(OMBRO_Y + 2, CINTURA_Y + 4):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y + 4 - OMBRO_Y - 2)
        x = CX - LARGURA_OMBRO - 1 + int(t * 2)
        px(x, y, LUVA_MEDIA)
        px(x + 1, y, LUVA_ESCURA)
        px(x - 1, y, LUVA_ESCURA)
    # mão esquerda
    px(CX - LARGURA_OMBRO + 1, CINTURA_Y + 5, PELE_BASE)
    px(CX - LARGURA_OMBRO + 2, CINTURA_Y + 5, PELE_BASE)
    px(CX - LARGURA_OMBRO + 1, CINTURA_Y + 6, PELE_BASE)
    px(CX - LARGURA_OMBRO + 2, CINTURA_Y + 6, PELE_BASE)

    # Braço direito (caído ao lado)
    for y in range(OMBRO_Y + 2, CINTURA_Y + 4):
        t = (y - OMBRO_Y - 2) / (CINTURA_Y + 4 - OMBRO_Y - 2)
        x = CX + LARGURA_OMBRO + 1 - int(t * 2)
        px(x, y, LUVA_MEDIA)
        px(x - 1, y, LUVA_ESCURA)
        px(x + 1, y, LUVA_ESCURA)
    # mão direita
    px(CX + LARGURA_OMBRO - 1, CINTURA_Y + 5, PELE_BASE)
    px(CX + LARGURA_OMBRO - 2, CINTURA_Y + 5, PELE_BASE)
    px(CX + LARGURA_OMBRO - 1, CINTURA_Y + 6, PELE_BASE)
    px(CX + LARGURA_OMBRO - 2, CINTURA_Y + 6, PELE_BASE)


def desenhar_botas():
    """Botas curtas nos pés."""
    for y in range(PE_Y - 6, PE_Y + 1):
        # pé esquerdo
        linha_h(y, CX - 8, CX - 2, BOTA_ESCURA)
        px(CX - 8, y, CONTORNO)
        px(CX - 2, y, CONTORNO)
        px(CX - 6, y, BOTA_MEDIA)
        # pé direito
        linha_h(y, CX + 2, CX + 8, BOTA_ESCURA)
        px(CX + 2, y, CONTORNO)
        px(CX + 8, y, CONTORNO)
        px(CX + 6, y, BOTA_MEDIA)


# ============================================================
# EXECUTA O DESENHO (ordem importa: de trás pra frente)
# ============================================================
desenhar_cabelo_tras()       # cabelo atrás do corpo
desenhar_corpo_base()        # pele/silhueta
desenhar_cabeca()            # cabeça por cima
desenhar_rosto()             # olhos, boca
desenhar_roupa()             # roupas
desenhar_bracos()            # braços
desenhar_botas()             # botas
desenhar_cabelo_frente()     # franja e mechas por cima

# Salva
pygame.image.save(SUPERFICIE, "personagem.png")
print(f"Sprite salvo: personagem.png ({W}x{H})")
pygame.quit()