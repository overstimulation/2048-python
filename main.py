import math
import random

import pygame

pygame.init()

# --- Game Constants ---
FPS = 60
MOVE_VELOCITY = 20  # Pixels per frame for tile animation

WIDTH = 800
HEIGHT = 800
ROWS = 4
COLS = 4

CELL_HEIGHT = HEIGHT // ROWS
CELL_WIDTH = WIDTH // COLS

OUTLINE_COLOUR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOUR = (205, 192, 180)

# --- Font Setup ---
FONT_SIZE = 60
FONT_COLOUR = (119, 110, 101)
try:
    FONT = pygame.font.SysFont("impact", FONT_SIZE)
except pygame.error:
    FONT = pygame.font.SysFont(None, FONT_SIZE, bold=True)

# --- Global Animation Flag ---
# This flag will track if a tile animation is currently in progress
IS_ANIMATING = False

# --- Pygame Window Setup ---
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 by @overstimulation on GitHub")


# --- Tile Class ---
class Tile:
    # Colours corresponding to different tile values
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
        # Draw the tile rectangle and the number text centered
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

    def set_tile_position(self, ceiling=False):
        # Update the tile's grid row and column based on pixel position
        if ceiling:
            self.col = math.ceil(self.x_position / CELL_WIDTH)
            self.row = math.ceil(self.y_position / CELL_HEIGHT)
        else:
            self.col = math.floor(self.x_position / CELL_WIDTH)
            self.row = math.floor(self.y_position / CELL_HEIGHT)

    def move_tile(self, delta):
        # Update the tile's pixel position
        self.x_position += delta[0]
        self.y_position += delta[1]


# --- Drawing Functions ---
def draw_grid(window):
    # Draw the grid lines and the outer border
    # Vertical lines
    for col in range(1, COLS):
        x = col * CELL_WIDTH
        pygame.draw.line(window, OUTLINE_COLOUR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)

    # Horizontal lines
    for row in range(1, ROWS):
        y = row * CELL_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOUR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)

    # Border outline
    pygame.draw.rect(window, OUTLINE_COLOUR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw_elements(window, tiles):
    # Fill background, draw all tiles, then draw the grid
    window.fill(BACKGROUND_COLOUR)

    for tile in tiles.values():
        tile.draw_tile(window)

    draw_grid(window)

    pygame.display.update()


# --- Tile Generation and Placement ---
def get_random_position(tiles):
    # Find a random empty position in the grid
    row = None
    col = None

    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f"{row}{col}" not in tiles:
            break

    return row, col


# --- Game Logic Functions ---
def move_tiles(window, tiles, clock, direction):
    # Declare IS_ANIMATING as global to modify it
    global IS_ANIMATING

    # Set the flag to True at the start of the move animation
    IS_ANIMATING = True

    # Handles animation, movement, and merging of tiles
    updated = True  # Keep animating as long as tiles are moving or merging
    blocks = set()  # Prevent double merges in one move
    tile_moved_or_merged = False  # Flag to track if any tile moved or merged

    # --- Define direction-specific logic ---
    if direction == "up":
        sort_function = lambda x: x.row
        ascending_order = False
        delta = (0, -MOVE_VELOCITY)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y_position > next_tile.y_position + MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.y_position > next_tile.y_position + MOVE_VELOCITY + CELL_HEIGHT
        ceiling = True
    elif direction == "down":
        sort_function = lambda x: x.row
        ascending_order = True
        delta = (0, MOVE_VELOCITY)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y_position < next_tile.y_position - MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.y_position + MOVE_VELOCITY + CELL_HEIGHT < next_tile.y_position
        ceiling = False
    elif direction == "left":
        sort_function = lambda x: x.col
        ascending_order = False
        delta = (-MOVE_VELOCITY, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x_position > next_tile.x_position + MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.x_position > next_tile.x_position + MOVE_VELOCITY + CELL_WIDTH
        ceiling = True
    elif direction == "right":
        sort_function = lambda x: x.col
        ascending_order = True
        delta = (MOVE_VELOCITY, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x_position < next_tile.x_position - MOVE_VELOCITY
        move_check = lambda tile, next_tile: tile.x_position + MOVE_VELOCITY + CELL_WIDTH < next_tile.x_position
        ceiling = False
    else:
        # If direction is invalid, reset the animation flag and return
        IS_ANIMATING = False
        return False  # No movement occurred

    # --- Animation Loop ---
    while updated:
        # Handle events during animation to allow quitting but ignore other inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()  # Exit the program cleanly

        tiles_to_remove = []
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_function, reverse=ascending_order)

        # Iterate and process tiles based on movement logic
        for tile in sorted_tiles:
            if boundary_check(tile):
                continue

            # Store initial position to check for movement later
            initial_pos = (tile.x_position, tile.y_position)

            # Handle movement and merging conditions
            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move_tile(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move_tile(delta)
                else:
                    next_tile.value *= 2
                    tiles_to_remove.append(tile)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move_tile(delta)
            else:
                continue

            # Update grid position after potential movement
            tile.set_tile_position(ceiling)

            # Check if the tile actually moved
            if initial_pos != (tile.x_position, tile.y_position):
                updated = True  # Indicate that a tile moved
                tile_moved_or_merged = True  # Set the flag if movement occurred

        # Remove merged tiles
        for tile in tiles_to_remove:
            try:
                sorted_tiles.remove(tile)
                tile_moved_or_merged = True  # Set the flag if merging occurred
            except ValueError:
                pass

        # Update tile positions in the main dictionary and redraw
        update_tiles(window, tiles, sorted_tiles)

    # Set the flag back to False after the animation is complete
    IS_ANIMATING = False

    return tile_moved_or_merged  # Return whether any tile moved or merged


def end_move(tiles):
    # Actions after tiles stop moving
    if len(tiles) == 16:
        # TODO: Implement a proper game over check (check if any moves are possible)
        return "lost"  # Grid is full (basic check)

    # Add a new tile (2 or 4)
    row, col = get_random_position(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def update_tiles(window, tiles, sorted_tiles):
    # Update the main tiles dictionary with new positions and redraw
    tiles.clear()

    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    # Redraw elements during the animation
    draw_elements(window, tiles)


def generate_tiles():
    # Create the initial two tiles for a new game
    tiles = {}
    for _ in range(2):
        row, col = get_random_position(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)

    return tiles


# --- Main Game Loop ---
def main(window):
    clock = pygame.time.Clock()
    game_running = True

    tiles = generate_tiles()

    # Main loop
    while game_running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
                break

            # Only process key presses if no animation is in progress
            if event.type == pygame.KEYDOWN and not IS_ANIMATING:
                # Handle arrow key presses for movement
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    direction = None
                    if event.key == pygame.K_UP:
                        direction = "up"
                    elif event.key == pygame.K_DOWN:
                        direction = "down"
                    elif event.key == pygame.K_LEFT:
                        direction = "left"
                    elif event.key == pygame.K_RIGHT:
                        direction = "right"

                    # Only attempt to move if a valid direction was determined
                    if direction:
                        # Call move_tiles and check if a move or merge occurred
                        move_occurred = move_tiles(window, tiles, clock, direction)
                        # Spawn new tile only if a move or merge happened
                        if move_occurred:
                            game_state = end_move(tiles)
                            # Handle game state - currently just passes
                            if game_state == "lost":
                                pass

        # Drawing (ensure the initial state is drawn and updates happen during animation)
        if not IS_ANIMATING:
            draw_elements(window, tiles)

    pygame.quit()


if __name__ == "__main__":
    main(GAME_WINDOW)
