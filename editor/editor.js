/* =========================================================
   editor/editor.js
   Lógica da IDE. Usa shared/schema.js e shared/storage.js.
   Lê imagens de ../images/manifest.json.
   ========================================================= */

let game = Schema.DEFAULT_GAME();
let selectedEntityId = null;
let manifest = { files: [] };      // { files: ["a.gif", ...] }

/* ---------------------------------------------------------
   BOOT
   --------------------------------------------------------- */

window.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadManifest();
  loadDraftOrNew();
  bindStaticEvents();
  refreshAllUI();
}

async function loadManifest() {
  try {
    const res = await fetch('../images/manifest.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    manifest = await res.json();
    if (!Array.isArray(manifest.files)) manifest.files = [];
  } catch (e) {
    console.warn('Falha ao ler manifest.json:', e.message);
    manifest = { files: [] };
    alert('Não foi possível ler images/manifest.json. Rode o gerar_manifest.html primeiro.');
  }
}

function loadDraftOrNew() {
  const draft = Storage.loadDraft();
  game = draft || Schema.DEFAULT_GAME();
}

/* ---------------------------------------------------------
   EVENTOS ESTÁTICOS
   --------------------------------------------------------- */

function bindStaticEvents() {
  // Meta
  document.getElementById('game-title').addEventListener('input', e => {
    game.meta.title = e.target.value;
    scheduleDraftSave();
  });

  document.getElementById('game-genre').addEventListener('change', e => {
    game.meta.genre = e.target.value;
    applyGenreLayout();
    renderStage();
    scheduleDraftSave();
  });

  // Cenário
  document.getElementById('bg-select').addEventListener('change', e => {
    const v = e.target.value;
    game.scene.backgroundImage = v ? `images/${v}` : "";
    renderScene();
    scheduleDraftSave();
  });

  document.getElementById('bg-mode').addEventListener('change', e => {
    game.scene.backgroundMode = e.target.value;
    renderScene();
    scheduleDraftSave();
  });

  // Entidade — seletor
  document.getElementById('entity-selector').addEventListener('change', e => {
    selectEntity(e.target.value);
  });

  // Propriedades
  document.getElementById('prop-role').addEventListener('change', e =>
    updateEntityProp('role', e.target.value));
  document.getElementById('prop-layer').addEventListener('change', e =>
    updateEntityProp('layer', e.target.value));
  document.getElementById('prop-density').addEventListener('change', e =>
    updateEntityProp('hasDensity', e.target.checked));
  document.getElementById('prop-lives').addEventListener('change', e =>
    updateEntityProp('extraLives', parseInt(e.target.value) || 0));
  document.getElementById('prop-speed').addEventListener('change', e =>
    updateEntityProp('speed', parseInt(e.target.value) || 0));
  document.getElementById('prop-jump').addEventListener('change', e =>
    updateEntityProp('jumpHeight', parseInt(e.target.value) || 0));
  document.getElementById('prop-float').addEventListener('change', e =>
    updateEntityProp('floatTime', parseInt(e.target.value) || 0));
  document.getElementById('prop-scale').addEventListener('change', e =>
    updateEntityProp('scale', parseFloat(e.target.value) || 1));
  document.getElementById('prop-offset-y').addEventListener('change', e =>
    updateEntityProp('offsetY', parseInt(e.target.value) || 0));

  // GIFs (todos os 6 selects)
  ['idle','run','jump','attack','bump','defeat'].forEach(action => {
    const sel = document.getElementById(`gif-${action}`);
    sel.addEventListener('change', e => {
      if (!selectedEntityId) return;
      const v = e.target.value;
      const ent = game.entities[selectedEntityId];
      if (!ent) return;
      ent.gifs[action] = v ? `images/${v}` : "";
      renderStage();
      scheduleDraftSave();
    });
  });

  // Import
  document.getElementById('import-file').addEventListener('change', async e => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      game = await Storage.importGameFromFile(file);
      selectedEntityId = null;
      refreshAllUI();
      Storage.saveDraft(game);
      alert('Projeto importado.');
    } catch (err) {
      alert('Erro: ' + err.message);
    }
    e.target.value = '';
  });

  // Lista de projetos
  document.getElementById('project-list').addEventListener('change', () => {}); // no-op
}

/* ---------------------------------------------------------
   DRAFT SAVE (debounced)
   --------------------------------------------------------- */

let draftTimer = null;
function scheduleDraftSave() {
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => Storage.saveDraft(game), 400);
}

/* ---------------------------------------------------------
   MANIFEST → OPTIONS
   --------------------------------------------------------- */

function fillManifestSelect(selectEl, { includeEmpty = true } = {}) {
  selectEl.innerHTML = '';
  if (includeEmpty) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.innerText = '-- Nenhum --';
    selectEl.appendChild(opt);
  }
  manifest.files.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.innerText = name;
    selectEl.appendChild(opt);
  });
}

function fillAllManifestSelects() {
  fillManifestSelect(document.getElementById('bg-select'));
  ['idle','run','jump','attack','bump','defeat'].forEach(action => {
    fillManifestSelect(document.getElementById(`gif-${action}`));
  });
}

/* ---------------------------------------------------------
   UI → REFRESH GERAL
   --------------------------------------------------------- */

function refreshAllUI() {
  fillAllManifestSelects();
  syncMetaFields();
  populateEntitySelector();
  applyGenreLayout();
  renderScene();
  renderStage();
  refreshProjectList();
}

function syncMetaFields() {
  document.getElementById('game-title').value = game.meta.title;
  document.getElementById('game-genre').value = game.meta.genre;
  document.getElementById('bg-mode').value = game.scene.backgroundMode;

  // Fundo: extrai só o nome do arquivo do caminho "images/xxx"
  const bgName = stripImagesPrefix(game.scene.backgroundImage);
  document.getElementById('bg-select').value = bgName;
}

function stripImagesPrefix(path) {
  if (!path) return '';
  return path.replace(/^images\//, '');
}

/* ---------------------------------------------------------
   CENÁRIO
   --------------------------------------------------------- */

function removeBackground() {
  game.scene.backgroundImage = '';
  document.getElementById('bg-select').value = '';
  renderScene();
  scheduleDraftSave();
}

function renderScene() {
  const bg = document.getElementById('background-layer');
  if (game.scene.backgroundImage) {
    bg.style.backgroundImage = `url('${resolveAssetPath(game.scene.backgroundImage)}')`;
    bg.style.backgroundRepeat =
      (game.scene.backgroundMode === 'repeat' || game.meta.genre === 'racing')
        ? 'repeat' : 'no-repeat';
    bg.style.backgroundSize =
      game.scene.backgroundMode === 'repeat' ? 'auto' : game.scene.backgroundMode;
  } else {
    bg.style.backgroundImage = 'none';
  }
}

// Converte "images/nome.gif" em "../images/nome.gif"
// (porque o editor/index.html está dentro de editor/)
function resolveAssetPath(path) {
  if (!path) return '';
  if (path.startsWith('images/')) return '../' + path;
  return path;
}

/* ---------------------------------------------------------
   ENTIDADES
   --------------------------------------------------------- */

function populateEntitySelector() {
  const sel = document.getElementById('entity-selector');
  sel.innerHTML = '';
  const keys = Object.keys(game.entities);

  if (keys.length === 0) {
    selectedEntityId = null;
    const opt = document.createElement('option');
    opt.innerText = '-- Nenhum Personagem --';
    sel.appendChild(opt);
    disableEntityPanels(true);
    return;
  }

  disableEntityPanels(false);
  if (!selectedEntityId || !game.entities[selectedEntityId]) {
    selectedEntityId = keys[0];
  }

  keys.forEach(id => {
    const opt = document.createElement('option');
    opt.value = id;
    opt.innerText = `${id} (${game.entities[id].role})`;
    sel.appendChild(opt);
  });
  sel.value = selectedEntityId;

  loadEntityPanelData();
}

function disableEntityPanels(disabled) {
  document.getElementById('group-properties').classList.toggle('disabled', disabled);
  document.getElementById('group-gifs').classList.toggle('disabled', disabled);
  document.getElementById('btn-delete-entity').style.display = disabled ? 'none' : 'block';
}

function selectEntity(id) {
  if (!game.entities[id]) return;
  selectedEntityId = id;
  loadEntityPanelData();
}

function loadEntityPanelData() {
  const ent = game.entities[selectedEntityId];
  if (!ent) return;

  document.getElementById('prop-role').value = ent.role;
  document.getElementById('prop-layer').value = ent.layer;
  document.getElementById('prop-density').checked = ent.hasDensity;
  document.getElementById('prop-lives').value = ent.extraLives;
  document.getElementById('prop-speed').value = ent.speed;
  document.getElementById('prop-jump').value = ent.jumpHeight;
  document.getElementById('prop-float').value = ent.floatTime;
  document.getElementById('prop-scale').value = ent.scale;
  document.getElementById('prop-offset-y').value = ent.offsetY;

  ['idle','run','jump','attack','bump','defeat'].forEach(action => {
    const name = stripImagesPrefix(ent.gifs[action]);
    document.getElementById(`gif-${action}`).value = name || '';
  });
}

function createEntity() {
  const input = document.getElementById('new-entity-id');
  const rawId = input.value.trim().toLowerCase().replace(/\s+/g, '_');

  if (!rawId || game.entities[rawId]) {
    alert('ID inválido ou já existente.');
    return;
  }

  const ent = Schema.DEFAULT_ENTITY();
  ent.id = rawId;
  game.entities[rawId] = ent;

  input.value = '';
  selectedEntityId = rawId;
  populateEntitySelector();
  renderStage();
  scheduleDraftSave();
}

function deleteEntity() {
  if (!selectedEntityId || !game.entities[selectedEntityId]) return;
  if (!confirm(`Excluir '${selectedEntityId}'?`)) return;

  delete game.entities[selectedEntityId];
  selectedEntityId = null;
  populateEntitySelector();
  renderStage();
  scheduleDraftSave();
}

function updateEntityProp(prop, value) {
  if (!selectedEntityId) return;
  const ent = game.entities[selectedEntityId];
  if (!ent) return;
  ent[prop] = value;
  renderStage();
  scheduleDraftSave();
}

/* ---------------------------------------------------------
   RENDER DO PALCO
   --------------------------------------------------------- */

function renderStage() {
  const container = document.getElementById('entities-container');
  container.innerHTML = '';

  const keys = Object.keys(game.entities);
  const genre = game.meta.genre;

  keys.forEach((id, index) => {
    const ent = game.entities[id];
    const el = document.createElement('div');
    el.className = `sprite-container layer-${ent.layer}`;

    let posX = ent.positionX;
    let flip = false;

    if (genre === 'fighting') {
      posX = index === 0 ? 25 : 70;
      if (index === 1) flip = true;
    } else if (genre === 'racing') {
      posX = 15 + (index * 25);
    }

    el.style.left = `${posX}%`;

    const src = ent.gifs.run || ent.gifs.idle || '';
    if (src) {
      const img = document.createElement('img');
      img.src = resolveAssetPath(src);
      const scale = ent.scale || 1;
      const offsetY = ent.offsetY || 0;
      const flipPart = flip ? ' scaleX(-1)' : '';
      img.style.transform = `scale(${scale}) translateY(${-offsetY}px)${flipPart}`;
      el.appendChild(img);
    }

    container.appendChild(el);

    if (genre === 'fighting') {
      if (index === 0) document.getElementById('p1-name').innerText = ent.id.toUpperCase();
      if (index === 1) document.getElementById('p2-name').innerText = ent.id.toUpperCase();
    }
  });
}

function applyGenreLayout() {
  const stage = document.getElementById('game-stage');
  const fightingUi = document.getElementById('fighting-ui');
  stage.className = `mode-${game.meta.genre}`;
  fightingUi.classList.toggle('hidden', game.meta.genre !== 'fighting');
}

/* ---------------------------------------------------------
   PROJETO: SALVAR / EXPORTAR / IMPORTAR / RESET
   --------------------------------------------------------- */

function saveProjectAs() {
  const name = prompt('Nome da versão:', `v${Storage.listProjects().length + 1}`);
  if (!name) return;
  Storage.saveProject(name, game);
  refreshProjectList();
  alert(`Versão "${name}" salva.`);
}

function exportGame() {
  Storage.exportGameToFile(game);
}

function resetProject() {
  if (!confirm('Isso apaga o projeto atual. Continuar?')) return;
  game = Schema.DEFAULT_GAME();
  selectedEntityId = null;
  Storage.clearDraft();
  refreshAllUI();
}

function refreshProjectList() {
  const sel = document.getElementById('project-list');
  sel.innerHTML = '';
  const list = Storage.listProjects();
  if (list.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.innerText = '-- Nenhuma versão salva --';
    sel.appendChild(opt);
    return;
  }
  list.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.name;
    opt.innerText = `${p.name}  (${new Date(p.savedAt).toLocaleString()})`;
    sel.appendChild(opt);
  });
}

function loadSelectedProject() {
  const name = document.getElementById('project-list').value;
  if (!name) return;
  const loaded = Storage.loadProject(name);
  if (!loaded) return alert('Versão não encontrada.');
  game = loaded;
  selectedEntityId = null;
  refreshAllUI();
  Storage.saveDraft(game);
  alert(`Versão "${name}" carregada.`);
}

function deleteSelectedProject() {
  const name = document.getElementById('project-list').value;
  if (!name) return;
  if (!confirm(`Apagar a versão "${name}"?`)) return;
  Storage.deleteProject(name);
  refreshProjectList();
}

/* ---------------------------------------------------------
   PLAY (nova aba)
   --------------------------------------------------------- */

function playGame() {
  Storage.saveDraft(game);
  window.open('../player/index.html', '_blank');
}