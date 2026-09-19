"""
Pega uma imagem de referência e pixeliza no tamanho especificado.
Uso: python pixelizar.py <imagem_entrada> <largura_saida> <altura_saida>
Exemplo: python pixelizar.py referencia.png 96 128
"""
import os
import sys

from PIL import Image

# Tenta importar pixeloe. Se não tiver, usa fallback com Pillow.
try:
    import pixeloe
    TEM_PIXELOE = True
except ImportError:
    TEM_PIXELOE = False
    print("[aviso] pixeloe não instalado. Usando fallback com Pillow (qualidade menor).")


def pixelizar_com_pixeloe(entrada, saida, largura, altura):
    """Usa o PixelOE para pixelizar preservando bordas."""
    img = Image.open(entrada).convert("RGBA")
    # pixeloe.pixelize retorna uma imagem pixelizada
    resultado = pixeloe.pixelize(
        img,
        target_size=(largura, altura),
        # parâmetros de qualidade
        thickness=2,       # espessura do contorno
        mode="contrast",   # modo: preserva contraste
    )
    resultado.save(saida)
    return resultado


def pixelizar_com_pillow(entrada, saida, largura, altura):
    """
    Fallback: reduz a imagem para o tamanho alvo e depois aumenta
    de volta com NEAREST (vizinho mais próximo) para ficar pixelado.
    """
    img = Image.open(entrada).convert("RGBA")
    # Primeiro passo: reduz para o tamanho alvo (isso mistura pixels)
    pequena = img.resize((largura, altura), Image.LANCZOS)
    # Segundo passo: reaumenta com NEAREST (fica pixelado, blocos duros)
    # Mas como o alvo JÁ é o tamanho final, salvamos direto
    pequena.save(saida)
    return pequena


def main():
    if len(sys.argv) < 4:
        print("Uso: python pixelizar.py <entrada> <largura> <altura>")
        print("Exemplo: python pixelizar.py referencia.png 96 128")
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
        resultado = pixelizar_com_pixeloe(entrada, saida, largura, altura)
    else:
        resultado = pixelizar_com_pillow(entrada, saida, largura, altura)

    print(f"OK: {saida} gerado ({resultado.size[0]}x{resultado.size[1]})")


if __name__ == "__main__":
    main()