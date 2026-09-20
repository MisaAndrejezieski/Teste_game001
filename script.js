// Estrutura Principal do Projeto do Jogo com os Dados Anteriores Preservados
let gameObject = {
  meta: {
    title: "Slot Anime Runner",
    genre: "runner",
    version: "1.0.0"
  },
  entities: {
    buro: {
      id: "buro",
      role: "player",
      layer: "foreground",
      hasDensity: true,
      extraLives: 3,
      speed: 300,
      jumpHeight: 150,
      floatTime: 800,
      scale: 0.9,
      offsetY: -60,
      positionX: 20,
      gifs: {
        idle: "images/muse-dash-buro_tela principal.gif",
        run: "images/muse-dash-buro_anda_normal.gif",
        jump: "images/muse-dash-buro_segunda_imagem_do_pulo_normal.gif",
        attack: "images/muse-dash-buro_segunda_imagem_do_pulo_especial.gif",
        bump: "images/muse-dash-buro_segunda_imagem_do_esbarrao.gif",
        defeat: "images/muse-dash-marija_morte.gif"
      }
    },
    inimiga_01: {
      id: "inimiga_01",
      role: "enemy",
      layer: "ground",
      hasDensity: true,
      extraLives: 0,
      speed: 200,
      jumpHeight: 0,
      floatTime: 0,
      scale: 0.35,
      offsetY: -150,
      positionX: 75,
      gifs: {
        idle: "images/inimiga_caminha.gif",
        run: "images/inimiga_caminha.gif",
        jump: "",
        attack: "images/inim004.gif",
        bump: "images/inimiga_esbarra_na_principal.gif",
        defeat: "images/inimiga_passa_da_principal.gif"
      }
    }
  }
};

let selectedEntityId = "buro";

function init() {
  populateSelectors();
  loadEntityPanelData();
  renderStage();
}

function updateGameMeta(key, value) {
  gameObject.meta[key] = value;
}

function renderStage() {
  const container = document.getElementById('entities-container');
  container.innerHTML = '';

  Object.keys(gameObject.entities).forEach(id => {
    const ent = gameObject.entities[id];

    const element = document.createElement('div');
    element.id = `entity-${id}`;
    element.className = `sprite-container layer-${ent.layer}`;
    element.style.left = `${ent.positionX}%`;

    const img = document.createElement('img');
    img.src = ent.gifs.run || ent.gifs.idle || '';
    img.style.transform = `scale(${ent.scale || 1}) translateY(${-(ent.offsetY || 0)}px)`;

    element.appendChild(img);
    container.appendChild(element);
  });
}

function populateSelectors() {
  document.getElementById('game-title').value = gameObject.meta.title;
  document.getElementById('game-genre').value = gameObject.meta.genre;

  const selector = document.getElementById('entity-selector');
  selector.innerHTML = '';
  Object.keys(gameObject.entities).forEach(id => {
    const opt = document.createElement('option');
    opt.value = id;
    opt.innerText = `${id} (${gameObject.entities[id].role})`;
    selector.appendChild(opt);
  });
  selector.value = selectedEntityId;
}

function selectEntity(id) {
  selectedEntityId = id;
  loadEntityPanelData();
}

function loadEntityPanelData() {
  const ent = gameObject.entities[selectedEntityId];
  if (!ent) return;

  document.getElementById('prop-role').value = ent.role;
  document.getElementById('prop-layer').value = ent.layer;
  document.getElementById('prop-density').checked = ent.hasDensity;
  document.getElementById('prop-lives').value = ent.extraLives;
  document.getElementById('prop-speed').value = ent.speed;
  document.getElementById('prop-jump').value = ent.jumpHeight;
  document.getElementById('prop-float').value = ent.floatTime;
  document.getElementById('prop-scale').value = ent.scale || 1;
  document.getElementById('prop-offset-y').value = ent.offsetY || 0;
}

function createEntity() {
  const input = document.getElementById('new-entity-id');
  const rawId = input.value.trim().toLowerCase().replace(/\s+/g, '_');

  if (!rawId || gameObject.entities[rawId]) {
    alert('ID inválido ou já existente!');
    return;
  }

  gameObject.entities[rawId] = {
    id: rawId,
    role: "enemy",
    layer: "ground",
    hasDensity: true,
    extraLives: 1,
    speed: 150,
    jumpHeight: 0,
    floatTime: 0,
    scale: 1,
    offsetY: 0,
    positionX: 70,
    gifs: { idle: "", run: "", jump: "", attack: "", bump: "", defeat: "" }
  };

  input.value = '';
  selectedEntityId = rawId;
  populateSelectors();
  loadEntityPanelData();
  renderStage();
}

function updateEntityProp(prop, value) {
  const ent = gameObject.entities[selectedEntityId];
  if (ent) {
    ent[prop] = value;
    renderStage();
  }
}

// Faz o upload do arquivo do PC e gera URL temporária para exibição no palco
function uploadEntityGif(action, file) {
  if (!file) return;
  const ent = gameObject.entities[selectedEntityId];
  if (ent) {
    const objectUrl = URL.createObjectURL(file);
    ent.gifs[action] = objectUrl;
    renderStage();
  }
}

function downloadGameFile() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(gameObject, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `${gameObject.meta.title.toLowerCase().replace(/\s+/g, '_')}_game.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

function loadGameFile(event) {
  const fileReader = new FileReader();
  fileReader.onload = function(e) {
    try {
      const loadedData = JSON.parse(e.target.result);
      if (loadedData.meta && loadedData.entities) {
        gameObject = loadedData;
        selectedEntityId = Object.keys(gameObject.entities)[0] || '';
        populateSelectors();
        loadEntityPanelData();
        renderStage();
        alert('Projeto carregado com sucesso!');
      } else {
        alert('Arquivo de jogo inválido.');
      }
    } catch (err) {
      alert('Erro ao ler o arquivo JSON.');
    }
  };
  fileReader.readAsText(event.target.files[0]);
}

window.addEventListener('DOMContentLoaded', init);