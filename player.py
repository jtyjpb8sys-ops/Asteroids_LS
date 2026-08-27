
import pygame

from circleshape import CircleShape
from constants import PLAYER_RADIUS, PLAYER_SHOOT_SPEED, PLAYER_SPEED, PLAYER_TURN_SPEED, PLAYER_SHOT_COOLDOWN_SECONDS, PLAYER_ACCELERATION, PLAYER_MAX_SPEED, PLAYER_DRAG, LINE_WIDTH
from shot import Shot
from collisions import circle_triangle_collision


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0.0
        self.shot_cooldown = 0.0
        self.invulnerable = 0.0
        self.fire_rate_timer = 0.0
        self.fire_rate_mult = 1.0
        self.has_shield = False
        self.weapon = "default"
        self.weapon_timer = 0.0
        
    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def collides_with(self, other) -> bool:
        return circle_triangle_collision(other.position, other.radius, self.triangle())

    def draw(self, screen: pygame.Surface) -> None:
        color = "green"
        if self.invulnerable > 0 and int(self.invulnerable * 10) % 2 == 0:
            color = "white"
        pygame.draw.polygon(screen, color, self.triangle(), LINE_WIDTH)
        if self.has_shield:
            pygame.draw.circle(screen, "purple", self.position, self.radius + 6, 2)

    def rotate(self, dt: float):
        rotation = PLAYER_TURN_SPEED * dt
        self.rotation += rotation

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        self.shot_cooldown -= dt

        if self.weapon_timer > 0:
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.weapon = "default"

        if self.invulnerable > 0:
            self.invulnerable -= dt
        if self.fire_rate_timer > 0:
            self.fire_rate_timer -= dt
            if self.fire_rate_timer <= 0:
                self.fire_rate_mult = 1.0

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.accelerate(dt, 1)
        if keys[pygame.K_s]:
            self.accelerate(dt, -1)
        if keys[pygame.K_SPACE]:
            self.shoot()

        drag_factor = pow(PLAYER_DRAG, dt)
        self.velocity *= drag_factor
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED)
        self.position += self.velocity * dt
        self.wrap()

    def accelerate(self, dt: float, direction: int):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += forward * PLAYER_ACCELERATION * direction * dt

    def move(self, dt: float):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector

    def shoot(self):
        if self.shot_cooldown > 0:
            return
        
        from constants import (
            SHOTGUN_PELLETS, SHOTGUN_SPREAD, SHOTGUN_LIFETIME, SHOTGUN_COOLDOWN,
            DOUBLE_OFFSET, DOUBLE_LIFETIME, DOUBLE_COOLDOWN,
        )
        forward = pygame.Vector2(0, 1).rotate(self.rotation)

        if self.weapon == "shotgun":
            for i in range(SHOTGUN_PELLETS):
                # fan the pellets across the spread
                offset = (i / (SHOTGUN_PELLETS - 1) - 0.5) * SHOTGUN_SPREAD
                shot = Shot(self.position.x, self.position.y, SHOTGUN_LIFETIME)
                shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation + offset) * PLAYER_SHOOT_SPEED
            cooldown = SHOTGUN_COOLDOWN

        elif self.weapon == "double":
            right = pygame.Vector2(forward.y, -forward.x)  # perpendicular
            for side in (-1, 1):
                pos = self.position + right * (DOUBLE_OFFSET * side)
                shot = Shot(pos.x, pos.y, DOUBLE_LIFETIME)
                shot.velocity = forward * PLAYER_SHOOT_SPEED
            cooldown = DOUBLE_COOLDOWN

        else:  # default single shot
            shot = Shot(self.position.x, self.position.y)
            shot.velocity = forward * PLAYER_SHOOT_SPEED
            cooldown = PLAYER_SHOT_COOLDOWN_SECONDS

        self.shot_cooldown = cooldown * self.fire_rate_mult
