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

# --- Paleta (baseada nas referências) ---
COR_CEU_TOPO = (35, 60, 105)       # azul escuro noturno
COR_CEU_BASE = (85, 130, 170)      # azul claro
COR_DUNA_FUNDO = (45, 65, 95)      # azul escuro distante
COR_DUNA_MEDIO = (90, 100, 115)    # azul acinzentado
COR_DUNA_PERTO = (140, 130, 120)   # areia fria
COR_CHAO = (55, 50, 55)            # chão escuro (como na imagem 1)

COR_CAPA_CLARA = (215, 55, 50)     # vermelho vivo
COR_CAPA_ESCURA = (150, 25, 35)    # vermelho escuro (camada de trás)
COR_CAPA_INTERNA = (100, 15, 25)   # interior da capa
COR_DOURADO = (240, 200, 90)       # borda dourada
COR_MASCARA = (15, 12, 18)         # rosto preto
COR_OLHO = (255, 230, 120)         # olho brilhante
COR_PE = (60, 40, 45)              # pés escuros

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

# offsets de parallax
off_fundo = off_medio = off_perto = 0.0

# estado da capa (atraso em relação ao corpo)
capa_offset_x = 0.0
capa_inclinacao = 0.0

# partículas do fundo
particulas = []
for _ in range(40):
    particulas.append({
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(0, ALTURA - 100),
        "tam": random.uniform(1, 2.5),
        "vel": random.uniform(5, 20),
        "fase": random.uniform(0, math.tau),
    })


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


def desenhar_particulas(tempo, direcao):
    """Estrelinhas/faíscas ao fundo, como na imagem 1."""
    for p in particulas:
        # movimento suave pra cima
        py = p["y"] - (tempo * p["vel"]) % ALTURA
        if py < 0:
            py += ALTURA
        # leve oscilação horizontal
        px = p["x"] + math.sin(tempo * 0.8 + p["fase"]) * 4
        # se move com o parallax
        px -= (off_fundo * 0.3) % LARGURA
        px = px % LARGURA
        alpha = 200 if p["tam"] > 1.8 else 130
        pygame.draw.circle(TELA, (alpha, alpha, 200), (int(px), int(py)), int(p["tam"]))


def desenhar_sombra(cx, cy, no_ar):
    """Sombra elíptica no chão. Encolhe quando ela sobe."""
    if no_ar:
        altura_voo = CHAO_Y - cy
        escala = max(0.3, 1.0 - altura_voo / 200.0)
    else:
        escala = 1.0
    largura = int(40 * escala)
    altura = int(8 * escala)
    sombra = pygame.Surface((largura, altura), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 100), (0, 0, largura, altura))
    TELA.blit(sombra, (cx - largura // 2, CHAO_Y + 4))


def desenhar_personagem(cx, cy, no_ar, tempo_anim, direcao, vel_y, capa_off_x, capa_incl):
    """
    Personagem estilo Journey: silhueta em gota, capa esvoaçante, rosto mascarado.
    cx, cy = ponto dos pés (base).
    """
    # balanço do corpo
    balanco = math.sin(tempo_anim * 5) * 1.5 if no_ar else math.sin(tempo_anim * 7) * 1.0
    # abertura da capa no ar
    abertura = 1.0 if no_ar else 0.65

    # geometria
    cabeca_cy = cy - 78
    ombro_y = cy - 62
    cintura_y = cy - 34

    # ----- Pés (aparecem por baixo da capa) -----
    pe_bal = math.sin(tempo_anim * 8) * 2 if not no_ar and direcao != 0 else 0
    if no_ar:
        pe_bal = 1
    # pé esquerdo
    pygame.draw.line(TELA, COR_PE,
                     (cx - 3 + balanco, cintura_y + 8),
                     (cx - 4 + balanco + pe_bal, cy), 3)
    # pé direito
    pygame.draw.line(TELA, COR_PE,
                     (cx + 3 + balanco, cintura_y + 8),
                     (cx + 4 + balanco - pe_bal, cy), 3)

    # ----- Capa: camada de trás (mais escura, atrasada) -----
    # atraso = o quanto a capa "fica pra trás" em relação ao movimento
    atraso = capa_off_x
    # abertura traseira
    abre_tras = abertura * 26
    bal_tras = math.sin(tempo_anim * 3.5) * 2.5

    # pontos da capa traseira (polígono em gota)
    tras_pontos = [
        (cx - 6 + balanco + atraso * 0.3, ombro_y),
        (cx + 6 + balanco + atraso * 0.3, ombro_y),
        (cx + 10 + balanco + atraso * 0.6, cintura_y),
        (cx + abre_tras + atraso + bal_tras, cy - 2),
        (cx - abre_tras + atraso + bal_tras, cy - 2),
        (cx - 10 + balanco + atraso * 0.6, cintura_y),
    ]
    pygame.draw.polygon(TELA, COR_CAPA_ESCURA, tras_pontos)

    # ----- Corpo (tronco interno, cor mais escura pra dar profundidade) -----
    pygame.draw.polygon(TELA, COR_CAPA_INTERNA, [
        (cx - 5 + balanco, ombro_y + 4),
        (cx + 5 + balanco, ombro_y + 4),
        (cx + 4 + balanco, cintura_y),
        (cx - 4 + balanco, cintura_y),
    ])

    # ----- Braços -----
    # braço de trás
    pygame.draw.line(TELA, COR_CAPA_ESCURA,
                     (cx - 7 + balanco, ombro_y + 2),
                     (cx - 14 + balanco + atraso * 0.5, cintura_y + 4), 3)
    # braço da frente (com borda dourada na ponta = luva)
    pygame.draw.line(TELA, COR_CAPA_CLARA,
                     (cx + 7 + balanco, ombro_y + 2),
                     (cx + 15 + balanco + atraso * 0.5, cintura_y + 6), 3)
    pygame.draw.circle(TELA, COR_DOURADO,
                       (int(cx + 15 + balanco + atraso * 0.5), int(cintura_y + 6)), 2)

    # ----- Capa: camada da frente (mais clara) -----
    abre_frente = abertura * 20
    bal_frente = math.sin(tempo_anim * 3.5 + 0.5) * 1.5
    frente_pontos = [
        (cx - 6 + balanco, ombro_y),
        (cx + 6 + balanco, ombro_y),
        (cx + 8 + balanco, cintura_y),
        (cx + abre_frente + bal_frente + atraso * 0.4, cy - 4),
        (cx - abre_frente + bal_frente + atraso * 0.4, cy - 4),
        (cx - 8 + balanco, cintura_y),
    ]
    pygame.draw.polygon(TELA, COR_CAPA_CLARA, frente_pontos)

    # ----- Borda dourada na capa da frente -----
    # desenha a linha da base da capa em dourado
    base_esq = (cx - abre_frente + bal_frente + atraso * 0.4, cy - 4)
    base_dir = (cx + abre_frente + bal_frente + atraso * 0.4, cy - 4)
    pygame.draw.line(TELA, COR_DOURADO, base_esq, base_dir, 2)
    # pequenas pontas douradas nas laterais
    pygame.draw.line(TELA, COR_DOURADO, base_esq, (base_esq[0], base_esq[1] - 4), 2)
    pygame.draw.line(TELA, COR_DOURADO, base_dir, (base_dir[0], base_dir[1] - 4), 2)
    # detalhes: pequenos "nós" dourados ao longo da borda
    for i in range(1, 5):
        t = i / 5
        px = base_esq[0] + (base_dir[0] - base_esq[0]) * t
        py = base_esq[1] + (base_dir[1] - base_esq[1]) * t
        pygame.draw.circle(TELA, COR_DOURADO, (int(px), int(py - 3)), 1)

    # ----- Cinto dourado -----
    pygame.draw.line(TELA, COR_DOURADO,
                     (cx - 7 + balanco, cintura_y - 1),
                     (cx + 7 + balanco, cintura_y - 1), 2)

    # ----- Cabeça + máscara -----
    cabeca_x = cx + balanco
    # capuz/cabelo (silhueta da cabeça em vermelho escuro)
    pygame.draw.polygon(TELA, COR_CAPA_ESCURA, [
        (cabeca_x - 10, cabeca_cy + 6),
        (cabeca_x - 9, cabeca_cy - 8),
        (cabeca_x - 4, cabeca_cy - 13),
        (cabeca_x + 4, cabeca_cy - 13),
        (cabeca_x + 9, cabeca_cy - 8),
        (cabeca_x + 10, cabeca_cy + 6),
    ])
    # rosto mascarado (preto)
    pygame.draw.polygon(TELA, COR_MASCARA, [
        (cabeca_x - 7, cabeca_cy + 4),
        (cabeca_x - 6, cabeca_cy - 5),
        (cabeca_x + 6, cabeca_cy - 5),
        (cabeca_x + 7, cabeca_cy + 4),
    ])
    # olho brilhante
    olho_x = cabeca_x + direcao * 2
    olho_y = cabeca_cy - 1
    pygame.draw.circle(TELA, COR_OLHO, (int(olho_x), int(olho_y)), 2)

    # ----- Cabelo/cauda que sai de trás da cabeça (movimento secundário) -----
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

    # atualiza direção
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

    # ----- Movimento secundário da capa (atraso em relação ao corpo) -----
    # alvo: a capa fica atrás quando anda, e levanta quando sobe
    alvo_capa_x = -direcao * 6  # atraso horizontal
    if no_ar:
        alvo_capa_incl = -vel_y / 300.0  # sobe quando ela sobe
    else:
        alvo_capa_incl = 0.0

    # lerp suave
    capa_offset_x += (alvo_capa_x - capa_offset_x) * min(1.0, dt * 4.0)
    capa_inclinacao += (alvo_capa_incl - capa_inclinacao) * min(1.0, dt * 3.0)

    # ----- Parallax -----
    off_fundo += nova_direcao * 25 * dt
    off_medio += nova_direcao * 70 * dt
    off_perto += nova_direcao * 150 * dt

    # ----- Desenho -----
    desenhar_ceu()
    desenhar_particulas(tempo_animacao, nova_direcao)
    desenhar_dunas(off_fundo, COR_DUNA_FUNDO, ALTURA - 200, 30, 180)
    desenhar_dunas(off_medio, COR_DUNA_MEDIO, ALTURA - 140, 22, 120)
    desenhar_dunas(off_perto, COR_DUNA_PERTO, ALTURA - 90, 14, 80)
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))

    desenhar_sombra(x, y, no_ar)
    desenhar_personagem(x, y, no_ar, tempo_animacao, direcao, vel_y, capa_offset_x, capa_inclinacao)

    pygame.display.flip()