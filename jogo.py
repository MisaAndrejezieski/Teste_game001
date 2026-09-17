import sys

import pygame

pygame.init()

# --- Configurações ---
LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Protótipo - Palitinho Vermelho")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Paleta do deserto ---
COR_CEU_TOPO = (180, 200, 220)      # azul claro
COR_CEU_BASE = (235, 220, 180)      # amarelo pálido
COR_DUNA_FUNDO = (150, 140, 130)    # cinza-marrom distante
COR_DUNA_MEDIO = (170, 150, 120)    # marrom claro
COR_DUNA_PERTO = (200, 170, 130)    # areia
COR_CHAO = (190, 160, 120)
COR_PERSONAGEM = (200, 40, 50)      # vermelho
COR_VESTIDO = (160, 25, 35)         # vermelho mais escuro

# --- Física ---
GRAVIDADE = 800.0        # pixels/s²  (baixo = queda longa)
IMPULSO = -420.0         # pixels/s   (suave)
VELOCIDADE_X = 220.0     # pixels/s
CHAO_Y = ALTURA - 80

# --- Estado da personagem ---
x = LARGURA // 2
y = CHAO_Y
vel_y = 0.0
no_ar = False
direcao = 0

# --- Parallax ---
# Cada camada: (offset_x, velocidade_relativa, funcao_de_desenho)
offset_fundo = 0.0
offset_medio = 0.0
offset_perto = 0.0

def desenhar_ceu():
    """Gradiente vertical simples do céu."""
    for i in range(ALTURA):
        t = i / ALTURA
        r = int(COR_CEU_TOPO[0] * (1 - t) + COR_CEU_BASE[0] * t)
        g = int(COR_CEU_TOPO[1] * (1 - t) + COR_CEU_BASE[1] * t)
        b = int(COR_CEU_TOPO[2] * (1 - t) + COR_CEU_BASE[2] * t)
        pygame.draw.line(TELA, (r, g, b), (0, i), (LARGURA, i))

def desenhar_dunas(offset, cor, altura_base, amplitude, comprimento_onda):
    """Desenha uma camada de dunas senoidais."""
    pontos = []
    for px in range(0, LARGURA + 10, 5):
        # onda senoidal deslocada pelo offset
        ang = (px + offset) / comprimento_onda
        import math
        py = altura_base + math.sin(ang) * amplitude + math.sin(ang * 2.3) * amplitude * 0.3
        pontos.append((px, py))
    pontos.append((LARGURA, ALTURA))
    pontos.append((0, ALTURA))
    pygame.draw.polygon(TELA, cor, pontos)

def desenhar_personagem(x, y, no_ar):
    """Palitinho vermelho com vestido triangular."""
    # corpo (linha vertical)
    pygame.draw.line(TELA, COR_PERSONAGEM, (x, y - 40), (x, y - 10), 4)
    # cabeça (círculo)
    pygame.draw.circle(TELA, COR_PERSONAGEM, (x, y - 46), 7)
    # pernas
    if no_ar:
        # no ar: pernas juntas, levemente pra trás
        pygame.draw.line(TELA, COR_PERSONAGEM, (x, y - 10), (x - 4, y), 3)
        pygame.draw.line(TELA, COR_PERSONAGEM, (x, y - 10), (x + 4, y), 3)
    else:
        pygame.draw.line(TELA, COR_PERSONAGEM, (x, y - 10), (x - 6, y), 3)
        pygame.draw.line(TELA, COR_PERSONAGEM, (x, y - 10), (x + 6, y), 3)
    # vestido (triângulo)
    if no_ar:
        # no ar, vestido abre mais
        pontos_vestido = [(x - 10, y - 30), (x + 10, y - 30), (x + 18, y - 4), (x - 18, y - 4)]
    else:
        pontos_vestido = [(x - 8, y - 30), (x + 8, y - 30), (x + 12, y - 4), (x - 12, y - 4)]
    pygame.draw.polygon(TELA, COR_VESTIDO, pontos_vestido)

# --- Loop principal ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0  # delta em segundos

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_UP, pygame.K_SPACE):
                if no_ar:
                    vel_y = IMPULSO

    teclas = pygame.key.get_pressed()
    direcao = 0
    if teclas[pygame.K_LEFT]:
        direcao = -1
    if teclas[pygame.K_RIGHT]:
        direcao = 1

    # Movimento horizontal
    x += direcao * VELOCIDADE_X * dt
    # Limita nas bordas
    x = max(30, min(LARGURA - 30, x))

    # Movimento vertical
    vel_y += GRAVIDADE * dt
    y += vel_y * dt

    # Chão
    if y >= CHAO_Y:
        y = CHAO_Y
        vel_y = 0
        no_ar = False
    else:
        no_ar = True

    # Parallax: camadas se movem conforme o movimento horizontal
    offset_fundo += direcao * 20 * dt
    offset_medio += direcao * 60 * dt
    offset_perto += direcao * 140 * dt

    # --- Desenho ---
    desenhar_ceu()
    desenhar_dunas(offset_fundo, COR_DUNA_FUNDO, ALTURA - 200, 30, 180)
    desenhar_dunas(offset_medio, COR_DUNA_MEDIO, ALTURA - 140, 22, 120)
    desenhar_dunas(offset_perto, COR_DUNA_PERTO, ALTURA - 90, 14, 80)
    # chão
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))
    desenhar_personagem(x, y, no_ar)

    pygame.display.flip()