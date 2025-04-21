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
        self.target_row = row
        self.target_col = col
        self.final_value = value
        self.merged_with = False  # Flag to prevent double merges in one move

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

    def move_tile(self, delta_x, delta_y):
        # Update the tile's pixel position incrementally
        self.x_position += delta_x
        self.y_position += delta_y


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

    # Sort tiles by value for drawing, so smaller tiles are drawn first during animation
    sorted_tiles_for_drawing = sorted(tiles.values(), key=lambda tile: tile.value)

    for tile in sorted_tiles_for_drawing:
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

    # Create a list of tiles for processing
    tile_list = list(tiles.values())
    tiles_to_remove = []
    move_or_merge_occurred = False  # Flag to track if any tile moved or merged

    # Reset merge status for the new move
    for tile in tile_list:
        tile.merged_with = False
        tile.final_value = tile.value  # Reset final value

    # --- Simulate the move to determine target positions and merges ---

    # Determine sort order and movement delta based on direction
    if direction == "up":
        sort_key = lambda tile: tile.row
        reverse_sort = False
        delta_row, delta_col = -1, 0
    elif direction == "down":
        sort_key = lambda tile: tile.row
        reverse_sort = True
        delta_row, delta_col = 1, 0
    elif direction == "left":
        sort_key = lambda tile: tile.col
        reverse_sort = False
        delta_row, delta_col = 0, -1
    elif direction == "right":
        sort_key = lambda tile: tile.col
        reverse_sort = True
        delta_row, delta_col = 0, 1
    else:
        IS_ANIMATING = False
        return False  # Invalid direction

    # Sort tiles based on direction for simulation
    sorted_tiles_for_simulation = sorted(tile_list, key=sort_key, reverse=reverse_sort)

    # Create a temporary grid representation to simulate moves
    temp_grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    for tile in tile_list:
        temp_grid[tile.row][tile.col] = tile  # Populate temp grid with current tiles

    # Simulate moves and merges
    for tile in sorted_tiles_for_simulation:
        current_row = tile.row
        current_col = tile.col

        target_row = current_row
        target_col = current_col

        next_row = current_row + delta_row
        next_col = current_col + delta_col

        while 0 <= next_row < ROWS and 0 <= next_col < COLS:
            next_tile = temp_grid[next_row][next_col]

            if next_tile is None:
                # Move to the next empty cell in the simulation
                target_row = next_row
                target_col = next_col

                # Update next cell to check
                next_row += delta_row
                next_col += delta_col

            elif next_tile.value == tile.value and not next_tile.merged_with:
                # Merge with the next tile if values match and it hasn't been merged into this move
                target_row = next_row
                target_col = next_col
                tiles_to_remove.append(tile)  # This tile will be removed visually and from the list later
                next_tile.final_value *= 2  # Update the final value of the target tile
                next_tile.merged_with = True  # Mark the target tile as merged into
                move_or_merge_occurred = True  # Indicate a merge happened

                # Update temp grid to reflect the merge: the moving tile is removed
                temp_grid[current_row][current_col] = None
                # The merged tile remains at (target_row, target_col) in temp_grid (conceptually)

                break  # Stop checking in this direction after a merge
            else:
                # Cannot move past the next tile (either different value or already merged into)
                # The tile stops at its current position before this blocking tile
                break

        # Set the tile's target grid position based on the simulation
        tile.target_row = target_row
        tile.target_col = target_col

        # If the tile's target is different from its current position, a move occurred
        if (tile.row, tile.col) != (tile.target_row, tile.target_col):
            move_or_merge_occurred = True

        # Update temp grid to reflect the tile's final simulated position if it wasn't removed by merge
        if tile not in tiles_to_remove:
            if temp_grid[current_row][current_col] == tile:  # Only move in temp_grid if it wasn't merged out
                temp_grid[current_row][current_col] = None
                temp_grid[tile.target_row][tile.target_col] = tile

    # If no move or merge occurred in the simulation, no animation is needed
    if not move_or_merge_occurred:
        IS_ANIMATING = False
        return False

    # --- Animation Loop ---
    animation_complete = False
    while not animation_complete:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        animation_complete = True  # Assume animation is complete unless a tile is still moving

        for tile in tile_list:
            # Animate all tiles that were initially part of this move
            # Exclude tiles that are being removed by a merge from pixel movement calculation,
            # but keep them in tile_list for drawing until the end of animation.
            # Their target position was set during the simulation.

            target_x = tile.target_col * CELL_WIDTH
            target_y = tile.target_row * CELL_HEIGHT

            # Calculate the distance to the target pixel position
            dx = target_x - tile.x_position
            dy = target_y - tile.y_position

            # Move by MOVE_VELOCITY or the remaining distance, whichever is smaller
            move_x = 0
            move_y = 0

            if dx != 0:
                move_x = min(abs(dx), MOVE_VELOCITY) * (1 if dx > 0 else -1)
                # If moving by MOVE_VELOCITY would overshoot, move exactly to the target
                if abs(move_x) > abs(dx):
                    move_x = dx
                tile.x_position += move_x

            if dy != 0:
                move_y = min(abs(dy), MOVE_VELOCITY) * (1 if dy > 0 else -1)
                # If moving by MOVE_VELOCITY would overshoot, move exactly to the target
                if abs(move_y) > abs(dy):
                    move_y = dy
                tile.y_position += move_y

            # Check if the tile has reached its target pixel position
            if tile.x_position != target_x or tile.y_position != target_y:
                animation_complete = False  # At least one tile is still moving

        # Redraw elements during animation
        # Draw all tiles in the initial tile_list at their current animated positions.
        # Tiles marked for removal will be visually animated until they reach the target
        # and are removed from the main tiles dictionary after the animation.
        # We need to create a dictionary from the tile_list for draw_elements
        # Use unique keys for drawing to avoid clashes if multiple tiles end up at the same target temporarily
        drawing_tiles_during_animation = {f"{t.row}_{t.col}_{id(t)}": t for t in tile_list}
        draw_elements(window, drawing_tiles_during_animation)

        clock.tick(FPS)

    # --- After animation, update actual tile grid positions, values, and remove merged tiles ---
    new_tiles = {}

    for tile in tile_list:
        if tile not in tiles_to_remove:
            # Update the tile's actual grid row and col to the target
            tile.row = tile.target_row
            tile.col = tile.target_col
            # Ensure pixel position is exactly at the center of the target cell
            tile.x_position = tile.target_col * CELL_WIDTH
            tile.y_position = tile.target_row * CELL_HEIGHT
            # Update the tile's value to its final value AFTER animation
            tile.value = tile.final_value
            # Add to the new tiles dictionary using the final grid position as the key
            new_tiles[f"{tile.row}{tile.col}"] = tile

    tiles.clear()
    tiles.update(new_tiles)

    # Redraw one last time after the tiles dictionary is fully updated
    draw_elements(window, tiles)

    IS_ANIMATING = False
    return move_or_merge_occurred  # Return whether any tile moved or merged


def end_move(tiles):
    # Actions after tiles stop moving
    # Check for game over (no more possible moves)
    if len(tiles) == ROWS * COLS:
        # Basic check: if the grid is full, check if any merges are possible
        for row in range(ROWS):
            for col in range(COLS):
                tile = tiles.get(f"{row}{col}")
                if tile:
                    # Check right
                    if col < COLS - 1:
                        right_tile = tiles.get(f"{row}{col + 1}")
                        if right_tile and right_tile.value == tile.value:
                            return "continue"  # Possible merge
                    # Check down
                    if row < ROWS - 1:
                        down_tile = tiles.get(f"{row + 1}{col}")
                        if down_tile and down_tile.value == tile.value:
                            return "continue"  # Possible merge
        return "lost"  # No possible moves

    # Add a new tile (2 or 4)
    row, col = get_random_position(tiles)
    if row is not None and col is not None:
        tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def generate_tiles():
    # Create the initial two tiles for a new game
    tiles = {}
    for _ in range(2):
        row, col = get_random_position(tiles)
        if row is not None and col is not None:
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
