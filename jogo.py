import math
import sys

import pygame

pygame.init()

LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Teste_game001 - Personagem Levitando")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Paleta ---
COR_CEU_TOPO = (170, 195, 220)
COR_CEU_BASE = (240, 225, 185)
COR_DUNA_FUNDO = (150, 140, 130)
COR_DUNA_MEDIO = (175, 155, 125)
COR_DUNA_PERTO = (205, 175, 135)
COR_CHAO = (195, 165, 125)

COR_PELE = (235, 200, 175)
COR_CABELO = (40, 25, 30)
COR_VESTIDO_CLARO = (215, 60, 70)
COR_VESTIDO_ESCURO = (155, 25, 40)
COR_CINTO = (80, 20, 30)

# --- Física (valores suaves) ---
GRAVIDADE = 320.0            # bem baixa = queda lenta
VELOCIDADE_X = 200.0         # horizontal
IMPULSO_EXTRA = -180.0       # impulso ao apertar ↑
ALTURA_LEVITACAO = 60.0      # altura média que ela flutua
AMPLITUDE_OSCILACAO = 10.0   # quanto sobe/desce sozinha
FREQ_OSCILACAO = 2.2         # velocidade da oscilação
VELOCIDADE_SUBIDA = 90.0     # quão rápido chega na altura de levitação
VELOCIDADE_DESCIDA = 110.0   # quão rápido desce ao soltar

CHAO_Y = ALTURA - 80

# --- Estado ---
x = LARGURA // 2
y = CHAO_Y
vel_y = 0.0
direcao = 0
no_ar = False
tempo_levitando = 0.0
tempo_animacao = 0.0

# offsets de parallax
off_fundo = off_medio = off_perto = 0.0


def desenhar_ceu():
    for i in range(ALTURA):
        t = i / ALTURA
        r = int(COR_CEU_TOPO[0] * (1 - t) + COR_CEU_BASE[0] * t)
        g = int(COR_CEU_TOPO[1] * (1 - t) + COR_CEU_BASE[1] * t)
        b = int(COR_CEU_TOPO[2] * (1 - t) + COR_CEU_BASE[2] * t)
        pygame.draw.line(TELA, (r, g, b), (0, i), (LARGURA, i))


def desenhar_dunas(offset, cor, altura_base, amplitude, comprimento):
    pontos = []
    for px in range(0, LARGURA + 10, 6):
        ang = (px + offset) / comprimento
        py = altura_base + math.sin(ang) * amplitude + math.sin(ang * 2.3) * amplitude * 0.3
        pontos.append((px, py))
    pontos.append((LARGURA, ALTURA))
    pontos.append((0, ALTURA))
    pygame.draw.polygon(TELA, cor, pontos)


def desenhar_personagem(cx, cy, no_ar, tempo_anim, direcao, vel_y):
    """
    Personagem com curvas, cabelo esvoaçante e vestido em camadas.
    cx, cy = ponto dos pés (base do vestido).
    """
    # ----- Parâmetros de animação -----
    # balanço do corpo
    balanco = math.sin(tempo_anim * 6) * 1.5 if no_ar else math.sin(tempo_anim * 8) * 1.0
    # inclinação do cabelo conforme movimento vertical
    inclinacao = max(-1, min(1, vel_y / 200.0))
    # abertura do vestido no ar
    abertura = 1.0 if no_ar else 0.55

    # ----- Corpo (tronco) -----
    # silhueta em "gota" invertida
    ombro_y = cy - 58
    cintura_y = cy - 34
    pescoco_y = cy - 62
    cabeca_cy = cy - 72

    # tronco: polígono de ombro até cintura
    tronco = [
        (cx - 9 + balanco, ombro_y),
        (cx + 9 + balanco, ombro_y),
        (cx + 7 + balanco, cintura_y),
        (cx - 7 + balanco, cintura_y),
    ]
    pygame.draw.polygon(TELA, COR_PELE, tronco)

    # ----- Cabelo traseiro (atrás do corpo) -----
    # 3 fios que reagem ao movimento
    for i, offset in enumerate([-6, 0, 6]):
        onda = math.sin(tempo_anim * 4 + i) * 3
        topo_x = cx + offset * 0.5
        topo_y = cabeca_cy - 2
        meio_x = cx - direcao * (4 + i * 2) + onda
        meio_y = cabeca_cy + 12
        fim_x = cx - direcao * (8 + i * 3) + onda * 1.5
        fim_y = cabeca_cy + 26 + inclinacao * 4
        pygame.draw.line(TELA, COR_CABELO, (topo_x, topo_y), (meio_x, meio_y), 3)
        pygame.draw.line(TELA, COR_CABELO, (meio_x, meio_y), (fim_x, fim_y), 3)

    # ----- Cabeça -----
    pygame.draw.circle(TELA, COR_PELE, (cx + balanco, cabeca_cy), 9)

    # ----- Cabelo frontal (topo da cabeça) -----
    pygame.draw.arc(
        TELA, COR_CABELO,
        (cx + balanco - 10, cabeca_cy - 11, 20, 14),
        math.radians(20), math.radians(160), 4
    )
    # franja
    pygame.draw.line(
        TELA, COR_CABELO,
        (cx + balanco - 6, cabeca_cy - 6),
        (cx + balanco + 2, cabeca_cy - 3), 2
    )

    # ----- Rosto: um olho fechado (linha horizontal) -----
    olho_x = cx + balanco + direcao * 3
    olho_y = cabeca_cy + 1
    pygame.draw.line(TELA, COR_CABELO, (olho_x - 2, olho_y), (olho_x + 2, olho_y), 1)

    # ----- Braços -----
    # braço de trás
    pygame.draw.line(TELA, COR_PELE,
                     (cx - 8 + balanco, ombro_y + 4),
                     (cx - 12 + balanco * 0.5, cintura_y + 6), 3)
    # braço da frente
    pygame.draw.line(TELA, COR_PELE,
                     (cx + 8 + balanco, ombro_y + 4),
                     (cx + 12 + balanco * 0.5, cintura_y + 6), 3)

    # ----- Vestido (3 camadas) -----
    # camada 1: saia de trás (mais escura, mais larga, mais "atrasada")
    atras_abre = abertura * 20
    atras_bal = math.sin(tempo_anim * 3) * 2
    saia_tras = [
        (cx - 8 + balanco, cintura_y - 2),
        (cx + 8 + balanco, cintura_y - 2),
        (cx + atras_abre + atras_bal, cy),
        (cx - atras_abre + atras_bal, cy),
    ]
    pygame.draw.polygon(TELA, COR_VESTIDO_ESCURO, saia_tras)

    # camada 2: saia da frente (mais clara)
    frente_abre = abertura * 16
    frente_bal = math.sin(tempo_anim * 3 + 0.5) * 1.5
    saia_frente = [
        (cx - 7 + balanco, cintura_y),
        (cx + 7 + balanco, cintura_y),
        (cx + frente_abre + frente_bal, cy - 2),
        (cx - frente_abre + frente_bal, cy - 2),
    ]
    pygame.draw.polygon(TELA, COR_VESTIDO_CLARO, saia_frente)

    # camada 3: cinto
    pygame.draw.line(TELA, COR_CINTO,
                     (cx - 8 + balanco, cintura_y - 1),
                     (cx + 8 + balanco, cintura_y - 1), 3)


# --- Loop ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0
    tempo_animacao += dt

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_SPACE) and no_ar:
                vel_y += IMPULSO_EXTRA  # impulso extra pra subir mais

    teclas = pygame.key.get_pressed()
    direcao = 0
    if teclas[pygame.K_LEFT]:
        direcao = -1
    if teclas[pygame.K_RIGHT]:
        direcao = 1

    # ----- Física vertical -----
    if direcao != 0:
        # SEGURANDO DIREÇÃO: levita com oscilação
        no_ar = True
        tempo_levitando += dt

        # altura alvo: CHAO_Y - ALTURA_LEVITACAO, com oscilação
        altura_alvo = CHAO_Y - ALTURA_LEVITACAO + math.sin(tempo_levitando * FREQ_OSCILACAO) * AMPLITUDE_OSCILACAO

        # sobe suavemente até a altura alvo
        if y > altura_alvo:
            y -= VELOCIDADE_SUBIDA * dt
            if y < altura_alvo:
                y = altura_alvo
        else:
            y = altura_alvo  # mantém na altura oscilante

        vel_y = 0.0  # sem gravidade enquanto levita
    else:
        # SOLTOU: cai suavemente
        tempo_levitando = 0.0
        vel_y += GRAVIDADE * dt
        # limita a velocidade de queda pra não cair rápido
        if vel_y > VELOCIDADE_DESCIDA:
            vel_y = VELOCIDADE_DESCIDA
        y += vel_y * dt

        if y >= CHAO_Y:
            y = CHAO_Y
            vel_y = 0
            no_ar = False

    # ----- Movimento horizontal -----
    x += direcao * VELOCIDADE_X * dt
    x = max(40, min(LARGURA - 40, x))

    # ----- Parallax -----
    off_fundo += direcao * 25 * dt
    off_medio += direcao * 70 * dt
    off_perto += direcao * 150 * dt

    # ----- Desenho -----
    desenhar_ceu()
    desenhar_dunas(off_fundo, COR_DUNA_FUNDO, ALTURA - 200, 30, 180)
    desenhar_dunas(off_medio, COR_DUNA_MEDIO, ALTURA - 140, 22, 120)
    desenhar_dunas(off_perto, COR_DUNA_PERTO, ALTURA - 90, 14, 80)
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))

    desenhar_personagem(x, y, no_ar, tempo_animacao, direcao, vel_y)

    pygame.display.flip()