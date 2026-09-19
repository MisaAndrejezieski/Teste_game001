"""
Pega uma imagem de referência (PNG ou JPG) e pixeliza no tamanho especificado.
Remove o fundo branco e gera personagem.png com transparência.

Uso: python pixelizar.py <entrada> <largura_saida> <altura_saida>
Exemplo: python pixelizar.py referencia.jpg 96 128
"""
import os
import sys

import numpy as np
from PIL import Image

# Tenta importar a função do pixeloe (API nova)
try:
    from pixeloe.pixelize import pixelize as pixeloe_pixelize
    TEM_PIXELOE = True
except Exception as e:
    TEM_PIXELOE = False
    print(f"[aviso] pixeloe nao disponivel ({e}). Usando fallback com Pillow.")


def remover_fundo_branco(img, tolerancia=240):
    """
    Remove fundo branco (ou quase branco) de uma imagem.
    tolerancia: 0-255. Pixels com R, G e B acima desse valor viram transparentes.
    """
    img = img.convert("RGBA")
    dados = list(img.getdata())
    novos_dados = []
    for r, g, b, a in dados:
        if r >= tolerancia and g >= tolerancia and b >= tolerancia:
            novos_dados.append((r, g, b, 0))
        else:
            novos_dados.append((r, g, b, a))
    img.putdata(novos_dados)
    return img


def pixelizar_com_pixeloe(entrada, largura, altura):
    img = Image.open(entrada).convert("RGBA")
    img = remover_fundo_branco(img)

    # PixelOE trabalha com numpy array (estilo OpenCV, BGRA)
    img_np = np.array(img)

    resultado_np = pixeloe_pixelize(
        img_np,
        target_size=(largura, altura),
        patch_size=8,
        thickness=2,
        mode="contrast",
    )

    return Image.fromarray(resultado_np)


def pixelizar_com_pillow(entrada, largura, altura):
    """
    Fallback: reduz para o tamanho alvo, quantiza as cores
    (pra dar aspecto de pixel art) e reaplica transparência.
    """
    img = Image.open(entrada).convert("RGBA")
    img = remover_fundo_branco(img)

    # reduz para o tamanho alvo
    pequena = img.resize((largura, altura), Image.LANCZOS)

    # quantiza para 32 cores (aspecto de pixel art)
    pequena = pequena.quantize(colors=32, method=Image.MEDIANCUT).convert("RGBA")

    # reaplica transparência
    pequena = remover_fundo_branco(pequena)

    return pequena


def main():
    if len(sys.argv) < 4:
        print("Uso: python pixelizar.py <entrada> <largura> <altura>")
        print("Exemplo: python pixelizar.py referencia.jpg 96 128")
        sys.exit(1)

    entrada = sys.argv[1]
    largura = int(sys.argv[2])
    altura = int(sys.argv[3])

    if not os.path.exists(entrada):
        print(f"[erro] Arquivo nao encontrado: {entrada}")
        sys.exit(1)

    saida = "personagem.png"
    print(f"Pixelizando {entrada} -> {saida} ({largura}x{altura})...")

    if TEM_PIXELOE:
        try:
            resultado = pixelizar_com_pixeloe(entrada, largura, altura)
            print("[ok] usado: pixeloe")
        except Exception as e:
            print(f"[aviso] pixeloe falhou ({e}). Caindo no fallback Pillow.")
            resultado = pixelizar_com_pillow(entrada, largura, altura)
    else:
        resultado = pixelizar_com_pillow(entrada, largura, altura)
        print("[ok] usado: fallback Pillow")

    resultado.save(saida)
    print(f"OK: {saida} gerado ({resultado.size[0]}x{resultado.size[1]})")


if __name__ == "__main__":
    main()