let gameObject = {
  meta: {
    title: "Meu Jogo Anime",
    genre: "runner",
    version: "1.0.0"
  },
  scene: {
    backgroundImage: "",
    backgroundMode: "cover" // 'cover', 'contain', 'repeat'
  },
  entities: {}
};

let selectedEntityId = null;

function init() {
  populateSelectors();
  renderScene();
  renderStage();
}

function updateGameMeta(key, value) {
  gameObject.meta[key] = value;
}

// Configurações do Cenário (Background)
function uploadBackground(file) {
  if (!file) return;
  const objectUrl = URL.createObjectURL(file);
  gameObject.scene.backgroundImage = objectUrl;
  renderScene();
}

function updateBackgroundMode(mode) {
  gameObject.scene.backgroundMode = mode;
  renderScene();
}

function removeBackground() {
  gameObject.scene.backgroundImage = "";
  renderScene();
}

function renderScene() {
  const bgLayer = document.getElementById('background-layer');
  if (gameObject.scene.backgroundImage) {
    bgLayer.style.backgroundImage = `url('${gameObject.scene.backgroundImage}')`;
    bgLayer.style.backgroundRepeat = gameObject.scene.backgroundMode === 'repeat' ? 'repeat' : 'no-repeat';
    bgLayer.style.backgroundSize = gameObject.scene.backgroundMode === 'repeat' ? 'auto' : gameObject.scene.backgroundMode;
  } else {
    bgLayer.style.backgroundImage = 'none';
  }
}

// Renderização dos Personagens
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
  document.getElementById('bg-mode').value = gameObject.scene.backgroundMode || 'cover';

  const selector = document.getElementById('entity-selector');
  selector.innerHTML = '';

  const entityKeys = Object.keys(gameObject.entities);

  if (entityKeys.length === 0) {
    selectedEntityId = null;
    const opt = document.createElement('option');
    opt.innerText = '-- Nenhum Personagem --';
    selector.appendChild(opt);
    disableEntityPanels(true);
  } else {
    disableEntityPanels(false);
    if (!selectedEntityId || !gameObject.entities[selectedEntityId]) {
      selectedEntityId = entityKeys[0];
    }
    entityKeys.forEach(id => {
      const opt = document.createElement('option');
      opt.value = id;
      opt.innerText = `${id} (${gameObject.entities[id].role})`;
      selector.appendChild(opt);
    });
    selector.value = selectedEntityId;
    loadEntityPanelData();
  }
}

function disableEntityPanels(disabled) {
  const propGroup = document.getElementById('group-properties');
  const gifGroup = document.getElementById('group-gifs');
  const deleteBtn = document.getElementById('btn-delete-entity');

  if (disabled) {
    propGroup.classList.add('disabled');
    gifGroup.classList.add('disabled');
    deleteBtn.style.display = 'none';
  } else {
    propGroup.classList.remove('disabled');
    gifGroup.classList.remove('disabled');
    deleteBtn.style.display = 'block';
  }
}

function selectEntity(id) {
  if (!gameObject.entities[id]) return;
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
    role: "player",
    layer: "foreground",
    hasDensity: true,
    extraLives: 3,
    speed: 200,
    jumpHeight: 150,
    floatTime: 0,
    scale: 1,
    offsetY: 0,
    positionX: 20,
    gifs: { idle: "", run: "", jump: "", attack: "", bump: "", defeat: "" }
  };

  input.value = '';
  selectedEntityId = rawId;
  populateSelectors();
  renderStage();
}

// Permite excluir TODOS os personagens sem limitação
function deleteEntity() {
  if (!selectedEntityId || !gameObject.entities[selectedEntityId]) return;

  if (confirm(`Excluir o personagem '${selectedEntityId}'?`)) {
    delete gameObject.entities[selectedEntityId];
    selectedEntityId = null;
    populateSelectors();
    renderStage();
  }
}

function updateEntityProp(prop, value) {
  if (!selectedEntityId) return;
  const ent = gameObject.entities[selectedEntityId];
  if (ent) {
    ent[prop] = value;
    renderStage();
  }
}

function uploadEntityGif(action, file) {
  if (!file || !selectedEntityId) return;
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
      if (loadedData.meta) {
        gameObject = loadedData;
        selectedEntityId = null;
        populateSelectors();
        renderScene();
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