
import pygame
import sys

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state
from game import Game


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen dimensions: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    pygame.init()
    clock = pygame.time.Clock()
    dt = 0.0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    game = Game(screen)

    while True:
        dt = clock.tick(60) / 1000
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            game.handle_event(event)

        screen.fill("black")
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()