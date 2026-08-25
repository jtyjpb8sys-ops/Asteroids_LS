import pygame

from constants import LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH

class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def wrap(self) -> None:
        r = self.radius
        if self.position.x < -r:
            self.position.x = SCREEN_WIDTH + r
        elif self.position.x > SCREEN_WIDTH + r:
            self.position.x = -r
        if self.position.y < -r:
            self.position.y = SCREEN_HEIGHT + r
        elif self.position.y > SCREEN_HEIGHT + r:
            self.position.y = -r
            
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
