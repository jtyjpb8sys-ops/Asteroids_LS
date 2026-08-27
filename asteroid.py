
import random
import math

import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.shape = []
        self.color = "white"
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            jitter = random.uniform(0.75, 1.15)   
            self.shape.append(pygame.Vector2(math.cos(angle), math.sin(angle)) * jitter)

    def draw(self, screen: pygame.surface) -> None:
        points = [self.position + p * self.radius for p in self.shape]
        pygame.draw.polygon(screen, self.color, points, LINE_WIDTH)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

        self.wrap()

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        log_event("asteroid_split")
        angle =random.uniform(20, 50)
        self.velocity.rotate(angle)
        self.velocity.rotate(-angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = self.velocity.rotate(angle) * 1.2

        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2.velocity = self.velocity.rotate(-angle) * 1.2



        