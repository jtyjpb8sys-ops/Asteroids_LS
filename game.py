
import pygame
import sys
import random

from powerup import PowerUp, random_powerup_kind
from player import Player
from asteroid import Asteroid
from shot import Shot
from logger import log_state, log_event
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASTEROID_MIN_RADIUS,
    POWERUP_DROP_CHANCE,
)

class Game():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        self.powerups = pygame.sprite.Group()
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.updatable, self.drawable, self.asteroids)
        Shot.containers = (self.updatable, self.drawable, self.shots)
        PowerUp.containers = (self.updatable, self.drawable, self.powerups)
        
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.lives = 3

        self.wave = 0
        self.kills_this_wave = 0
        self.quota = 0
        self.concurrent_target = 0
        self.spawn_timer = 0.0
        self.start_next_wave()
        
    def update(self, dt: float) -> None:
        self.updatable.update(dt)
        self.update_spawning(dt)
        self.handle_collisions()
        self.handle_pickups()
        if self.kills_this_wave >= self.quota and len(self.asteroids) == 0:
            self.start_next_wave()

    def draw(self, screen: pygame.Surface) -> None:
        for obj in self.drawable:
            obj.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def handle_collisions(self) -> None:
        for asteroid in self.asteroids:
            if self.player.invulnerable <= 0 and self.player.collides_with(asteroid):
                if self.player.has_shield:
                    self.player.has_shield = False
                    self.player.invulnerable = 1.0   # brief grace so you can escape
                    log_event("shield_absorbed")
                    asteroid.split()
                    break
                log_event("player_hit")
                self.lives -= 1
                if self.lives <= 0:
                    print("Game over!")
                    pygame.quit()
                    sys.exit()
                else:
                    self.respawn_player()
                break

            for shot in self.shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    if asteroid.radius <= ASTEROID_MIN_RADIUS and random.random() < POWERUP_DROP_CHANCE:
                        self.spawn_powerup(asteroid.position)
                    asteroid.split()
                    self.kills_this_wave += 1

    def respawn_player(self) -> None:
        self.player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.rotation = 0.0
        self.player.invulnerable = 2.0

    def spawn_asteroid(self) -> None:
        import random
        from constants import (
            ASTEROID_MIN_RADIUS, ASTEROID_KINDS, ASTEROID_MAX_RADIUS,
            SCREEN_WIDTH, SCREEN_HEIGHT,
        )
        edges = [
            (pygame.Vector2(1, 0), lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)),
            (pygame.Vector2(-1, 0), lambda y: pygame.Vector2(SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)),
            (pygame.Vector2(0, 1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS)),
            (pygame.Vector2(0, -1), lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS)),
        ]
        edge = random.choice(edges)
        speed = random.randint(40, 100) * (1 + self.wave * 0.05)  
        velocity = edge[0] * speed
        velocity = velocity.rotate(random.randint(-30, 30))
        position = edge[1](random.uniform(0, 1))
        kind = random.randint(1, ASTEROID_KINDS)
        asteroid = Asteroid(position.x, position.y, ASTEROID_MIN_RADIUS * kind)
        asteroid.velocity = velocity

    def start_next_wave(self) -> None:
        from constants import (
            WAVE_BASE_CONCURRENT, WAVE_BASE_QUOTA,
            WAVE_CONCURRENT_GROWTH, WAVE_QUOTA_GROWTH,
            )
        self.wave += 1
        self.kills_this_wave = 0
        self.concurrent_target = WAVE_BASE_CONCURRENT + (self.wave - 1) * WAVE_CONCURRENT_GROWTH
        self.quota = WAVE_BASE_QUOTA + (self.wave - 1) * WAVE_QUOTA_GROWTH
        log_event("wave_start", wave=self.wave)
        print(f"Wave {self.wave}  (quota {self.quota}, concurrent {self.concurrent_target})")

    def update_spawning(self, dt: float) -> None:
        from constants import ASTEROID_SPAWN_INTERVAL
        self.spawn_timer += dt
        if self.spawn_timer < ASTEROID_SPAWN_INTERVAL:
            return
        self.spawn_timer = 0.0

        remaining_to_spawn = self.quota - self.kills_this_wave - len(self.asteroids)
        
        while len(self.asteroids) < self.concurrent_target and remaining_to_spawn > 0:
            self.spawn_asteroid()
            remaining_to_spawn -= 1

    def spawn_powerup(self, position: pygame.Vector2) -> None:
        kind = random_powerup_kind()
        PowerUp(position.x, position.y, kind)
        log_event("powerup_drop", kind=kind)

    def handle_pickups(self) -> None:
        for powerup in self.powerups:
            if self.player.collides_with(powerup):
                log_event("powerup_pickup", kind=powerup.kind)
                self.apply_powerup(powerup.kind)
                powerup.kill()

    def apply_powerup(self, kind: str) -> None:
        from constants import FIRE_RATE_BUFF_DURATION, FIRE_RATE_BUFF_MULTIPLIER
        if kind == "fire_rate":
            self.player.fire_rate_mult = FIRE_RATE_BUFF_MULTIPLIER
            self.player.fire_rate_timer = FIRE_RATE_BUFF_DURATION
        elif kind == "shield":
            self.player.has_shield = True
        elif kind == "weapon":
            pass   # next piece
        elif kind == "bomb":
            pass   # piece after