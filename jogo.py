import math
import random
import sys

import pygame

pygame.init()

# --- Configurações da Janela ---
LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("A Jornada - Pixel Art Edition")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Carregamento de Sprites ---
SPRITE_W, SPRITE_H = 64, 64
FOLHA = pygame.image.load("personagem.png").convert_alpha()
ESCALA = 3.0

def carregar_frame(i):
    sub = FOLHA.subsurface((i * SPRITE_W, 0, SPRITE_W, SPRITE_H))
    return pygame.transform.scale(sub, (int(SPRITE_W * ESCALA), int(SPRITE_H * ESCALA)))

FRAMES = [carregar_frame(i) for i in range(4)]

# --- Paleta de Cores Mágica / Desértica ---
COR_CEU_TOPO = (12, 10, 30)
COR_CEU_ALTO = (28, 22, 58)
COR_CEU_MEDIO = (60, 42, 95)
COR_CEU_BASE = (110, 75, 120)
COR_LUA = (255, 245, 220)
COR_LUA_HALO = (200, 160, 210)
COR_ESTRELA = (240, 230, 255)
COR_PIRAMIDE = (35, 28, 52)
COR_MONTANHA = (50, 38, 70)
COR_DUNA_FUNDO = (80, 52, 95)
COR_DUNA_MEDIO = (115, 70, 110)
COR_DUNA_PERTO = (150, 92, 120)
COR_CHAO = (90, 58, 85)
COR_PARTICULA = (210, 160, 255)

# --- Física e Mundo ---
GRAVIDADE = 380.0
FORCA_FLUTUACAO = -280.0
VELOCIDADE_X = 220.0
VEL_Y_MAX = 200.0
CHAO_Y = ALTURA - 75

# --- Estado do Jogador ---
x, y = LARGURA // 2, CHAO_Y
vel_y = 0.0
direcao = 1
no_ar = False
tempo_animacao = 0.0
nova_direcao = 0

off_fundo = off_medio = off_perto = 0.0

# --- Sistemas de Partículas e Estrelas ---
particulas = []
estrelas = [
    {
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(0, ALTURA * 0.65),
        "tam": random.choice([1, 1, 2]),
        "fase": random.uniform(0, math.tau),
        "vel": random.uniform(0.8, 2.5),
    }
    for _ in range(80)
]

def criar_particula(px, py):
    particulas.append({
        "x": px + random.uniform(-10, 10),
        "y": py + random.uniform(-5, 5),
        "vel_x": random.uniform(-30, 30),
        "vel_y": random.uniform(10, 40),
        "vida": 1.0,
        "tam": random.uniform(2, 4)
    })

def atualizar_desenhar_particulas(dt):
    for p in particulas[:]:
        p["vida"] -= dt * 1.5
        if p["vida"] <= 0:
            particulas.remove(p)
            continue
        p["x"] += p["vel_x"] * dt
        p["y"] += p["vel_y"] * dt
        alpha = int(255 * p["vida"])
        surf = pygame.Surface((p["tam"], p["tam"]), pygame.SRCALPHA)
        surf.fill((*COR_PARTICULA, alpha))
        TELA.blit(surf, (p["x"], p["y"]))

def desenhar_cenario(tempo):
    # Gradiente do Céu Otimizado
    for i in range(0, ALTURA, 3):
        t = i / ALTURA
        if t < 0.4:
            tt = t / 0.4
            c = [int(COR_CEU_TOPO[k]*(1-tt) + COR_CEU_ALTO[k]*tt) for k in range(3)]
        elif t < 0.75:
            tt = (t - 0.4) / 0.35
            c = [int(COR_CEU_ALTO[k]*(1-tt) + COR_CEU_MEDIO[k]*tt) for k in range(3)]
        else:
            tt = (t - 0.75) / 0.25
            c = [int(COR_CEU_MEDIO[k]*(1-tt) + COR_CEU_BASE[k]*tt) for k in range(3)]
        pygame.draw.rect(TELA, c, (0, i, LARGURA, 3))

    # Estrelas Cintilantes
    for e in estrelas:
        b = 0.5 + 0.5 * math.sin(tempo * e["vel"] + e["fase"])
        px = (e["x"] - off_fundo * 0.08) % LARGURA
        cor = [min(255, int(COR_ESTRELA[k] * b)) for k in range(3)]
        pygame.draw.circle(TELA, cor, (int(px), int(e["y"])), e["tam"])

    # Lua com Halo Alpha
    lx, ly = LARGURA - 160, 100
    for r, a in [(80, 15), (55, 30), (35, 60)]:
        h = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(h, (*COR_LUA_HALO, a), (r, r), r)
        TELA.blit(h, (lx - r, ly - r))
    pygame.draw.circle(TELA, COR_LUA, (lx, ly), 20)

def desenhar_dunas(offset, cor, alt_base, amp, comp):
    pts = [(px, alt_base + math.sin((px + offset)/comp)*amp + math.sin((px + offset)*2.5/comp)*(amp*0.3))
           for px in range(0, LARGURA + 12, 10)]
    pts.extend([(LARGURA, ALTURA), (0, ALTURA)])
    pygame.draw.polygon(TELA, cor, pts)

def desenhar_sombra(cx, cy):
    dist = CHAO_Y - cy
    fator = max(0.2, 1.0 - dist / 160.0)
    w, h = int(36 * fator), int(8 * fator)
    if w > 0 and h > 0:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 110), (0, 0, w, h))
        TELA.blit(s, (cx - w // 2, CHAO_Y - 3))

# --- Loop Principal ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0
    tempo_animacao += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()
    nova_direcao = 0
    if teclas[pygame.K_LEFT]: nova_direcao = -1
    if teclas[pygame.K_RIGHT]: nova_direcao = 1
    if nova_direcao != 0: direcao = nova_direcao

    # Física Fluida de Flutuação (Arco Fluido)
    if teclas[pygame.K_SPACE] or teclas[pygame.K_UP]:
        vel_y += FORCA_FLUTUACAO * dt * 7.5
        criar_particula(x, y - 10)
    else:
        vel_y += GRAVIDADE * dt

    vel_y = max(-240.0, min(VEL_Y_MAX, vel_y))
    y += vel_y * dt

    if y >= CHAO_Y:
        y = CHAO_Y
        vel_y = 0.0
        no_ar = False
    else:
        no_ar = True

    x += nova_direcao * VELOCIDADE_X * dt
    x = max(30, min(LARGURA - 30, x))

    # Atualização do Paralaxe
    off_fundo += nova_direcao * 18 * dt
    off_medio += nova_direcao * 55 * dt
    off_perto += nova_direcao * 120 * dt

    # --- Renderização ---
    desenhar_cenario(tempo_animacao)
    desenhar_dunas(off_fundo, COR_MONTANHA, ALTURA - 220, 30, 220)
    desenhar_dunas(off_medio, COR_DUNA_FUNDO, ALTURA - 160, 20, 140)
    desenhar_dunas(off_medio * 1.3, COR_DUNA_MEDIO, ALTURA - 110, 14, 90)
    desenhar_dunas(off_perto, COR_DUNA_PERTO, ALTURA - 75, 8, 60)
    
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 5, LARGURA, ALTURA - CHAO_Y))

    atualizar_desenhar_particulas(dt)
    desenhar_sombra(x, y)

    # Animação da Personagem
    frame_idx = 3 if no_ar else (1 if nova_direcao != 0 and int(tempo_animacao * 8) % 2 == 0 else (2 if nova_direcao != 0 else 0))
    sprite = FRAMES[frame_idx]
    if direcao == -1:
        sprite = pygame.transform.flip(sprite, True, False)

    rect = sprite.get_rect()
    rect.midbottom = (int(x), int(y))
    TELA.blit(sprite, rect)

    pygame.display.flip()