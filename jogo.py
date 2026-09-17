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

# --- Paleta: Noite profunda no deserto ---
COR_CEU_TOPO = (8, 12, 28)         # quase preto azulado
COR_CEU_ALTO = (18, 28, 55)        # azul profundo
COR_CEU_MEDIO = (40, 55, 90)       # azul noite
COR_CEU_BASE = (90, 90, 110)       # cinza-azulado no horizonte

COR_LUA = (245, 240, 220)
COR_LUA_HALO = (180, 190, 210)
COR_ESTRELA = (230, 235, 255)

COR_PIRAMIDE = (25, 32, 52)
COR_MONTANHA = (35, 45, 70)
COR_DUNA_FUNDO = (55, 60, 80)
COR_DUNA_MEDIO = (75, 75, 90)
COR_DUNA_PERTO = (100, 95, 100)
COR_CHAO = (70, 65, 75)
COR_CHAO_BRILHO = (130, 125, 140)

COR_VESTIDO_CLARO = (180, 40, 55)
COR_VESTIDO_ESCURO = (105, 15, 30)
COR_VESTIDO_INTERNO = (60, 8, 18)
COR_DOURADO = (200, 165, 90)
COR_PELE = (215, 190, 175)
COR_CABELO = (20, 18, 28)
COR_MASCARA = (8, 8, 14)
COR_OLHO = (255, 220, 150)

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

# Estrelas
estrelas = []
for _ in range(90):
    estrelas.append({
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(0, ALTURA * 0.7),
        "tam": random.choice([1, 1, 1, 2, 2]),
        "fase": random.uniform(0, math.tau),
        "vel_cint": random.uniform(0.5, 2.0),
    })


def desenhar_ceu():
    """Gradiente de 4 paradas: noite profunda -> horizonte."""
    for i in range(ALTURA):
        t = i / ALTURA
        if t < 0.4:
            tt = t / 0.4
            r = int(COR_CEU_TOPO[0] * (1 - tt) + COR_CEU_ALTO[0] * tt)
            g = int(COR_CEU_TOPO[1] * (1 - tt) + COR_CEU_ALTO[1] * tt)
            b = int(COR_CEU_TOPO[2] * (1 - tt) + COR_CEU_ALTO[2] * tt)
        elif t < 0.75:
            tt = (t - 0.4) / 0.35
            r = int(COR_CEU_ALTO[0] * (1 - tt) + COR_CEU_MEDIO[0] * tt)
            g = int(COR_CEU_ALTO[1] * (1 - tt) + COR_CEU_MEDIO[1] * tt)
            b = int(COR_CEU_ALTO[2] * (1 - tt) + COR_CEU_MEDIO[2] * tt)
        else:
            tt = (t - 0.75) / 0.25
            r = int(COR_CEU_MEDIO[0] * (1 - tt) + COR_CEU_BASE[0] * tt)
            g = int(COR_CEU_MEDIO[1] * (1 - tt) + COR_CEU_BASE[1] * tt)
            b = int(COR_CEU_MEDIO[2] * (1 - tt) + COR_CEU_BASE[2] * tt)
        pygame.draw.line(TELA, (r, g, b), (0, i), (LARGURA, i))


def desenhar_lua(tempo):
    """Lua com halo suave."""
    lua_x = LARGURA - 180
    lua_y = 110

    # halo em várias camadas (transparente -> opaco)
    for raio, alpha in [(90, 12), (70, 20), (50, 35), (36, 55)]:
        halo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*COR_LUA_HALO, alpha), (raio, raio), raio)
        TELA.blit(halo, (lua_x - raio, lua_y - raio))

    # corpo da lua
    pygame.draw.circle(TELA, COR_LUA, (lua_x, lua_y), 22)
    # manchas sutis
    pygame.draw.circle(TELA, (225, 220, 200), (lua_x - 6, lua_y - 4), 4)
    pygame.draw.circle(TELA, (225, 220, 200), (lua_x + 7, lua_y + 5), 3)
    pygame.draw.circle(TELA, (225, 220, 200), (lua_x + 2, lua_y - 9), 2)


def desenhar_estrelas(tempo):
    for e in estrelas:
        # cintilação
        brilho = 0.6 + 0.4 * math.sin(tempo * e["vel_cint"] + e["fase"])
        alpha = int(255 * brilho)
        px = (e["x"] - off_fundo * 0.1) % LARGURA
        py = e["y"]
        # desenha com alpha
        cor = (
            min(255, int(COR_ESTRELA[0] * brilho)),
            min(255, int(COR_ESTRELA[1] * brilho)),
            min(255, int(COR_ESTRELA[2] * brilho)),
        )
        if e["tam"] == 1:
            TELA.set_at((int(px), int(py)), cor)
        else:
            pygame.draw.circle(TELA, cor, (int(px), int(py)), e["tam"])


def desenhar_camada_senoidal(offset, cor, altura_base, amplitude, comprimento):
    pontos = []
    for px in range(0, LARGURA + 10, 6):
        ang = (px + offset) / comprimento
        py = altura_base + math.sin(ang) * amplitude + math.sin(ang * 2.7) * amplitude * 0.4
        pontos.append((px, py))
    pontos.append((LARGURA, ALTURA))
    pontos.append((0, ALTURA))
    pygame.draw.polygon(TELA, cor, pontos)


def desenhar_piramides(offset):
    """Pirâmides em degraus, silhueta azul-escura no fundo."""
    base_y = ALTURA - 250
    piramides = [
        (120, 130, 70, 5),
        (380, 170, 90, 6),
        (700, 150, 75, 5),
        (900, 110, 60, 4),
    ]
    for (px_base, largura, altura, degraus) in piramides:
        px_base = (px_base + offset * 0.25) % (LARGURA + 400) - 200
        for d in range(degraus):
            t = d / degraus
            largura_degrau = largura * (1 - t)
            altura_degrau = altura / degraus
            x_esq = px_base - largura_degrau / 2
            y_topo = base_y - altura_degrau * (d + 1)
            pygame.draw.rect(TELA, COR_PIRAMIDE,
                             (int(x_esq), int(y_topo),
                              int(largura_degrau), int(altura_degrau) + 1))


def desenhar_nevoa(y, altura, alpha_max):
    """Faixa de névoa horizontal, sutil."""
    nevoa = pygame.Surface((LARGURA, altura), pygame.SRCALPHA)
    for i in range(altura):
        t = i / altura
        # fade in e fade out
        if t < 0.5:
            a = int(alpha_max * (t / 0.5))
        else:
            a = int(alpha_max * (1 - (t - 0.5) / 0.5))
        pygame.draw.line(nevoa, (180, 190, 210, a), (0, i), (LARGURA, i))
    TELA.blit(nevoa, (0, y))


def desenhar_chao_lunar():
    """Chão de areia noturna, com brilho prateado na parte de cima."""
    # base
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))
    # brilho prateado (primeiras linhas)
    for i in range(30):
        t = 1 - (i / 30)
        r = int(COR_CHAO[0] * (1 - t) + COR_CHAO_BRILHO[0] * t)
        g = int(COR_CHAO[1] * (1 - t) + COR_CHAO_BRILHO[1] * t)
        b = int(COR_CHAO[2] * (1 - t) + COR_CHAO_BRILHO[2] * t)
        pygame.draw.line(TELA, (r, g, b), (0, CHAO_Y + 10 + i), (LARGURA, CHAO_Y + 10 + i))


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
    pygame.draw.ellipse(sombra, (0, 0, 0, 120), (0, 0, largura, altura))
    TELA.blit(sombra, (cx - largura // 2, CHAO_Y + 6))


def desenhar_personagem(cx, cy, no_ar, tempo_anim, direcao, vel_y, capa_off_x):
    balanco = math.sin(tempo_anim * 5) * 1.5 if no_ar else math.sin(tempo_anim * 7) * 1.0
    abertura = 1.0 if no_ar else 0.65

    cabeca_cy = cy - 76
    pescoco_y = cy - 64
    ombro_y = cy - 58
    cintura_y = cy - 34

    pe_bal = math.sin(tempo_anim * 8) * 2 if (not no_ar and direcao != 0) else 0

    # Pés
    pygame.draw.line(TELA, (35, 25, 30),
                     (cx - 4 + balanco, cintura_y + 8),
                     (cx - 5 + balanco + pe_bal, cy), 3)
    pygame.draw.line(TELA, (35, 25, 30),
                     (cx + 4 + balanco, cintura_y + 8),
                     (cx + 5 + balanco - pe_bal, cy), 3)

    # Capa traseira
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
    pygame.draw.polygon(TELA, COR_VESTIDO_ESCURO, tras_pontos)

    # Tronco interno
    pygame.draw.polygon(TELA, COR_VESTIDO_INTERNO, [
        (cx - 6 + balanco, ombro_y + 2),
        (cx + 6 + balanco, ombro_y + 2),
        (cx + 5 + balanco, cintura_y),
        (cx - 5 + balanco, cintura_y),
    ])

    # Pescoço
    pygame.draw.rect(TELA, COR_PELE,
                     (cx - 4 + balanco, pescoco_y, 8, ombro_y - pescoco_y + 2))

    # Braços
    pygame.draw.line(TELA, COR_VESTIDO_ESCURO,
                     (cx - 8 + balanco, ombro_y + 2),
                     (cx - 15 + balanco + atraso * 0.5, cintura_y + 4), 3)
    pygame.draw.line(TELA, COR_VESTIDO_CLARO,
                     (cx + 8 + balanco, ombro_y + 2),
                     (cx + 16 + balanco + atraso * 0.5, cintura_y + 6), 3)
    pygame.draw.circle(TELA, COR_DOURADO,
                       (int(cx + 16 + balanco + atraso * 0.5), int(cintura_y + 6)), 2)

    # Capa frontal
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
    pygame.draw.polygon(TELA, COR_VESTIDO_CLARO, frente_pontos)

    # Borda dourada
    base_esq = (cx - abre_frente + bal_frente + atraso * 0.4, cy - 4)
    base_dir = (cx + abre_frente + bal_frente + atraso * 0.4, cy - 4)
    pygame.draw.line(TELA, COR_DOURADO, base_esq, base_dir, 2)
    for i in range(1, 5):
        t = i / 5
        px = base_esq[0] + (base_dir[0] - base_esq[0]) * t
        py = base_esq[1] + (base_dir[1] - base_esq[1]) * t
        pygame.draw.circle(TELA, COR_DOURADO, (int(px), int(py - 3)), 1)

    # Cinto
    pygame.draw.line(TELA, COR_DOURADO,
                     (cx - 8 + balanco, cintura_y - 1),
                     (cx + 8 + balanco, cintura_y - 1), 2)

    # Cabeça
    cabeca_x = cx + balanco
    pygame.draw.polygon(TELA, COR_VESTIDO_ESCURO, [
        (cabeca_x - 10, cabeca_cy + 8),
        (cabeca_x - 9, cabeca_cy - 6),
        (cabeca_x - 4, cabeca_cy - 11),
        (cabeca_x + 4, cabeca_cy - 11),
        (cabeca_x + 9, cabeca_cy - 6),
        (cabeca_x + 10, cabeca_cy + 8),
    ])
    pygame.draw.polygon(TELA, COR_MASCARA, [
        (cabeca_x - 7, cabeca_cy + 6),
        (cabeca_x - 6, cabeca_cy - 4),
        (cabeca_x + 6, cabeca_cy - 4),
        (cabeca_x + 7, cabeca_cy + 6),
    ])
    olho_x = cabeca_x + direcao * 2
    olho_y = cabeca_cy - 1
    pygame.draw.circle(TELA, COR_OLHO, (int(olho_x), int(olho_y)), 2)

    # Cabelo/cauda
    cauda_onda = math.sin(tempo_anim * 4) * 4
    cauda_x = cabeca_x - direcao * 8 + cauda_onda
    cauda_y = cabeca_cy + 2
    pygame.draw.line(TELA, COR_CABELO,
                     (cabeca_x - direcao * 5, cabeca_cy - 2),
                     (cauda_x, cauda_y), 4)
    pygame.draw.line(TELA, COR_CABELO,
                     (cauda_x, cauda_y),
                     (cauda_x - direcao * 6 + cauda_onda, cauda_y + 8), 3)


# --- Loop Principal ---
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

    # Física vertical
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

    # Movimento horizontal
    x += nova_direcao * VELOCIDADE_X * dt
    x = max(40, min(LARGURA - 40, x))

    # Movimento secundário
    alvo_capa_x = -direcao * 6
    capa_offset_x += (alvo_capa_x - capa_offset_x) * min(1.0, dt * 4.0)

    # Parallax
    off_fundo += nova_direcao * 15 * dt
    off_medio += nova_direcao * 50 * dt
    off_perto += nova_direcao * 110 * dt

    # --- Desenho (ordem importa) ---
    desenhar_ceu()
    desenhar_estrelas(tempo_animacao)
    desenhar_lua(tempo_animacao)

    # pirâmides distantes (mais escuras)
    desenhar_piramides(off_fundo)

    # montanhas médias
    desenhar_camada_senoidal(off_fundo, COR_MONTANHA, ALTURA - 240, 35, 240)

    # névoa fina entre montanhas e dunas
    desenhar_nevoa(ALTURA - 210, 40, 35)

    # dunas de fundo
    desenhar_camada_senoidal(off_medio, COR_DUNA_FUNDO, ALTURA - 180, 22, 150)

    # névoa entre dunas
    desenhar_nevoa(ALTURA - 140, 35, 30)

    # dunas médias
    desenhar_camada_senoidal(off_medio * 1.2, COR_DUNA_MEDIO, ALTURA - 120, 16, 100)

    # dunas próximas
    desenhar_camada_senoidal(off_perto, COR_DUNA_PERTO, ALTURA - 80, 10, 70)

    # chão
    desenhar_chao_lunar()

    # sombra + personagem
    desenhar_sombra(x, y, no_ar)
    desenhar_personagem(x, y, no_ar, tempo_animacao, direcao, vel_y, capa_offset_x)

    pygame.display.flip()