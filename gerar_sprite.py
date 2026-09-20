"""
Gera a folha de sprites (256x64) fiel à imagem de referência (andando.gif):
- Capuz Branco
- Máscara/Rosto Vermelho Vinho
- Gola Cinza
- Vestido Escuro
- Meias Vermelhas e Sapatos Escuros

4 Frames: 0=Idle, 1=Passo 1, 2=Passo 2, 3=Levitar
"""
import pygame

pygame.init()

SPRITE_W, SPRITE_H = 64, 64
NUM_FRAMES = 4
LARGURA_FOLHA = SPRITE_W * NUM_FRAMES

# --- Paleta Extraída da Imagem de Referência ---
COR_CAPUZ = (245, 245, 235)         # Branco/Creme
COR_CAPUZ_SOMBRA = (200, 200, 190)
COR_MASCARA = (150, 15, 20)          # Vermelho Vinho
COR_MASCARA_SOMBRA = (90, 5, 10)
COR_GOLA = (140, 145, 150)           # Cinza
COR_PELE = (255, 220, 175)           # Tom de pele nos braços/pernas
COR_VESTIDO = (20, 15, 30)           # Preto / Roxo muito escuro
COR_MEIA = (215, 20, 25)             # Vermelho Vivo
COR_SAPATO = (30, 10, 35)            # Escuro

folha = pygame.Surface((LARGURA_FOLHA, SPRITE_H), pygame.SRCALPHA)

def desenhar_pixel_rect(surf, cor, x, y, w, h):
    pygame.draw.rect(surf, cor, (int(x), int(y), int(w), int(h)))

def desenhar_frame(frame_idx):
    offset_x = frame_idx * SPRITE_W
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Posições base
    offset_y = -3 if frame_idx == 3 else 0
    cx = 32
    cy = 22 + offset_y

    # 1. CAPUZ (Atrás da cabeça)
    desenhar_pixel_rect(surf, COR_CAPUZ, cx - 8, cy - 10, 16, 16)
    desenhar_pixel_rect(surf, COR_CAPUZ, cx - 10, cy - 6, 4, 12)
    desenhar_pixel_rect(surf, COR_CAPUZ_SOMBRA, cx - 10, cy + 2, 6, 6)

    # 2. MÁSCARA / ROSTO (Vermelho Vinho)
    desenhar_pixel_rect(surf, COR_MASCARA, cx - 2, cy - 8, 11, 13)
    desenhar_pixel_rect(surf, COR_PELE, cx + 2, cy - 2, 4, 4)         # Parte visível do rosto
    surf.set_at((cx + 3, cy - 4), (10, 10, 10))                        # Olho escuro

    # 3. GOLA CINZA
    desenhar_pixel_rect(surf, COR_GOLA, cx - 8, cy + 5, 16, 4)

    # 4. BRAÇOS
    if frame_idx in (1, 2):
        # Braço em movimento de corrida/caminhada
        desenhar_pixel_rect(surf, COR_PELE, cx + 5, cy + 7, 6, 3)
        desenhar_pixel_rect(surf, COR_PELE, cx - 7, cy + 6, 4, 3)
    else:
        desenhar_pixel_rect(surf, COR_PELE, cx + 4, cy + 8, 4, 4)
        desenhar_pixel_rect(surf, COR_PELE, cx - 6, cy + 8, 4, 4)

    # 5. VESTIDO ESCURO
    desenhar_pixel_rect(surf, COR_VESTIDO, cx - 6, cy + 9, 13, 10)
    desenhar_pixel_rect(surf, COR_VESTIDO, cx - 8, cy + 17, 17, 4)   # Saia levemente aberta

    # 6. PERNAS, MEIAS VERMELHAS E SAPATOS
    y_pernas = cy + 21

    if frame_idx == 0:  # IDLE (Parada)
        # Perna Esquerda
        desenhar_pixel_rect(surf, COR_PELE, cx - 4, y_pernas, 3, 2)
        desenhar_pixel_rect(surf, COR_MEIA, cx - 4, y_pernas + 2, 3, 8)
        desenhar_pixel_rect(surf, COR_SAPATO, cx - 5, y_pernas + 10, 5, 3)
        # Perna Direita
        desenhar_pixel_rect(surf, COR_PELE, cx + 2, y_pernas, 3, 2)
        desenhar_pixel_rect(surf, COR_MEIA, cx + 2, y_pernas + 2, 3, 8)
        desenhar_pixel_rect(surf, COR_SAPATO, cx + 2, y_pernas + 10, 5, 3)

    elif frame_idx == 1:  # PASSO 1 (Passada aberta)
        # Perna Traseira (Esticada para trás)
        desenhar_pixel_rect(surf, COR_MEIA, cx - 11, y_pernas + 1, 8, 3)
        desenhar_pixel_rect(surf, COR_SAPATO, cx - 14, y_pernas + 2, 4, 4)
        # Perna Dianteira (Frentista)
        desenhar_pixel_rect(surf, COR_PELE, cx + 1, y_pernas, 3, 3)
        desenhar_pixel_rect(surf, COR_MEIA, cx + 3, y_pernas + 3, 4, 7)
        desenhar_pixel_rect(surf, COR_SAPATO, cx + 5, y_pernas + 9, 5, 3)

    elif frame_idx == 2:  # PASSO 2 (Inversão dos pés)
        # Perna Traseira
        desenhar_pixel_rect(surf, COR_PELE, cx - 3, y_pernas, 3, 2)
        desenhar_pixel_rect(surf, COR_MEIA, cx - 2, y_pernas + 2, 4, 7)
        desenhar_pixel_rect(surf, COR_SAPATO, cx - 1, y_pernas + 9, 5, 3)
        # Perna Dianteira
        desenhar_pixel_rect(surf, COR_MEIA, cx + 2, y_pernas + 1, 7, 3)
        desenhar_pixel_rect(surf, COR_SAPATO, cx + 8, y_pernas + 2, 4, 4)

    elif frame_idx == 3:  # LEVITAR / AR
        # Pernas ligeiramente dobradas para trás ao flutuar
        desenhar_pixel_rect(surf, COR_PELE, cx - 4, y_pernas - 1, 3, 2)
        desenhar_pixel_rect(surf, COR_MEIA, cx - 5, y_pernas + 1, 4, 7)
        desenhar_pixel_rect(surf, COR_SAPATO, cx - 6, y_pernas + 8, 4, 3)

        desenhar_pixel_rect(surf, COR_PELE, cx + 1, y_pernas - 1, 3, 2)
        desenhar_pixel_rect(surf, COR_MEIA, cx + 2, y_pernas + 1, 4, 6)
        desenhar_pixel_rect(surf, COR_SAPATO, cx + 3, y_pernas + 7, 4, 3)

    folha.blit(surf, (offset_x, 0))

for idx in range(NUM_FRAMES):
    desenhar_frame(idx)

pygame.image.save(folha, "personagem.png")
print("✅ Spritesheet 'personagem.png' gerado com as cores e detalhes da sua referência!")