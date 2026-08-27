
import pygame

from circleshape import CircleShape
from constants import LINE_WIDTH, SHOT_RADIUS, SHOT_LIFETIME_SECONDS


class Shot(CircleShape):
    def __init__(self, x, y, lifetime=None, color="white"):
        super().__init__(x, y, SHOT_RADIUS)
        self.lifetime = lifetime if lifetime is not None else SHOT_LIFETIME_SECONDS
        self.color = color

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self.color, self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()

        