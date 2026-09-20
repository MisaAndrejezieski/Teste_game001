const SCHEMA_VERSION = "1.3.0";

const DEFAULT_ENTITY = () => ({
  id: "",
  role: "player",
  layer: "foreground",
  hasDensity: true,
  extraLives: 3,
  speed: 200,
  spawnSide: "right",
  flip: false,
  jumpHeight: 150,
  floatTime: 0,
  scale: 1,
  offsetY: 0,
  positionX: 20,
  actions: {
    idle: { gif: "", scale: 1, positionX: 20, positionY: 0 },
    run: { gif: "", scale: 1, positionX: 20, positionY: 0 },
    jump: { gif: "", scale: 1, positionX: 20, positionY: 0 },
    bump: { gif: "", scale: 1, positionX: 20, positionY: 0 },
    defeat: { gif: "", scale: 1, positionX: 20, positionY: 0 }
  }
});

const DEFAULT_GAME = () => ({
  meta: { title: "Meu Jogo Anime", genre: "runner", version: SCHEMA_VERSION },
  scene: {
    backgroundImage: "",
    backgroundMode: "cover",
    layers: [
      { image: "images/cenario001.jpg", speed: 0.2 },
      { image: "images/cenario002.jpg", speed: 0.6 },
      { image: "images/cenario003.png", speed: 1.0 }
    ]
  },
  rules: {
    runner: { worldSpeed: 300, spawnRate: 1400, playerX: 20 }
  },
  entities: {
    jogador: {
      id: "jogador",
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
      actions: {
        idle: { gif: "images/muse-dash-buro_ tela principal.gif", scale: 1, positionX: 20, positionY: 0 },
        run: { gif: "images/muse-dash-buro_anda_normal.gif", scale: 1, positionX: 20, positionY: 0 },
        jump: { gif: "images/muse-dash-buro_primeira_imagem_do_pulo.gif", scale: 1, positionX: 20, positionY: 0 },
        bump: { gif: "images/muse-dash-buro_primeira_imagem_do_esbarrao.gif", scale: 1, positionX: 20, positionY: 0 },
        defeat: { gif: "images/muse-dash-marija_morte.gif", scale: 1, positionX: 20, positionY: 0 }
      }
    },
    obstaculo: {
      id: "obstaculo",
      role: "enemy",
      layer: "foreground",
      hasDensity: true,
      extraLives: 1,
      speed: 0,
      spawnSide: "right",
      flip: true,
      jumpHeight: 0,
      floatTime: 0,
      scale: 1,
      offsetY: 0,
      positionX: 100,
      actions: {
        idle: { gif: "images/inim004.gif", scale: 1, positionX: 100, positionY: 0 },
        run: { gif: "images/inim004.gif", scale: 1, positionX: 100, positionY: 0 },
        jump: { gif: "", scale: 1, positionX: 100, positionY: 0 },
        bump: { gif: "", scale: 1, positionX: 100, positionY: 0 },
        defeat: { gif: "", scale: 1, positionX: 100, positionY: 0 }
      }
    }
  }
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
  const spawnSide = ['left', 'right'].includes(e.spawnSide) ? e.spawnSide : b.spawnSide;
  const actions = {};
  const legacyGifs = isObject(e.gifs) ? e.gifs : {};
  const legacySettings = isObject(e.actionSettings) ? e.actionSettings : {};
  const sourceActions = isObject(e.actions) ? e.actions : {};
  const actionNames = new Set([
    ...Object.keys(b.actions), ...Object.keys(sourceActions),
    ...Object.keys(legacyGifs), ...Object.keys(legacySettings)
  ]);
  actionNames.forEach(action => {
    if (!/^[a-zA-Z0-9_-]+$/.test(action)) return;
    const rawAction = isObject(sourceActions[action]) ? sourceActions[action] : {};
    const legacyAction = isObject(legacySettings[action]) ? legacySettings[action] : {};
    const defaultAction = b.actions[action] || {
      gif: "", scale: e.scale, positionX: e.positionX, positionY: e.offsetY
    };
    const legacyScale = isNumber(e.scale) ? e.scale : (defaultAction.scale || 1);
    const legacyPositionX = isNumber(e.positionX) ? e.positionX : (defaultAction.positionX || 20);
    const legacyPositionY = isNumber(e.offsetY) ? e.offsetY : (defaultAction.positionY || 0);
    actions[action] = {
      gif: isString(rawAction.gif) ? rawAction.gif
        : (isString(legacyGifs[action]) ? legacyGifs[action] : defaultAction.gif),
      scale: numberOrDefault(rawAction.scale, numberOrDefault(legacyAction.scale,
        legacyScale, 0.1, 5), 0.1, 5),
      positionX: numberOrDefault(rawAction.positionX, legacyPositionX, 0, 100),
      positionY: numberOrDefault(rawAction.positionY,
        numberOrDefault(legacyAction.offsetY, legacyPositionY, -300, 300), -300, 300)
    };
  });
  return {
    id: id,
    role: ['player','enemy','prop'].includes(e.role) ? e.role : b.role,
    layer: ['background','ground','foreground'].includes(e.layer) ? e.layer : b.layer,
    hasDensity: isBool(e.hasDensity) ? e.hasDensity : b.hasDensity,
    extraLives: numberOrDefault(e.extraLives, b.extraLives, 0, 99),
    speed: numberOrDefault(e.speed, b.speed, 0, 1000),
    spawnSide,
    flip: isBool(e.flip) ? e.flip : (e.role === 'enemy' && spawnSide === 'right'),
    jumpHeight: numberOrDefault(e.jumpHeight, b.jumpHeight, 0, 300),
    floatTime: isNumber(e.floatTime) ? e.floatTime : b.floatTime,
    scale: numberOrDefault(e.scale, b.scale, 0.1, 5),
    offsetY: numberOrDefault(e.offsetY, b.offsetY, -300, 300),
    positionX: numberOrDefault(e.positionX, b.positionX, 0, 100),
    actions
  };
}

function normalizeGame(data) {
  const b = DEFAULT_GAME();
  if (!isObject(data)) return b;

  const meta = isObject(data.meta) ? data.meta : {};
  const isLegacyProject = meta.version !== SCHEMA_VERSION;
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
      genre: 'runner',
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
      }
    },
    entities: {}
  };

  const ids = Object.keys(entities).filter(Boolean);
  const preferredPlayer = ids.includes('jogador') &&
    normalizeEntity('jogador', entities.jogador).role === 'player'
    ? 'jogador'
    : ids.find(id => normalizeEntity(id, entities[id]).role === 'player') ||
      ids[0];

  ids.forEach(id => {
    if (!id) return;
    const entity = normalizeEntity(id, entities[id]);
    if (id === preferredPlayer) {
      entity.role = 'player';
    } else {
      entity.role = 'enemy';
      entity.spawnSide = 'right';
      if (isLegacyProject) {
        entity.flip = true;
      }
      Object.values(entity.actions).forEach(action => {
        action.positionX = 100;
      });
    }
    normalized.entities[id] = entity;
  });

  return normalized;
}

function isValidGameFile(d){ return isObject(d) && isObject(d.meta) && isObject(d.entities); }

window.Schema = {
  SCHEMA_VERSION, DEFAULT_ENTITY, DEFAULT_GAME,
  normalizeEntity, normalizeGame, isValidGameFile
};