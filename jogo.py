import random
import sys

import pygame
from PIL import Image

pygame.init()

# --- Configurações da Janela ---
LARGURA, ALTURA = 960, 540
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Runner Infinite - Muse Dash Edition")
RELOGIO = pygame.time.Clock()
FPS = 60

# --- Otimização: Carregador e Otimizador de GIFs ---
def carregar_gif_otimizado(caminho_arquivo, escala=1.0, inverter_x=False):
    """Carrega o GIF, escala e converte para o formato nativo da GPU/PyGame uma única vez."""
    try:
        pil_img = Image.open(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao carregar {caminho_arquivo}: {e}")
        surf = pygame.Surface((50, 50))
        surf.fill((255, 105, 180))
        return [surf.convert_alpha()]

    frames = []
    try:
        while True:
            frame_rgba = pil_img.convert("RGBA")
            largura, altura = frame_rgba.size
            dados = frame_rgba.tobytes()
            
            # Converte para PyGame Surface
            surf = pygame.image.fromstring(dados, (largura, altura), "RGBA")
            
            if inverter_x:
                surf = pygame.transform.flip(surf, True, False)

            if escala != 1.0:
                novo_w = int(largura * escala)
                novo_h = int(altura * escala)
                surf = pygame.transform.scale(surf, (novo_w, novo_h))
            
            # convert_alpha() crucial para performance fluida no PyGame
            frames.append(surf.convert_alpha())
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    
    return frames


class AnimacaoGIF:
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


# --- Carregamento Pré-Otimizado das Animações ---
print("Otimizando e carregando sprites na memória...")

GIFS = {
    "INICIAL": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-buro.gif", escala=0.6), fps=10),
    "ANDANDO_1": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-buro001.gif", escala=0.5), fps=14),
    "ANDANDO_2": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-buro002.gif", escala=0.5), fps=14),
    "PULO": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-buro008.gif", escala=0.5), fps=14),
    "TROPECO": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-buro007.gif", escala=0.5), fps=10),
    "MORTE": AnimacaoGIF(carregar_gif_otimizado("images/muse-dash-marij a.gif", escala=0.5), fps=10),
}

ANIMS_INIMIGA = {
    "CORRENDO": carregar_gif_otimizado("images/inim001.gif", escala=0.22, inverter_x=True),
    "PASSOU": carregar_gif_otimizado("images/inim002.gif", escala=0.22, inverter_x=True),
    "IMPACTO": carregar_gif_otimizado("images/inim003.gif", escala=0.22, inverter_x=True),
}

# --- Fontes e Cores ---
FONTE_TITULO = pygame.font.SysFont("arial", 28, bold=True)
FONTE_SUB = pygame.font.SysFont("arial", 18)

COR_FUNDO = (25, 20, 35)
COR_CHAO = (180, 80, 120)
COR_TEXTO = (255, 240, 250)

# --- Física e Configurações do Jogo ---
CHAO_Y = ALTURA - 80
GRAVIDADE = 1300.0
FORCA_PULO = -420.0

class Inimiga:
    def __init__(self, x, y):
        self.anim_correndo = AnimacaoGIF(ANIMS_INIMIGA["CORRENDO"], fps=12)
        self.anim_passou = AnimacaoGIF(ANIMS_INIMIGA["PASSOU"], fps=12)
        self.anim_impacto = AnimacaoGIF(ANIMS_INIMIGA["IMPACTO"], fps=12)
        
        self.rect = pygame.Rect(x, y - 55, 40, 55)
        self.esbarrou = False

    def atualizar(self, dt, velocidade, pos_x_jogador):
        self.rect.x -= int(velocidade * dt)
        
        if self.esbarrou:
            self.anim_impacto.atualizar(dt)
        elif self.rect.right < pos_x_jogador:
            self.anim_passou.atualizar(dt)
        else:
            self.anim_correndo.atualizar(dt)

    def desenhar(self, tela, pos_x_jogador):
        if self.esbarrou:
            frame = self.anim_impacto.obter_frame()
        elif self.rect.right < pos_x_jogador:
            frame = self.anim_passou.obter_frame()
        else:
            frame = self.anim_correndo.obter_frame()
            
        rect_img = frame.get_rect(midbottom=self.rect.midbottom)
        tela.blit(frame, rect_img)


# --- Estado do Jogo ---
estado_jogo = "TELA_INICIAL"
tempo_corrida = 0.0
tempo_morte = 0.0
tempo_tropeco = 0.0
esbarroes_sofridos = 0

pos_x, pos_y = 120, CHAO_Y
vel_y = 0.0
no_chao = True

inimigas = []
tempo_spawn = 0.0
VELOCIDADE_CENARIO = 500.0

def resetar_jogo():
    global pos_x, pos_y, vel_y, no_chao, tempo_corrida, tempo_morte, tempo_tropeco, esbarroes_sofridos, inimigas, estado_jogo
    pos_x, pos_y = 120, CHAO_Y
    vel_y = 0.0
    no_chao = True
    tempo_corrida = 0.0
    tempo_morte = 0.0
    tempo_tropeco = 0.0
    esbarroes_sofridos = 0
    inimigas.clear()
    estado_jogo = "JOGANDO"

# --- Loop Principal ---
while True:
    dt = RELOGIO.tick(FPS) / 1000.0

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

    if estado_jogo == "TELA_INICIAL":
        GIFS["INICIAL"].atualizar(dt)

    elif estado_jogo == "JOGANDO":
        tempo_corrida += dt

        if tempo_tropeco > 0:
            tempo_tropeco -= dt

        vel_y += GRAVIDADE * dt
        pos_y += vel_y * dt

        if pos_y >= CHAO_Y:
            pos_y = CHAO_Y
            vel_y = 0.0
            no_chao = True

        tempo_spawn += dt
        if tempo_spawn >= random.uniform(1.2, 2.2):
            tempo_spawn = 0.0
            inimigas.append(Inimiga(LARGURA + 20, CHAO_Y))

        rect_jogador = pygame.Rect(pos_x - 20, pos_y - 60, 40, 60)

        for ini in inimigas[:]:
            ini.atualizar(dt, VELOCIDADE_CENARIO, pos_x)

            if ini.rect.right < 0:
                inimigas.remove(ini)
                continue

            if not ini.esbarrou and rect_jogador.colliderect(ini.rect):
                intersecao = rect_jogador.clip(ini.rect)
                ini.esbarrou = True
                
                if intersecao.width < 18 and rect_jogador.centerx < ini.rect.centerx:
                    esbarroes_sofridos += 1
                    if esbarroes_sofridos >= 2:
                        estado_jogo = "MORTO"
                        tempo_morte = 0.0
                    else:
                        tempo_tropeco = 1.0
                else:
                    estado_jogo = "MORTO"
                    tempo_morte = 0.0

        if tempo_tropeco > 0:
            anim_ativa = GIFS["TROPECO"]
        elif not no_chao:
            anim_ativa = GIFS["PULO"]
        elif tempo_corrida > 5.0:
            anim_ativa = GIFS["ANDANDO_2"]
        else:
            anim_ativa = GIFS["ANDANDO_1"]

        anim_ativa.atualizar(dt)

    elif estado_jogo == "MORTO":
        tempo_morte += dt
        GIFS["MORTE"].atualizar(dt)

        if tempo_morte >= 10.0:
            estado_jogo = "MENU_REINICIAR"

    # --- Renderização ---
    TELA.fill(COR_FUNDO)

    if estado_jogo == "TELA_INICIAL":
        frame = GIFS["INICIAL"].obter_frame()
        rect = frame.get_rect(center=(LARGURA // 2, ALTURA // 2 - 30))
        TELA.blit(frame, rect)

        txt = FONTE_TITULO.render("Pressione qualquer tecla ou clique para iniciar", True, COR_TEXTO)
        TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, ALTURA - 60)))

    elif estado_jogo in ("JOGANDO", "MORTO", "MENU_REINICIAR"):
        pygame.draw.rect(TELA, COR_CHAO, (0, CHAO_Y, LARGURA, ALTURA - CHAO_Y))

        for ini in inimigas:
            ini.desenhar(TELA, pos_x)

        if estado_jogo in ("MORTO", "MENU_REINICIAR"):
            frame = GIFS["MORTE"].obter_frame()
        elif tempo_tropeco > 0:
            frame = GIFS["TROPECO"].obter_frame()
        elif not no_chao:
            frame = GIFS["PULO"].obter_frame()
        elif tempo_corrida > 5.0:
            frame = GIFS["ANDANDO_2"].obter_frame()
        else:
            frame = GIFS["ANDANDO_1"].obter_frame()

        rect = frame.get_rect(midbottom=(int(pos_x), int(pos_y)))
        TELA.blit(frame, rect)

        if estado_jogo == "JOGANDO":
            txt_vidas = FONTE_SUB.render(f"Esbarrões: {esbarroes_sofridos}/2", True, COR_TEXTO)
            TELA.blit(txt_vidas, (20, 20))

        elif estado_jogo == "MORTO":
            tempo_restante = max(0, int(10 - tempo_morte))
            txt = FONTE_SUB.render(f"Aguarde... {tempo_restante}s", True, COR_TEXTO)
            TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, 80)))

        elif estado_jogo == "MENU_REINICIAR":
            txt = FONTE_TITULO.render("Pressione qualquer tecla para Reiniciar", True, COR_TEXTO)
            TELA.blit(txt, txt.get_rect(center=(LARGURA // 2, 80)))

    pygame.display.flip()