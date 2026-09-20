/* =========================================================
   player/player.js
   Runtime do jogo. Lê o draft do localStorage, monta a cena
   e roda o loop principal.
   ========================================================= */

const RUNTIME = {
  running: false,
  rafId: null,
  lastTime: 0,
  keys: { left: false, right: false, jump: false },

  // Atores em tempo real: { id: { x, y, vx, vy, onGround, action, el, img, data } }
  actors: {},

  GRAVITY: 1800,       // px/s²
  GROUND_Y: 80,        // mesma altura da ground-line
  WORLD_SCROLL: 0,     // deslocamento horizontal (para paralaxe futura)
  SCROLL_SPEED: 180,   // velocidade do scroll do mundo em px/s

  game: null,

  /* ---------- BOOT ---------- */

  boot() {
    const draft = Storage.loadDraft();
    if (!draft) {
      alert('Nenhum projeto encontrado. Monte um jogo na IDE primeiro.');
      window.close();
      return;
    }
    this.game = draft;
    this.applyMeta();
    this.renderScene();
    this.buildActors();
    this.attachInput();
    this.running = true;
    this.lastTime = performance.now();
    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  /* ---------- CENA ---------- */

  applyMeta() {
    document.title = this.game.meta.title + ' — Anime Game Studio';
    document.getElementById('hud-title').innerText = this.game.meta.title;

    const genre = this.game.meta.genre;
    if (genre === 'fighting') {
      document.getElementById('fighting-ui').classList.remove('hidden');
    }
  },

  renderScene() {
    const bg = document.getElementById('background-layer');
    const img = this.game.scene.backgroundImage;
    if (img) {
      bg.style.backgroundImage = `url('${this.resolveAsset(img)}')`;
      const mode = this.game.scene.backgroundMode;
      const repeat = (mode === 'repeat' || this.game.meta.genre === 'racing');
      bg.style.backgroundRepeat = repeat ? 'repeat' : 'no-repeat';
      bg.style.backgroundSize   = (mode === 'repeat') ? 'auto' : mode;
    }
  },

  resolveAsset(path) {
    if (!path) return '';
    if (path.startsWith('images/')) return '../' + path;
    return path;
  },

  /* ---------- ATORES ---------- */

  buildActors() {
    const container = document.getElementById('entities-container');
    container.innerHTML = '';
    this.actors = {};

    const genre = this.game.meta.genre;
    const stageW = window.innerWidth;

    Object.keys(this.game.entities).forEach((id, index) => {
      const ent = this.game.entities[id];

      let posXPercent = ent.positionX ?? 20;
      let flip = false;

      if (genre === 'fighting') {
        posXPercent = index === 0 ? 25 : 70;
        flip = (index === 1);
      } else if (genre === 'racing') {
        posXPercent = 15 + (index * 25);
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
      container.appendChild(el);

      this.actors[id] = {
        id,
        role: ent.role,
        data: ent,
        el, img,
        x: (posXPercent / 100) * stageW,
        y: 0,               // 0 = no chão; positivo = acima
        vx: 0, vy: 0,
        onGround: true,
        action: 'idle',
        flip,
        baseOffsetY: ent.offsetY || 0
      };

      if (genre === 'fighting') {
        if (index === 0) document.getElementById('p1-name').innerText = ent.id.toUpperCase();
        if (index === 1) document.getElementById('p2-name').innerText = ent.id.toUpperCase();
      }
    });
  },

  /* ---------- LOOP ---------- */

  loop(now) {
    if (!this.running) return;
    const dt = Math.min((now - this.lastTime) / 1000, 0.05);
    this.lastTime = now;

    this.update(dt);
    this.render();

    this.rafId = requestAnimationFrame(t => this.loop(t));
  },

  update(dt) {
    const stageW = window.innerWidth;

    // Rolagem do mundo (visual; prepara terreno para paralaxe)
    this.WORLD_SCROLL += this.SCROLL_SPEED * dt;

    Object.values(this.actors).forEach(a => {
      if (a.role !== 'player') return; // inimigos por enquanto estáticos

      const speed = a.data.speed || 200;

      // Movimento horizontal
      a.vx = 0;
      if (this.keys.left)  a.vx -= speed;
      if (this.keys.right) a.vx += speed;
      a.x += a.vx * dt;

      // Limites da tela
      const margin = 40;
      a.x = Math.max(margin, Math.min(stageW - margin, a.x));

      // Pulo
      if (this.keys.jump && a.onGround) {
        a.vy = -(a.data.jumpHeight || 150) * 4; // escala p/ ficar visível
        a.onGround = false;
      }

      // Gravidade
      if (!a.onGround) {
        a.vy += this.GRAVITY * dt;
        a.y -= a.vy * dt * 0.02;   // converte p/ px
        if (a.y <= 0) { a.y = 0; a.vy = 0; a.onGround = true; }
      }

      // Ação para o sprite
      let next = 'idle';
      if (!a.onGround) next = 'jump';
      else if (a.vx !== 0) next = 'run';
      this.setAction(a, next);
    });
  },

  render() {
    Object.values(this.actors).forEach(a => {
      a.el.style.left = `${a.x}px`;
      a.el.style.bottom = `${this.GROUND_Y + a.y + (a.baseOffsetY || 0)}px`;
    });

    // Scroll horizontal simples do fundo (base para paralaxe)
    const bg = document.getElementById('background-layer');
    if (bg && this.game.scene.backgroundImage) {
      bg.style.backgroundPositionX = `${-this.WORLD_SCROLL % 2000}px`;
    }
  },

  setAction(actor, action) {
    if (actor.action === action) return;
    const src = actor.data.gifs[action];
    if (!src) return; // sem GIF para essa ação: mantém atual
    actor.img.src = this.resolveAsset(src);
    actor.action = action;
  },

  /* ---------- INPUT ---------- */

  attachInput() {
    this._onKeyDown = e => this.handleKey(e, true);
    this._onKeyUp   = e => this.handleKey(e, false);
    window.addEventListener('keydown', this._onKeyDown);
    window.addEventListener('keyup',   this._onKeyUp);
  },

  handleKey(e, pressed) {
    switch (e.code) {
      case 'ArrowLeft':  case 'KeyA': this.keys.left  = pressed; break;
      case 'ArrowRight': case 'KeyD': this.keys.right = pressed; break;
      case 'ArrowUp':    case 'KeyW': case 'Space':
        this.keys.jump = pressed;
        e.preventDefault();
        break;
      case 'Escape':
        if (pressed) this.exit();
        break;
    }
  }
};

/* ---------- CONTROLE EXTERNO ---------- */

function exitGame() {
  RUNTIME.running = false;
  cancelAnimationFrame(RUNTIME.rafId);
  window.close();  // pode ser bloqueado pelo browser; senão, volta pra IDE
  window.location.href = '../editor/index.html';
}

/* ---------- INÍCIO ---------- */

window.addEventListener('DOMContentLoaded', () => RUNTIME.boot());