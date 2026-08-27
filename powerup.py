import random
import pygame

from circleshape import CircleShape
from constants import POWERUP_RADIUS, POWERUP_LIFETIME_SECONDS, POWERUP_DRIFT_SPEED, LINE_WIDTH

POWERUP_WEIGHTS = [
    ("shield", 30),
    ("fire_rate", 30),
    ("weapon", 50),
    ("bomb", 20),
]

POWERUP_COLORS = {
    "shield": "purple",
    "speed": "blue",
    "weapon": "orange",
    "bomb": "red",
}


def random_powerup_kind() -> str:
    kinds = [k for k, _ in POWERUP_WEIGHTS]
    weights = [w for _, w in POWERUP_WEIGHTS]
    return random.choices(kinds, weights=weights, k=1)[0]


class PowerUp(CircleShape):
    def __init__(self, x: float, y: float, kind: str) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind
        self.lifetime = POWERUP_LIFETIME_SECONDS
    
        self.velocity = pygame.Vector2(POWERUP_DRIFT_SPEED, 0).rotate(random.uniform(0, 360))

    def draw(self, screen: pygame.Surface) -> None:
        color = POWERUP_COLORS.get(self.kind, "white")
        
        if self.lifetime < 2.0 and int(self.lifetime * 8) % 2 == 0:
            return
        pygame.draw.circle(screen, color, self.position, self.radius, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        self.wrap()