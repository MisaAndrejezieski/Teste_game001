"""
Remove o fundo branco de uma imagem e salva como personagem.png
SEM reduzir o tamanho. Preserva os pixels originais.

Uso: python pixelizar.py referencia.jpg
"""
import os
import sys

from PIL import Image


def remover_fundo_branco(img, tolerancia=235):
    img = img.convert("RGBA")
    dados = list(img.getdata())
    novos = []
    for r, g, b, a in dados:
        if r >= tolerancia and g >= tolerancia and b >= tolerancia:
            novos.append((r, g, b, 0))
        else:
            novos.append((r, g, b, a))
    img.putdata(novos)
    return img


def main():
    if len(sys.argv) < 2:
        print("Uso: python pixelizar.py <entrada>")
        print("Exemplo: python pixelizar.py referencia.jpg")
        sys.exit(1)

    entrada = sys.argv[1]
    if not os.path.exists(entrada):
        print(f"[erro] Arquivo nao encontrado: {entrada}")
        sys.exit(1)

    saida = "personagem.png"
    print(f"Processando {entrada} -> {saida} (tamanho original)...")

    img = Image.open(entrada)
    print(f"Tamanho original: {img.size[0]}x{img.size[1]}")

    img = remover_fundo_branco(img)
    img.save(saida)

    print(f"OK: {saida} gerado ({img.size[0]}x{img.size[1]}) com fundo transparente")


if __name__ == "__main__":
    main()