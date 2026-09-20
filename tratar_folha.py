"""
Script de Tratamento de Folha de Sprites
Remove o fundo xadrez (azul e branco) e limpa resíduos de bordas.
Uso: python tratar_folha.py sprites001.jpg
"""
import os
import sys

from PIL import Image


def tratar_folha(caminho_entrada):
    if not os.path.exists(caminho_entrada):
        print(f"❌ Ficheiro não encontrado: {caminho_entrada}")
        return

    print(f"🔄 Processando {caminho_entrada}...")
    img = Image.open(caminho_entrada).convert("RGBA")
    largura, altura = img.size
    pix = img.load()

    for y in range(altura):
        for x in range(largura):
            r, g, b, a = pix[x, y]
            
            # Fundo branco / cinza claro do xadrez
            eh_branco = (r >= 180 and g >= 180 and b >= 180)
            
            # Fundo azul / cyan do xadrez
            eh_azul = (g >= 140 and b >= 140 and r < 140)
            
            # Linhas de artefatos/bordas cinzentas claras
            eh_cinza_borda = (abs(r - g) < 15 and abs(g - b) < 15 and r > 160)

            if eh_branco or eh_azul or eh_cinza_borda:
                pix[x, y] = (0, 0, 0, 0)

    saida = "personagem.png"
    img.save(saida, "PNG")
    print(f"✅ 'personagem.png' salvo com sucesso e fundo transparente ({largura}x{altura}px)!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tratar_folha(sys.argv[1])
    else:
        print("Uso: python tratar_folha.py sprites001.jpg")