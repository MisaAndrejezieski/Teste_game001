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
      if (ent.role === 'enemy') return; // spawn dinâmico

      let posXPercent = ent.positionX;
      const el = document.createElement('div');
      el.className = `sprite-container layer-${ent.layer}`;
      const img = document.createElement('img');
      const initial = ent.gifs.idle || ent.gifs.run || '';
      if (initial) {
        img.src = this.resolveAsset(initial);
      }

      const scale = ent.scale || 1;
      img.style.transform = `scale(${scale})`;
      el.appendChild(img);
      c.appendChild(el);

      this.actors[id] = {
        id, role: ent.role, data: ent, el, img,
        x: (posXPercent/100)*W,
        y: 0, vx: 0, vy: 0,
        onGround: true,
        action: 'idle',
        hitboxWidth: 60,
        hitboxHeight: 60,
        baseOffsetY: ent.offsetY || 0
      };

      const updateHitbox = () => {
        this.actors[id].hitboxWidth = img.naturalWidth || 60;
        this.actors[id].hitboxHeight = img.naturalHeight || 60;
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
      if (this.keys.left) player.x -= playerSpeed * dt;
      if (this.keys.right) player.x += playerSpeed * dt;
      player.x = Math.max(window.innerWidth * 0.1, Math.min(window.innerWidth * 0.45, player.x));

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
      o.x -= this.worldSpeed * dt;
      if (o.x < -200) o.dead = true;
    });

    // colisão
    if (player && !player.hitCooldown) {
      this.obstacles.forEach(o => {
        if (o.dead) return;
        if (this.collide(player, o)) {
          this.hitPlayer(player);
          o.dead = true;
        }
      });
    }

    this.obstacles = this.obstacles.filter(o => !o.dead);
  },

  spawnObstacle() {
    const enemies = Object.values(this.game.entities).filter(e => e.role === 'enemy');
    if (enemies.length === 0) return;
    const ent = enemies[Math.floor(Math.random()*enemies.length)];
    const container = document.getElementById('entities-container');
    const el = document.createElement('div');
    el.className = `sprite-container layer-${ent.layer}`;
    const img = document.createElement('img');
    const src = ent.gifs.run || ent.gifs.idle || '';
    if (src) img.src = this.resolveAsset(src);
    const scale = ent.scale || 1;
    img.style.transform = `scale(${scale})`;
    el.appendChild(img);
    container.appendChild(el);

    this.obstacles.push({
      data: ent, el, img,
      x: window.innerWidth + 40,
      y: 0,
      w: 60 * scale,
      h: 60 * scale,
      dead: false
    });
    const obstacle = this.obstacles[this.obstacles.length - 1];
    img.addEventListener('load', () => {
      obstacle.w = (img.naturalWidth || 60) * scale;
      obstacle.h = (img.naturalHeight || 60) * scale;
    }, { once: true });
  },

  collide(a, o) {
    const ax = a.x, ay = a.y + a.baseOffsetY;
    const aw = (a.hitboxWidth || 60) * (a.data.scale||1);
    const ah = (a.hitboxHeight || 60) * (a.data.scale||1);
    const ox = o.x - o.w/2, oy = o.y + (o.data.offsetY||0);
    const pad = 12;
    return (ax - aw/2 + pad < ox + o.w - pad) &&
           (ax + aw/2 - pad > ox + pad) &&
           (ay < oy + o.h - pad) &&
           (ay + ah - pad > oy);
  },

  hitPlayer(player) {
    player.hitCooldown = true;
    this.setAction(player, 'bump');
    this.lives--;
    this.updateHudLives();
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
      a.el.style.bottom = `${this.GROUND_Y + a.y + (a.baseOffsetY||0)}px`;
    });

    this.obstacles.forEach(o => {
      o.el.style.left = `${o.x}px`;
      o.el.style.bottom = `${this.GROUND_Y + (o.data.offsetY||0)}px`;
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
    const src = actor.data.gifs[action] || actor.data.gifs.idle || actor.data.gifs.run || '';
    if (!src) return;
    actor.img.src = this.resolveAsset(src);
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