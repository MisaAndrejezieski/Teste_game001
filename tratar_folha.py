"""
Script para tratar folhas de sprites com fundo xadrez/colorido.
Remove as cores de fundo (azul e branco) e exporta a animação para o jogo.

Uso: python tratar_folha.py <sua_imagem.jpg/png>
"""
import os
import sys
from PIL import Image


def tratar_imagem(caminho_entrada, tolerancia_brancos=220, tolerancia_azuis=180):
    if not os.path.exists(caminho_entrada):
        print(f"❌ Ficheiro não encontrado: {caminho_entrada}")
        return

    print(f"🔄 Processando {caminho_entrada}...")
    img = Image.open(caminho_entrada).convert("RGBA")
    largura, altura = img.size
    dados = img.getdata()

    novos_dados = []
    
    # Percorre cada pixel e verifica se é fundo azul ou branco/cinza claro
    for r, g, b, a in dados:
        # Padrão Fundo Branco / Cinza claro do xadrez
        eh_branco = (r >= tolerancia_brancos and g >= tolerancia_brancos and b >= tolerancia_brancos)
        
        # Padrão Fundo Azul Cyan do xadrez (G e B bem mais altos que o R)
        eh_azul = (g >= tolerancia_azuis and b >= tolerancia_azuis and r < 120)

        if eh_branco or eh_azul:
            # Torna o pixel completamente transparente
            novos_dados.append((0, 0, 0, 0))
        else:
            novos_dados.append((r, g, b, a))

    img.putdata(novos_dados)

    # Salva a versão tratada com fundo transparente
    saida = "personagem.png"
    img.save(saida, "PNG")
    print(f"✅ Sucesso! Imagem sem fundo salva como '{saida}' ({largura}x{altura}px).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tratar_folha.py <nome_da_imagem>")
        print("Exemplo: python tratar_folha.py sprites001.jpg")
    else:
        tratar_imagem(sys.argv[1])