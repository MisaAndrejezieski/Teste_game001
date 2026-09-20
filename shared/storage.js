/* =========================================================
   shared/storage.js
   Persistência do projeto: localStorage + import/export .json
   Usa window.Schema para normalizar tudo que entra e sai.
   ========================================================= */

const STORAGE_KEY_DRAFT   = "ags_draft";         // rascunho de trabalho
const STORAGE_KEY_PROJECTS = "ags_projects";     // lista de snapshots salvos

/* ---------- Rascunho (auto-save) ---------- */

function saveDraft(game) {
  try {
    const normalized = window.Schema.normalizeGame(game);
    localStorage.setItem(STORAGE_KEY_DRAFT, JSON.stringify(normalized));
    return true;
  } catch (e) {
    console.warn("Falha ao salvar rascunho:", e);
    return false;
  }
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_DRAFT);
    if (!raw) return null;
    return window.Schema.normalizeGame(JSON.parse(raw));
  } catch (e) {
    console.warn("Falha ao carregar rascunho:", e);
    return null;
  }
}

function clearDraft() {
  localStorage.removeItem(STORAGE_KEY_DRAFT);
}

/* ---------- Snapshots versionados (o "GitHub Desktop" simples) ---------- */

function listProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PROJECTS);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveProject(name, game) {
  const list = listProjects();
  const snapshot = {
    name: name || `snapshot_${Date.now()}`,
    savedAt: new Date().toISOString(),
    data: window.Schema.normalizeGame(game)
  };
  // Se já existe um com o mesmo nome, substitui
  const idx = list.findIndex(p => p.name === snapshot.name);
  if (idx >= 0) list[idx] = snapshot;
  else list.push(snapshot);

  localStorage.setItem(STORAGE_KEY_PROJECTS, JSON.stringify(list));
  return snapshot;
}

function loadProject(name) {
  const list = listProjects();
  const found = list.find(p => p.name === name);
  return found ? window.Schema.normalizeGame(found.data) : null;
}

function deleteProject(name) {
  const list = listProjects().filter(p => p.name !== name);
  localStorage.setItem(STORAGE_KEY_PROJECTS, JSON.stringify(list));
}

/* ---------- Import / Export de arquivos .json ---------- */

function exportGameToFile(game) {
  const normalized = window.Schema.normalizeGame(game);
  const safeName = (normalized.meta.title || "projeto")
    .toLowerCase()
    .replace(/[^a-z0-9_\-]/gi, '_')
    .replace(/_+/g, '_');

  const blob = new Blob(
    [JSON.stringify(normalized, null, 2)],
    { type: "application/json" }
  );
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${safeName}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function importGameFromFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (!window.Schema.isValidGameFile(parsed)) {
          reject(new Error("Arquivo inválido: falta meta ou entities."));
          return;
        }
        resolve(window.Schema.normalizeGame(parsed));
      } catch (err) {
        reject(new Error("Erro ao ler JSON: " + err.message));
      }
    };
    reader.onerror = () => reject(new Error("Falha ao ler o arquivo."));
    reader.readAsText(file);
  });
}

/* Exporta para o window */
window.Storage = {
  saveDraft, loadDraft, clearDraft,
  listProjects, saveProject, loadProject, deleteProject,
  exportGameToFile, importGameFromFile
};