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
# ANIMAÇÃO
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
    counted: bool = False


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
# ESTADO DA APLICAÇÃO
# =============================================================

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"


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
        self.huge_font = pygame.font.Font(None, 96)

        self.background = self.load_background()

        # Cada ação tem (filename, scale) agora
        self.nora_animations = self.load_action_set(config.NORA_ACTIONS)
        self.enemy_animations = self.load_action_set(
            config.ENEMY_ACTIONS, flip=True
        )

        self.state = STATE_MENU

        self.speed_multiplier = 1.0
        self.enemy_count_total = 15

        self.player: Player | None = None
        self.enemies: list[Enemy] = []
        self.lives = config.MAX_LIVES
        self.score = 0.0
        self.scroll = 0.0
        self.spawn_timer = 0.0
        self.damage_timer = 0.0
        self.enemies_spawned = 0
        self.enemies_passed = 0
        self.game_over = False
        self.won = False

    # ---------- CARREGAMENTO ----------

    def load_background(self) -> pygame.Surface | None:
        path = config.ASSET_DIR / config.BACKGROUND
        try:
            image = pygame.image.load(str(path)).convert()
        except pygame.error:
            return None

        img_w, img_h = image.get_size()
        target_w, target_h = config.WIDTH, config.HEIGHT

        if img_w >= target_w and img_h >= target_h:
            crop_x = (img_w - target_w) // 2
            crop_y = (img_h - target_h) // 2
            return image.subsurface(
                pygame.Rect(crop_x, crop_y, target_w, target_h)
            ).copy()

        scale_factor = min(target_w / img_w, target_h / img_h)
        new_w = int(img_w * scale_factor)
        new_h = int(img_h * scale_factor)
        image = pygame.transform.smoothscale(image, (new_w, new_h))

        canvas = pygame.Surface((target_w, target_h))
        canvas.fill((135, 198, 235))
        canvas.blit(image, ((target_w - new_w) // 2, (target_h - new_h) // 2))
        return canvas

    def load_action_set(
        self,
        actions: dict[str, tuple[str, float]],
        flip: bool = False,
    ) -> dict[str, AnimatedImage]:
        """
        Agora cada entrada é uma tupla (filename, scale).
        """
        result = {}
        for name, (filename, scale) in actions.items():
            result[name] = AnimatedImage(
                config.ASSET_DIR / filename,
                scale=scale,
                flip=flip,
            )
        return result

    # ---------- TRANSIÇÕES ----------

    def start_game(self) -> None:
        self.player = Player(
            x=config.PLAYER_X,
            animations=self.nora_animations,
        )
        self.enemies.clear()
        self.lives = config.MAX_LIVES
        self.score = 0.0
        self.scroll = 0.0
        self.spawn_timer = 0.5
        self.damage_timer = 0.0
        self.enemies_spawned = 0
        self.enemies_passed = 0
        self.game_over = False
        self.won = False
        self.state = STATE_PLAYING

    def back_to_menu(self) -> None:
        self.state = STATE_MENU

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
                else:
                    self.handle_event(event)

            if self.state == STATE_MENU:
                self.update_menu(dt)
                self.draw_menu()
            else:
                self.update(dt)
                self.draw()

        self.close()
        sys.exit()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if self.state == STATE_MENU:
            if event.key == pygame.K_UP:
                self.speed_multiplier = min(
                    config.SPEED_MAX,
                    round(self.speed_multiplier + config.SPEED_STEP, 2),
                )
            elif event.key == pygame.K_DOWN:
                self.speed_multiplier = max(
                    config.SPEED_MIN,
                    round(self.speed_multiplier - config.SPEED_STEP, 2),
                )
            elif event.key == pygame.K_RIGHT:
                self.enemy_count_total = min(
                    config.ENEMY_COUNT_MAX,
                    self.enemy_count_total + 5,
                )
            elif event.key == pygame.K_LEFT:
                self.enemy_count_total = max(
                    config.ENEMY_COUNT_MIN,
                    self.enemy_count_total - 5,
                )
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif self.state == STATE_PLAYING:
            if event.key in (pygame.K_SPACE, pygame.K_UP) and self.player:
                self.player.jump(config.JUMP_SPEED)
            elif event.key == pygame.K_ESCAPE:
                self.back_to_menu()

        elif self.state == STATE_GAME_OVER:
            if event.key == pygame.K_r:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.back_to_menu()

    # ---------- MENU ----------

    def update_menu(self, dt: float) -> None:
        self.scroll += config.WORLD_SPEED * dt

    def draw_menu(self) -> None:
        if self.background is not None:
            bg_w = self.background.get_width()
            offset = int(-self.scroll) % bg_w
            self.screen.blit(self.background, (offset - bg_w, 0))
            self.screen.blit(self.background, (offset, 0))
        else:
            self.screen.fill((135, 198, 235))

        overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.huge_font.render("NORA RUNNER", True, (255, 80, 140))
        self.screen.blit(title, title.get_rect(center=(config.WIDTH // 2, 120)))

        speed_txt = self.font.render(
            f"Velocidade: {self.speed_multiplier:.2f}x", True, (255, 255, 255)
        )
        self.screen.blit(speed_txt, speed_txt.get_rect(center=(config.WIDTH // 2, 260)))
        speed_hint = self.font.render("↑ / ↓ para ajustar", True, (180, 180, 180))
        self.screen.blit(speed_hint, speed_hint.get_rect(center=(config.WIDTH // 2, 295)))

        count_txt = self.font.render(
            f"Inimigas: {self.enemy_count_total}", True, (255, 255, 255)
        )
        self.screen.blit(count_txt, count_txt.get_rect(center=(config.WIDTH // 2, 360)))
        count_hint = self.font.render("← / → para ajustar", True, (180, 180, 180))
        self.screen.blit(count_hint, count_hint.get_rect(center=(config.WIDTH // 2, 395)))

        start_txt = self.font.render(
            "Pressione ENTER ou ESPAÇO para começar", True, (120, 255, 160)
        )
        self.screen.blit(start_txt, start_txt.get_rect(center=(config.WIDTH // 2, 480)))
        exit_txt = self.font.render("ESC para sair", True, (180, 180, 180))
        self.screen.blit(exit_txt, exit_txt.get_rect(center=(config.WIDTH // 2, 520)))

        pygame.display.flip()

    # ---------- UPDATE ----------

    def update(self, dt: float) -> None:
        if self.state == STATE_PLAYING and not self.game_over:
            self._update_world(dt)
            self._update_player(dt)
            self._update_enemies(dt)
            self._check_collisions()

        self._update_animations(dt)

    def _update_world(self, dt: float) -> None:
        speed = config.WORLD_SPEED * self.speed_multiplier

        self.damage_timer = max(0.0, self.damage_timer - dt)
        self.score += dt * 10
        self.scroll += speed * dt

        if self.enemies_spawned < self.enemy_count_total:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = config.SPAWN_INTERVAL
                self.enemies.append(
                    Enemy(
                        x=config.WIDTH + 80,
                        animation=self.enemy_animations["run"],
                    )
                )
                self.enemies_spawned += 1

    def _update_player(self, dt: float) -> None:
        p = self.player
        if p is None:
            return

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
        enemy_speed = config.ENEMY_SPEED * self.speed_multiplier

        for enemy in self.enemies:
            enemy.x -= enemy_speed * dt
            enemy.hit_timer = max(0.0, enemy.hit_timer - dt)
            if enemy.hit_timer <= 0 and enemy.action != "run":
                enemy.action = "run"
                enemy.animation = self.enemy_animations["run"]

        still_alive: list[Enemy] = []
        for enemy in self.enemies:
            if enemy.x < config.PLAYER_X and not enemy.counted:
                self.enemies_passed += 1
                enemy.counted = True

            if enemy.x > -200:
                still_alive.append(enemy)

        self.enemies = still_alive

        if (
            self.enemies_spawned >= self.enemy_count_total
            and self.enemies_passed >= self.enemy_count_total
            and len(self.enemies) == 0
            and not self.game_over
        ):
            self.won = True
            self.game_over = True
            self.state = STATE_GAME_OVER

    def _check_collisions(self) -> None:
        if self.damage_timer > 0:
            return
        if self.player is None:
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
                    self.state = STATE_GAME_OVER
                break

    def _player_rect(self) -> pygame.Rect:
        anim = (
            self.nora_animations.get(self.player.action)
            or self.nora_animations.get("run")
        )
        w = int(anim.width * 0.45)
        h = int(anim.height * 0.80)
        cx = self.player.x
        feet_y = config.GROUND_Y - int(self.player.y)
        return pygame.Rect(cx - w // 2, feet_y - h, w, h)

    def _enemy_rect(self, enemy: Enemy) -> pygame.Rect:
        w = int(enemy.animation.width * 0.45)
        h = int(enemy.animation.height * 0.80)
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
        if self.background is not None:
            bg_w = self.background.get_width()
            offset = int(-self.scroll) % bg_w
            self.screen.blit(self.background, (offset - bg_w, 0))
            self.screen.blit(self.background, (offset, 0))
        else:
            self.screen.fill((135, 198, 235))

        if self.player is not None:
            nora_anim = (
                self.nora_animations.get(self.player.action)
                or self.nora_animations.get("run")
            )
            if nora_anim:
                nora_anim.draw(
                    self.screen,
                    (int(self.player.x), config.GROUND_Y - int(self.player.y)),
                )

        for enemy in self.enemies:
            enemy.animation.draw(
                self.screen,
                (int(enemy.x), config.GROUND_Y),
            )

        hud = self.font.render(
            f"Nora  |  Vidas: {self.lives}  |  Pontos: {int(self.score)}  "
            f"|  Inimigas: {self.enemies_passed}/{self.enemy_count_total}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(hud, (20, 20))

        if self.state == STATE_GAME_OVER:
            if self.won:
                title = self.big_font.render("VOCÊ VENCEU!", True, (255,255,255))
            else:
                title = self.big_font.render("GAME OVER", True, (255, 255, 255))

            hint = self.font.render(
                "Pressione R para reiniciar ou Esc para o menu",
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