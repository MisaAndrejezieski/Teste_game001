const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const buroSprite = document.getElementById("buroSprite");
const menuSprite = document.getElementById("menuSprite");
const inimigasContainer = document.getElementById("inimigasContainer");

const LARGURA = 960;
const ALTURA = 540;
const CHAO_Y = ALTURA - 80;

const GRAVIDADE = 1000;
const FORCA_PULO = -480;
const VELOCIDADE_CENARIO = 280;

const CAMINHOS = {
  buroAndando1: "images/muse-dash-buro001.gif",
  buroAndando2: "images/muse-dash-buro002.gif",
  buroPulo: "images/muse-dash-buro008.gif",
  buroTropeco: "images/muse-dash-buro007.gif",
  buroMorte: "images/muse-dash-marija.gif",
  inimigaCorrendo: "images/inim001.gif",
  inimigaPassou: "images/inim002.gif",
  inimigaImpacto: "images/inim003.gif"
};

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

class Inimiga {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.largura = 35;
    this.altura = 50;
    this.esbarrou = false;

    this.element = document.createElement("img");
    this.element.className = "sprite inimigaSprite";
    this.element.src = CAMINHOS.inimigaCorrendo;
    inimigasContainer.appendChild(this.element);

    this.atualizarPosicaoDOM();
  }

  atualizar(dt, posXJogador) {
    this.x -= VELOCIDADE_CENARIO * dt;

    if (this.esbarrou) {
      if (!this.element.src.includes(CAMINHOS.inimigaImpacto)) {
        this.element.src = CAMINHOS.inimigaImpacto;
      }
    } else if (this.x + this.largura < posXJogador) {
      if (!this.element.src.includes(CAMINHOS.inimigaPassou)) {
        this.element.src = CAMINHOS.inimigaPassou;
      }
    }

    this.atualizarPosicaoDOM();
  }

  atualizarPosicaoDOM() {
    this.element.style.left = `${this.x}px`;
    this.element.style.top = `${this.y}px`;
  }

  destruir() {
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }
}

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
document.getElementById("gameArea").addEventListener("click", acaoJogador);

function resetarJogo() {
  posX = 120;
  posY = CHAO_Y;
  velY = 0;
  noChao = true;
  tempoCorrida = 0;
  tempoMorte = 0;
  tempoTropeco = 0;
  esbarroesSofridos = 0;

  inimigas.forEach(i => i.destruir());
  inimigas = [];

  menuSprite.style.display = "none";
  buroSprite.style.display = "block";
  buroSprite.classList.remove("morte");

  estadoJogo = "JOGANDO";
}

function acionarMorte() {
  estadoJogo = "MORTO";
  tempoMorte = 0;
  buroSprite.classList.add("morte");
  buroSprite.src = `${CAMINHOS.buroMorte}?t=${Date.now()}`;
}

function atualizarSpriteJogador(novoSrc) {
  if (!buroSprite.src.includes(novoSrc)) {
    buroSprite.src = novoSrc;
  }
}

function gameLoop(tempoAtual) {
  const dt = Math.min((tempoAtual - ultimoTempo) / 1000, 0.1);
  ultimoTempo = tempoAtual;

  ctx.clearRect(0, 0, LARGURA, ALTURA);

  if (estadoJogo === "TELA_INICIAL") {
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
        ini.atualizar(dt, posX);

        if (ini.x < -60) {
          ini.destruir();
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
            acionarMorte();
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

    ctx.fillStyle = "#b45078";
    ctx.fillRect(0, CHAO_Y, LARGURA, ALTURA - CHAO_Y);

    if (estadoJogo !== "MORTO" && estadoJogo !== "MENU_REINICIAR") {
      let srcAtual = CAMINHOS.buroAndando1;
      if (tempoTropeco > 0) {
        srcAtual = CAMINHOS.buroTropeco;
      } else if (!noChao) {
        srcAtual = CAMINHOS.buroPulo;
      } else if (tempoCorrida > 5.0) {
        srcAtual = CAMINHOS.buroAndando2;
      }
      atualizarSpriteJogador(srcAtual);
    }

    buroSprite.style.left = `${posX}px`;
    buroSprite.style.top = `${posY}px`;

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