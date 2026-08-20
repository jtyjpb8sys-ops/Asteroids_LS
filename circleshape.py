import pygame

from constants import LINE_WIDTH


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.polygon(screen, "green", self.triangle(), LINE_WIDTH)

    def update(self, dt: float) -> None:
        # must override
        pass

    def collides_with(self,other) -> bool:
        distance = self.position.distance_to(other.position)
        if distance <= (self.radius + other.radius):
            return True
        else:
            return False
