let game = Schema.DEFAULT_GAME();
let selectedEntityId = null;
let manifest = { files: [] };

window.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadManifest();
  const draft = Storage.loadDraft();
  game = draft || Schema.DEFAULT_GAME();
  bindEvents();
  refreshAll();
}

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

function bindEvents() {
  document.getElementById('game-title').addEventListener('input', e => {
    game.meta.title = e.target.value; saveDebounced();
  });
  document.getElementById('game-genre').addEventListener('change', e => {
    game.meta.genre = e.target.value; refreshAll(); saveDebounced();
  });

  document.getElementById('bg-select').addEventListener('change', e => {
    game.scene.backgroundImage = e.target.value ? `images/${e.target.value}` : "";
    renderScene(); saveDebounced();
  });
  document.getElementById('bg-mode').addEventListener('change', e => {
    game.scene.backgroundMode = e.target.value; renderScene(); saveDebounced();
  });

  [0,1,2].forEach(i => {
    document.getElementById(`layer-${i}-img`).addEventListener('change', e => {
      game.scene.layers[i].image = e.target.value ? `images/${e.target.value}` : "";
      renderScene(); saveDebounced();
    });
    document.getElementById(`layer-${i}-speed`).addEventListener('change', e => {
      game.scene.layers[i].speed = parseFloat(e.target.value) || 0;
      saveDebounced();
    });
  });

  document.getElementById('entity-selector').addEventListener('change', e => selectEntity(e.target.value));

  document.getElementById('prop-role').addEventListener('change', e => updateProp('role', e.target.value));
  document.getElementById('prop-layer').addEventListener('change', e => updateProp('layer', e.target.value));
  document.getElementById('prop-density').addEventListener('change', e => updateProp('hasDensity', e.target.checked));
  document.getElementById('prop-lives').addEventListener('change', e => updateProp('extraLives', parseInt(e.target.value)||0));
  document.getElementById('prop-speed').addEventListener('change', e => updateProp('speed', parseInt(e.target.value)||0));
  document.getElementById('prop-jump').addEventListener('change', e => updateProp('jumpHeight', parseInt(e.target.value)||0));
  document.getElementById('prop-scale').addEventListener('change', e => updateProp('scale', parseFloat(e.target.value)||1));
  document.getElementById('prop-offset-y').addEventListener('change', e => updateProp('offsetY', parseInt(e.target.value)||0));
  document.getElementById('prop-position-x').addEventListener('change', e => updateProp('positionX', parseInt(e.target.value)||0));

  ['idle','run','jump','attack','bump','defeat'].forEach(a => {
    document.getElementById(`gif-${a}`).addEventListener('change', e => {
      if (!selectedEntityId) return;
      const ent = game.entities[selectedEntityId]; if (!ent) return;
      ent.gifs[a] = e.target.value ? `images/${e.target.value}` : "";
      renderStage(); saveDebounced();
    });
  });

  document.getElementById('rule-runner-speed').addEventListener('change', e => {
    game.rules.runner.worldSpeed = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-runner-spawn').addEventListener('change', e => {
    game.rules.runner.spawnRate = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-fight-hp').addEventListener('change', e => {
    game.rules.fighting.maxHp = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-fight-dmg').addEventListener('change', e => {
    game.rules.fighting.damage = parseInt(e.target.value)||0; saveDebounced();
  });

  document.getElementById('import-file').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      game = await Storage.importGameFromFile(f);
      selectedEntityId = null;
      refreshAll(); Storage.saveDraft(game);
    } catch (err) { alert('Erro: ' + err.message); }
    e.target.value = '';
  });
}

let draftTimer = null;
function saveDebounced() {
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => Storage.saveDraft(game), 350);
}

function fillManifestSelect(sel) {
  sel.innerHTML = '';
  const o = document.createElement('option'); o.value=''; o.innerText='-- Nenhum --';
  sel.appendChild(o);
  manifest.files.forEach(n => {
    const opt = document.createElement('option'); opt.value=n; opt.innerText=n;
    sel.appendChild(opt);
  });
}

function stripPrefix(p){ return p ? p.replace(/^images\//,'') : ''; }
function resolveAsset(p){ return p && p.startsWith('images/') ? '../'+p : p; }

function refreshAll() {
  fillManifestSelect(document.getElementById('bg-select'));
  [0,1,2].forEach(i => fillManifestSelect(document.getElementById(`layer-${i}-img`)));
  ['idle','run','jump','attack','bump','defeat'].forEach(a =>
    fillManifestSelect(document.getElementById(`gif-${a}`)));

  document.getElementById('game-title').value = game.meta.title;
  document.getElementById('game-genre').value = game.meta.genre;
  document.getElementById('bg-mode').value = game.scene.backgroundMode;
  document.getElementById('bg-select').value = stripPrefix(game.scene.backgroundImage);

  [0,1,2].forEach(i => {
    document.getElementById(`layer-${i}-img`).value = stripPrefix(game.scene.layers[i].image);
    document.getElementById(`layer-${i}-speed`).value = game.scene.layers[i].speed;
  });

  document.getElementById('rule-runner-speed').value = game.rules.runner.worldSpeed;
  document.getElementById('rule-runner-spawn').value = game.rules.runner.spawnRate;
  document.getElementById('rule-fight-hp').value = game.rules.fighting.maxHp;
  document.getElementById('rule-fight-dmg').value = game.rules.fighting.damage;

  document.getElementById('layers-block').style.display =
    game.meta.genre === 'runner' ? 'block' : 'none';

  populateEntitySelector();
  applyGenreLayout();
  renderScene();
  renderStage();
  refreshProjectList();
}

function removeBackground() {
  game.scene.backgroundImage = '';
  document.getElementById('bg-select').value = '';
  renderScene(); saveDebounced();
}

function renderScene() {
  const bg = document.getElementById('background-layer');
  const genre = game.meta.genre;

  if (genre === 'runner') {
    bg.style.backgroundImage = 'none';
    [0,1,2].forEach(i => {
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      const l = game.scene.layers[i];
      el.style.backgroundImage = l.image ? `url('${resolveAsset(l.image)}')` : 'none';
      el.style.backgroundRepeat = 'repeat-x';
      el.style.backgroundSize = 'auto 100%';
      el.style.backgroundPositionX = '0px';
    });
  } else {
    [0,1,2].forEach(i => {
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      el.style.backgroundImage = 'none';
    });
    if (game.scene.backgroundImage) {
      bg.style.backgroundImage = `url('${resolveAsset(game.scene.backgroundImage)}')`;
      bg.style.backgroundRepeat =
        game.scene.backgroundMode === 'repeat' ? 'repeat' : 'no-repeat';
      bg.style.backgroundSize =
        game.scene.backgroundMode === 'repeat' ? 'auto' : game.scene.backgroundMode;
    } else {
      bg.style.backgroundImage = 'none';
    }
  }
}

function populateEntitySelector() {
  const sel = document.getElementById('entity-selector');
  sel.innerHTML = '';
  const keys = Object.keys(game.entities);
  if (keys.length === 0) {
    selectedEntityId = null;
    const o = document.createElement('option'); o.innerText='-- Nenhum --'; sel.appendChild(o);
    disableEntityPanels(true); return;
  }
  disableEntityPanels(false);
  if (!selectedEntityId || !game.entities[selectedEntityId]) selectedEntityId = keys[0];
  keys.forEach(id => {
    const o = document.createElement('option');
    o.value = id; o.innerText = `${id} (${game.entities[id].role})`;
    sel.appendChild(o);
  });
  sel.value = selectedEntityId;
  loadEntityPanel();
}

function disableEntityPanels(d) {
  document.getElementById('group-properties').classList.toggle('disabled', d);
  document.getElementById('group-gifs').classList.toggle('disabled', d);
  document.getElementById('btn-delete-entity').style.display = d ? 'none':'block';
}

function selectEntity(id){ if(!game.entities[id])return; selectedEntityId=id; loadEntityPanel(); }

function loadEntityPanel() {
  const e = game.entities[selectedEntityId]; if (!e) return;
  document.getElementById('prop-role').value = e.role;
  document.getElementById('prop-layer').value = e.layer;
  document.getElementById('prop-density').checked = e.hasDensity;
  document.getElementById('prop-lives').value = e.extraLives;
  document.getElementById('prop-speed').value = e.speed;
  document.getElementById('prop-jump').value = e.jumpHeight;
  document.getElementById('prop-scale').value = e.scale;
  document.getElementById('prop-offset-y').value = e.offsetY;
  document.getElementById('prop-position-x').value = e.positionX;
  ['idle','run','jump','attack','bump','defeat'].forEach(a =>
    document.getElementById(`gif-${a}`).value = stripPrefix(e.gifs[a]));
}

function createEntity() {
  const inp = document.getElementById('new-entity-id');
  const id = inp.value.trim().toLowerCase().replace(/\s+/g,'_');
  if (!id || game.entities[id]) return alert('ID inválido ou já existente.');
  const e = Schema.DEFAULT_ENTITY(); e.id = id;
  game.entities[id] = e;
  inp.value=''; selectedEntityId = id;
  populateEntitySelector(); renderStage(); saveDebounced();
}

function deleteEntity() {
  if (!selectedEntityId || !game.entities[selectedEntityId]) return;
  if (!confirm(`Excluir '${selectedEntityId}'?`)) return;
  delete game.entities[selectedEntityId];
  selectedEntityId = null;
  populateEntitySelector(); renderStage(); saveDebounced();
}

function updateProp(p, v) {
  if (!selectedEntityId) return;
  const e = game.entities[selectedEntityId]; if (!e) return;
  e[p] = v; renderStage(); saveDebounced();
}

function renderStage() {
  const c = document.getElementById('entities-container');
  c.innerHTML = '';
  const keys = Object.keys(game.entities);
  const genre = game.meta.genre;

  keys.forEach((id, index) => {
    const e = game.entities[id];
    const el = document.createElement('div');
    el.className = `sprite-container layer-${e.layer}`;

    let posX = e.positionX;
    let flip = false;
    if (genre === 'fighting') {
      posX = index === 0 ? 25 : 70;
      flip = (index === 1);
    }

    el.style.left = `${posX}%`;

    const src = e.gifs.run || e.gifs.idle || '';
    if (src) {
      const img = document.createElement('img');
      img.src = resolveAsset(src);
      const scale = e.scale || 1;
      const offY = e.offsetY || 0;
      const flipPart = flip ? ' scaleX(-1)' : '';
      img.style.transform = `scale(${scale}) translateY(${-offY}px)${flipPart}`;
      el.appendChild(img);
    }
    c.appendChild(el);

    if (genre === 'fighting') {
      if (index === 0) document.getElementById('p1-name').innerText = e.id.toUpperCase();
      if (index === 1) document.getElementById('p2-name').innerText = e.id.toUpperCase();
    }
  });
}

function applyGenreLayout() {
  document.getElementById('game-stage').className = `mode-${game.meta.genre}`;
  document.getElementById('fighting-ui').classList.toggle('hidden', game.meta.genre !== 'fighting');
}

function saveProjectAs() {
  const name = prompt('Nome da versão:', `v${Storage.listProjects().length+1}`);
  if (!name) return;
  Storage.saveProject(name, game); refreshProjectList();
}

function exportGame(){ Storage.exportGameToFile(game); }

function resetProject() {
  if (!confirm('Apagar projeto atual?')) return;
  game = Schema.DEFAULT_GAME(); selectedEntityId = null;
  Storage.clearDraft(); refreshAll();
}

function refreshProjectList() {
  const sel = document.getElementById('project-list'); sel.innerHTML='';
  const list = Storage.listProjects();
  if (list.length === 0) {
    const o = document.createElement('option'); o.value=''; o.innerText='-- Nenhuma --';
    sel.appendChild(o); return;
  }
  list.forEach(p => {
    const o = document.createElement('option');
    o.value = p.name;
    o.innerText = `${p.name} (${new Date(p.savedAt).toLocaleString()})`;
    sel.appendChild(o);
  });
}

function loadSelectedProject() {
  const n = document.getElementById('project-list').value; if (!n) return;
  const g = Storage.loadProject(n); if (!g) return alert('Não encontrada.');
  game = g; selectedEntityId = null; refreshAll(); Storage.saveDraft(game);
}

function deleteSelectedProject() {
  const n = document.getElementById('project-list').value; if (!n) return;
  if (!confirm(`Apagar "${n}"?`)) return;
  Storage.deleteProject(n); refreshProjectList();
}

function playGame() {
  Storage.saveDraft(game);
  window.open('../player/index.html', '_blank');
}/* =========================================================
   editor/editor.js — IDE completa
   ========================================================= */

let game = Schema.DEFAULT_GAME();
let selectedEntityId = null;
let manifest = { files: [] };

/* ---------- BOOT ---------- */

window.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadManifest();
  const draft = Storage.loadDraft();
  game = draft || Schema.DEFAULT_GAME();
  bindEvents();
  refreshAll();
}

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

/* ---------- EVENTOS ---------- */

function bindEvents() {
  // Meta
  document.getElementById('game-title').addEventListener('input', e => {
    game.meta.title = e.target.value; saveDebounced();
  });
  document.getElementById('game-genre').addEventListener('change', e => {
    game.meta.genre = e.target.value; refreshAll(); saveDebounced();
  });

  // Fundo estático
  document.getElementById('bg-select').addEventListener('change', e => {
    game.scene.backgroundImage = e.target.value ? `images/${e.target.value}` : "";
    renderScene(); saveDebounced();
  });
  document.getElementById('bg-mode').addEventListener('change', e => {
    game.scene.backgroundMode = e.target.value; renderScene(); saveDebounced();
  });

  // Camadas de paralaxe
  [0,1,2].forEach(i => {
    document.getElementById(`layer-${i}-img`).addEventListener('change', e => {
      game.scene.layers[i].image = e.target.value ? `images/${e.target.value}` : "";
      renderScene(); saveDebounced();
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

  // Entidade
  document.getElementById('entity-selector').addEventListener('change', e =>
    selectEntity(e.target.value));

  // Propriedades
  document.getElementById('prop-role').addEventListener('change', e => updateProp('role', e.target.value));
  document.getElementById('prop-layer').addEventListener('change', e => updateProp('layer', e.target.value));
  document.getElementById('prop-density').addEventListener('change', e => updateProp('hasDensity', e.target.checked));
  document.getElementById('prop-lives').addEventListener('change', e => updateProp('extraLives', parseInt(e.target.value)||0));
  document.getElementById('prop-speed').addEventListener('change', e => updateProp('speed', parseInt(e.target.value)||0));
  document.getElementById('prop-jump').addEventListener('change', e => updateProp('jumpHeight', parseInt(e.target.value)||0));
  document.getElementById('prop-scale').addEventListener('change', e => updateProp('scale', parseFloat(e.target.value)||1));
  document.getElementById('prop-offset-y').addEventListener('change', e => updateProp('offsetY', parseInt(e.target.value)||0));
  document.getElementById('prop-position-x').addEventListener('change', e => updateProp('positionX', parseInt(e.target.value)||0));

  // GIFs
  ['idle','run','jump','attack','bump','defeat'].forEach(a => {
    document.getElementById(`gif-${a}`).addEventListener('change', e => {
      if (!selectedEntityId) return;
      const ent = game.entities[selectedEntityId]; if (!ent) return;
      ent.gifs[a] = e.target.value ? `images/${e.target.value}` : "";
      renderStage(); saveDebounced();
    });
  });

  // Regras
  document.getElementById('rule-runner-speed').addEventListener('change', e => {
    game.rules.runner.worldSpeed = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-runner-spawn').addEventListener('change', e => {
    game.rules.runner.spawnRate = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-fight-hp').addEventListener('change', e => {
    game.rules.fighting.maxHp = parseInt(e.target.value)||0; saveDebounced();
  });
  document.getElementById('rule-fight-dmg').addEventListener('change', e => {
    game.rules.fighting.damage = parseInt(e.target.value)||0; saveDebounced();
  });

  // Import
  document.getElementById('import-file').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      game = await Storage.importGameFromFile(f);
      selectedEntityId = null;
      refreshAll(); Storage.saveDraft(game);
    } catch (err) { alert('Erro: ' + err.message); }
    e.target.value = '';
  });
}

let draftTimer = null;
function saveDebounced() {
  clearTimeout(draftTimer);
  draftTimer = setTimeout(() => Storage.saveDraft(game), 350);
}

/* ---------- HELPERS ---------- */

function stripPrefix(p){ return p ? p.replace(/^images\//,'') : ''; }
function resolveAsset(p){ return p && p.startsWith('images/') ? '../'+p : p; }

function fillManifestSelect(sel) {
  sel.innerHTML = '';
  const o = document.createElement('option');
  o.value = ''; o.innerText = '-- Nenhum --';
  sel.appendChild(o);
  manifest.files.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n; opt.innerText = n;
    sel.appendChild(opt);
  });
}

/* ---------- REFRESH GERAL ---------- */

function refreshAll() {
  fillManifestSelect(document.getElementById('bg-select'));
  [0,1,2].forEach(i => fillManifestSelect(document.getElementById(`layer-${i}-img`)));
  ['idle','run','jump','attack','bump','defeat'].forEach(a =>
    fillManifestSelect(document.getElementById(`gif-${a}`)));

  document.getElementById('game-title').value = game.meta.title;
  document.getElementById('game-genre').value = game.meta.genre;
  document.getElementById('bg-mode').value = game.scene.backgroundMode;
  document.getElementById('bg-select').value = stripPrefix(game.scene.backgroundImage);

  [0,1,2].forEach(i => {
    document.getElementById(`layer-${i}-img`).value = stripPrefix(game.scene.layers[i].image);
    document.getElementById(`layer-${i}-speed`).value = game.scene.layers[i].speed;
  });

  document.getElementById('rule-runner-speed').value = game.rules.runner.worldSpeed;
  document.getElementById('rule-runner-spawn').value = game.rules.runner.spawnRate;
  document.getElementById('rule-fight-hp').value = game.rules.fighting.maxHp;
  document.getElementById('rule-fight-dmg').value = game.rules.fighting.damage;

  document.getElementById('layers-block').style.display =
    game.meta.genre === 'runner' ? 'block' : 'none';

  populateEntitySelector();
  applyGenreLayout();
  renderScene();
  renderStage();
  refreshProjectList();
}

/* ---------- CENÁRIO ---------- */

function removeBackground() {
  game.scene.backgroundImage = '';
  document.getElementById('bg-select').value = '';
  [0,1,2].forEach(i => {
    game.scene.layers[i].image = '';
    const sel = document.getElementById(`layer-${i}-img`);
    if (sel) sel.value = '';
    const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
    if (el) el.style.backgroundImage = 'none';
  });
  renderScene();
  saveDebounced();
}

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

function removeAllLayers() {
  [0,1,2].forEach(i => removeLayer(i));
}

function renderScene() {
  const bg = document.getElementById('background-layer');
  const genre = game.meta.genre;

  if (genre === 'runner') {
    bg.style.backgroundImage = 'none';
    [0,1,2].forEach(i => {
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      const l = game.scene.layers[i];
      el.style.backgroundImage = l.image ? `url('${resolveAsset(l.image)}')` : 'none';
      el.style.backgroundRepeat = 'repeat-x';
      el.style.backgroundSize = 'auto 100%';
      el.style.backgroundPositionX = '0px';
    });
  } else {
    [0,1,2].forEach(i => {
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      el.style.backgroundImage = 'none';
    });
    if (game.scene.backgroundImage) {
      bg.style.backgroundImage = `url('${resolveAsset(game.scene.backgroundImage)}')`;
      bg.style.backgroundRepeat =
        game.scene.backgroundMode === 'repeat' ? 'repeat' : 'no-repeat';
      bg.style.backgroundSize =
        game.scene.backgroundMode === 'repeat' ? 'auto' : game.scene.backgroundMode;
    } else {
      bg.style.backgroundImage = 'none';
    }
  }
}

/* ---------- ENTIDADES ---------- */

function populateEntitySelector() {
  const sel = document.getElementById('entity-selector');
  sel.innerHTML = '';
  const keys = Object.keys(game.entities);
  if (keys.length === 0) {
    selectedEntityId = null;
    const o = document.createElement('option');
    o.innerText = '-- Nenhum --'; sel.appendChild(o);
    disableEntityPanels(true); return;
  }
  disableEntityPanels(false);
  if (!selectedEntityId || !game.entities[selectedEntityId]) selectedEntityId = keys[0];
  keys.forEach(id => {
    const o = document.createElement('option');
    o.value = id; o.innerText = `${id} (${game.entities[id].role})`;
    sel.appendChild(o);
  });
  sel.value = selectedEntityId;
  loadEntityPanel();
}

function disableEntityPanels(d) {
  document.getElementById('group-properties').classList.toggle('disabled', d);
  document.getElementById('group-gifs').classList.toggle('disabled', d);
  document.getElementById('btn-delete-entity').style.display = d ? 'none':'block';
}

function selectEntity(id){ if(!game.entities[id])return; selectedEntityId=id; loadEntityPanel(); }

function loadEntityPanel() {
  const e = game.entities[selectedEntityId]; if (!e) return;
  document.getElementById('prop-role').value = e.role;
  document.getElementById('prop-layer').value = e.layer;
  document.getElementById('prop-density').checked = e.hasDensity;
  document.getElementById('prop-lives').value = e.extraLives;
  document.getElementById('prop-speed').value = e.speed;
  document.getElementById('prop-jump').value = e.jumpHeight;
  document.getElementById('prop-scale').value = e.scale;
  document.getElementById('prop-offset-y').value = e.offsetY;
  document.getElementById('prop-position-x').value = e.positionX;
  ['idle','run','jump','attack','bump','defeat'].forEach(a =>
    document.getElementById(`gif-${a}`).value = stripPrefix(e.gifs[a]));
}

function createEntity() {
  const inp = document.getElementById('new-entity-id');
  const id = inp.value.trim().toLowerCase().replace(/\s+/g,'_');
  if (!id || game.entities[id]) return alert('ID inválido ou já existente.');
  const e = Schema.DEFAULT_ENTITY(); e.id = id;
  game.entities[id] = e;
  inp.value=''; selectedEntityId = id;
  populateEntitySelector(); renderStage(); saveDebounced();
}

function deleteEntity() {
  if (!selectedEntityId || !game.entities[selectedEntityId]) return;
  if (!confirm(`Excluir '${selectedEntityId}'?`)) return;
  delete game.entities[selectedEntityId];
  selectedEntityId = null;
  populateEntitySelector(); renderStage(); saveDebounced();
}

function updateProp(p, v) {
  if (!selectedEntityId) return;
  const e = game.entities[selectedEntityId]; if (!e) return;
  e[p] = v; renderStage(); saveDebounced();
}

/* ---------- RENDER DO PALCO ---------- */

function renderStage() {
  const c = document.getElementById('entities-container');
  c.innerHTML = '';
  const keys = Object.keys(game.entities);
  const genre = game.meta.genre;

  keys.forEach((id, index) => {
    const e = game.entities[id];
    const el = document.createElement('div');
    el.className = `sprite-container layer-${e.layer}`;

    let posX = e.positionX;
    let flip = false;
    if (genre === 'fighting') {
      posX = index === 0 ? 25 : 70;
      flip = (index === 1);
    }
    el.style.left = `${posX}%`;

    const src = e.gifs.run || e.gifs.idle || '';
    if (src) {
      const img = document.createElement('img');
      img.src = resolveAsset(src);
      const scale = e.scale || 1;
      const offY = e.offsetY || 0;
      const flipPart = flip ? ' scaleX(-1)' : '';
      img.style.transform = `scale(${scale}) translateY(${-offY}px)${flipPart}`;
      el.appendChild(img);
    }
    c.appendChild(el);

    if (genre === 'fighting') {
      if (index === 0) document.getElementById('p1-name').innerText = e.id.toUpperCase();
      if (index === 1) document.getElementById('p2-name').innerText = e.id.toUpperCase();
    }
  });
}

function applyGenreLayout() {
  document.getElementById('game-stage').className = `mode-${game.meta.genre}`;
  document.getElementById('fighting-ui').classList.toggle('hidden', game.meta.genre !== 'fighting');
}

/* ---------- PROJETO ---------- */

function saveProjectAs() {
  const name = prompt('Nome da versão:', `v${Storage.listProjects().length+1}`);
  if (!name) return;
  Storage.saveProject(name, game); refreshProjectList();
}

function exportGame(){ Storage.exportGameToFile(game); }

function resetProject() {
  if (!confirm('Apagar projeto atual?')) return;
  game = Schema.DEFAULT_GAME(); selectedEntityId = null;
  Storage.clearDraft(); refreshAll();
}

function refreshProjectList() {
  const sel = document.getElementById('project-list'); sel.innerHTML='';
  const list = Storage.listProjects();
  if (list.length === 0) {
    const o = document.createElement('option'); o.value=''; o.innerText='-- Nenhuma --';
    sel.appendChild(o); return;
  }
  list.forEach(p => {
    const o = document.createElement('option');
    o.value = p.name;
    o.innerText = `${p.name} (${new Date(p.savedAt).toLocaleString()})`;
    sel.appendChild(o);
  });
}

function loadSelectedProject() {
  const n = document.getElementById('project-list').value; if (!n) return;
  const g = Storage.loadProject(n); if (!g) return alert('Não encontrada.');
  game = g; selectedEntityId = null; refreshAll(); Storage.saveDraft(game);
}

function deleteSelectedProject() {
  const n = document.getElementById('project-list').value; if (!n) return;
  if (!confirm(`Apagar "${n}"?`)) return;
  Storage.deleteProject(n); refreshProjectList();
}

/* ---------- PLAY ---------- */

function playGame() {
  Storage.saveDraft(game);
  window.open('../player/index.html', '_blank');
}