# Nora Runner (Pygame)

Runtime desktop separado do editor web. Usa os mesmos arquivos da pasta `images/`.

## Preparar

No PowerShell, na raiz do projeto:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Executar

```powershell
.venv\Scripts\python.exe pygame_runner\main.py
```

## Controles

- `Space` ou `Seta para cima`: pular
- `R`: reiniciar depois do game over
- `Esc`: sair

## Regras

- Nora fica fixa no lado esquerdo.
- O cenário rola em paralaxe.
- As inimigas entram pela direita e saem pela esquerda.
- Cada contato tira uma vida.
- Após três contatos, Nora morre.
- A inimiga não morre; pode mostrar a ação de dano e continua atravessando a tela.
