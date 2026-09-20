const RUNTIME = {
  game: null,
  running: false,
  rafId: null,
  lastTime: 0,
  keys: { left:false, right:false, jump:false },

  actors: {},
  obstacles: [],
  obstacleTimer: 0,

  GRAVITY: 2200,
  GROUND_Y: 80,

  worldScroll: 0,
  worldSpeed: 0,

  lives: 0,
  score: 0,
  bestScore: 0,
  baseWorldSpeed: 0,
  currentSpawnRate: 0,
  gameOver: false,

  boot() {
    const draft = Storage.loadDraft();
    if (!draft) { alert('Nenhum projeto. Monte na IDE primeiro.'); return; }
    this.game = draft;

    document.title = this.game.meta.title + ' — Anime Game Studio';
    document.getElementById('hud-title').innerText = this.game.meta.title;

    this.worldSpeed = this.game.rules.runner.worldSpeed;
    this.baseWorldSpeed = this.worldSpeed;
    this.currentSpawnRate = this.game.rules.runner.spawnRate;
    this.bestScore = Number(localStorage.getItem('ags_best_score')) || 0;
    this.playerId = Object.keys(this.game.entities).find(id =>
      this.game.entities[id].role === 'player'
    );

    this.renderScene();
    this.buildActors();
    this.updateHudLives();
    this.updateHudScore();
    this.attachInput();

    this.running = true;
    this.lastTime = performance.now();
    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  /* ---------- SCENE ---------- */

  resolveAsset(p){ return p && p.startsWith('images/') ? '../'+p : p; },

  getAction(entity, preferred) {
    const names = [preferred, 'idle', 'run', ...Object.keys(entity.actions)];
    return names.map(name => entity.actions[name])
      .find(action => action && action.gif) || entity.actions.idle || entity.actions.run;
  },

  renderScene() {
    const bg = document.getElementById('background-layer');
    bg.style.backgroundImage = 'none';
    [0,1,2].forEach(i => {
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      const l = this.game.scene.layers[i];
      el.style.backgroundImage = l.image ? `url('${this.resolveAsset(l.image)}')` : 'none';
      el.style.backgroundPositionX = '0px';
      el.dataset.speed = String(l.speed || (i + 1) * 0.35);
    });
  },

  /* ---------- ACTORS ---------- */

  buildActors() {
    const c = document.getElementById('entities-container');
    c.innerHTML = '';
    this.actors = {};
    const W = window.innerWidth;

    Object.keys(this.game.entities).forEach((id, index) => {
      const ent = this.game.entities[id];
      if (id !== this.playerId) return; // apenas o jogador fica fixo

      const initialAction = this.getAction(ent, 'idle');
      const posXPercent = ent.positionX;
      const el = document.createElement('div');
      el.className = `sprite-container layer-${ent.layer}`;
      const img = document.createElement('img');
      const initial = initialAction && initialAction.gif || '';
      if (initial) {
        img.src = this.resolveAsset(initial);
      }

      const scale = initialAction.scale;
      img.style.transform = `scale(${scale})`;
      el.appendChild(img);
      c.appendChild(el);

      this.actors[id] = {
        id, role: ent.role, data: ent, el, img,
        x: (posXPercent/100)*W,
        baseX: (posXPercent/100)*W,
        y: 0, vx: 0, vy: 0,
        onGround: true,
        action: 'idle',
        actionScale: initialAction.scale,
        actionPositionY: initialAction.positionY,
        actionPositionX: initialAction.positionX,
        hitboxWidth: 60,
        hitboxHeight: 60,
        baseOffsetY: ent.offsetY || 0
      };

      const updateHitbox = () => {
        this.actors[id].hitboxWidth = (img.naturalWidth || 60) * 0.58;
        this.actors[id].hitboxHeight = (img.naturalHeight || 60) * 0.82;
      };
      if (initial) img.addEventListener('load', updateHitbox, { once: true });
      if (img.complete) updateHitbox();

      if (ent.role === 'player') {
        this.lives = ent.extraLives || 3;
      }
    });
  },

  /* ---------- LOOP ---------- */

  loop(now) {
    if (!this.running) return;
    const dt = Math.min((now - this.lastTime)/1000, 0.05);
    this.lastTime = now;

    if (!this.gameOver) this.update(dt);
    this.render();

    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  update(dt) {
    this.updateRunner(dt);
  },

  /* ---------- RUNNER ---------- */

  updateRunner(dt) {
    this.score += dt * 10;
    this.worldSpeed = Math.min(this.baseWorldSpeed + Math.floor(this.score / 100) * 5, 2000);
    this.currentSpawnRate = Math.max(400, this.game.rules.runner.spawnRate - Math.floor(this.score / 100) * 20);
    this.updateHudScore();
    this.worldScroll += this.worldSpeed * dt;

    // spawn de obstáculos
    this.obstacleTimer += dt*1000;
    if (this.obstacleTimer >= this.currentSpawnRate) {
      this.obstacleTimer = 0;
      this.spawnObstacle();
    }

    // player
    const player = Object.values(this.actors).find(a => a.role === 'player');
    if (player) {
      const playerSpeed = player.data.speed || 200;
      player.x = player.baseX;

      // pulo
      if (this.keys.jump && player.onGround) {
        player.vy = -Math.sqrt(2 * this.GRAVITY * (player.data.jumpHeight || 150));
        player.onGround = false;
      }
      if (!player.onGround) {
        player.vy += this.GRAVITY * dt;
        player.y -= player.vy * dt * 0.02;
        if (player.y <= 0) { player.y = 0; player.vy = 0; player.onGround = true; }
      }
      const next = !player.onGround ? 'jump' : 'run';
      this.setAction(player, next);
    }

    // obstáculos se movem
    const W = window.innerWidth;
    this.obstacles.forEach(o => {
      o.x += o.direction * this.worldSpeed * dt;
      if (o.hitTimer > 0) {
        o.hitTimer -= dt;
        if (o.hitTimer <= 0) {
          o.actionData = this.getAction(o.data, 'run');
          o.img.src = this.resolveAsset(o.actionData.gif);
          o.img.style.transform =
            `scale(${o.actionData.scale}) scaleX(${o.data.flip ? -1 : 1})`;
        }
      }
      if ((o.direction < 0 && o.x < -200) ||
          (o.direction > 0 && o.x > window.innerWidth + 200)) o.dead = true;
    });

    // colisão
    if (player && !player.hitCooldown) {
      this.obstacles.forEach(o => {
        if (o.dead) return;
        if (this.collide(player, o)) {
          this.hitPlayer(player);
          this.hitObstacle(o);
        }
      });
    }

    this.obstacles = this.obstacles.filter(o => !o.dead);
  },

  spawnObstacle() {
    const enemies = Object.entries(this.game.entities)
      .filter(([id]) => id !== this.playerId)
      .map(([, entity]) => entity);
    if (enemies.length === 0) return;
    const ent = enemies[Math.floor(Math.random()*enemies.length)];
    const container = document.getElementById('entities-container');
    const el = document.createElement('div');
    el.className = `sprite-container layer-${ent.layer}`;
    const img = document.createElement('img');
      const runAction = this.getAction(ent, 'run');
    const src = runAction.gif || '';
    if (src) img.src = this.resolveAsset(src);
      const scale = runAction.scale;
      const direction = ent.spawnSide === 'left' ? 1 : -1;
      const flip = ent.flip ? -1 : 1;
      img.style.transform = `scale(${scale}) scaleX(${flip})`;
    el.appendChild(img);
    container.appendChild(el);

    this.obstacles.push({
      data: ent, actionData: runAction, el, img,
      x: ent.spawnSide === 'left' ? -40 : window.innerWidth + 40,
      y: 0,
      direction,
      w: 60 * scale,
      h: 60 * scale,
      hitTimer: 0,
      dead: false
    });
    const obstacle = this.obstacles[this.obstacles.length - 1];
    img.addEventListener('load', () => {
      obstacle.w = (img.naturalWidth || 60) * scale * 0.58;
      obstacle.h = (img.naturalHeight || 60) * scale * 0.82;
    }, { once: true });
  },

  hitObstacle(obstacle) {
    if (obstacle.hitTimer > 0) return;
    const damageAction = obstacle.data.actions.bump || obstacle.data.actions.hit;
    if (!damageAction || !damageAction.gif) return;
    obstacle.actionData = damageAction;
    obstacle.hitTimer = 0.4;
    obstacle.img.src = this.resolveAsset(damageAction.gif);
    obstacle.img.style.transform =
      `scale(${damageAction.scale}) scaleX(${obstacle.data.flip ? -1 : 1})`;
  },

  collide(a, o) {
    const playerAction = a.data.actions[a.action] || a.data.actions.idle;
    const aw = (a.hitboxWidth || 60) * (a.actionScale || 1);
    const ah = (a.hitboxHeight || 60) * (a.actionScale || 1);
    const playerBottom = this.GROUND_Y + a.y + (playerAction.positionY || 0);
    const obstacleAction = o.actionData || this.getAction(o.data, 'run');
    const obstacleBottom = this.GROUND_Y + (obstacleAction.positionY || 0);
    const playerLeft = a.x + (a.hitboxWidth || 60) * 0.21;
    const playerRight = playerLeft + aw;
    const obstacleLeft = o.x + o.w * 0.21;
    const obstacleRight = obstacleLeft + o.w;
    const playerTop = playerBottom - ah;
    const obstacleTop = obstacleBottom - o.h;
    return playerLeft < obstacleRight &&
      playerRight > obstacleLeft &&
      playerTop < obstacleBottom &&
      playerBottom > obstacleTop;
  },

  hitPlayer(player) {
    player.hitCooldown = true;
    this.setAction(player, 'bump');
    this.lives--;
    this.updateHudLives();
    player.el.classList.add('hit');
    setTimeout(() => player.el.classList.remove('hit'), 180);
    if (this.lives <= 0) {
      this.setAction(player, 'defeat');
      this.endGame();
    } else {
      setTimeout(() => {
        player.hitCooldown = false;
        if (!player.onGround) this.setAction(player, 'jump');
        else this.setAction(player, 'run');
      }, 700);
    }
  },

  /* ---------- RENDER ---------- */

  render() {
    const W = window.innerWidth;

    Object.values(this.actors).forEach(a => {
      a.el.style.left = `${a.x}px`;
      a.el.style.bottom = `${this.GROUND_Y + a.y + a.actionPositionY}px`;
    });

    this.obstacles.forEach(o => {
      o.el.style.left = `${o.x}px`;
      o.el.style.bottom = `${this.GROUND_Y + (o.actionData.positionY || 0)}px`;
    });

    [0,1,2].forEach(i => {
      const l = this.game.scene.layers[i];
      if (!l.image) return;
      const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
      const speed = Number(el.dataset.speed) || (i + 1) * 0.35;
      el.style.backgroundPositionX = `${-this.worldScroll * speed}px`;
    });
  },

  setAction(actor, action) {
    if (actor.action === action) return;
    const actionData = this.getAction(actor.data, action);
    const src = actionData && actionData.gif;
    if (!src) return;
    const settings = actionData;
    actor.img.src = this.resolveAsset(src);
    actor.actionScale = settings.scale;
    actor.actionPositionY = settings.positionY;
    actor.actionPositionX = actor.baseX;
    actor.img.style.transform = `scale(${actor.actionScale})`;
    actor.action = action;
  },

  updateHudLives() {
    const el = document.getElementById('hud-lives');
    if (el) el.innerText = 'VIDAS: ' + this.lives;
  },

  updateHudScore() {
    const score = Math.floor(this.score);
    const scoreEl = document.getElementById('hud-score');
    const bestEl = document.getElementById('hud-best');
    if (scoreEl) scoreEl.innerText = 'PONTOS: ' + score;
    if (bestEl) bestEl.innerText = 'RECORDE: ' + Math.max(this.bestScore, score);
  },

  endGame() {
    this.gameOver = true;
    this.bestScore = Math.max(this.bestScore, Math.floor(this.score));
    localStorage.setItem('ags_best_score', String(this.bestScore));
    const scoreEl = document.getElementById('game-over-score');
    if (scoreEl) scoreEl.innerText = 'PONTOS: ' + Math.floor(this.score);
    this.updateHudScore();
    document.getElementById('game-over').classList.remove('hidden');
  },

  restart() {
    this.running = false;
    cancelAnimationFrame(this.rafId);
    this.obstacles.forEach(obstacle => obstacle.el.remove());
    this.obstacles = [];
    this.obstacleTimer = 0;
    this.worldScroll = 0;
    this.worldSpeed = this.baseWorldSpeed;
    this.currentSpawnRate = this.game.rules.runner.spawnRate;
    this.score = 0;
    this.gameOver = false;
    this.clearKeys();
    document.getElementById('game-over').classList.add('hidden');
    this.buildActors();
    this.updateHudLives();
    this.updateHudScore();
    this.lastTime = performance.now();
    this.running = true;
    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  /* ---------- INPUT ---------- */

  attachInput() {
    this._kd = e => this.onKey(e, true);
    this._ku = e => this.onKey(e, false);
    this._blur = () => this.clearKeys();
    this._vis  = () => { if (document.hidden) this.clearKeys(); };
    this._tap = () => {
      if (!this.gameOver) this.keys.jump = true;
      setTimeout(() => { this.keys.jump = false; }, 0);
    };
    window.addEventListener('keydown', this._kd);
    window.addEventListener('keyup', this._ku);
    window.addEventListener('blur', this._blur);
    document.addEventListener('visibilitychange', this._vis);
    document.getElementById('game-stage').addEventListener('pointerdown', this._tap);
  },

  clearKeys() {
    this.keys.left = false;
    this.keys.right = false;
    this.keys.jump = false;
  },

  onKey(e, pressed) {
    if (e.code === 'Space' && pressed && this.gameOver) {
      restartGame();
      return;
    }

    switch (e.code) {
      case 'ArrowLeft': case 'KeyA':
        this.keys.left = pressed;
        e.preventDefault();
        break;
      case 'ArrowRight': case 'KeyD':
        this.keys.right = pressed;
        e.preventDefault();
        break;
      case 'ArrowUp': case 'KeyW': case 'Space':
        this.keys.jump = pressed; e.preventDefault(); break;
      case 'Escape': if (pressed) exitGame(); break;
    }
  }
};

function exitGame() {
  RUNTIME.running = false;
  cancelAnimationFrame(RUNTIME.rafId);
  window.location.href = '../editor/index.html';
}

function restartGame() {
  RUNTIME.restart();
}

window.addEventListener('DOMContentLoaded', () => RUNTIME.boot());