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
  gifs: { idle: "", run: "", jump: "", bump: "", defeat: "" }
  ,actionSettings: {
    idle: { scale: 1, offsetY: 0 },
    run: { scale: 1, offsetY: 0 },
    jump: { scale: 1, offsetY: 0 },
    bump: { scale: 1, offsetY: 0 },
    defeat: { scale: 1, offsetY: 0 }
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
      gifs: {
        idle: "images/muse-dash-buro_ tela principal.gif",
        run: "images/muse-dash-buro_anda_normal.gif",
        jump: "images/muse-dash-buro_primeira_imagem_do_pulo.gif",
        bump: "images/muse-dash-buro_primeira_imagem_do_esbarrao.gif",
        defeat: "images/muse-dash-marija_morte.gif"
      }
    },
    obstaculo: {
      id: "obstaculo",
      role: "enemy",
      layer: "foreground",
      hasDensity: true,
      extraLives: 1,
      speed: 0,
      jumpHeight: 0,
      floatTime: 0,
      scale: 1,
      offsetY: 0,
      positionX: 100,
      gifs: {
        idle: "images/inim004.gif",
        run: "images/inim004.gif",
        jump: "",
        bump: "",
        defeat: ""
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
  const actionSettings = {};
  Object.keys(b.actionSettings).forEach(action => {
    const settings = isObject(e.actionSettings && e.actionSettings[action])
      ? e.actionSettings[action] : {};
    actionSettings[action] = {
      scale: numberOrDefault(settings.scale, e.scale, 0.1, 5),
      offsetY: numberOrDefault(settings.offsetY, e.offsetY, -300, 300)
    };
  });
  return {
    id: id,
    role: ['player','enemy','prop'].includes(e.role) ? e.role : b.role,
    layer: ['background','ground','foreground'].includes(e.layer) ? e.layer : b.layer,
    hasDensity: isBool(e.hasDensity) ? e.hasDensity : b.hasDensity,
    extraLives: numberOrDefault(e.extraLives, b.extraLives, 0, 99),
    speed: numberOrDefault(e.speed, b.speed, 0, 1000),
    jumpHeight: numberOrDefault(e.jumpHeight, b.jumpHeight, 0, 300),
    floatTime: isNumber(e.floatTime) ? e.floatTime : b.floatTime,
    scale: numberOrDefault(e.scale, b.scale, 0.1, 5),
    offsetY: numberOrDefault(e.offsetY, b.offsetY, -300, 300),
    positionX: numberOrDefault(e.positionX, b.positionX, 0, 100),
    gifs: {
      idle:   (e.gifs && isString(e.gifs.idle))   ? e.gifs.idle   : "",
      run:    (e.gifs && isString(e.gifs.run))    ? e.gifs.run    : "",
      jump:   (e.gifs && isString(e.gifs.jump))   ? e.gifs.jump   : "",
      bump:   (e.gifs && isString(e.gifs.bump))   ? e.gifs.bump   : "",
      defeat: (e.gifs && isString(e.gifs.defeat)) ? e.gifs.defeat : ""
    },
    actionSettings
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