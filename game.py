
import pygame
import sys

from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from logger import log_state, log_event
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Game():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.updatable, self.drawable, self.asteroids)
        Shot.containers = (self.updatable, self.drawable, self.shots)
        AsteroidField.containers = (self.updatable,)

        
        self.asteroid_field = AsteroidField()
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.lives = 3
        
    def update(self, dt: float) -> None:
        self.updatable.update(dt)
        self.handle_collisions()

    def draw(self, screen: pygame.Surface) -> None:
        for obj in self.drawable:
            obj.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        # game-specific events will go here later (upgrades, name entry, etc.)
        pass

    def handle_collisions(self) -> None:
        for asteroid in self.asteroids:
            if self.player.invulnerable <= 0 and self.player.collides_with(asteroid):
                log_event("player_hit")
                self.lives -= 1
                if self.lives <= 0:
                    print("Game over!")
                    pygame.quit()
                    sys.exit()
                else:
                    self.respawn_player()
                break   # stop checking asteroids this frame; player has moved to center

            for shot in self.shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    asteroid.split()

    def respawn_player(self) -> None:
        self.player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.rotation = 0.0
        self.player.invulnerable = 2.0