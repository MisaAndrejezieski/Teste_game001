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
  document.getElementById('action-selector').addEventListener('change', e => {
    previewAction = e.target.value;
    loadActionSettings();
    renderStage();
  });

  // --- Propriedades ---
  document.getElementById('prop-role').addEventListener('change', e => updateProp('role', e.target.value));
  document.getElementById('prop-layer').addEventListener('change', e => updateProp('layer', e.target.value));
  document.getElementById('prop-density').addEventListener('change', e => updateProp('hasDensity', e.target.checked));
  document.getElementById('prop-lives').addEventListener('change', e => updateProp('extraLives', parseInt(e.target.value) || 0));
  document.getElementById('prop-speed').addEventListener('change', e => updateProp('speed', parseInt(e.target.value) || 0));
  document.getElementById('prop-jump').addEventListener('change', e => updateProp('jumpHeight', parseInt(e.target.value) || 0));
  document.getElementById('prop-scale').addEventListener('change', e => updateActionProp('scale', parseFloat(e.target.value) || 1));
  document.getElementById('prop-offset-y').addEventListener('change', e => updateActionProp('offsetY', parseInt(e.target.value) || 0));
  document.getElementById('prop-position-x').addEventListener('change', e => updateProp('positionX', parseInt(e.target.value) || 0));

  // --- GIFs por ação ---
  ['idle','run','jump','bump','defeat'].forEach(action => {
    document.getElementById(`gif-${action}`).addEventListener('change', e => {
      if (!selectedEntityId) return;
      const ent = game.entities[selectedEntityId];
      if (!ent) return;
      ent.gifs[action] = e.target.value ? `images/${e.target.value}` : "";
      previewAction = action;
      document.getElementById('action-selector').value = action;
      loadActionSettings();
      renderStage();
      saveDebounced();
    });
  });

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
  ['idle','run','jump','bump','defeat'].forEach(a =>
    fillManifestSelect(document.getElementById(`gif-${a}`)));

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

function loadActionSettings() {
  const e = game.entities[selectedEntityId];
  if (!e) return;
  const settings = e.actionSettings[previewAction];
  document.getElementById('prop-scale').value = settings.scale;
  document.getElementById('prop-offset-y').value = settings.offsetY;
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
  document.getElementById('action-selector').value = previewAction;
  loadActionSettings();
  document.getElementById('prop-position-x').value = e.positionX;

  ['idle','run','jump','bump','defeat'].forEach(a => {
    document.getElementById(`gif-${a}`).value = stripPrefix(e.gifs[a]);
  });
}

function createEntity() {
  const inp = document.getElementById('new-entity-id');
  const id = inp.value.trim().toLowerCase().replace(/\s+/g, '_');
  if (!id || game.entities[id]) return alert('ID inválido ou já existente.');

  const e = Schema.DEFAULT_ENTITY();
  e.id = id;
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

function updateActionProp(p, v) {
  if (!selectedEntityId) return;
  const e = game.entities[selectedEntityId];
  if (!e) return;
  e.actionSettings[previewAction][p] = v;
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

    let posX = e.positionX;
    el.style.left = `${posX}%`;

    const src = e.gifs[previewAction] || e.gifs.idle || e.gifs.run || '';
    if (src) {
      const img = document.createElement('img');
      img.src = resolveAsset(src);

      const settings = e.actionSettings[previewAction];
      const scale = settings.scale || 1;
      const offY = settings.offsetY || 0;
      img.style.transform = `scale(${scale}) translateY(${-offY}px)`;

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