import random
import sys
import time

import pygame
from PIL import Image

pygame.init()

# --- Configurações da Janela ---
LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Runner Infinite - Muse Dash Edition")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Leitor de GIFs via PIL ---
def carregar_gif(caminho_arquivo, escala=1.0):
    """Carrega todos os frames de um GIF da pasta images/ e os converte para Superfícies do Pygame."""
    try:
        pil_img = Image.open(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao carregar {caminho_arquivo}: {e}")
        # Cria uma superfície rosa de fallback se a imagem falhar
        surf = pygame.Surface((100, 100))
        surf.fill((255, 105, 180))
        return [surf]

    frames = []
    try:
        while True:
            # Converte o frame atual do GIF para RGBA
            frame_rgba = pil_img.convert("RGBA")
            largura, altura = frame_rgba.size
            dados = frame_rgba.tobytes()
            
            # Converte bytes para Superfície do Pygame
            surf = pygame.image.fromstring(dados, (largura, altura), "RGBA")
            
            if escala != 1.0:
                novo_w = int(largura * escala)
                novo_h = int(altura * escala)
                surf = pygame.transform.scale(surf, (novo_w, novo_h))
                
            frames.append(surf)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass  # Fim dos frames do GIF
    
    return frames


class AnimaçãoGIF:
    """Classe para gerenciar a reprodução e temporização dos frames do GIF."""
    def __init__(self, frames, fps=12):
        self.frames = frames
        self.fps = fps
        self.frame_atual = 0
        self.tempo_frame = 1.0 / fps
        self.acumulador = 0.0

    def atualizar(self, dt):
        if len(self.frames) <= 1:
            return
        self.acumulador += dt
        if self.acumulador >= self.tempo_frame:
            self.acumulador -= self.tempo_frame
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)

    def obter_frame(self):
        return self.frames[self.frame_atual]


# --- Carregamento dos GIFs na pasta images/ ---
#[cite: 5, 6, 7, 8, 9]
GIFS = {
    "INICIAL": AnimaçãoGIF(carregar_gif("images/muse-dash-buro.jpg", escala=0.6), fps=10),      # Tela de Abertura[cite: 5]
    "ANDANDO_1": AnimaçãoGIF(carregar_gif("images/muse-dash-buro001.jpg", escala=0.5), fps=12),  # 0 a 5s de corrida[cite: 7]
    "ANDANDO_2": AnimaçãoGIF(carregar_gif("images/muse-dash-buro002.jpg", escala=0.5), fps=12),  # 5s+ de corrida contínua[cite: 8]
    "PULO": AnimaçãoGIF(carregar_gif("images/muse-dash-buro003.jpg", escala=0.5), fps=12),       # Foice / Ação no ar[cite: 6]
    "MORTE": AnimaçãoGIF(carregar_gif("images/muse-dash-marija.jpg", escala=0.5), fps=10),      # Fantasma
    "VITORIA": AnimaçãoGIF(carregar_gif("images/muse-dash-buro004.jpg", escala=0.5), fps=10),    # Celebração[cite: 9]
}

# --- Fontes e Cores ---
FONTE_TITULO = pygame.font.SysFont("arial", 28, bold=True)
FONTE_SUB = pygame.font.SysFont("arial", 18)

COR_FUNDO = (25, 20, 35)
COR_CHAO = (180, 80, 120)
COR_TEXTO = (255, 240, 250)
COR_OBSTACULO = (220, 50, 90)

# --- Variáveis de Física do Runner ---
CHAO_Y = ALTURA - 80
GRAVIDADE = 1200.0
FORCA_PULO = -500.0

# --- Estado Inicial do Jogo ---
estado_jogo = "TELA_INICIAL"  # "TELA_INICIAL", "JOGANDO", "MORTO", "MENU_REINICIAR"
tempo_corrida = 0.0
tempo_morte = 0.0

# Jogador
pos_x, pos_y = 120, CHAO_Y
vel_y = 0.0
no_chao = True

# Obstáculos
obstaculos = []
tempo_spawn = 0.0
VELOCIDADE_CENARIO = 350.0

def resetar_jogo():
    global pos_x, pos_y, vel_y, no_chao, tempo_corrida, tempo_morte, obstaculos, estado_jogo
    pos_x, pos_y = 120, CHAO_Y
    vel_y = 0.0
    no_chao = True
    tempo_corrida = 0.0
    tempo_morte = 0.0
    obstaculos.clear()
    estado_jogo = "JOGANDO"

# --- Loop Principal ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0

    # Processamento de Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if estado_jogo == "TELA_INICIAL":
                resetar_jogo()
            elif estado_jogo == "JOGANDO" and no_chao:
                vel_y = FORCA_PULO
                no_chao = False
            elif estado_jogo == "MENU_REINICIAR":
                resetar_jogo()

    # --- Atualização do Estado do Jogo ---
    if estado_jogo == "TELA_INICIAL":
        GIFS["INICIAL"].atualizar(dt)

    elif estado_jogo == "JOGANDO":
        tempo_corrida += dt

        # Física do Pulo
        vel_y += GRAVIDADE * dt
        pos_y += vel_y * dt

        if pos_y >= CHAO_Y:
            pos_y = CHAO_Y
            vel_y = 0.0
            no_chao = True

        # Gerenciamento de Obstáculos
        tempo_spawn += dt
        if tempo_spawn >= random.uniform(1.5, 2.5):
            tempo_spawn = 0.0
            obstaculos.append(pygame.Rect(LARGURA + 20, CHAO_Y - 40, 30, 40))

        # Movimento dos Obstáculos e Colisão
        rect_jogador = pygame.Rect(pos_x - 30, pos_y - 60, 60, 60)
        for obs in obstaculos[:]:
            obs.x -= int(VELOCIDADE_CENARIO * dt)
            if obs.x < -50:
                obstaculos.remove(obs)

            # Colisão detectada: entra no estado de morte
            if rect_jogador.colliderect(obs):
                estado_jogo = "MORTO"
                tempo_morte = 0.0

        # Seleção do GIF ativo com base na mecânica
        if not no_chao:
            anim_ativa = GIFS["PULO"][cite: 6]
        elif tempo_corrida > 5.0:
            anim_ativa = GIFS["ANDANDO_2"][cite: 8]
        else:
            anim_ativa = GIFS["ANDANDO_1"][cite: 7]

        anim_ativa.atualizar(dt)

    elif estado_jogo == "MORTO":
        tempo_morte += dt
        GIFS["MORTE"].atualizar(dt)

        # Após 10 segundos na forma de fantasma, libera a opção de reiniciar
        if tempo_morte >= 10.0:
            estado_jogo = "MENU_REINICIAR"

    # --- Renderização na Tela ---
    TELA.fill(COR_FUNDO)

    if estado_jogo == "TELA_INICIAL":
        frame = GIFS["INICIAL"].obter_frame()
        rect = frame.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
        TELA.blit(frame, rect)

        txt = FONTE_TITULO.render("Pressione qualquer tecla ou clique para iniciar", True, COR_TEXTO)
        TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, ALTURA - 60)))

    elif estado_jogo in ("JOGANDO", "MORTO", "MENU_REINICIAR"):
        # Desenha o Chão
        pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y, LARGURA, ALTURA - CHAO_Y))

        # Desenha Obstáculos
        for obs in obstaculos:
            pygame.draw.rect(TELA, COR_OBSTACULO, obs, border_radius=6)

        # Escolhe a imagem da personagem
        if estado_jogo == "MORTO" or estado_jogo == "MENU_REINICIAR":
            frame = GIFS["MORTE"].obter_frame()
        elif not no_chao:
            frame = GIFS["PULO"].obter_frame()[cite: 6]
        elif tempo_corrida > 5.0:
            frame = GIFS["ANDANDO_2"].obter_frame()[cite: 8]
        else:
            frame = GIFS["ANDANDO_1"].obter_frame()[cite: 7]

        rect = frame.get_rect(midbottom=(int(pos_x), int(pos_y)))
        TELA.blit(frame, rect)

        # Exibe cronômetro e instrução de reinício
        if estado_jogo == "MORTO":
            tempo_restante = max(0, int(10 - tempo_morte))
            txt = FONTE_SUB.render(f"Aguarde... {tempo_restante}s", True, COR_TEXTO)
            TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, 80)))

        elif estado_jogo == "MENU_REINICIAR":
            txt = FONTE_TITULO.render("Pressione qualquer tecla para Reiniciar", True, COR_TEXTO)
            TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, 80)))

    pygame.display.flip()