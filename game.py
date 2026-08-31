
import pygame
import sys
import random

from leaderboard import is_high_score, add_score, top_scores
from explosion import Particle
from powerup import PowerUp, random_powerup_kind
from player import Player
from asteroid import Asteroid
from shot import Shot
from logger import log_state, log_event
from constants import (
    SCREEN_WIDTH,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    ASTEROID_MIN_RADIUS,
    POWERUP_DROP_CHANCE,
    BOMB_PENALTY
)

class Game():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        self.state = "playing"
        self.name_entry = ""      

        self.powerups = pygame.sprite.Group()
        self.updatable = pygame.sprite.Group()
        self.drawable = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.shots = pygame.sprite.Group()

        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill("black")
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.randint(80, 255)
            self.background.set_at((x, y), (brightness, brightness, brightness))
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (self.updatable, self.drawable, self.asteroids)
        Shot.containers = (self.updatable, self.drawable, self.shots)
        PowerUp.containers = (self.updatable, self.drawable, self.powerups)
        
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.particles = []

        self.lives = 3
        self.bombs = 0

        self.elapsed = 0.0          
        self.spawn_timer = 0.0
        self.score = 0

    def draw_hud(self, screen: pygame.Surface) -> None:
        bar_h = 40

        for i in range(self.lives):
            cx = 24 + i * 26
            cy = bar_h // 2
            pts = [
                pygame.Vector2(cx, cy - 9),
                pygame.Vector2(cx - 7, cy + 8),
                pygame.Vector2(cx + 7, cy + 8),
            ]
            pygame.draw.polygon(screen, "green", pts, LINE_WIDTH)

        mins = int(self.elapsed) // 60
        secs = int(self.elapsed) % 60
        score_surf = self.font.render(f"{self.score}", True, "white")
        screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 6))
        time_surf = self.small_font.render(f"{mins}:{secs:02d}", True, "grey")
        screen.blit(time_surf, (SCREEN_WIDTH // 2 - time_surf.get_width() // 2, 6 + score_surf.get_height()))

        for i in range(self.bombs):
            cx = SCREEN_WIDTH - 20 - i * 22
            pygame.draw.circle(screen, "red", (cx, bar_h // 2), 7)

        buffs = []
        if self.player.has_shield:
            buffs.append(("SHIELD", "cyan"))
        if self.player.weapon_timer > 0:
            buffs.append((f"{self.player.weapon.upper()} {self.player.weapon_timer:.0f}", "orange"))
        if self.player.fire_rate_timer > 0:
            buffs.append((f"RAPID {self.player.fire_rate_timer:.0f}", "yellow"))

        bx = SCREEN_WIDTH - 20 - self.bombs * 22 - 20
        for label, color in buffs:
            s = self.small_font.render(label, True, color)
            bx -= s.get_width() + 12
            screen.blit(s, (bx, bar_h // 2 - s.get_height() // 2))


    def current_concurrent_target(self) -> int:
        from constants import DIFFICULTY_BASE_CONCURRENT, DIFFICULTY_CONCURRENT_PER_MIN
        minutes = self.elapsed / 60.0
        return int(DIFFICULTY_BASE_CONCURRENT + minutes * DIFFICULTY_CONCURRENT_PER_MIN)

    def current_speed_mult(self) -> float:
        from constants import DIFFICULTY_SPEED_PER_MIN
        minutes = self.elapsed / 60.0
        return 1.0 + minutes * DIFFICULTY_SPEED_PER_MIN

    def update(self, dt: float) -> None:
        if self.state != "playing":
            return
        self.elapsed += dt
        self.updatable.update(dt)
        self.update_spawning(dt)
        self.handle_collisions()
        self.handle_pickups()
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.dead]
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))
        for obj in self.drawable:
            obj.draw(screen)
        for p in self.particles:
            p.draw(screen)

        if self.state == "playing":
            self.draw_hud(screen)
        elif self.state == "enter_name":
            self.draw_enter_name(screen)
        elif self.state == "game_over":
            self.draw_game_over(screen)

    def draw_enter_name(self, screen: pygame.Surface) -> None:
        cx = SCREEN_WIDTH // 2
        title = self.font.render("NEW HIGH SCORE!", True, "yellow")
        screen.blit(title, (cx - title.get_width() // 2, 180))

        score_surf = self.font.render(f"Score: {self.score}", True, "white")
        screen.blit(score_surf, (cx - score_surf.get_width() // 2, 230))

        prompt = self.small_font.render("Enter your initials:", True, "grey")
        screen.blit(prompt, (cx - prompt.get_width() // 2, 300))

        display = self.name_entry + "_" * (3 - len(self.name_entry))
        initials = pygame.font.Font(None, 96).render(" ".join(display), True, "cyan")
        screen.blit(initials, (cx - initials.get_width() // 2, 340))

    def draw_game_over(self, screen: pygame.Surface) -> None:
        cx = SCREEN_WIDTH // 2
        title = self.font.render("GAME OVER", True, "red")
        screen.blit(title, (cx - title.get_width() // 2, 100))

        score_surf = self.small_font.render(f"Your score: {self.score}", True, "white")
        screen.blit(score_surf, (cx - score_surf.get_width() // 2, 145))

        header = self.font.render("LEADERBOARD", True, "yellow")
        screen.blit(header, (cx - header.get_width() // 2, 200))

        y = 250
        for i, entry in enumerate(self.scores):
            line = f"{i + 1:2d}.  {entry['name']:<3}   {entry['score']}"
            color = "cyan" if entry["score"] == self.score else "white"
            row = self.small_font.render(line, True, color)
            screen.blit(row, (cx - 100, y))
            y += 30

        prompt = self.small_font.render("Press R to play again", True, "grey")
        screen.blit(prompt, (cx - prompt.get_width() // 2, y + 20))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if self.state == "playing":
            if event.key == pygame.K_b:
                self.deploy_bomb()

        elif self.state == "enter_name":
            if event.key == pygame.K_BACKSPACE:
                self.name_entry = self.name_entry[:-1]
            elif event.key == pygame.K_RETURN and len(self.name_entry) > 0:
                self.scores = add_score(self.name_entry, self.score)
                self.state = "game_over"
            elif len(self.name_entry) < 3 and event.unicode.isalpha():
                self.name_entry += event.unicode.upper()

        elif self.state == "game_over":
            if event.key == pygame.K_r:
                self.restart()
                
    def restart(self) -> None:
        for group in (self.updatable, self.drawable, self.asteroids, self.shots, self.powerups):
            group.empty()
        self.particles = []
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.lives = 3
        self.bombs = 0
        self.score = 0
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.name_entry = ""
        self.state = "playing"

    def handle_collisions(self) -> None:
        for asteroid in self.asteroids:
            if self.player.invulnerable <= 0 and self.player.collides_with(asteroid):
                if self.player.has_shield:
                    self.player.has_shield = False
                    self.player.invulnerable = 1.0   
                    log_event("shield_absorbed")
                    asteroid.split()
                    break
                log_event("player_hit")
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over()
                    return
                else:
                    self.respawn_player()
                break

            for shot in self.shots:
               if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    self.score += self.asteroid_score(asteroid.radius)
                    burst = int(asteroid.radius / 3)
                    self.spawn_explosion(asteroid.position, asteroid.color, burst)
                    if asteroid.radius <= ASTEROID_MIN_RADIUS and random.random() < POWERUP_DROP_CHANCE:
                        self.spawn_powerup(asteroid.position)
                    asteroid.split()

    def respawn_player(self) -> None:
        self.player.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.rotation = 0.0
        self.player.invulnerable = 2.0

    def game_over(self) -> None:
        log_event("game_over", score=self.score)
        if is_high_score(self.score):
            self.state = "enter_name"
            self.name_entry = ""
        else:
            self.scores = top_scores()
            self.state = "game_over"

    def spawn_asteroid(self) -> None:
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
        speed = random.randint(40, 100) * self.current_speed_mult()
        velocity = edge[0] * speed
        velocity = velocity.rotate(random.randint(-30, 30))
        position = edge[1](random.uniform(0, 1))
        kind = random.randint(1, ASTEROID_KINDS)
        asteroid = Asteroid(position.x, position.y, ASTEROID_MIN_RADIUS * kind)
        asteroid.velocity = velocity


    def update_spawning(self, dt: float) -> None:
        from constants import ASTEROID_SPAWN_INTERVAL
        self.spawn_timer += dt
        if self.spawn_timer < ASTEROID_SPAWN_INTERVAL:
            return
        self.spawn_timer = 0.0

        target = self.current_concurrent_target()
        while len(self.asteroids) < target:
            self.spawn_asteroid()

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
            self.player.fire_rate_timer = min(self.player.fire_rate_timer + FIRE_RATE_BUFF_DURATION, 30.0)
        elif kind == "shield":
            self.player.has_shield = True
        elif kind == "weapon":
            from constants import WEAPON_BUFF_DURATION
            self.player.weapon = random.choice(["shotgun", "double"])
            self.player.weapon_timer = min(self.player.weapon_timer + WEAPON_BUFF_DURATION, 30.0)
            log_event("weapon_equipped", weapon=self.player.weapon)
        elif kind == "bomb":
            from constants import MAX_BOMBS
            self.bombs = min(self.bombs + 1, MAX_BOMBS)
            log_event("bomb_collected", bombs = self.bombs)

    def deploy_bomb(self) -> None:
        if self.bombs <= 0:
            return
        self.bombs -= 1
        self.score = max(0, self.score - BOMB_PENALTY)
        log_event("bomb_deployed")
        for asteroid in list(self.asteroids):
            self.spawn_explosion(asteroid.position, asteroid.color)
            asteroid.kill()

    def asteroid_score(self, radius: float) -> int:
        from constants import SCORE_LARGE, SCORE_MEDIUM, SCORE_SMALL, ASTEROID_MIN_RADIUS
        if radius <= ASTEROID_MIN_RADIUS:
            return SCORE_SMALL
        elif radius <= ASTEROID_MIN_RADIUS * 2:
            return SCORE_MEDIUM
        else:
            return SCORE_LARGE

    def spawn_explosion(self, position, color="white", count=12) -> None:
        for _ in range(count):
            self.particles.append(Particle(position, color))