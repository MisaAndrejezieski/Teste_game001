"""
Gera um sprite sheet em pixel art da personagem.
Paleta:
- Cabelo: preto-azulado
- Pele: pêssego claro
- Vestido: vermelho vivo com borda dourada
- Cinto: dourado
- Máscara: preta
- Olho: brilhante dourado
"""
import pygame

pygame.init()

# Tamanho de cada sprite: 48x64 pixels (silhueta em gota)
SPRITE_W, SPRITE_H = 48, 64
# 6 frames: idle, passo_esq, passo_dir, levitar_1, levitar_2, pousar
NUM_FRAMES = 6
FOLHA_W = SPRITE_W * NUM_FRAMES
FOLHA_H = SPRITE_H

folha = pygame.Surface((FOLHA_W, FOLHA_H), pygame.SRCALPHA)

# --- Paleta ---
TRANSPARENTE = (0, 0, 0, 0)
CABELO = (28, 22, 38, 255)
CABELO_LUZ = (55, 45, 70, 255)
PELE = (240, 205, 180, 255)
PELE_SOMBRA = (200, 165, 145, 255)
VESTIDO = (200, 45, 55, 255)
VESTIDO_ESCURO = (120, 20, 35, 255)
VESTIDO_LUZ = (240, 80, 80, 255)
DOURADO = (230, 190, 100, 255)
DOURADO_ESCURO = (170, 130, 60, 255)
MASCARA = (12, 10, 18, 255)
OLHO = (255, 230, 140, 255)
PE = (45, 35, 40, 255)


def px(x, y, cor, frame=0):
    """Coloca um pixel no frame especificado."""
    if 0 <= x < SPRITE_W and 0 <= y < SPRITE_H:
        folha.set_at((frame * SPRITE_W + x, y), cor)


def retangulo(x0, y0, x1, y1, cor, frame=0):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, cor, frame)


def desenhar_personagem_base(frame, pose="idle"):
    """
    Desenha a personagem em pixel art. Coordenadas relativas ao sprite 48x64.
    Base dos pés em y=62.
    """
    # --- Geometria central ---
    cx = SPRITE_W // 2   # 24
    cabeca_cy = 16
    ombro_y = 26
    cintura_y = 40
    pe_y = 62

    # Variação por pose
    if pose == "idle":
        balanco = 0
        abertura_saia = 8   # quanto a saia abre
        altura_pe = 0
    elif pose == "passo_esq":
        balanco = -1
        abertura_saia = 9
        altura_pe = -2
    elif pose == "passo_dir":
        balanco = 1
        abertura_saia = 9
        altura_pe = -2
    elif pose == "levitar_1":
        balanco = 0
        abertura_saia = 13
        altura_pe = -3
    elif pose == "levitar_2":
        balanco = 0
        abertura_saia = 14
        altura_pe = -3
    elif pose == "pousar":
        balanco = 0
        abertura_saia = 11
        altura_pe = 1

    # --- Pés (aparecem por baixo) ---
    # pé esquerdo
    retangulo(cx - 4 + balanco, pe_y + altura_pe - 2, cx - 2 + balanco, pe_y + altura_pe, PE, frame)
    # pé direito
    retangulo(cx + 1 + balanco, pe_y + altura_pe - 2, cx + 3 + balanco, pe_y + altura_pe, PE, frame)

    # --- Saia/capa de trás (mais escura) ---
    for y in range(cintura_y, pe_y - 2):
        t = (y - cintura_y) / (pe_y - 2 - cintura_y)
        meia_largura = int(6 + abertura_saia * t)
        # camada de trás, um pouco mais larga
        retangulo(cx - meia_largura - 2 + balanco, y, cx + meia_largura + 2 + balanco, y, VESTIDO_ESCURO, frame)

    # --- Corpo/tronco (vermelho vivo) ---
    for y in range(ombro_y, cintura_y):
        meia_largura = 5
        retangulo(cx - meia_largura + balanco, y, cx + meia_largura + balanco, y, VESTIDO, frame)

    # --- Saia da frente (mais clara) ---
    for y in range(cintura_y, pe_y - 2):
        t = (y - cintura_y) / (pe_y - 2 - cintura_y)
        meia_largura = int(5 + abertura_saia * t * 0.9)
        # só desenha a frente, deixa as bordas escuras aparecerem
        retangulo(cx - meia_largura + balanco, y, cx + meia_largura + balanco, y, VESTIDO, frame)

    # --- Detalhe de luz no vestido (do lado esquerdo) ---
    for y in range(ombro_y + 2, cintura_y):
        px(cx - 4 + balanco, y, VESTIDO_LUZ, frame)

    # --- Cinto dourado ---
    retangulo(cx - 6 + balanco, cintura_y - 1, cx + 6 + balanco, cintura_y, DOURADO, frame)

    # --- Borda dourada da saia ---
    for y in [pe_y - 3, pe_y - 4]:
        t = (y - cintura_y) / (pe_y - 2 - cintura_y)
        meia_largura = int(6 + abertura_saia * t)
        retangulo(cx - meia_largura - 2 + balanco, y, cx - meia_largura + balanco, y, DOURADO, frame)
        retangulo(cx + meia_largura + balanco, y, cx + meia_largura + 2 + balanco, y, DOURADO, frame)

    # --- Pescoço ---
    retangulo(cx - 1 + balanco, ombro_y - 4, cx + 1 + balanco, ombro_y, PELE, frame)

    # --- Cabeça ---
    # formato arredondado
    retangulo(cx - 4 + balanco, cabeca_cy - 5, cx + 4 + balanco, cabeca_cy + 5, PELE, frame)
    retangulo(cx - 5 + balanco, cabeca_cy - 3, cx - 5 + balanco, cabeca_cy + 3, PELE, frame)
    retangulo(cx + 5 + balanco, cabeca_cy - 3, cx + 5 + balanco, cabeca_cy + 3, PELE, frame)

    # --- Cabelo (por cima da cabeça) ---
    retangulo(cx - 5 + balanco, cabeca_cy - 7, cx + 5 + balanco, cabeca_cy - 4, CABELO, frame)
    retangulo(cx - 6 + balanco, cabeca_cy - 5, cx - 6 + balanco, cabeca_cy + 2, CABELO, frame)
    retangulo(cx + 6 + balanco, cabeca_cy - 5, cx + 6 + balanco, cabeca_cy + 2, CABELO, frame)
    # franja
    retangulo(cx - 4 + balanco, cabeca_cy - 6, cx + 2 + balanco, cabeca_cy - 5, CABELO, frame)
    # luz no cabelo
    px(cx - 2 + balanco, cabeca_cy - 6, CABELO_LUZ, frame)
    px(cx - 1 + balanco, cabeca_cy - 6, CABELO_LUZ, frame)

    # --- Cabelo comprido atrás (cai pelos ombros) ---
    retangulo(cx - 6 + balanco, cabeca_cy + 2, cx - 4 + balanco, cabeca_cy + 8, CABELO, frame)
    retangulo(cx + 4 + balanco, cabeca_cy + 2, cx + 6 + balanco, cabeca_cy + 8, CABELO, frame)

    # --- Rosto: olho (um só, voltado pra direção) ---
    px(cx + 2 + balanco, cabeca_cy, OLHO, frame)
    px(cx + 3 + balanco, cabeca_cy, OLHO, frame)

    # --- Braços ---
    # braço esquerdo (mais escuro)
    for y in range(ombro_y + 1, cintura_y - 2):
        px(cx - 6 + balanco, y, VESTIDO_ESCURO, frame)
        px(cx - 7 + balanco, y, VESTIDO_ESCURO, frame)
    # braço direito (mais claro, com mão dourada)
    for y in range(ombro_y + 1, cintura_y - 2):
        px(cx + 6 + balanco, y, VESTIDO, frame)
        px(cx + 7 + balanco, y, VESTIDO, frame)
    # mão direita
    px(cx + 7 + balanco, cintura_y - 2, DOURADO, frame)
    px(cx + 8 + balanco, cintura_y - 2, DOURADO, frame)


# --- Gera os 6 frames ---
poses = ["idle", "passo_esq", "passo_dir", "levitar_1", "levitar_2", "pousar"]
for i, pose in enumerate(poses):
    desenhar_personagem_base(i, pose)

# Salva
pygame.image.save(folha, "personagem.png")
print(f"Sprite salvo: personagem.png ({FOLHA_W}x{FOLHA_H} px, {NUM_FRAMES} frames)")
pygame.quit()