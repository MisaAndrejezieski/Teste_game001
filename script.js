const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const LARGURA = 960;
const ALTURA = 540;
const CHAO_Y = ALTURA - 80;

// --- Configurações de Física ---
const GRAVIDADE = 1000;
const FORCA_PULO = -480;
const VELOCIDADE_CENARIO = 280;

// --- Dicionário de Animações ---
const animacoes = {};
const caminhos = {
  buroInicial: "images/muse-dash-buro.gif",
  buroAndando1: "images/muse-dash-buro001.gif",
  buroAndando2: "images/muse-dash-buro002.gif",
  buroPulo: "images/muse-dash-buro008.gif",
  buroTropeco: "images/muse-dash-buro007.gif",
  buroMorte: "images/muse-dash-marij a.gif",
  inimigaCorrendo: "images/inim001.gif",
  inimigaPassou: "images/inim002.gif",
  inimigaImpacto: "images/inim003.gif"
};

// Gerenciador de Animação para Canvas
class AnimadorGif {
  constructor(caminho) {
    this.canvasFrame = document.createElement("canvas");
    this.ctxFrame = this.canvasFrame.getContext("2d");
    this.carregado = false;

    if (window.gifler) {
      gifler(caminho).get((anim) => {
        this.canvasFrame.width = anim.width;
        this.canvasFrame.height = anim.height;
        anim.animateIn(this.canvasFrame);
        this.carregado = true;
      });
    }
  }

  obterCanvas() {
    return this.carregado ? this.canvasFrame : null;
  }
}

// Carrega todos os GIFs com animação
Object.keys(caminhos).forEach(chave => {
  animacoes[chave] = new AnimadorGif(caminhos[chave]);
});

// --- Estado do Jogo ---
let estadoJogo = "TELA_INICIAL";
let tempoCorrida = 0;
let tempoMorte = 0;
let tempoTropeco = 0;
let esbarroesSofridos = 0;

let posX = 120;
let posY = CHAO_Y;
let velY = 0;
let noChao = true;

let inimigas = [];
let tempoSpawn = 0;
let ultimoTempo = performance.now();

// --- Classe Inimiga ---
class Inimiga {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.largura = 35;
    this.altura = 50;
    this.esbarrou = false;
  }

  atualizar(dt) {
    this.x -= VELOCIDADE_CENARIO * dt;
  }

  desenhar(ctx, posXJogador) {
    let anim = animacoes.inimigaCorrendo;

    if (this.esbarrou) {
      anim = animacoes.inimigaImpacto;
    } else if (this.x + this.largura < posXJogador) {
      anim = animacoes.inimigaPassou;
    }

    const frameCanvas = anim.obterCanvas();
    if (!frameCanvas) return;

    ctx.save();
    ctx.translate(this.x + this.largura / 2, this.y);
    ctx.scale(-1, 1);
    
    const larguraImg = 65;
    const alturaImg = 65;
    
    ctx.drawImage(frameCanvas, -larguraImg / 2, -alturaImg, larguraImg, alturaImg);
    ctx.restore();
  }
}

// --- Controles ---
function acaoJogador() {
  if (estadoJogo === "TELA_INICIAL" || estadoJogo === "MENU_REINICIAR") {
    resetarJogo();
  } else if (estadoJogo === "JOGANDO" && noChao) {
    velY = FORCA_PULO;
    noChao = false;
  }
}

window.addEventListener("keydown", (e) => {
  if (e.code === "Space" || e.code === "ArrowUp") acaoJogador();
});
canvas.addEventListener("click", acaoJogador);

function resetarJogo() {
  posX = 120;
  posY = CHAO_Y;
  velY = 0;
  noChao = true;
  tempoCorrida = 0;
  tempoMorte = 0;
  tempoTropeco = 0;
  esbarroesSofridos = 0;
  inimigas = [];
  estadoJogo = "JOGANDO";
}

// --- Loop Principal ---
function gameLoop(tempoAtual) {
  const dt = Math.min((tempoAtual - ultimoTempo) / 1000, 0.1);
  ultimoTempo = tempoAtual;

  ctx.fillStyle = "#191423";
  ctx.fillRect(0, 0, LARGURA, ALTURA);

  if (estadoJogo === "TELA_INICIAL") {
    const frame = animacoes.buroInicial.obterCanvas();
    if (frame) {
      ctx.drawImage(frame, LARGURA / 2 - 100, ALTURA / 2 - 120, 200, 200);
    }
    
    ctx.fillStyle = "#fff0fa";
    ctx.font = "bold 24px Arial";
    ctx.textAlign = "center";
    ctx.fillText("Pressione ESPAÇO ou Clique para iniciar", LARGURA / 2, ALTURA - 60);

  } else if (estadoJogo === "JOGANDO" || estadoJogo === "MORTO" || estadoJogo === "MENU_REINICIAR") {
    
    if (estadoJogo === "JOGANDO") {
      tempoCorrida += dt;
      if (tempoTropeco > 0) tempoTropeco -= dt;

      velY += GRAVIDADE * dt;
      posY += velY * dt;

      if (posY >= CHAO_Y) {
        posY = CHAO_Y;
        velY = 0;
        noChao = true;
      }

      tempoSpawn += dt;
      if (tempoSpawn >= 1.8 + Math.random() * 1.2) {
        tempoSpawn = 0;
        inimigas.push(new Inimiga(LARGURA + 20, CHAO_Y));
      }

      const rectJogador = { x: posX - 15, y: posY - 55, largura: 30, altura: 55 };

      for (let i = inimigas.length - 1; i >= 0; i--) {
        let ini = inimigas[i];
        ini.atualizar(dt);

        if (ini.x < -60) {
          inimigas.splice(i, 1);
          continue;
        }

        if (!ini.esbarrou &&
            rectJogador.x < ini.x + ini.largura &&
            rectJogador.x + rectJogador.largura > ini.x &&
            rectJogador.y < ini.y &&
            rectJogador.y + rectJogador.altura > ini.y - ini.altura) {
          
          ini.esbarrou = true;
          esbarroesSofridos++;

          if (esbarroesSofridos >= 2) {
            estadoJogo = "MORTO";
            tempoMorte = 0;
          } else {
            tempoTropeco = 1.0;
          }
        }
      }
    } else if (estadoJogo === "MORTO") {
      tempoMorte += dt;
      if (tempoMorte >= 10.0) {
        estadoJogo = "MENU_REINICIAR";
      }
    }

    // Desenhar Chão
    ctx.fillStyle = "#b45078";
    ctx.fillRect(0, CHAO_Y, LARGURA, ALTURA - CHAO_Y);

    // Desenhar Inimigas
    inimigas.forEach(ini => ini.desenhar(ctx, posX));

    // Selecionar Animação da Jogadora
    let animBuro = animacoes.buroAndando1;
    if (estadoJogo === "MORTO" || estadoJogo === "MENU_REINICIAR") {
      animBuro = animacoes.buroMorte;
    } else if (tempoTropeco > 0) {
      animBuro = animacoes.buroTropeco;
    } else if (!noChao) {
      animBuro = animacoes.buroPulo;
    } else if (tempoCorrida > 5.0) {
      animBuro = animacoes.buroAndando2;
    }

    const frameBuro = animBuro.obterCanvas();
    if (frameBuro) {
      const larguraBuro = 105;
      const alturaBuro = 105;
      ctx.drawImage(frameBuro, posX - larguraBuro / 2, posY - alturaBuro, larguraBuro, alturaBuro);
    }

    // Textos de Interface
    ctx.fillStyle = "#fff0fa";
    ctx.textAlign = "left";
    ctx.font = "18px Arial";

    if (estadoJogo === "JOGANDO") {
      ctx.fillText(`Esbarrões: ${esbarroesSofridos}/2`, 20, 30);
    } else if (estadoJogo === "MORTO") {
      ctx.textAlign = "center";
      const restante = Math.max(0, Math.ceil(10 - tempoMorte));
      ctx.fillText(`Aguarde... ${restante}s`, LARGURA / 2, 80);
    } else if (estadoJogo === "MENU_REINICIAR") {
      ctx.textAlign = "center";
      ctx.font = "bold 24px Arial";
      ctx.fillText("Pressione ESPAÇO para Reiniciar", LARGURA / 2, 80);
    }
  }

  requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);