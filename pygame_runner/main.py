from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from . import config
except ImportError:
    import config

import pygame
from PIL import Image, ImageSequence


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
                surface = pygame.image.fromstring(rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
                self.frames.append(surface)
                self.durations.append(max(30, frame.info.get("duration", 100)))
        except (FileNotFoundError, OSError):
            self.frames = [pygame.Surface((64, 64), pygame.SRCALPHA)]
            self.durations = [100]

    def update(self, dt_ms: int) -> None:
        if len(self.frames) < 2:
            return
        self.elapsed += dt_ms
        if self.elapsed >= self.durations[self.index]:
            self.elapsed = 0
            self.index = (self.index + 1) % len(self.frames)

    def draw(self, target: pygame.Surface, center: tuple[int, int]) -> pygame.Rect:
        frame = self.frames[self.index]
        size = (max(1, int(frame.width * self.scale)), max(1, int(frame.height * self.scale)))
        frame = pygame.transform.smoothscale(frame, size)
        if self.flip:
            frame = pygame.transform.flip(frame, True, False)
        rect = frame.get_rect(midbottom=center)
        target.blit(frame, rect)
        return rect


@dataclass
class Enemy:
    x: float
    animation: AnimatedImage
    action: str = "run"
    hit_timer: float = 0.0


class RunnerGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Nora Runner")
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.big_font = pygame.font.Font(None, 72)
        self.backgrounds = self.load_backgrounds()
        self.nora = self.load_action_set(config.NORA_ACTIONS)
        self.enemy_actions = self.load_action_set(config.ENEMY_ACTIONS, flip=True)
        self.action = "run"
        self.lives = config.MAX_LIVES
        self.score = 0.0
        self.scroll = 0.0
        self.spawn_timer = config.SPAWN_INTERVAL
        self.damage_timer = 0.0
        self.game_over = False
        self.enemies: list[Enemy] = []

    def load_backgrounds(self) -> list[tuple[pygame.Surface, float]]:
        backgrounds = []
        for filename, speed in config.SCENERY:
            path = config.ASSET_DIR / filename
            try:
                image = pygame.image.load(path).convert()
                image = pygame.transform.scale(image, (config.WIDTH, config.HEIGHT))
                backgrounds.append((image, speed))
            except pygame.error:
                continue
        return backgrounds

    def load_action_set(self, actions: dict[str, str], flip: bool = False) -> dict[str, AnimatedImage]:
        return {
            name: AnimatedImage(config.ASSET_DIR / filename, flip=flip)
            for name, filename in actions.items()
        }

    def reset(self) -> None:
        self.action = "run"
        self.lives = config.MAX_LIVES
        self.score = 0
        self.scroll = 0
        self.spawn_timer = config.SPAWN_INTERVAL
        self.damage_timer = 0
        self.game_over = False
        self.enemies.clear()

    def close(self) -> None:
        pygame.quit()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP) and not self.game_over:
                        self.action = "jump"
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            self.update(dt)
            self.draw()
        self.close()
        sys.exit()

    def update(self, dt: float) -> None:
        if self.game_over:
            self.update_animations(dt)
            return
        self.damage_timer = max(0, self.damage_timer - dt)
        self.score += dt * 10
        self.scroll += config.WORLD_SPEED * dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = config.SPAWN_INTERVAL
            self.enemies.append(Enemy(config.WIDTH + 80, self.enemy_actions["run"]))

        if self.action == "jump":
            self.action = "run"
        for enemy in self.enemies:
            enemy.x -= config.WORLD_SPEED * dt
            enemy.hit_timer = max(0, enemy.hit_timer - dt)
            if enemy.hit_timer <= 0:
                enemy.animation = self.enemy_actions["run"]
        self.enemies = [enemy for enemy in self.enemies if enemy.x > -120]

        nora_rect = pygame.Rect(config.PLAYER_X - 28, config.GROUND_Y - 100, 56, 100)
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(int(enemy.x - 28), config.GROUND_Y - 90, 56, 90)
            if self.damage_timer <= 0 and nora_rect.colliderect(enemy_rect):
                self.lives -= 1
                self.damage_timer = config.DAMAGE_COOLDOWN
                enemy.animation = self.enemy_actions["bump"]
                enemy.hit_timer = 0.4
                self.action = "bump" if self.lives > 0 else "defeat"
                if self.lives <= 0:
                    self.game_over = True
                break
        self.update_animations(dt)

    def update_animations(self, dt: float) -> None:
        dt_ms = int(dt * 1000)
        for animation in self.background_animations:
            animation.update(dt_ms)
        self.nora[self.action].update(dt_ms)
        for enemy in self.enemies:
            enemy.animation.update(dt_ms)

    @property
    def background_animations(self):
        return []

    def draw(self) -> None:
        self.screen.fill((135, 198, 235))
        for image, speed in self.backgrounds:
            offset = int(-self.scroll * speed) % config.WIDTH
            self.screen.blit(image, (offset - config.WIDTH, 0))
            self.screen.blit(image, (offset, 0))

        self.screen.fill((96, 75, 55), (0, config.GROUND_Y, config.WIDTH, config.HEIGHT - config.GROUND_Y))
        nora_animation = self.nora[self.action]
        nora_animation.draw(self.screen, (config.PLAYER_X, config.GROUND_Y))
        for enemy in self.enemies:
            enemy.animation.draw(self.screen, (int(enemy.x), config.GROUND_Y))

        hud = self.font.render(f"Nora  |  Vidas: {self.lives}  |  Pontos: {int(self.score)}", True, (255, 255, 255))
        self.screen.blit(hud, (20, 20))
        if self.game_over:
            title = self.big_font.render("GAME OVER", True, (255, 80, 100))
            hint = self.font.render("Pressione R para reiniciar ou Esc para sair", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(config.WIDTH // 2, 250)))
            self.screen.blit(hint, hint.get_rect(center=(config.WIDTH // 2, 320)))
        pygame.display.flip()


if __name__ == "__main__":
    RunnerGame().run()
