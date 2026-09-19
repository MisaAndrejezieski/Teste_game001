"""
Personagem em pixel art 64x64, estilo chibi de ação.
Virada para DIREITA.
4 frames: idle, passo_1, passo_2, levitar.
Baseada na referência enviada.
"""
import pygame

pygame.init()

W, H = 64, 64
NUM_FRAMES = 4
FOLHA = pygame.Surface((W * NUM_FRAMES, H), pygame.SRCALPHA)

# --- Paleta (extraída da referência) ---
CAPUZ = (240, 235, 220, 255)          # branco/creme
CAPUZ_SOMBRA = (200, 195, 180, 255)
CABELO_RUIVO = (170, 40, 30, 255)     # vermelho escuro
CABELO_RUIVO_LUZ = (215, 70, 50, 255)
PELE = (240, 195, 170, 255)
PELE_SOMBRA = (200, 150, 130, 255)
OLHO = (30, 25, 35, 255)
CICLO = (15, 12, 20, 255)
DETALHE_ROSTO = (200, 50, 40, 255)    # marca vermelha na bochecha
VESTIDO = (30, 25, 35, 255)           # preto
VESTIDO_LUZ = (60, 55, 70, 255)
VERMELHO_BOTA = (180, 40, 40, 255)
DOURADO = (220, 180, 90, 255)
CONTORNO = (15, 12, 20, 255)


def px(x, y, cor, frame):
    if 0 <= x < W and 0 <= y < H:
        FOLHA.set_at((frame * W + x, y), cor)


def rect(x0, y0, x1, y1, cor, frame):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor, frame)


def linha_h(y, x0, x1, cor, frame):
    for x in range(x0, x1 + 1):
        px(x, y, cor, frame)


def desenhar_personagem(frame, pose):
    """
    Personagem chibi de perfil virada pra direita.
    """
    CX = W // 2  # 32

    # --- Parâmetros por pose ---
    # corpo_dy: deslocamento vertical do corpo todo (respiração/pulo)
    # cabeca_dy: deslocamento vertical da cabeça
    # perna_frente: qual perna está à frente (-1 = esquerda, 1 = direita)
    # braco_frente: qual braço está à frente
    configs = {
        "idle":    {"corpo_dy": 0,  "cabeca_dy": 0, "perna_frente": 0,  "braco_frente": 0, "levitar": False},
        "passo_1": {"corpo_dy": -1, "cabeca_dy": -1, "perna_frente": 1, "braco_frente": -1, "levitar": False},
        "passo_2": {"corpo_dy": 0,  "cabeca_dy": 0,  "perna_frente": -1, "braco_frente": 1, "levitar": False},
        "levitar": {"corpo_dy": -2, "cabeca_dy": -2, "perna_frente": -1, "braco_frente": 1, "levitar": True},
    }
    cfg = configs[pose]
    cdy = cfg["corpo_dy"]
    hdy = cfg["cabeca_dy"]
    perna_f = cfg["perna_frente"]
    braco_f = cfg["braco_frente"]
    levitando = cfg["levitar"]

    # ============================================================
    # GEOMETRIA
    # ============================================================
    # Corpo pequeno na parte de baixo
    # Cabeça grande em cima
    PE_Y = 58 + cdy              # base dos pés
    QUADRIL_Y = 46 + cdy         # onde começa o vestido
    CINTURA_Y = 40 + cdy
    OMBRO_Y = 36 + cdy
    CABECA_BASE = 34 + hdy       # base da cabeça (queixo)
    CABECA_TOPO = 8 + hdy        # topo da cabeça

    # ============================================================
    # PERNAS
    # ============================================================
    # perna de trás (mais escura/deslocada)
    if perna_f == 1:
        # perna esquerda atrás
        pt_x = CX - 6
        pf_x = CX + 2
    elif perna_f == -1:
        # perna direita atrás
        pt_x = CX - 4
        pf_x = CX + 4
    else:
        pt_x = CX - 4
        pf_x = CX + 2

    # perna de trás: em meia corrida, dobrada
    if levitando:
        # pernas juntas e dobradas pra trás
        # coxa esquerda
        rect(CX - 6, QUADRIL_Y, CX - 3, QUADRIL_Y + 3, VESTIDO, frame)
        # canela esquerda
        rect(CX - 6, QUADRIL_Y + 4, CX - 4, PE_Y - 2, VESTIDO, frame)
        # bota esquerda
        rect(CX - 7, PE_Y - 3, CX - 2, PE_Y - 1, VERMELHO_BOTA, frame)
        px(CX - 7, PE_Y - 3, DOURADO, frame)

        # perna direita (à frente, dobrada)
        rect(CX + 1, QUADRIL_Y, CX + 4, QUADRIL_Y + 3, VESTIDO, frame)
        rect(CX + 2, QUADRIL_Y + 4, CX + 4, PE_Y - 3, VESTIDO, frame)
        rect(CX + 1, PE_Y - 4, CX + 6, PE_Y - 2, VERMELHO_BOTA, frame)
        px(CX + 6, PE_Y - 4, DOURADO, frame)
    else:
        # perna de trás (perna esquerda se perna_f == 1)
        # coxa
        rect(pt_x - 1, QUADRIL_Y, pt_x + 2, QUADRIL_Y + 4, PELE_SOMBRA, frame)
        # canela
        if perna_f == 1:
            # atrás, dobrada
            rect(pt_x - 2, QUADRIL_Y + 5, pt_x + 1, PE_Y - 4, PELE_SOMBRA, frame)
            # bota
            rect(pt_x - 3, PE_Y - 4, pt_x + 2, PE_Y - 1, VERMELHO_BOTA, frame)
            px(pt_x - 3, PE_Y - 4, DOURADO, frame)
        else:
            # à frente
            rect(pt_x, QUADRIL_Y + 5, pt_x + 2, PE_Y - 4, PELE, frame)
            rect(pt_x - 1, PE_Y - 4, pt_x + 4, PE_Y - 1, VERMELHO_BOTA, frame)
            px(pt_x + 4, PE_Y - 4, DOURADO, frame)

        # perna da frente
        # coxa
        rect(pf_x - 1, QUADRIL_Y, pf_x + 3, QUADRIL_Y + 4, PELE, frame)
        # canela
        if perna_f == 1:
            # à frente
            rect(pf_x, QUADRIL_Y + 5, pf_x + 3, PE_Y - 4, PELE, frame)
            rect(pf_x - 1, PE_Y - 4, pf_x + 5, PE_Y - 1, VERMELHO_BOTA, frame)
            px(pf_x + 5, PE_Y - 4, DOURADO, frame)
        else:
            # atrás, dobrada
            rect(pf_x - 2, QUADRIL_Y + 5, pf_x + 1, PE_Y - 4, PELE, frame)
            rect(pf_x - 3, PE_Y - 4, pf_x + 2, PE_Y - 1, VERMELHO_BOTA, frame)
            px(pf_x - 3, PE_Y - 4, DOURADO, frame)

    # ============================================================
    # VESTIDO (curto, na cintura)
    # ============================================================
    if levitando:
        # vestido esvoaçante
        for y in range(CINTURA_Y - 2, QUADRIL_Y + 2):
            t = (y - CINTURA_Y + 2) / (QUADRIL_Y + 2 - CINTURA_Y + 2)
            meia = 7 + int(t * 4)
            linha_h(y, CX - meia, CX + meia, VESTIDO, frame)
        # detalhes vermelhos no vestido
        px(CX - 3, QUADRIL_Y, VERMELHO_BOTA, frame)
        px(CX + 3, QUADRIL_Y, VERMELHO_BOTA, frame)
    else:
        # vestido cobre quadril
        for y in range(CINTURA_Y - 2, QUADRIL_Y + 3):
            t = (y - CINTURA_Y + 2) / (QUADRIL_Y + 3 - CINTURA_Y + 2)
            meia = 6 + int(t * 3)
            linha_h(y, CX - meia, CX + meia, VESTIDO, frame)
        # luz no vestido
        px(CX - 1, CINTURA_Y + 2, VESTIDO_LUZ, frame)

    # ============================================================
    # TRONCO (pele + vestido por cima)
    # ============================================================
    # tronco de pele
    for y in range(OMBRO_Y, CINTURA_Y):
        linha_h(y, CX - 4, CX + 4, PELE, frame)

    # vestido cobre parte do tronco
    for y in range(OMBRO_Y + 4, CINTURA_Y):
        linha_h(y, CX - 4, CX + 4, VESTIDO, frame)
        px(CX - 4, y, CONTORNO, frame)
        px(CX + 4, y, CONTORNO, frame)

    # ============================================================
    # BRAÇOS
    # ============================================================
    # braço de trás
    if braco_f == 1:
        # braço esquerdo à frente
        rect(CX - 7, OMBRO_Y + 2, CX - 5, CINTURA_Y - 1, VESTIDO, frame)
        px(CX - 8, CINTURA_Y, PELE, frame)
    else:
        # braço esquerdo atrás
        rect(CX - 7, OMBRO_Y + 2, CX - 6, CINTURA_Y, VESTIDO, frame)
        px(CX - 8, CINTURA_Y, PELE, frame)

    # braço da frente
    if braco_f == -1:
        # braço direito à frente
        rect(CX + 5, OMBRO_Y + 2, CX + 7, CINTURA_Y - 2, VESTIDO, frame)
        px(CX + 7, CINTURA_Y - 1, PELE, frame)
    else:
        # braço direito atrás
        rect(CX + 5, OMBRO_Y + 2, CX + 6, CINTURA_Y, VESTIDO, frame)
        px(CX + 6, CINTURA_Y, PELE, frame)

    # ============================================================
    # PESCOÇO (curto, conecta cabeça ao corpo)
    # ============================================================
    rect(CX - 2, CABECA_BASE - 1, CX + 2, OMBRO_Y + 2, PELE_SOMBRA, frame)

    # ============================================================
    # CABEÇA (grande, chibi)
    # ============================================================
    # forma geral da cabeça: oval
    for y in range(CABECA_TOPO, CABECA_BASE + 1):
        t = (y - CABECA_TOPO) / (CABECA_BASE - CABECA_TOPO)
        # largura da cabeça por linha
        if t < 0.3:
            meia = 4 + int(t * 3 * 8)
        elif t < 0.7:
            meia = 12
        else:
            meia = 12 - int((t - 0.7) * 3 * 6)
        # pele
        linha_h(y, CX - meia, CX + meia, PELE, frame)
        # sombra nas laterais
        px(CX - meia, y, PELE_SOMBRA, frame)
        px(CX + meia, y, PELE_SOMBRA, frame)

    # ============================================================
    # ROSTO (perfil, virado pra direita)
    # ============================================================
    # olho único (perfil)
    olho_y = CABECA_TOPO + 8
    rect(CX + 3, olho_y - 1, CX + 7, olho_y + 1, OLHO, frame)
    # brilho
    px(CX + 4, olho_y - 1, (255, 255, 255, 255), frame)
    # cílios
    linha_h(olho_y - 2, CX + 3, CX + 7, CICLO, frame)

    # marca vermelha na bochecha
    px(CX + 9, olho_y + 3, DETALHE_ROSTO, frame)
    px(CX + 8, olho_y + 3, DETALHE_ROSTO, frame)

    # ============================================================
    # CAPUZ/CABELO (envolve a cabeça)
    # ============================================================
    # capuz branco/creme cobrindo o topo e as laterais da cabeça
    for y in range(CABECA_TOPO - 3, CABECA_BASE + 3):
        t = (y - CABECA_TOPO + 3) / (CABECA_BASE + 3 - CABECA_TOPO + 3)
        if t < 0.2:
            meia = 5 + int(t * 5 * 9)
        elif t < 0.6:
            meia = 14
        else:
            meia = 14 - int((t - 0.6) * 2.5 * 6)
        # capuz atrás da cabeça
        for x in range(CX - meia, CX - 3):
            px(x, y, CAPUZ, frame)
        # sombra do capuz atrás
        px(CX - meia, y, CAPUZ_SOMBRA, frame)

    # parte da frente do capuz (encima da testa)
    for y in range(CABECA_TOPO - 3, CABECA_TOPO + 5):
        t = (y - CABECA_TOPO + 3) / 8
        meia = 8 + int(t * 6)
        for x in range(CX - 3, CX + meia):
            px(x, y, CAPUZ, frame)

    # cabelo ruivo saindo do capuz (na frente, sobre a testa)
    for y in range(CABECA_TOPO + 3, CABECA_TOPO + 9):
        t = (y - CABECA_TOPO - 3) / 6
        largura = 6 - int(t * 2)
        for x in range(CX - 2, CX + 2 + largura):
            if (x + y) % 3 != 0:
                px(x, y, CABELO_RUIVO, frame)

    # mecha de cabelo ruivo caindo pela lateral
    for y in range(CABECA_TOPO + 6, OMBRO_Y):
        t = (y - CABECA_TOPO - 6) / (OMBRO_Y - CABECA_TOPO - 6)
        x_cabelo = CX - 6 + int(t * 1)
        px(x_cabelo, y, CABELO_RUIVO, frame)
        px(x_cabelo + 1, y, CABELO_RUIVO_LUZ, frame)

    # ============================================================
    # DETALHES FINAIS
    # ============================================================
    # laço/faixa no capuz (se tiver)
    px(CX - 8, CABECA_TOPO + 2, VERMELHO_BOTA, frame)
    px(CX - 8, CABECA_TOPO + 3, VERMELHO_BOTA, frame)


poses = ["idle", "passo_1", "passo_2", "levitar"]
for i, pose in enumerate(poses):
    desenhar_personagem(i, pose)

pygame.image.save(FOLHA, "personagem.png")
print(f"Sprite sheet salvo: personagem.png ({W * NUM_FRAMES}x{H}, {NUM_FRAMES} frames)")
pygame.quit()