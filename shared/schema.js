const SCHEMA_VERSION = "1.2.0";

const DEFAULT_ENTITY = () => ({
  id: "",
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
});

const DEFAULT_GAME = () => ({
  meta: { title: "Meu Jogo Anime", genre: "runner", version: SCHEMA_VERSION },
  scene: {
    backgroundImage: "",
    backgroundMode: "cover",
    layers: [
      { image: "", speed: 0.2 },
      { image: "", speed: 0.6 },
      { image: "", speed: 1.0 }
    ]
  },
  rules: {
    runner:  { worldSpeed: 300, spawnRate: 1400, playerX: 20 },
    fighting:{ maxHp: 100, damage: 10 }
  },
  entities: {}
});

function isObject(v){ return v !== null && typeof v === 'object' && !Array.isArray(v); }
function isString(v){ return typeof v === 'string'; }
function isNumber(v){ return typeof v === 'number' && isFinite(v); }
function isBool(v){ return typeof v === 'boolean'; }
function numberOrDefault(v, fallback, min, max) {
  if (!isNumber(v)) return fallback;
  return Math.min(max, Math.max(min, v));
}

function normalizeEntity(id, raw) {
  const b = DEFAULT_ENTITY();
  const e = isObject(raw) ? raw : {};
  return {
    id: id,
    role: ['player','enemy','prop'].includes(e.role) ? e.role : b.role,
    layer: ['background','ground','foreground'].includes(e.layer) ? e.layer : b.layer,
    hasDensity: isBool(e.hasDensity) ? e.hasDensity : b.hasDensity,
    extraLives: numberOrDefault(e.extraLives, b.extraLives, 0, 99),
    speed: numberOrDefault(e.speed, b.speed, 0, 1000),
    jumpHeight: numberOrDefault(e.jumpHeight, b.jumpHeight, 0, 500),
    floatTime: isNumber(e.floatTime) ? e.floatTime : b.floatTime,
    scale: numberOrDefault(e.scale, b.scale, 0.1, 5),
    offsetY: numberOrDefault(e.offsetY, b.offsetY, -300, 300),
    positionX: numberOrDefault(e.positionX, b.positionX, 0, 100),
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

function normalizeGame(data) {
  const b = DEFAULT_GAME();
  if (!isObject(data)) return b;

  const meta = isObject(data.meta) ? data.meta : {};
  const scene = isObject(data.scene) ? data.scene : {};
  const rules = isObject(data.rules) ? data.rules : {};
  const entities = isObject(data.entities) ? data.entities : {};

  const layersIn = Array.isArray(scene.layers) ? scene.layers : [];
  const layers = [0,1,2].map(i => {
    const l = isObject(layersIn[i]) ? layersIn[i] : {};
    return {
      image: isString(l.image) ? l.image : "",
      speed: isNumber(l.speed) ? l.speed : [0.2,0.6,1.0][i]
    };
  });

  const normalized = {
    meta: {
      title: isString(meta.title) && meta.title.trim() ? meta.title : b.meta.title,
      genre: ['runner','fighting'].includes(meta.genre) ? meta.genre : 'runner',
      version: SCHEMA_VERSION
    },
    scene: {
      backgroundImage: isString(scene.backgroundImage) ? scene.backgroundImage : "",
      backgroundMode: ['cover','contain','repeat'].includes(scene.backgroundMode)
        ? scene.backgroundMode : 'cover',
      layers
    },
    rules: {
      runner: {
        worldSpeed: numberOrDefault(
          rules.runner && rules.runner.worldSpeed,
          b.rules.runner.worldSpeed, 0, 2000
        ),
        spawnRate: numberOrDefault(
          rules.runner && rules.runner.spawnRate,
          b.rules.runner.spawnRate, 200, 10000
        )
      },
      fighting: {
        maxHp: numberOrDefault(
          rules.fighting && rules.fighting.maxHp,
          b.rules.fighting.maxHp, 10, 9999
        ),
        damage: numberOrDefault(
          rules.fighting && rules.fighting.damage,
          b.rules.fighting.damage, 1, 9999
        )
      }
    },
    entities: {}
  };

  Object.keys(entities).forEach(id => {
    if (!id) return;
    normalized.entities[id] = normalizeEntity(id, entities[id]);
  });

  return normalized;
}

function isValidGameFile(d){ return isObject(d) && isObject(d.meta) && isObject(d.entities); }

window.Schema = {
  SCHEMA_VERSION, DEFAULT_ENTITY, DEFAULT_GAME,
  normalizeEntity, normalizeGame, isValidGameFile
};