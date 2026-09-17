import math
import random
import sys

import pygame

pygame.init()

LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Teste_game001 - A Jornada")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Paleta: amanhecer no deserto ---
COR_CEU_TOPO = (70, 110, 165)      # azul do amanhecer
COR_CEU_MEIO = (160, 180, 195)     # azul esbranquiçado
COR_CEU_BASE = (245, 215, 170)     # dourado pálido no horizonte

COR_MONTANHA_DISTANTE = (110, 130, 155)   # azul acinzentado
COR_PIRAMIDE = (135, 145, 160)            # azul mais claro
COR_DUNA_FUNDO = (175, 160, 140)          # marrom claro
COR_DUNA_MEDIO = (200, 175, 140)          # areia média
COR_DUNA_PERTO = (220, 195, 155)          # areia clara
COR_CHAO = (210, 180, 140)                # chão de areia

COR_CAPA_CLARA = (215, 55, 50)
COR_CAPA_ESCURA = (150, 25, 35)
COR_CAPA_INTERNA = (100, 15, 25)
COR_DOURADO = (240, 200, 90)
COR_MASCARA = (15, 12, 18)
COR_OLHO = (255, 230, 120)
COR_PE = (60, 40, 45)

# --- Física ---
GRAVIDADE = 320.0
VELOCIDADE_X = 200.0
IMPULSO_EXTRA = -180.0
ALTURA_LEVITACAO = 60.0
AMPLITUDE_OSCILACAO = 10.0
FREQ_OSCILACAO = 2.2
VELOCIDADE_SUBIDA = 90.0
VELOCIDADE_DESCIDA = 110.0

CHAO_Y = ALTURA - 80

# --- Estado ---
x = LARGURA // 2
y = CHAO_Y
vel_y = 0.0
direcao = 0
no_ar = False
tempo_levitando = 0.0
tempo_animacao = 0.0

off_fundo = off_medio = off_perto = 0.0

capa_offset_x = 0.0
capa_inclinacao = 0.0

particulas = []
for _ in range(30):
    particulas.append({
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(0, ALTURA * 0.6),
        "tam": random.uniform(1, 2),
        "vel": random.uniform(3, 10),
        "fase": random.uniform(0, math.tau),
    })


def desenhar_ceu():
    """Gradiente de 3 cores: azul topo, azul claro, dourado base."""
    for i in range(ALTURA):
        t = i / ALTURA
        if t < 0.5:
            # topo -> meio
            tt = t / 0.5
            r = int(COR_CEU_TOPO[0] * (1 - tt) + COR_CEU_MEIO[0] * tt)
            g = int(COR_CEU_TOPO[1] * (1 - tt) + COR_CEU_MEIO[1] * tt)
            b = int(COR_CEU_TOPO[2] * (1 - tt) + COR_CEU_MEIO[2] * tt)
        else:
            # meio -> base
            tt = (t - 0.5) / 0.5
            r = int(COR_CEU_MEIO[0] * (1 - tt) + COR_CEU_BASE[0] * tt)
            g = int(COR_CEU_MEIO[1] * (1 - tt) + COR_CEU_BASE[1] * tt)
            b = int(COR_CEU_MEIO[2] * (1 - tt) + COR_CEU_BASE[2] * tt)
        pygame.draw.line(TELA, (r, g, b), (0, i), (LARGURA, i))


def desenhar_montanhas(offset, cor, altura_base, amplitude, comprimento):
    pontos = []
    for px in range(0, LARGURA + 10, 6):
        ang = (px + offset) / comprimento
        py = altura_base + math.sin(ang) * amplitude + math.sin(ang * 2.3) * amplitude * 0.3
        pontos.append((px, py))
    pontos.append((LARGURA, ALTURA))
    pontos.append((0, ALTURA))
    pygame.draw.polygon(TELA, cor, pontos)


def desenhar_piramides(offset):
    """Pirâmides em degraus no horizonte distante (silhueta)."""
    base_y = ALTURA - 200
    # cada pirâmide: (x, largura_base, altura, numero_degraus)
    piramides = [
        (120, 140, 70, 5),
        (400, 180, 90, 6),
        (700, 160, 80, 5),
    ]
    for (px_base, largura, altura, degraus) in piramides:
        px_base = (px_base + offset * 0.4) % (LARGURA + 400) - 200
        # desenha cada degrau, de baixo pra cima
        for d in range(degraus):
            t = d / degraus
            largura_degrau = largura * (1 - t)
            altura_degrau = altura / degraus
            x_esq = px_base - largura_degrau / 2
            y_topo = base_y - altura_degrau * (d + 1)
            pygame.draw.rect(TELA, COR_PIRAMIDE,
                             (int(x_esq), int(y_topo),
                              int(largura_degrau), int(altura_degrau) + 1))


def desenhar_portais(offset):
    """Torii/portais pequenos no horizonte médio."""
    base_y = ALTURA - 140
    portais = [80, 320, 580, 820]
    for px in portais:
        px_vis = (px + offset * 0.7) % (LARGURA + 200) - 100
        # cada portal: 2 pilares + 2 travessas
        altura_portal = 30
        largura_portal = 18
        # pilares
        pygame.draw.rect(TELA, COR_DUNA_FUNDO,
                         (px_vis - largura_portal // 2, base_y - altura_portal,
                          3, altura_portal))
        pygame.draw.rect(TELA, COR_DUNA_FUNDO,
                         (px_vis + largura_portal // 2 - 3, base_y - altura_portal,
                          3, altura_portal))
        # travessa de cima (curva pra cima)
        pygame.draw.rect(TELA, COR_DUNA_FUNDO,
                         (px_vis - largura_portal // 2 - 3, base_y - altura_portal - 3,
                          largura_portal + 6, 3))
        # travessa do meio
        pygame.draw.rect(TELA, COR_DUNA_FUNDO,
                         (px_vis - largura_portal // 2, base_y - altura_portal + 10,
                          largura_portal, 2))


def desenhar_lanternas(offset):
    """Lanternas/estelas no chão perto."""
    base_y = ALTURA - 60
    lanternas = [150, 450, 750]
    for px in lanternas:
        px_vis = (px + offset * 1.2) % (LARGURA + 200) - 100
        # poste
        pygame.draw.rect(TELA, (120, 90, 60),
                         (px_vis - 1, base_y - 30, 3, 30))
        # caixa da lanterna
        pygame.draw.rect(TELA, (140, 100, 60),
                         (px_vis - 5, base_y - 38, 11, 10))
        # brilho no topo
        pygame.draw.circle(TELA, (255, 200, 100), (int(px_vis), int(base_y - 33)), 3)
        pygame.draw.circle(TELA, (255, 240, 200), (int(px_vis), int(base_y - 33)), 1)


def desenhar_particulas(tempo):
    for p in particulas:
        py = p["y"] - (tempo * p["vel"]) % (ALTURA * 0.6)
        if py < 0:
            py += ALTURA * 0.6
        px = p["x"] + math.sin(tempo * 0.8 + p["fase"]) * 4
        px -= (off_fundo * 0.2) % LARGURA
        px = px % LARGURA
        pygame.draw.circle(TELA, (240, 240, 255), (int(px), int(py)), int(p["tam"]))


def desenhar_sombra(cx, cy, no_ar):
    if no_ar:
        altura_voo = CHAO_Y - cy
        escala = max(0.3, 1.0 - altura_voo / 200.0)
    else:
        escala = 1.0
    largura = int(40 * escala)
    altura = int(8 * escala)
    if largura <= 0 or altura <= 0:
        return
    sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 100), (0, 0, largura, altura))
    TELA.blit(sombra, (cx - largura // 2, CHAO_Y + 4))


def desenhar_personagem(cx, cy, no_ar, tempo_anim, direcao, vel_y, capa_off_x, capa_incl):
    """
    Personagem estilo Journey.
    cx, cy = ponto dos pés (base).
    """
    balanco = math.sin(tempo_anim * 5) * 1.5 if no_ar else math.sin(tempo_anim * 7) * 1.0
    abertura = 1.0 if no_ar else 0.65

    # --- Geometria corrigida ---
    # Proporções (do pé pra cima):
    #   pés:           cy
    #   base da capa:  cy - 4
    #   cintura:       cy - 34
    #   ombro:         cy - 58
    #   pescoço:       cy - 64
    #   base cabeça:   cy - 70
    #   centro cabeça: cy - 76
    cabeca_cy = cy - 76
    pescoco_y = cy - 64
    ombro_y = cy - 58
    cintura_y = cy - 34

    # ----- Pés -----
    pe_bal = math.sin(tempo_anim * 8) * 2 if (not no_ar and direcao != 0) else 0
    pygame.draw.line(TELA, COR_PE,
                     (cx - 3 + balanco, cintura_y + 8),
                     (cx - 4 + balanco + pe_bal, cy), 3)
    pygame.draw.line(TELA, COR_PE,
                     (cx + 3 + balanco, cintura_y + 8),
                     (cx + 4 + balanco - pe_bal, cy), 3)

    # ----- Capa: camada de trás -----
    atraso = capa_off_x
    abre_tras = abertura * 26
    bal_tras = math.sin(tempo_anim * 3.5) * 2.5
    tras_pontos = [
        (cx - 8 + balanco + atraso * 0.3, ombro_y),
        (cx + 8 + balanco + atraso * 0.3, ombro_y),
        (cx + 11 + balanco + atraso * 0.6, cintura_y),
        (cx + abre_tras + atraso + bal_tras, cy - 2),
        (cx - abre_tras + atraso + bal_tras, cy - 2),
        (cx - 11 + balanco + atraso * 0.6, cintura_y),
    ]
    pygame.draw.polygon(TELA, COR_CAPA_ESCURA, tras_pontos)

    # ----- Tronco interno (mais escuro) -----
    pygame.draw.polygon(TELA, COR_CAPA_INTERNA, [
        (cx - 6 + balanco, ombro_y + 2),
        (cx + 6 + balanco, ombro_y + 2),
        (cx + 5 + balanco, cintura_y),
        (cx - 5 + balanco, cintura_y),
    ])

    # ----- Pescoço (agora conecta cabeça ao corpo) -----
    pygame.draw.rect(TELA, COR_MASCARA,
                     (cx - 3 + balanco, pescoco_y, 6, ombro_y - pescoco_y + 2))

    # ----- Braços -----
    pygame.draw.line(TELA, COR_CAPA_ESCURA,
                     (cx - 8 + balanco, ombro_y + 2),
                     (cx - 15 + balanco + atraso * 0.5, cintura_y + 4), 3)
    pygame.draw.line(TELA, COR_CAPA_CLARA,
                     (cx + 8 + balanco, ombro_y + 2),
                     (cx + 16 + balanco + atraso * 0.5, cintura_y + 6), 3)
    pygame.draw.circle(TELA, COR_DOURADO,
                       (int(cx + 16 + balanco + atraso * 0.5), int(cintura_y + 6)), 2)

    # ----- Capa da frente -----
    abre_frente = abertura * 20
    bal_frente = math.sin(tempo_anim * 3.5 + 0.5) * 1.5
    frente_pontos = [
        (cx - 8 + balanco, ombro_y),
        (cx + 8 + balanco, ombro_y),
        (cx + 10 + balanco, cintura_y),
        (cx + abre_frente + bal_frente + atraso * 0.4, cy - 4),
        (cx - abre_frente + bal_frente + atraso * 0.4, cy - 4),
        (cx - 10 + balanco, cintura_y),
    ]
    pygame.draw.polygon(TELA, COR_CAPA_CLARA, frente_pontos)

    # ----- Borda dourada -----
    base_esq = (cx - abre_frente + bal_frente + atraso * 0.4, cy - 4)
    base_dir = (cx + abre_frente + bal_frente + atraso * 0.4, cy - 4)
    pygame.draw.line(TELA, COR_DOURADO, base_esq, base_dir, 2)
    pygame.draw.line(TELA, COR_DOURADO, base_esq, (base_esq[0], base_esq[1] - 4), 2)
    pygame.draw.line(TELA, COR_DOURADO, base_dir, (base_dir[0], base_dir[1] - 4), 2)
    for i in range(1, 5):
        t = i / 5
        px = base_esq[0] + (base_dir[0] - base_esq[0]) * t
        py = base_esq[1] + (base_dir[1] - base_esq[1]) * t
        pygame.draw.circle(TELA, COR_DOURADO, (int(px), int(py - 3)), 1)

    # ----- Cinto dourado -----
    pygame.draw.line(TELA, COR_DOURADO,
                     (cx - 8 + balanco, cintura_y - 1),
                     (cx + 8 + balanco, cintura_y - 1), 2)

    # ----- Cabeça + máscara (agora encostada no pescoço) -----
    cabeca_x = cx + balanco
    # capuz (silhueta vermelha escura)
    pygame.draw.polygon(TELA, COR_CAPA_ESCURA, [
        (cabeca_x - 10, cabeca_cy + 8),
        (cabeca_x - 9, cabeca_cy - 6),
        (cabeca_x - 4, cabeca_cy - 11),
        (cabeca_x + 4, cabeca_cy - 11),
        (cabeca_x + 9, cabeca_cy - 6),
        (cabeca_x + 10, cabeca_cy + 8),
    ])
    # rosto mascarado
    pygame.draw.polygon(TELA, COR_MASCARA, [
        (cabeca_x - 7, cabeca_cy + 6),
        (cabeca_x - 6, cabeca_cy - 4),
        (cabeca_x + 6, cabeca_cy - 4),
        (cabeca_x + 7, cabeca_cy + 6),
    ])
    # olho brilhante
    olho_x = cabeca_x + direcao * 2
    olho_y = cabeca_cy - 1
    pygame.draw.circle(TELA, COR_OLHO, (int(olho_x), int(olho_y)), 2)

    # ----- Cauda/cabelo atrás da cabeça -----
    cauda_onda = math.sin(tempo_anim * 4) * 4
    cauda_x = cabeca_x - direcao * 8 + cauda_onda
    cauda_y = cabeca_cy + 2
    pygame.draw.line(TELA, COR_CAPA_ESCURA,
                     (cabeca_x - direcao * 5, cabeca_cy - 2),
                     (cauda_x, cauda_y), 4)
    pygame.draw.line(TELA, COR_CAPA_ESCURA,
                     (cauda_x, cauda_y),
                     (cauda_x - direcao * 6 + cauda_onda, cauda_y + 8), 3)


# --- Loop principal ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0
    tempo_animacao += dt

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_SPACE) and no_ar:
                vel_y += IMPULSO_EXTRA

    teclas = pygame.key.get_pressed()
    nova_direcao = 0
    if teclas[pygame.K_LEFT]:
        nova_direcao = -1
    if teclas[pygame.K_RIGHT]:
        nova_direcao = 1

    if nova_direcao != 0:
        direcao = nova_direcao

    # ----- Física vertical -----
    if nova_direcao != 0:
        no_ar = True
        tempo_levitando += dt
        altura_alvo = CHAO_Y - ALTURA_LEVITACAO + math.sin(tempo_levitando * FREQ_OSCILACAO) * AMPLITUDE_OSCILACAO
        if y > altura_alvo:
            y -= VELOCIDADE_SUBIDA * dt
            if y < altura_alvo:
                y = altura_alvo
        else:
            y = altura_alvo
        vel_y = 0.0
    else:
        tempo_levitando = 0.0
        vel_y += GRAVIDADE * dt
        if vel_y > VELOCIDADE_DESCIDA:
            vel_y = VELOCIDADE_DESCIDA
        y += vel_y * dt
        if y >= CHAO_Y:
            y = CHAO_Y
            vel_y = 0
            no_ar = False

    # ----- Movimento horizontal -----
    x += nova_direcao * VELOCIDADE_X * dt
    x = max(40, min(LARGURA - 40, x))

    # ----- Movimento secundário da capa -----
    alvo_capa_x = -direcao * 6
    if no_ar:
        alvo_capa_incl = -vel_y / 300.0
    else:
        alvo_capa_incl = 0.0
    capa_offset_x += (alvo_capa_x - capa_offset_x) * min(1.0, dt * 4.0)
    capa_inclinacao += (alvo_capa_incl - capa_inclinacao) * min(1.0, dt * 3.0)

    # ----- Parallax -----
    off_fundo += nova_direcao * 25 * dt
    off_medio += nova_direcao * 70 * dt
    off_perto += nova_direcao * 150 * dt

    # ----- Desenho -----
    desenhar_ceu()
    desenhar_particulas(tempo_animacao)

    # montanhas distantes
    desenhar_montanhas(off_fundo, COR_MONTANHA_DISTANTE, ALTURA - 260, 40, 220)

    # pirâmides no horizonte
    desenhar_piramides(off_fundo)

    # dunas médias
    desenhar_montanhas(off_medio, COR_DUNA_FUNDO, ALTURA - 180, 25, 140)

    # portais
    desenhar_portais(off_medio)

    # dunas próximas
    desenhar_montanhas(off_perto, COR_DUNA_MEDIO, ALTURA - 120, 18, 100)

    # chão
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))

    # dunas ainda mais próximas (detalhe)
    desenhar_montanhas(off_perto * 1.5, COR_DUNA_PERTO, ALTURA - 70, 8, 60)

    # lanternas no chão
    desenhar_lanternas(off_perto)

    # personagem
    desenhar_sombra(x, y, no_ar)
    desenhar_personagem(x, y, no_ar, tempo_animacao, direcao, vel_y, capa_offset_x, capa_inclinacao)

    pygame.display.flip()