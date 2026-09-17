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

# --- Paleta: Noite no Deserto ---
COR_CEU_TOPO = (15, 22, 45)        # azul quase preto
COR_CEU_MEIO = (35, 55, 90)        # azul profundo
COR_CEU_BASE = (120, 100, 90)      # marrom acinzentado (luz da lua)

COR_MONTANHA = (30, 38, 60)        # silhueta de montanhas
COR_PIRAMIDE = (40, 50, 70)        # silhueta de pirâmides
COR_ARVORE = (25, 30, 45)          # silhueta de árvores
COR_DUNA_FUNDO = (80, 75, 80)      # areia na sombra
COR_DUNA_MEDIO = (110, 95, 85)     # areia média
COR_DUNA_PERTO = (140, 120, 100)   # areia clara
COR_CHAO = (90, 80, 75)            # chão de areia

COR_VESTIDO_CLARO = (200, 50, 60)
COR_VESTIDO_ESCURO = (120, 20, 35)
COR_DOURADO = (220, 180, 100)
COR_PELE = (230, 200, 180)
COR_CABELO = (30, 25, 35)
COR_MASCARA = (10, 10, 15)
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
capa_inclinacao = 0.0

particulas = []
for _ in range(50):
    particulas.append({
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(0, ALTURA * 0.7),
        "tam": random.uniform(1, 2.5),
        "vel": random.uniform(2, 8),
        "fase": random.uniform(0, math.tau),
    })


def desenhar_ceu():
    for i in range(ALTURA):
        t = i / ALTURA
        if t < 0.6:
            tt = t / 0.6
            r = int(COR_CEU_TOPO[0] * (1 - tt) + COR_CEU_MEIO[0] * tt)
            g = int(COR_CEU_TOPO[1] * (1 - tt) + COR_CEU_MEIO[1] * tt)
            b = int(COR_CEU_TOPO[2] * (1 - tt) + COR_CEU_MEIO[2] * tt)
        else:
            tt = (t - 0.6) / 0.4
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
    base_y = ALTURA - 220
    piramides = [
        (150, 140, 80, 5),
        (420, 200, 100, 6),
        (720, 160, 85, 5),
    ]
    for (px_base, largura, altura, degraus) in piramides:
        px_base = (px_base + offset * 0.4) % (LARGURA + 400) - 200
        for d in range(degraus):
            t = d / degraus
            largura_degrau = largura * (1 - t)
            altura_degrau = altura / degraus
            x_esq = px_base - largura_degrau / 2
            y_topo = base_y - altura_degrau * (d + 1)
            pygame.draw.rect(TELA, COR_PIRAMIDE,
                             (int(x_esq), int(y_topo),
                              int(largura_degrau), int(altura_degrau) + 1))


def desenhar_arvores_silhueta(offset):
    base_y = ALTURA - 140
    arvores = [120, 340, 560, 780]
    for px in arvores:
        px_vis = (px + offset * 0.7) % (LARGURA + 200) - 100
        altura_tronco = 30
        pygame.draw.rect(TELA, COR_ARVORE,
                         (px_vis - 2, base_y - altura_tronco, 4, altura_tronco))
        copa = [
            (px_vis - 25, base_y - altura_tronco),
            (px_vis - 10, base_y - altura_tronco - 20),
            (px_vis + 10, base_y - altura_tronco - 20),
            (px_vis + 25, base_y - altura_tronco),
        ]
        pygame.draw.polygon(TELA, COR_ARVORE, copa)


def desenhar_lanternas(offset):
    base_y = ALTURA - 55
    lanternas = [200, 500, 800]
    for px in lanternas:
        px_vis = (px + offset * 1.2) % (LARGURA + 200) - 100
        pygame.draw.rect(TELA, (60, 50, 45),
                         (px_vis - 1, base_y - 25, 3, 25))
        pygame.draw.rect(TELA, (80, 70, 60),
                         (px_vis - 6, base_y - 33, 13, 10))
        brilho = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(brilho, (255, 200, 100, 60), (15, 15), 12)
        TELA.blit(brilho, (px_vis - 15, base_y - 38))


def desenhar_particulas(tempo):
    for p in particulas:
        py = p["y"] - (tempo * p["vel"]) % (ALTURA * 0.7)
        if py < 0:
            py += ALTURA * 0.7
        px = p["x"] + math.sin(tempo * 0.5 + p["fase"]) * 6
        px -= (off_fundo * 0.15) % LARGURA
        px = px % LARGURA
        pygame.draw.circle(TELA, (200, 200, 220), (int(px), int(py)), int(p["tam"]))


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


def desenhar_personagem(cx, cy, no_ar, tempo_anim, direcao, vel_y, capa_off_x):
    balanco = math.sin(tempo_anim * 5) * 1.5 if no_ar else math.sin(tempo_anim * 7) * 1.0
    abertura = 1.0 if no_ar else 0.65

    cabeca_cy = cy - 76
    pescoco_y = cy - 64
    ombro_y = cy - 58
    cintura_y = cy - 34

    pe_bal = math.sin(tempo_anim * 8) * 2 if (not no_ar and direcao != 0) else 0

    # Pés
    pygame.draw.line(TELA, (40, 30, 35), (cx - 4 + balanco, cintura_y + 8), (cx - 5 + balanco + pe_bal, cy), 3)
    pygame.draw.line(TELA, (40, 30, 35), (cx + 4 + balanco, cintura_y + 8), (cx + 5 + balanco - pe_bal, cy), 3)

    # Capa de trás
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
    pygame.draw.polygon(TELA, COR_MASCARA, [
        (cx - 6 + balanco, ombro_y + 2),
        (cx + 6 + balanco, ombro_y + 2),
        (cx + 5 + balanco, cintura_y),
        (cx - 5 + balanco, cintura_y),
    ])

    # Pescoço
    pygame.draw.rect(TELA, COR_PELE, (cx - 4 + balanco, pescoco_y, 8, ombro_y - pescoco_y + 2))

    # Braços
    pygame.draw.line(TELA, COR_VESTIDO_ESCURO, (cx - 8 + balanco, ombro_y + 2), (cx - 15 + balanco + atraso * 0.5, cintura_y + 4), 3)
    pygame.draw.line(TELA, COR_VESTIDO_CLARO, (cx + 8 + balanco, ombro_y + 2), (cx + 16 + balanco + atraso * 0.5, cintura_y + 6), 3)
    pygame.draw.circle(TELA, COR_DOURADO, (int(cx + 16 + balanco + atraso * 0.5), int(cintura_y + 6)), 2)

    # Capa da frente
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

    # Cinto dourado
    pygame.draw.line(TELA, COR_DOURADO, (cx - 8 + balanco, cintura_y - 1), (cx + 8 + balanco, cintura_y - 1), 2)

    # Cabeça + Rosto
    cabeca_x = cx + balanco
    # Silhueta da cabeça/capuz
    pygame.draw.polygon(TELA, COR_VESTIDO_ESCURO, [
        (cabeca_x - 10, cabeca_cy + 8),
        (cabeca_x - 9, cabeca_cy - 6),
        (cabeca_x - 4, cabeca_cy - 11),
        (cabeca_x + 4, cabeca_cy - 11),
        (cabeca_x + 9, cabeca_cy - 6),
        (cabeca_x + 10, cabeca_cy + 8),
    ])
    # Rosto mascarado
    pygame.draw.polygon(TELA, COR_MASCARA, [
        (cabeca_x - 7, cabeca_cy + 6),
        (cabeca_x - 6, cabeca_cy - 4),
        (cabeca_x + 6, cabeca_cy - 4),
        (cabeca_x + 7, cabeca_cy + 6),
    ])
    # Olho brilhante
    olho_x = cabeca_x + direcao * 2
    olho_y = cabeca_cy - 1
    pygame.draw.circle(TELA, COR_OLHO, (int(olho_x), int(olho_y)), 2)

    # Cauda/Cabelo atrás
    cauda_onda = math.sin(tempo_anim * 4) * 4
    cauda_x = cabeca_x - direcao * 8 + cauda_onda
    cauda_y = cabeca_cy + 2
    pygame.draw.line(TELA, COR_CABELO, (cabeca_x - direcao * 5, cabeca_cy - 2), (cauda_x, cauda_y), 4)
    pygame.draw.line(TELA, COR_CABELO, (cauda_x, cauda_y), (cauda_x - direcao * 6 + cauda_onda, cauda_y + 8), 3)


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

    # Física Vertical
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

    # Movimento Horizontal
    x += nova_direcao * VELOCIDADE_X * dt
    x = max(40, min(LARGURA - 40, x))

    # Movimento Secundário da Capa
    alvo_capa_x = -direcao * 6
    capa_offset_x += (alvo_capa_x - capa_offset_x) * min(1.0, dt * 4.0)

    # Parallax
    off_fundo += nova_direcao * 25 * dt
    off_medio += nova_direcao * 70 * dt
    off_perto += nova_direcao * 150 * dt

    # Desenho
    desenhar_ceu()
    desenhar_particulas(tempo_animacao)
    desenhar_montanhas(off_fundo, COR_MONTANHA, ALTURA - 260, 40, 220)
    desenhar_piramides(off_fundo)
    desenhar_montanhas(off_medio, COR_DUNA_FUNDO, ALTURA - 180, 25, 140)
    desenhar_arvores_silhueta(off_medio)
    desenhar_montanhas(off_perto, COR_DUNA_MEDIO, ALTURA - 120, 18, 100)
    pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y + 10, LARGURA, ALTURA - CHAO_Y))
    desenhar_montanhas(off_perto * 1.5, COR_DUNA_PERTO, ALTURA - 70, 8, 60)
    desenhar_lanternas(off_perto)
    desenhar_sombra(x, y, no_ar)
    desenhar_personagem(x, y, no_ar, tempo_animacao, direcao, vel_y, capa_offset_x)

    pygame.display.flip()