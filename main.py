import math
import random

import pygame

pygame.init()

FPS = 60
MOVE_VELOCITY = 20  # pixels per frame

WIDTH = 800
HEIGHT = 800
ROWS = 4
COLS = 4

CELL_HEIGHT = HEIGHT // ROWS
CELL_WIDTH = WIDTH // COLS

OUTLINE_COLOUR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOUR = (205, 192, 180)
FONT_SIZE = 60
FONT_COLOUR = (119, 110, 101)
try:
    FONT = pygame.font.SysFont("impact", FONT_SIZE)
except pygame.error:
    FONT = pygame.font.SysFont(None, FONT_SIZE, bold=True)

GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 by @overstimulation on GitHub")


def main(window):
    clock = pygame.time.Clock()
    game_running = True

    while game_running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                break

    pygame.quit()


if __name__ == "__main__":
    main(GAME_WINDOW)
