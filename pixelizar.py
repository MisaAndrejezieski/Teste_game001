"""
Pega uma imagem de referência (PNG ou JPG) e pixeliza no tamanho especificado.
Remove o fundo branco e gera personagem.png com transparência.

Uso: python pixelizar.py <entrada> <largura_saida> <altura_saida>
Exemplo: python pixelizar.py referencia.jpg 96 128
"""
import os
import sys

from PIL import Image

try:
    import pixeloe
    TEM_PIXELOE = True
except ImportError:
    TEM_PIXELOE = False
    print("[aviso] pixeloe não instalado. Usando fallback com Pillow.")


def remover_fundo_branco(img, tolerancia=240):
    """
    Remove fundo branco (ou quase branco) de uma imagem.
    Converte pixels claros em transparentes.
    tolerancia: 0-255. Pixels com R, G e B acima desse valor viram transparentes.
    """
    img = img.convert("RGBA")
    dados = img.getdata()
    novos_dados = []
    for r, g, b, a in dados:
        if r >= tolerancia and g >= tolerancia and b >= tolerancia:
            novos_dados.append((r, g, b, 0))  # transparente
        else:
            novos_dados.append((r, g, b, a))
    img.putdata(novos_dados)
    return img


def pixelizar_com_pixeloe(entrada, largura, altura):
    img = Image.open(entrada).convert("RGBA")
    img = remover_fundo_branco(img)
    resultado = pixeloe.pixelize(
        img,
        target_size=(largura, altura),
        thickness=2,
        mode="contrast",
    )
    return resultado


def pixelizar_com_pillow(entrada, largura, altura):
    """
    Fallback: reduz para o tamanho alvo e depois reaumenta com NEAREST
    para ficar pixelado de verdade (blocos duros).
    """
    img = Image.open(entrada).convert("RGBA")
    img = remover_fundo_branco(img)
    # reduz para o tamanho alvo
    pequena = img.resize((largura, altura), Image.LANCZOS)
    # "quantiza" as cores pra dar aspecto de pixel art (paleta reduzida)
    pequena = pequena.quantize(colors=32, method=Image.MEDIANCUT).convert("RGBA")
    # reaplica transparência (a quantize pode ter quebrado o alpha)
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
        print(f"[erro] Arquivo não encontrado: {entrada}")
        sys.exit(1)

    saida = "personagem.png"
    print(f"Pixelizando {entrada} -> {saida} ({largura}x{altura})...")

    if TEM_PIXELOE:
        resultado = pixelizar_com_pixeloe(entrada, largura, altura)
    else:
        resultado = pixelizar_com_pillow(entrada, largura, altura)

    resultado.save(saida)
    print(f"OK: {saida} gerado ({resultado.size[0]}x{resultado.size[1]})")


if __name__ == "__main__":
    main()