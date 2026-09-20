const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const LARGURA = 960;
const ALTURA = 540;
const CHAO_Y = ALTURA - 80;

// --- Configurações de Física e Velocidade ---
const GRAVIDADE = 1000;         // Gravidade levemente menor para o pulo flutuar melhor
const FORCA_PULO = -480;        // Pulo mais alto
const VELOCIDADE_CENARIO = 280; // Jogo mais lento e cadenciado

// --- Pré-carregamento das Imagens (GIFs) ---
const imagens = {};
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

Object.keys(caminhos).forEach(chave => {
  imagens[chave] = new Image();
  imagens[chave].src = caminhos[chave];
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

// --- Classe da Inimiga ---
class Inimiga {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    // Hitbox aumentada proporcionalmente
    this.largura = 35;
    this.altura = 50;
    this.esbarrou = false;
  }

  atualizar(dt, posXJogador) {
    this.x -= VELOCIDADE_CENARIO * dt;
  }

  desenhar(ctx, posXJogador) {
    let img = imagens.inimigaCorrendo;

    if (this.esbarrou) {
      img = imagens.inimigaImpacto;
    } else if (this.x + this.largura < posXJogador) {
      img = imagens.inimigaPassou;
    }

    ctx.save();
    ctx.translate(this.x + this.largura / 2, this.y);
    ctx.scale(-1, 1);
    
    // Tamanho visual da inimiga aumentado (de 45px para 65px)
    const larguraImg = 65;
    const alturaImg = 65;
    
    ctx.drawImage(img, -larguraImg / 2, -alturaImg, larguraImg, alturaImg);
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
  const dt = Math.min((tempoAtual - ultimoTempo) / 1000, 0.1); // Trava dt máximo para evitar saltos
  ultimoTempo = tempoAtual;

  // Limpa a tela
  ctx.fillStyle = "#191423";
  ctx.fillRect(0, 0, LARGURA, ALTURA);

  if (estadoJogo === "TELA_INICIAL") {
    ctx.drawImage(imagens.buroInicial, LARGURA / 2 - 100, ALTURA / 2 - 120, 200, 200);
    
    ctx.fillStyle = "#fff0fa";
    ctx.font = "bold 24px Arial";
    ctx.textAlign = "center";
    ctx.fillText("Pressione ESPAÇO ou Clique para iniciar", LARGURA / 2, ALTURA - 60);

  } else if (estadoJogo === "JOGANDO" || estadoJogo === "MORTO" || estadoJogo === "MENU_REINICIAR") {
    
    if (estadoJogo === "JOGANDO") {
      tempoCorrida += dt;

      if (tempoTropeco > 0) tempoTropeco -= dt;

      // Aplicar gravidade
      velY += GRAVIDADE * dt;
      posY += velY * dt;

      if (posY >= CHAO_Y) {
        posY = CHAO_Y;
        velY = 0;
        noChao = true;
      }

      // Spawner de inimigas (ajustado para a nova velocidade do jogo)
      tempoSpawn += dt;
      if (tempoSpawn >= 1.8 + Math.random() * 1.2) {
        tempoSpawn = 0;
        inimigas.push(new Inimiga(LARGURA + 20, CHAO_Y));
      }

      // Hitbox maior da jogadora (30px largura por 55px altura)
      const rectJogador = { x: posX - 15, y: posY - 55, largura: 30, altura: 55 };

      // Atualiza Inimigas e Colisão
      for (let i = inimigas.length - 1; i >= 0; i--) {
        let ini = inimigas[i];
        ini.atualizar(dt, posX);

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

    // --- Desenhar Chão ---
    ctx.fillStyle = "#b45078";
    ctx.fillRect(0, CHAO_Y, LARGURA, ALTURA - CHAO_Y);

    // --- Desenhar Inimigas ---
    inimigas.forEach(ini => ini.desenhar(ctx, posX));

    // --- Selecionar Sprite da Jogadora ---
    let imgBuro = imagens.buroAndando1;
    if (estadoJogo === "MORTO" || estadoJogo === "MENU_REINICIAR") {
      imgBuro = imagens.buroMorte;
    } else if (tempoTropeco > 0) {
      imgBuro = imagens.buroTropeco;
    } else if (!noChao) {
      imgBuro = imagens.buroPulo;
    } else if (tempoCorrida > 5.0) {
      imgBuro = imagens.buroAndando2;
    }

    // Tamanho visual da jogadora aumentado (de 75px para 105px)
    const larguraBuro = 105;
    const alturaBuro = 105;
    ctx.drawImage(imgBuro, posX - larguraBuro / 2, posY - alturaBuro, larguraBuro, alturaBuro);

    // --- Interface de Texto ---
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