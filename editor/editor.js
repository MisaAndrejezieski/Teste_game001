/* =========================================================
   editor/editor.js — lógica completa da IDE
   ========================================================= */

// Estado global do editor
let game = Schema.DEFAULT_GAME();
let selectedEntityId = null;
let manifest = { files: [] };
let previewAction = 'idle';
let previewScroll = 0;
let previewLastTime = 0;

/* =========================================================
   BOOT
   ========================================================= */

window.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadManifest();
  const draft = Storage.loadDraft();
  game = draft || Schema.DEFAULT_GAME();
  bindEvents();
  refreshAll();
  startPreviewLoop();
}

// Lê o manifest de imagens (uma única vez, na inicialização)
async function loadManifest() {
  try {
    const r = await fetch('../images/manifest.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    manifest = await r.json();
    if (!Array.isArray(manifest.files)) manifest.files = [];
  } catch (e) {
    console.warn('manifest:', e.message);
    manifest = { files: [] };
  }
}

/* =========================================================
   EVENTOS
   ========================================================= */

function bindEvents() {
  // --- Meta ---
  document.getElementById('game-title').addEventListener('input', e => {
    game.meta.title = e.target.value;
    saveDebounced();
  });
  // --- Camadas de paralaxe ---
  [0, 1, 2].forEach(i => {
    document.getElementById(`layer-${i}-img`).addEventListener('change', e => {
      game.scene.layers[i].image = e.target.value ? `images/${e.target.value}` : "";
      renderScene();
      saveDebounced();
    });
    document.getElementById(`layer-${i}-speed`).addEventListener('change', e => {
      game.scene.layers[i].speed = parseFloat(e.target.value) || 0;
      saveDebounced();
    });
  });

  // Botões ✕ de cada camada
  document.querySelectorAll('.btn-clear-layer').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      removeLayer(parseInt(e.currentTarget.dataset.idx));
    });
  });

  // --- Entidade ---
  document.getElementById('entity-selector').addEventListener('change', e =>
    selectEntity(e.target.value));

  // --- Propriedades ---
  document.getElementById('prop-role').addEventListener('change', e => updateProp('role', e.target.value));
  document.getElementById('prop-layer').addEventListener('change', e => updateProp('layer', e.target.value));
  document.getElementById('prop-density').addEventListener('change', e => updateProp('hasDensity', e.target.checked));
  document.getElementById('prop-lives').addEventListener('change', e => updateProp('extraLives', parseInt(e.target.value) || 0));
  document.getElementById('prop-speed').addEventListener('change', e => updateProp('speed', parseInt(e.target.value) || 0));
  document.getElementById('prop-jump').addEventListener('change', e => updateProp('jumpHeight', parseInt(e.target.value) || 0));
  document.getElementById('prop-position-x').addEventListener('change', e => updateProp('positionX', parseInt(e.target.value) || 0));
  document.getElementById('prop-spawn-side').addEventListener('change', e => updateProp('spawnSide', e.target.value));
  document.getElementById('prop-flip').addEventListener('change', e => updateProp('flip', e.target.checked));


  // --- Regras ---
  document.getElementById('rule-runner-speed').addEventListener('change', e => {
    game.rules.runner.worldSpeed = parseInt(e.target.value) || 0;
    saveDebounced();
  });
  document.getElementById('rule-runner-spawn').addEventListener('change', e => {
    game.rules.runner.spawnRate = parseInt(e.target.value) || 0;
    saveDebounced();
  });
  // --- Import ---
  document.getElementById('import-file').addEventListener('change', async e => {
    const f = e.target.files[0];
    if (!f) return;
    try {
      game = await Storage.importGameFromFile(f);
      selectedEntityId = null;
      refreshAll();
      Storage.saveDraft(game);
    } catch (err) {
      alert('Erro: ' + err.message);
    }
    e.target.value = '';
  });
}

// Auto-save do draft (debounce de 350ms)
let draftTimer = null;
function saveDebounced() {
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => Storage.saveDraft(game), 350);
}

/* =========================================================
   HELPERS
   ========================================================= */

// Remove o prefixo "images/" de um caminho, para usar em <select>
function stripPrefix(p) {
  return p ? p.replace(/^images\//, '') : '';
}

// Adiciona prefixo "../" para o navegador achar o arquivo (estamos em editor/)
function resolveAsset(p) {
  return p && p.startsWith('images/') ? '../' + p : p;
}

// Preenche um <select> com a lista de arquivos do manifest
function fillManifestSelect(sel) {
  sel.innerHTML = '';
  const opt = document.createElement('option');
  opt.value = '';
  opt.innerText = '-- Nenhum --';
  sel.appendChild(opt);

  manifest.files.forEach(name => {
    const o = document.createElement('option');
    o.value = name;
    o.innerText = name;
    sel.appendChild(o);
  });
}

/* =========================================================
   REFRESH GERAL
   ========================================================= */

function refreshAll() {
  // 1) Preenche TODOS os selects com o manifest
  [0, 1, 2].forEach(i =>
    fillManifestSelect(document.getElementById(`layer-${i}-img`)));
  // 2) Sincroniza campos com o gameObject atual
  document.getElementById('game-title').value = game.meta.title;

  [0, 1, 2].forEach(i => {
    document.getElementById(`layer-${i}-img`).value = stripPrefix(game.scene.layers[i].image);
    document.getElementById(`layer-${i}-speed`).value = game.scene.layers[i].speed;
  });

  document.getElementById('rule-runner-speed').value = game.rules.runner.worldSpeed;
  document.getElementById('rule-runner-spawn').value = game.rules.runner.spawnRate;

  document.getElementById('layers-block').style.display = 'block';

  // 3) Popula entidades e renderiza palco
  populateEntitySelector();
  renderScene();
  renderStage();
  refreshProjectList();
}

/* =========================================================
   CENÁRIO
   ========================================================= */

// Limpa o fundo estático E todas as camadas de paralaxe
function removeBackground() {
  [0, 1, 2].forEach(i => {
    game.scene.layers[i].image = '';
    const sel = document.getElementById(`layer-${i}-img`);
    if (sel) sel.value = '';
    const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
    if (el) el.style.backgroundImage = 'none';
  });

  renderScene();
  saveDebounced();
}

// Remove uma camada individual
function removeLayer(idx) {
  if (idx < 0 || idx > 2) return;
  game.scene.layers[idx].image = '';
  const sel = document.getElementById(`layer-${idx}-img`);
  if (sel) sel.value = '';
  const el = document.querySelector(`.parallax-layer[data-layer="${idx}"]`);
  if (el) el.style.backgroundImage = 'none';
  renderScene();
  saveDebounced();
}

// Remove todas as camadas
function removeAllLayers() {
  [0, 1, 2].forEach(i => removeLayer(i));
}

// Aplica o cenário do runner no palco
function renderScene() {
  const bg = document.getElementById('background-layer');
  bg.style.backgroundImage = 'none';
  [0, 1, 2].forEach(i => {
    const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
    const l = game.scene.layers[i];
    el.style.backgroundImage = l.image ? `url('${resolveAsset(l.image)}')` : 'none';
    el.style.backgroundRepeat = 'repeat-x';
    el.style.backgroundSize = 'auto 100%';
    el.style.backgroundPositionX = '0px';
  });
}

function startPreviewLoop() {
  previewLastTime = performance.now();
  requestAnimationFrame(updatePreview);
}

function updatePreview(now) {
  const dt = Math.min((now - previewLastTime) / 1000, 0.05);
  previewLastTime = now;
  previewScroll += game.rules.runner.worldSpeed * dt;

  [0, 1, 2].forEach(i => {
    const layer = game.scene.layers[i];
    const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
    if (!el || !layer.image) return;
    const speed = layer.speed || (i + 1) * 0.35;
    el.style.backgroundPositionX = `${-previewScroll * speed}px`;
  });

  document.querySelectorAll('.preview-obstacle').forEach(obstacle => {
    const side = obstacle.dataset.spawnSide === 'left' ? 1 : -1;
    const distance = (previewScroll * 0.35) % (window.innerWidth + 320);
    const start = side < 0 ? window.innerWidth + 80 : -80;
    obstacle.style.left = `${start + side * distance}px`;
  });

  requestAnimationFrame(updatePreview);
}

/* =========================================================
   ENTIDADES
   ========================================================= */

function populateEntitySelector() {
  const sel = document.getElementById('entity-selector');
  sel.innerHTML = '';
  const keys = Object.keys(game.entities);

  if (keys.length === 0) {
    selectedEntityId = null;
    const o = document.createElement('option');
    o.innerText = '-- Nenhum --';
    sel.appendChild(o);
    disableEntityPanels(true);
    return;
  }

  disableEntityPanels(false);
  if (!selectedEntityId || !game.entities[selectedEntityId]) {
    selectedEntityId = keys[0];
  }

  keys.forEach(id => {
    const o = document.createElement('option');
    o.value = id;
    o.innerText = `${id} (${game.entities[id].role})`;
    sel.appendChild(o);
  });

  sel.value = selectedEntityId;
  loadEntityPanel();
}

function disableEntityPanels(d) {
  document.getElementById('group-properties').classList.toggle('disabled', d);
  document.getElementById('group-gifs').classList.toggle('disabled', d);
  document.getElementById('btn-delete-entity').style.display = d ? 'none' : 'block';
}

function selectEntity(id) {
  if (!game.entities[id]) return;
  selectedEntityId = id;
  previewAction = 'idle';
  loadEntityPanel();
}

function loadEntityPanel() {
  const e = game.entities[selectedEntityId];
  if (!e) return;

  document.getElementById('prop-role').value = e.role;
  document.getElementById('prop-layer').value = e.layer;
  document.getElementById('prop-density').checked = e.hasDensity;
  document.getElementById('prop-lives').value = e.extraLives;
  document.getElementById('prop-speed').value = e.speed;
  document.getElementById('prop-jump').value = e.jumpHeight;
  document.getElementById('prop-position-x').value = e.positionX;
  document.getElementById('prop-spawn-side').value = e.spawnSide;
  document.getElementById('prop-flip').checked = e.flip;
  renderActionList();
}

function createEntity() {
  const inp = document.getElementById('new-entity-id');
  const id = inp.value.trim().toLowerCase().replace(/\s+/g, '_');
  if (!id || game.entities[id]) return alert('ID inválido ou já existente.');

  const e = Schema.DEFAULT_ENTITY();
  e.id = id;
  if (Object.values(game.entities).some(entity => entity.role === 'player')) {
    e.role = 'enemy';
    e.positionX = 100;
    Object.values(e.actions).forEach(action => { action.positionX = 100; });
  }
  game.entities[id] = e;

  inp.value = '';
  selectedEntityId = id;
  populateEntitySelector();
  renderStage();
  saveDebounced();
}

function deleteEntity() {
  if (!selectedEntityId || !game.entities[selectedEntityId]) return;
  if (!confirm(`Excluir '${selectedEntityId}'?`)) return;

  delete game.entities[selectedEntityId];
  selectedEntityId = null;
  populateEntitySelector();
  renderStage();
  saveDebounced();
}

function updateProp(p, v) {
  if (!selectedEntityId) return;
  const e = game.entities[selectedEntityId];
  if (!e) return;
  e[p] = v;
  renderStage();
  saveDebounced();
}

function renderActionList() {
  const list = document.getElementById('actions-list');
  list.innerHTML = '';
  const entity = game.entities[selectedEntityId];
  if (!entity) return;

  Object.keys(entity.actions).forEach(action => {
    const settings = entity.actions[action];
    const row = document.createElement('div');
    row.className = `action-row${action === previewAction ? ' selected' : ''}`;
    row.innerHTML = `
      <div class="action-title"><strong>${action}</strong>
        <button type="button" class="action-preview">Ver</button>
        <button type="button" class="action-delete">Excluir</button>
      </div>
      <select class="action-gif"></select>
      <label>Escala <input class="action-scale" type="number" step="0.05" min="0.1" max="5" value="${settings.scale}"></label>
      <label>Posição X (%) <input class="action-position-x" type="number" min="0" max="100" value="${settings.positionX}"></label>
      <label>Posição Y (px) <input class="action-position-y" type="number" min="-300" max="300" value="${settings.positionY}"></label>`;

    const gifSelect = row.querySelector('.action-gif');
    fillManifestSelect(gifSelect);
    gifSelect.value = stripPrefix(settings.gif);
    gifSelect.addEventListener('change', event => {
      settings.gif = event.target.value ? `images/${event.target.value}` : '';
      previewAction = action;
      renderActionList();
      renderStage();
      saveDebounced();
    });
    row.querySelector('.action-scale').addEventListener('change', event => {
      settings.scale = parseFloat(event.target.value) || 1;
      previewAction = action;
      renderStage();
      saveDebounced();
    });
    row.querySelector('.action-position-x').addEventListener('change', event => {
      settings.positionX = parseInt(event.target.value) || 0;
      previewAction = action;
      renderStage();
      saveDebounced();
    });
    row.querySelector('.action-position-y').addEventListener('change', event => {
      settings.positionY = parseInt(event.target.value) || 0;
      previewAction = action;
      renderStage();
      saveDebounced();
    });
    row.querySelector('.action-preview').addEventListener('click', () => {
      previewAction = action;
      renderActionList();
      renderStage();
    });
    row.querySelector('.action-delete').addEventListener('click', () => {
      if (['idle', 'run', 'jump'].includes(action)) return;
      delete entity.actions[action];
      previewAction = 'idle';
      renderActionList();
      renderStage();
      saveDebounced();
    });
    list.appendChild(row);
  });
}

function createAction() {
  if (!selectedEntityId) return;
  const input = document.getElementById('new-action-name');
  const action = input.value.trim().toLowerCase().replace(/\s+/g, '_');
  if (!/^[a-z0-9_-]+$/.test(action) || game.entities[selectedEntityId].actions[action]) {
    alert('Nome inválido ou ação já existente.');
    return;
  }
  game.entities[selectedEntityId].actions[action] = {
    gif: '', scale: 1, positionX: 20, positionY: 0
  };
  input.value = '';
  previewAction = action;
  renderActionList();
  renderStage();
  saveDebounced();
}

/* =========================================================
   RENDER DO PALCO
   ========================================================= */

function renderStage() {
  const c = document.getElementById('entities-container');
  c.innerHTML = '';

  const keys = Object.keys(game.entities);

  keys.forEach(id => {
    const e = game.entities[id];
    const el = document.createElement('div');
    el.className = `sprite-container layer-${e.layer}`;
    if (e.role === 'enemy') {
      el.classList.add('preview-obstacle');
      el.dataset.spawnSide = e.spawnSide;
    }

    let posX = e.role === 'enemy'
      ? (e.spawnSide === 'left' ? 0 : 100)
      : e.positionX;
    el.style.left = `${posX}%`;

    const action = e.actions[previewAction] || e.actions.idle || e.actions.run;
    const src = action && action.gif;
    if (src) {
      const img = document.createElement('img');
      img.src = resolveAsset(src);

      const scale = action.scale || 1;
      const posY = action.positionY || 0;
      if (e.role !== 'enemy') el.style.left = `${action.positionX}%`;
      img.style.transform = `scale(${scale}) translateY(${-posY}px)`;

      el.appendChild(img);
    }

    c.appendChild(el);

  });
}

/* =========================================================
   PROJETO (salvar / exportar / importar / resetar)
   ========================================================= */

function saveProjectAs() {
  const name = prompt('Nome da versão:', `v${Storage.listProjects().length + 1}`);
  if (!name) return;
  Storage.saveProject(name, game);
  refreshProjectList();
}

function exportGame() {
  Storage.exportGameToFile(game);
}

function resetProject() {
  if (!confirm('Apagar projeto atual?')) return;
  game = Schema.DEFAULT_GAME();
  selectedEntityId = null;
  Storage.clearDraft();
  refreshAll();
}

function refreshProjectList() {
  const sel = document.getElementById('project-list');
  sel.innerHTML = '';

  const list = Storage.listProjects();
  if (list.length === 0) {
    const o = document.createElement('option');
    o.value = '';
    o.innerText = '-- Nenhuma --';
    sel.appendChild(o);
    return;
  }

  list.forEach(p => {
    const o = document.createElement('option');
    o.value = p.name;
    o.innerText = `${p.name} (${new Date(p.savedAt).toLocaleString()})`;
    sel.appendChild(o);
  });
}

function loadSelectedProject() {
  const n = document.getElementById('project-list').value;
  if (!n) return;
  const g = Storage.loadProject(n);
  if (!g) return alert('Não encontrada.');
  game = g;
  selectedEntityId = null;
  refreshAll();
  Storage.saveDraft(game);
}

function deleteSelectedProject() {
  const n = document.getElementById('project-list').value;
  if (!n) return;
  if (!confirm(`Apagar "${n}"?`)) return;
  Storage.deleteProject(n);
  refreshProjectList();
}

/* =========================================================
   PLAY
   ========================================================= */

function playGame() {
  Storage.saveDraft(game);
  window.open('../player/index.html', 'ags-player');
}