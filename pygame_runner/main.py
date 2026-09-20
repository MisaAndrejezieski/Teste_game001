from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from . import config
except ImportError:
    import config

import pygame
from PIL import Image, ImageSequence

# =============================================================
# ANIMAÇÃO (GIF → lista de frames, já escalados e flipados)
# =============================================================

class AnimatedImage:
    def __init__(self, path: Path, scale: float = 1.0, flip: bool = False):
        self.frames: list[pygame.Surface] = []
        self.durations: list[int] = []
        self.index = 0
        self.elapsed = 0
        self.scale = scale
        self.flip = flip
        self._load(path)

    def _load(self, path: Path) -> None:
        try:
            source = Image.open(path)
            for frame in ImageSequence.Iterator(source):
                rgba = frame.convert("RGBA")
                surface = pygame.image.fromstring(
                    rgba.tobytes(), rgba.size, "RGBA"
                ).convert_alpha()

                if self.scale != 1.0:
                    w = max(1, int(surface.width * self.scale))
                    h = max(1, int(surface.height * self.scale))
                    surface = pygame.transform.smoothscale(surface, (w, h))

                if self.flip:
                    surface = pygame.transform.flip(surface, True, False)

                self.frames.append(surface)
                self.durations.append(max(30, frame.info.get("duration", 100)))
        except (FileNotFoundError, OSError):
            size = max(1, int(64 * self.scale))
            self.frames = [pygame.Surface((size, size), pygame.SRCALPHA)]
            self.durations = [100]

    def update(self, dt_ms: int) -> None:
        if len(self.frames) < 2:
            return
        self.elapsed += dt_ms
        if self.elapsed >= self.durations[self.index]:
            self.elapsed = 0
            self.index = (self.index + 1) % len(self.frames)

    @property
    def width(self) -> int:
        return self.frames[self.index].get_width()

    @property
    def height(self) -> int:
        return self.frames[self.index].get_height()

    def draw(self, target: pygame.Surface, midbottom: tuple[int, int]) -> pygame.Rect:
        frame = self.frames[self.index]
        rect = frame.get_rect(midbottom=midbottom)
        target.blit(frame, rect)
        return rect


# =============================================================
# ENTIDADES
# =============================================================

@dataclass
class Enemy:
    x: float
    animation: AnimatedImage
    action: str = "run"
    hit_timer: float = 0.0


@dataclass
class Player:
    x: float
    y: float = 0.0
    vy: float = 0.0
    on_ground: bool = True
    action: str = "run"
    hit_timer: float = 0.0
    animations: dict = field(default_factory=dict)

    def jump(self, jump_speed: float) -> None:
        if self.on_ground:
            self.vy = -jump_speed
            self.on_ground = False


# =============================================================
# JOGO
# =============================================================

class RunnerGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Nora Runner")
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 72)

        # Camadas de paralaxe: [(surface, y_destino, velocidade), ...]
        self.parallax_layers = self.load_parallax_layers()

        self.nora_animations = self.load_action_set(
            config.NORA_ACTIONS, scale=config.NORA_SCALE
        )
        self.enemy_animations = self.load_action_set(
            config.ENEMY_ACTIONS, scale=config.ENEMY_SCALE, flip=True
        )

        self.player = Player(
            x=config.PLAYER_X,
            animations=self.nora_animations,
        )

        self.enemies: list[Enemy] = []
        self.lives = config.MAX_LIVES
        self.score = 0.0
        self.scroll = 0.0
        self.spawn_timer = config.SPAWN_INTERVAL
        self.damage_timer = 0.0
        self.game_over = False

    # ---------- CARREGAMENTO ----------

    def load_parallax_layers(self) -> list[tuple[pygame.Surface, int, float]]:
        """
        Divide o cenario004.jpg em faixas horizontais e monta
        cada faixa como uma camada de paralaxe.

        Retorna lista de (surface_da_faixa, y_destino_na_tela, velocidade).
        """
        layers: list[tuple[pygame.Surface, int, float]] = []

        # Cache das imagens já carregadas (caso a mesma imagem seja
        # usada em várias faixas, evitamos recarregar)
        cache: dict[str, pygame.Surface] = {}

        for filename, y_start_pct, y_end_pct, speed in config.SCENERY:
            path = config.ASSET_DIR / filename

            # Carrega imagem original (ou pega do cache)
            if filename not in cache:
                try:
                    cache[filename] = pygame.image.load(str(path)).convert()
                except pygame.error:
                    continue
            original = cache[filename]

            img_w, img_h = original.get_size()

            # Calcula a faixa horizontal (em pixels) a recortar
            y_start_px = int(img_h * y_start_pct)
            y_end_px = int(img_h * y_end_pct)
            band_h = y_end_px - y_start_px
            if band_h <= 0:
                continue

            # Recorta a faixa
            band = original.subsurface(
                pygame.Rect(0, y_start_px, img_w, band_h)
            ).copy()

            # Ajusta a largura para preencher a tela mantendo a
            # proporção da faixa (para não esticar)
            scale_factor = config.WIDTH / img_w
            new_w = config.WIDTH
            new_h = max(1, int(band_h * scale_factor))
            band = pygame.transform.smoothscale(band, (new_w, new_h))

            # Calcula onde essa faixa vai ser desenhada na tela
            # (o topo de cada faixa na tela)
            y_dest = int(config.HEIGHT * y_start_pct)

            layers.append((band, y_dest, speed))

        return layers

    def load_action_set(
        self,
        actions: dict[str, str],
        scale: float = 1.0,
        flip: bool = False,
    ) -> dict[str, AnimatedImage]:
        return {
            name: AnimatedImage(
                config.ASSET_DIR / filename,
                scale=scale,
                flip=flip,
            )
            for name, filename in actions.items()
        }

    # ---------- RESET / CLOSE ----------

    def reset(self) -> None:
        self.player = Player(
            x=config.PLAYER_X,
            animations=self.nora_animations,
        )
        self.enemies.clear()
        self.lives = config.MAX_LIVES
        self.score = 0.0
        self.scroll = 0.0
        self.spawn_timer = config.SPAWN_INTERVAL
        self.damage_timer = 0.0
        self.game_over = False

    def close(self) -> None:
        pygame.quit()

    # ---------- LOOP PRINCIPAL ----------

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP) and not self.game_over:
                        self.player.jump(config.JUMP_SPEED)
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.update(dt)
            self.draw()

        self.close()
        sys.exit()

    # ---------- UPDATE ----------

    def update(self, dt: float) -> None:
        if not self.game_over:
            self._update_world(dt)
            self._update_player(dt)
            self._update_enemies(dt)
            self._check_collisions()

        self._update_animations(dt)

    def _update_world(self, dt: float) -> None:
        self.damage_timer = max(0.0, self.damage_timer - dt)
        self.score += dt * 10
        self.scroll += config.WORLD_SPEED * dt

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = config.SPAWN_INTERVAL
            self.enemies.append(
                Enemy(
                    x=config.WIDTH + 80,
                    animation=self.enemy_animations["run"],
                )
            )

    def _update_player(self, dt: float) -> None:
        p = self.player

        if not p.on_ground:
            p.vy += config.GRAVITY * dt
            p.y -= p.vy * dt
            if p.y <= 0:
                p.y = 0.0
                p.vy = 0.0
                p.on_ground = True

        p.hit_timer = max(0.0, p.hit_timer - dt)

        if p.hit_timer > 0:
            p.action = "bump"
        elif not p.on_ground:
            p.action = "jump"
        else:
            p.action = "run"

    def _update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            enemy.x -= config.WORLD_SPEED * dt
            enemy.hit_timer = max(0.0, enemy.hit_timer - dt)
            if enemy.hit_timer <= 0 and enemy.action != "run":
                enemy.action = "run"
                enemy.animation = self.enemy_animations["run"]

        self.enemies = [e for e in self.enemies if e.x > -200]

    def _check_collisions(self) -> None:
        if self.damage_timer > 0:
            return

        player_rect = self._player_rect()
        for enemy in self.enemies:
            enemy_rect = self._enemy_rect(enemy)
            if player_rect.colliderect(enemy_rect):
                self.lives -= 1
                self.damage_timer = config.DAMAGE_COOLDOWN
                self.player.hit_timer = 0.5

                if "bump" in self.enemy_animations:
                    enemy.animation = self.enemy_animations["bump"]
                    enemy.action = "bump"
                    enemy.hit_timer = 0.4

                if self.lives <= 0:
                    self.player.action = "defeat"
                    self.game_over = True
                break

    def _player_rect(self) -> pygame.Rect:
        anim = (
            self.nora_animations.get(self.player.action)
            or self.nora_animations.get("run")
        )
        w = int(anim.width * 0.55)
        h = int(anim.height * 0.85)
        cx = self.player.x
        feet_y = config.GROUND_Y - int(self.player.y)
        return pygame.Rect(cx - w // 2, feet_y - h, w, h)

    def _enemy_rect(self, enemy: Enemy) -> pygame.Rect:
        w = int(enemy.animation.width * 0.55)
        h = int(enemy.animation.height * 0.85)
        cx = int(enemy.x)
        return pygame.Rect(cx - w // 2, config.GROUND_Y - h, w, h)

    def _update_animations(self, dt: float) -> None:
        dt_ms = int(dt * 1000)
        for anim in self.nora_animations.values():
            anim.update(dt_ms)
        for anim in self.enemy_animations.values():
            anim.update(dt_ms)

    # ---------- DRAW ----------

    def draw(self) -> None:
        self.screen.fill((135, 198, 235))

        # Paralaxe real: cada faixa rola em velocidade própria
        for band_surface, y_dest, speed in self.parallax_layers:
            band_w = band_surface.get_width()
            offset = int(-self.scroll * speed) % band_w

            # Desenha duas vezes para criar o loop infinito
            self.screen.blit(band_surface, (offset - band_w, y_dest))
            self.screen.blit(band_surface, (offset, y_dest))

        # Nora
        nora_anim = (
            self.nora_animations.get(self.player.action)
            or self.nora_animations.get("run")
        )
        if nora_anim:
            nora_anim.draw(
                self.screen,
                (int(self.player.x), config.GROUND_Y - int(self.player.y)),
            )

        # Inimigos
        for enemy in self.enemies:
            enemy.animation.draw(
                self.screen,
                (int(enemy.x), config.GROUND_Y),
            )

        # HUD
        hud = self.font.render(
            f"Nora  |  Vidas: {self.lives}  |  Pontos: {int(self.score)}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(hud, (20, 20))

        # Game Over
        if self.game_over:
            title = self.big_font.render("GAME OVER", True, (255, 80, 100))
            hint = self.font.render(
                "Pressione R para reiniciar ou Esc para sair",
                True,
                (255, 255, 255),
            )
            self.screen.blit(title, title.get_rect(center=(config.WIDTH // 2, 250)))
            self.screen.blit(hint, hint.get_rect(center=(config.WIDTH // 2, 320)))

        pygame.display.flip()


# =============================================================
# ENTRY POINT
# =============================================================

if __name__ == "__main__":
    RunnerGame().run()