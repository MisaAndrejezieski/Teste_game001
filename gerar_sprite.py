"""
Gera a folha de sprites (256x64) para a personagem feminina com vestido esvoaçante.
4 Frames: 0=Idle, 1=Passo 1, 2=Passo 2, 3=Levitar/Esvoaçar
"""
import math

import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 64
NUM_FRAMES = 4
LARGURA_FOLHA = SPRITE_W * NUM_FRAMES

# Cores da Personagem
PELE = (245, 215, 195)
CABELO = (210, 110, 45)       # Ruivo/Acobreado
CABELO_SOMBRA = (160, 70, 25)
VESTIDO = (130, 80, 210)      # Púrpura/Mágico
VESTIDO_LUZ = (170, 120, 240)
VESTIDO_SOMBRA = (80, 45, 140)
OLHOS = (40, 30, 60)

folha = pygame.Surface((LARGURA_FOLHA, SPRITE_H), pygame.SRCALPHA)

def desenhar_personagem(frame_idx):
    offset_x = frame_idx * SPRITE_W
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    
    # Parâmetros de animação por frame
    offset_y = 0
    t = frame_idx
    
    if frame_idx == 3: # Levitar
        offset_y = -3
    
    cx = 32
    cy = 28 + offset_y

    # --- 1. CABELO DE TRÁS (Esvoaçante) ---
    for i in range(12):
        wave = math.sin(i * 0.4 + t * 1.5) * (3 if frame_idx == 3 else 1.5)
        raio = 6 - (i // 2)
        if raio > 1:
            pygame.draw.circle(surf, CABELO_SOMBRA, (int(cx - 3 + wave), int(cy - 2 + i * 1.5)), raio)

    # --- 2. CORPO E CABEÇA ---
    # Cabeça
    pygame.draw.circle(surf, PELE, (cx, cy), 6)
    # Olhos
    pygame.draw.set_at((surf, cx + 3, cy - 1), OLHOS)
    pygame.draw.set_at((surf, cx + 3, cy + 1), OLHOS)

    # --- 3. CABELO DA FRENTE ---
    pygame.draw.circle(surf, CABELO, (cx - 1, cy - 2), 6)
    pygame.draw.circle(surf, CABELO, (cx - 3, cy + 1), 3)

    # --- 4. VESTIDO (Esvoaçante com Polígonos e Ondas) ---
    # Tronco
    pygame.draw.polygon(surf, VESTIDO, [(cx - 3, cy + 5), (cx + 3, cy + 5), (cx + 4, cy + 14), (cx - 4, cy + 14)])
    
    # Saia Esvoaçante (Geometria dinâmica de acordo com o estado)
    largura_saia = 10 if frame_idx < 3 else 16
    desvio_vento = -4 if frame_idx == 3 else (-2 if frame_idx in (1, 2) else 0)
    
    p1 = (cx - 4, cy + 13)
    p2 = (cx + 4, cy + 13)
    p3 = (cx + largura_saia + desvio_vento, cy + 28)
    p4 = (cx - largura_saia + desvio_vento - 2, cy + 28)
    
    pygame.draw.polygon(surf, VESTIDO, [p1, p2, p3, p4])
    
    # Camadas/Dobras de Luz no Vestido
    p_luz1 = (cx - 1, cy + 13)
    p_luz2 = (cx + 3, cy + 13)
    p_luz3 = (cx + (largura_saia // 2) + desvio_vento, cy + 28)
    pygame.draw.polygon(surf, VESTIDO_LUZ, [p_luz1, p_luz2, p_luz3])
    
    # Sombra da Bainha
    pygame.draw.line(surf, VESTIDO_SOMBRA, p4, p3, 2)

    # --- 5. PERNAS / PASSOS ---
    y_pernas = cy + 28
    if frame_idx == 0: # Idle
        pygame.draw.line(surf, PELE, (cx - 2, y_pernas), (cx - 2, y_pernas + 6), 2)
        pygame.draw.line(surf, PELE, (cx + 2, y_pernas), (cx + 2, y_pernas + 6), 2)
    elif frame_idx == 1: # Passo 1
        pygame.draw.line(surf, PELE, (cx - 4, y_pernas), (cx - 6, y_pernas + 6), 2)
        pygame.draw.line(surf, PELE, (cx + 2, y_pernas), (cx + 4, y_pernas + 5), 2)
    elif frame_idx == 2: # Passo 2
        pygame.draw.line(surf, PELE, (cx - 2, y_pernas), (cx - 3, y_pernas + 5), 2)
        pygame.draw.line(surf, PELE, (cx + 4, y_pernas), (cx + 6, y_pernas + 6), 2)
    elif frame_idx == 3: # Levitar (Pernas recolhidas suavemente)
        pygame.draw.line(surf, PELE, (cx - 3, y_pernas - 2), (cx - 5, y_pernas + 3), 2)
        pygame.draw.line(surf, PELE, (cx + 1, y_pernas - 2), (cx + 3, y_pernas + 4), 2)

    folha.blit(surf, (offset_x, 0))

for idx in range(NUM_FRAMES):
    desenhar_personagem(idx)

pygame.image.save(folha, "personagem.png")
print("✅ Novo spritesheet 'personagem.png' (Feminina/Esvoaçante) gerado com sucesso!")