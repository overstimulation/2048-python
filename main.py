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


class Tile:
    COLOURS = [
        (237, 229, 218),  # 2
        (238, 225, 201),  # 4
        (243, 178, 122),  # 8
        (246, 150, 101),  # 16
        (247, 124, 95),  # 32
        (247, 95, 59),  # 64
        (237, 208, 115),  # 128
        (237, 204, 99),  # 256
        (236, 202, 80),  # 512
        (237, 197, 63),  # 1024
        (237, 194, 46),  # 2048
        (238, 204, 97),  # 4096
        (237, 197, 63),  # 8192 and higher
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x_position = col * CELL_WIDTH
        self.y_position = row * CELL_HEIGHT

    def get_tile_colour(self):
        # Calculate the base index using log2
        calculated_index = int(math.log2(self.value)) - 1

        # Ensure the index does not exceed the maximum index in COLOURS
        colour_index = min(calculated_index, len(self.COLOURS) - 1)

        colour = self.COLOURS[colour_index]
        return colour

    def draw_tile(self, window):
        colour = self.get_tile_colour()
        pygame.draw.rect(window, colour, (self.x_position, self.y_position, CELL_WIDTH, CELL_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOUR)
        window.blit(
            text,
            (
                self.x_position + (CELL_WIDTH / 2 - text.get_width() / 2),
                self.y_position + (CELL_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_tile_position(self):
        pass

    def move_tile(self, delta):
        pass


def draw_grid(window):
    # vertical lines
    for col in range(1, COLS):
        x = col * CELL_WIDTH
        pygame.draw.line(window, OUTLINE_COLOUR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    # horizontal lines
    for row in range(1, ROWS):
        y = row * CELL_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOUR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    # border outline
    pygame.draw.rect(window, OUTLINE_COLOUR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw_elements(window, tiles):
    window.fill(BACKGROUND_COLOUR)

    for tile in tiles.values():
        tile.draw_tile(window)

    draw_grid(window)

    pygame.display.update()


def get_random_position(tiles):
    row = None
    col = None

    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_position(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles


def main(window):
    clock = pygame.time.Clock()
    game_running = True

    tiles = generate_tiles()

    while game_running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                break

        draw_elements(window, tiles)

    pygame.quit()


if __name__ == "__main__":
    main(GAME_WINDOW)
