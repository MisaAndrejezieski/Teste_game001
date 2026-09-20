/* =========================================================
   shared/schema.js
   Fonte da verdade do formato do projeto (gameObject).
   Usado tanto pela IDE quanto pelo Player.
   ========================================================= */

const SCHEMA_VERSION = "1.1.0";

/* Estrutura padrão de uma entidade nova */
const DEFAULT_ENTITY = () => ({
  id: "",
  role: "player",          // player | enemy | prop
  layer: "foreground",     // background | ground | foreground
  hasDensity: true,
  extraLives: 3,
  speed: 200,
  jumpHeight: 150,
  floatTime: 0,
  scale: 1,
  offsetY: 0,
  positionX: 20,
  gifs: { idle: "", run: "", jump: "", attack: "", bump: "", defeat: "" }
});

/* Estrutura padrão do projeto inteiro */
const DEFAULT_GAME = () => ({
  meta: {
    title: "Meu Jogo Anime",
    genre: "runner",       // runner | fighting | racing
    version: SCHEMA_VERSION
  },
  scene: {
    backgroundImage: "",
    backgroundMode: "cover"
  },
  entities: {}
});

/* ---------- Helpers de validação ---------- */

function isObject(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
function isString(v) { return typeof v === 'string'; }
function isNumber(v) { return typeof v === 'number' && isFinite(v); }
function isBool(v)   { return typeof v === 'boolean'; }

/* Garante que uma entidade tenha todos os campos esperados */
function normalizeEntity(id, raw) {
  const base = DEFAULT_ENTITY();
  const e = isObject(raw) ? raw : {};

  return {
    id: id,
    role: ['player','enemy','prop'].includes(e.role) ? e.role : base.role,
    layer: ['background','ground','foreground'].includes(e.layer) ? e.layer : base.layer,
    hasDensity: isBool(e.hasDensity) ? e.hasDensity : base.hasDensity,
    extraLives: isNumber(e.extraLives) ? e.extraLives : base.extraLives,
    speed: isNumber(e.speed) ? e.speed : base.speed,
    jumpHeight: isNumber(e.jumpHeight) ? e.jumpHeight : base.jumpHeight,
    floatTime: isNumber(e.floatTime) ? e.floatTime : base.floatTime,
    scale: isNumber(e.scale) ? e.scale : base.scale,
    offsetY: isNumber(e.offsetY) ? e.offsetY : base.offsetY,
    positionX: isNumber(e.positionX) ? e.positionX : base.positionX,
    gifs: {
      idle:   (e.gifs && isString(e.gifs.idle))   ? e.gifs.idle   : "",
      run:    (e.gifs && isString(e.gifs.run))    ? e.gifs.run    : "",
      jump:   (e.gifs && isString(e.gifs.jump))   ? e.gifs.jump   : "",
      attack: (e.gifs && isString(e.gifs.attack)) ? e.gifs.attack : "",
      bump:   (e.gifs && isString(e.gifs.bump))   ? e.gifs.bump   : "",
      defeat: (e.gifs && isString(e.gifs.defeat)) ? e.gifs.defeat : ""
    }
  };
}

/* Normaliza o gameObject completo, preenchendo defaults */
function normalizeGame(data) {
  const base = DEFAULT_GAME();
  if (!isObject(data)) return base;

  const meta = isObject(data.meta) ? data.meta : {};
  const scene = isObject(data.scene) ? data.scene : {};
  const entities = isObject(data.entities) ? data.entities : {};

  const normalized = {
    meta: {
      title: isString(meta.title) && meta.title.trim() ? meta.title : base.meta.title,
      genre: ['runner','fighting','racing'].includes(meta.genre) ? meta.genre : base.meta.genre,
      version: SCHEMA_VERSION
    },
    scene: {
      backgroundImage: isString(scene.backgroundImage) ? scene.backgroundImage : "",
      backgroundMode: ['cover','contain','repeat'].includes(scene.backgroundMode)
        ? scene.backgroundMode : base.scene.backgroundMode
    },
    entities: {}
  };

  Object.keys(entities).forEach(id => {
    if (!id) return;
    normalized.entities[id] = normalizeEntity(id, entities[id]);
  });

  return normalized;
}

/* Validação mínima antes de aceitar carregar um arquivo */
function isValidGameFile(data) {
  return isObject(data) && isObject(data.meta) && isObject(data.entities);
}

/* Exporta para os dois lados (IDE e Player) */
window.Schema = {
  SCHEMA_VERSION,
  DEFAULT_ENTITY,
  DEFAULT_GAME,
  normalizeEntity,
  normalizeGame,
  isValidGameFile
};