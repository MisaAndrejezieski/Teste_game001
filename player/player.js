const RUNTIME = {
  game: null,
  running: false,
  rafId: null,
  lastTime: 0,
  keys: { left:false, right:false, jump:false, attack:false },
  keysPrev: { attack:false },

  actors: {},
  obstacles: [],
  obstacleTimer: 0,

  GRAVITY: 2200,
  GROUND_Y: 80,

  worldScroll: 0,
  worldSpeed: 0,

  lives: 0,
  hp: 0,
  maxHp: 0,
  gameOver: false,

  boot() {
    const draft = Storage.loadDraft();
    if (!draft) { alert('Nenhum projeto. Monte na IDE primeiro.'); return; }
    this.game = draft;

    document.title = this.game.meta.title + ' — Anime Game Studio';
    document.getElementById('hud-title').innerText = this.game.meta.title;

    this.maxHp = this.game.rules.fighting.maxHp;
    this.hp = this.maxHp;
    this.worldSpeed = this.game.rules.runner.worldSpeed;

    document.getElementById('fighting-ui').classList.toggle('hidden',
      this.game.meta.genre !== 'fighting');

    if (this.game.meta.genre === 'fighting') {
      document.getElementById('p1-name').innerText = 'P1';
      document.getElementById('p2-name').innerText = 'P2';
      this.updateHpBars();
    }

    this.renderScene();
    this.buildActors();
    this.updateHudLives();
    this.attachInput();

    this.running = true;
    this.lastTime = performance.now();
    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  /* ---------- SCENE ---------- */

  resolveAsset(p){ return p && p.startsWith('images/') ? '../'+p : p; },

  renderScene() {
    const genre = this.game.meta.genre;
    const bg = document.getElementById('background-layer');

    if (genre === 'runner') {
      bg.style.backgroundImage = 'none';
      [0,1,2].forEach(i => {
        const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
        const l = this.game.scene.layers[i];
        el.style.backgroundImage = l.image ? `url('${this.resolveAsset(l.image)}')` : 'none';
        el.style.backgroundPositionX = '0px';
      });
    } else {
      [0,1,2].forEach(i => {
        document.querySelector(`.parallax-layer[data-layer="${i}"]`).style.backgroundImage = 'none';
      });
      if (this.game.scene.backgroundImage) {
        bg.style.backgroundImage = `url('${this.resolveAsset(this.game.scene.backgroundImage)}')`;
      }
    }
  },

  /* ---------- ACTORS ---------- */

  buildActors() {
    const c = document.getElementById('entities-container');
    c.innerHTML = '';
    this.actors = {};
    const genre = this.game.meta.genre;
    const W = window.innerWidth;

    Object.keys(this.game.entities).forEach((id, index) => {
      const ent = this.game.entities[id];
      if (ent.role === 'enemy' && genre === 'runner') return; // spawn dinâmico

      let posXPercent = ent.positionX;
      let flip = false;
      if (genre === 'fighting') {
        posXPercent = index === 0 ? 25 : 70;
        flip = (index === 1);
      }

      const el = document.createElement('div');
      el.className = `sprite-container layer-${ent.layer}`;
      const img = document.createElement('img');
      const initial = ent.gifs.idle || ent.gifs.run || '';
      if (initial) img.src = this.resolveAsset(initial);

      const scale = ent.scale || 1;
      const flipPart = flip ? ' scaleX(-1)' : '';
      img.style.transform = `scale(${scale})${flipPart}`;
      el.appendChild(img);
      c.appendChild(el);

      this.actors[id] = {
        id, role: ent.role, data: ent, el, img,
        x: (posXPercent/100)*W,
        y: 0, vx: 0, vy: 0,
        onGround: true,
        action: 'idle',
        flip, baseOffsetY: ent.offsetY || 0
      };

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
    if (this.game.meta.genre === 'runner') this.updateRunner(dt);
    else if (this.game.meta.genre === 'fighting') this.updateFighting(dt);
    this.keysPrev.attack = this.keys.attack;
  },

  /* ---------- RUNNER ---------- */

  updateRunner(dt) {
    this.worldScroll += this.worldSpeed * dt;

    // spawn de obstáculos
    this.obstacleTimer += dt*1000;
    if (this.obstacleTimer >= this.game.rules.runner.spawnRate) {
      this.obstacleTimer = 0;
      this.spawnObstacle();
    }

    // player
    const player = Object.values(this.actors).find(a => a.role === 'player');
    if (player) {
      // pulo
      if (this.keys.jump && player.onGround) {
        player.vy = -(player.data.jumpHeight || 150) * 4;
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
      w: img.naturalWidth * scale || 60,
      h: img.naturalHeight * scale || 60,
      dead: false
    });
  },

  collide(a, o) {
    const ax = a.x, ay = a.y + a.baseOffsetY;
    const aw = a.img.naturalWidth * (a.data.scale||1) || 60;
    const ah = a.img.naturalHeight * (a.data.scale||1) || 60;
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

  /* ---------- FIGHTING ---------- */

  updateFighting(dt) {
    const list = Object.values(this.actors);
    const p1 = list[0], p2 = list[1];
    if (!p1) return;

    const W = window.innerWidth;
    const speed = p1.data.speed || 250;

    p1.vx = 0;
    if (this.keys.left)  p1.vx -= speed;
    if (this.keys.right) p1.vx += speed;
    p1.x += p1.vx * dt;
    p1.x = Math.max(60, Math.min(W - 60, p1.x));

    if (p2) {
      const minDist = 80;
      if (Math.abs(p1.x - p2.x) < minDist) {
        if (p1.x < p2.x) p1.x = p2.x - minDist;
        else p1.x = p2.x + minDist;
      }
    }

    if (this.keys.jump && p1.onGround) {
      p1.vy = -(p1.data.jumpHeight || 150) * 4;
      p1.onGround = false;
    }
    if (!p1.onGround) {
      p1.vy += this.GRAVITY * dt;
      p1.y -= p1.vy * dt * 0.02;
      if (p1.y <= 0) { p1.y = 0; p1.vy = 0; p1.onGround = true; }
    }

    // ataque
    if (this.keys.attack && !this.keysPrev.attack) {
      this.setAction(p1, 'attack');
      p1.attackLock = 0.3;
      if (p2 && Math.abs(p1.x - p2.x) < 110) {
        this.damageP2(p2);
      }
    }
    if (p1.attackLock > 0) {
      p1.attackLock -= dt;
      if (p1.attackLock <= 0) this.setAction(p1, 'idle');
      return;
    }

    let next = 'idle';
    if (!p1.onGround) next = 'jump';
    else if (p1.vx !== 0) next = 'run';
    this.setAction(p1, next);
  },

  damageP2(p2) {
    this.hp = Math.max(0, this.hp - this.game.rules.fighting.damage);
    this.updateHpBars();
    const prev = p2.action;
    this.setAction(p2, 'bump');
    setTimeout(() => {
      if (this.hp <= 0) this.setAction(p2, 'defeat');
      else this.setAction(p2, 'idle');
    }, 400);
  },

  updateHpBars() {
    const pct = (this.hp / this.maxHp) * 100;
    const el = document.getElementById('p2-hp');
    if (el) el.style.width = pct + '%';
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

    if (this.game.meta.genre === 'runner') {
      [0,1,2].forEach(i => {
        const l = this.game.scene.layers[i];
        if (!l.image) return;
        const el = document.querySelector(`.parallax-layer[data-layer="${i}"]`);
        el.style.backgroundPositionX = `${-this.worldScroll * l.speed}px`;
      });
    }
  },

  setAction(actor, action) {
    if (actor.action === action) return;
    const src = actor.data.gifs[action];
    if (!src) return;
    actor.img.src = this.resolveAsset(src);
    actor.action = action;
  },

  updateHudLives() {
    const el = document.getElementById('hud-lives');
    if (el) el.innerText = 'VIDAS: ' + this.lives;
  },

  endGame() {
    this.gameOver = true;
    document.getElementById('game-over').classList.remove('hidden');
  },

  /* ---------- INPUT ---------- */

  attachInput() {
    this._kd = e => this.onKey(e, true);
    this._ku = e => this.onKey(e, false);
    this._blur = () => this.clearKeys();
    this._vis  = () => { if (document.hidden) this.clearKeys(); };
    window.addEventListener('keydown', this._kd);
    window.addEventListener('keyup', this._ku);
    window.addEventListener('blur', this._blur);
    document.addEventListener('visibilitychange', this._vis);
  },

  clearKeys() {
    this.keys.left = this.keys.right = this.keys.jump = this.keys.attack = false;
  },

  onKey(e, pressed) {
    switch (e.code) {
      case 'ArrowLeft': case 'KeyA': this.keys.left = pressed; e.preventDefault(); break;
      case 'ArrowRight': case 'KeyD': this.keys.right = pressed; e.preventDefault(); break;
      case 'ArrowUp': case 'KeyW': case 'Space':
        this.keys.jump = pressed; e.preventDefault(); break;
      case 'KeyF': this.keys.attack = pressed; e.preventDefault(); break;
      case 'Escape': if (pressed) exitGame(); break;
    }
  }
};

function exitGame() {
  RUNTIME.running = false;
  cancelAnimationFrame(RUNTIME.rafId);
  window.location.href = '../editor/index.html';
}

window.addEventListener('DOMContentLoaded', () => RUNTIME.boot());