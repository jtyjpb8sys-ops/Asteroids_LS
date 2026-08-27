import random
import pygame


class Particle:
    def __init__(self, pos, color):
        self.pos = pygame.Vector2(pos)
        speed = random.uniform(40, 160)
        self.vel = pygame.Vector2(speed, 0).rotate(random.uniform(0, 360))
        self.max_life = random.uniform(0.3, 0.6)
        self.life = self.max_life
        self.color = color

    def update(self, dt):
        self.pos += self.vel * dt
        self.vel *= 0.90        
        self.life -= dt

    def draw(self, screen):
        if self.life <= 0:
            return
        
        r = max(1, int(3 * (self.life / self.max_life)))
        pygame.draw.circle(screen, self.color, self.pos, r)

    @property
    def dead(self):
        return self.life <= 0