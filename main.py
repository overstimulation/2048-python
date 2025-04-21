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

# --- Game State ---
GAME_STATE = "playing"  # Possible states: "playing", "won", "lost"

# --- Pygame Window Setup ---
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

try:
    icon_surface = pygame.image.load("2048_icon.png")
    pygame.display.set_icon(icon_surface)
except pygame.error:
    pass  # If icon fails to load, continue with default

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
        return self.COLOURS[colour_index]

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


def draw_game_over(window):
    # Create a semi-transparent overlay to darken the background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # RGBA: black with alpha for transparency
    window.blit(overlay, (0, 0))

    # Draw the message box in the center
    message_box_width, message_box_height = 600, 200  # Box size for the overlay message
    message_box_x = (WIDTH - message_box_width) // 2
    message_box_y = (HEIGHT - message_box_height) // 2
    pygame.draw.rect(window, BACKGROUND_COLOUR, (message_box_x, message_box_y, message_box_width, message_box_height))
    pygame.draw.rect(
        window, OUTLINE_COLOUR, (message_box_x, message_box_y, message_box_width, message_box_height), OUTLINE_THICKNESS
    )

    # Render and center the "Game Over!" and restart instructions
    game_over_text = FONT.render("Game Over!", True, FONT_COLOUR)
    restart_text = FONT.render("Press SPACE to Restart", True, FONT_COLOUR)
    window.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    window.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


def draw_game_won(window):
    # Create a semi-transparent gold overlay to highlight the win
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 215, 0, 128))  # RGBA: gold with alpha for transparency
    window.blit(overlay, (0, 0))

    # Draw the message box in the center
    message_box_width, message_box_height = 700, 250  # Box size for the overlay message
    message_box_x = (WIDTH - message_box_width) // 2
    message_box_y = (HEIGHT - message_box_height) // 2
    pygame.draw.rect(window, BACKGROUND_COLOUR, (message_box_x, message_box_y, message_box_width, message_box_height))
    pygame.draw.rect(
        window, OUTLINE_COLOUR, (message_box_x, message_box_y, message_box_width, message_box_height), OUTLINE_THICKNESS
    )

    # Render and center the win message and instructions
    win_text = FONT.render("You Won!", True, FONT_COLOUR)
    restart_text = FONT.render("Press SPACE to Restart", True, FONT_COLOUR)
    continue_text = FONT.render("Press C to Keep Playing", True, FONT_COLOUR)
    window.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
    window.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    window.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))


# --- Tile Generation and Placement ---
def get_random_position(tiles):
    # Find a random empty position in the grid
    while True:
        row, col = random.randrange(ROWS), random.randrange(COLS)
        if f"{row}{col}" not in tiles:
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
        current_row, current_col = tile.row, tile.col
        target_row, target_col = current_row, current_col
        next_row, next_col = current_row + delta_row, current_col + delta_col

        while 0 <= next_row < ROWS and 0 <= next_col < COLS:
            next_tile = temp_grid[next_row][next_col]

            if next_tile is None:
                # Move to the next empty cell in the simulation
                target_row, target_col = next_row, next_col
                # Update next cell to check
                next_row += delta_row
                next_col += delta_col

            elif next_tile.value == tile.value and not next_tile.merged_with:
                # Merge with the next tile if values match and it hasn't been merged into this move
                target_row, target_col = next_row, next_col
                tiles_to_remove.append(tile)  # This tile will be removed visually and from the list later
                next_tile.final_value *= 2  # Update the final value of the target tile
                next_tile.merged_with = True  # Mark the target tile as merged into
                move_or_merge_occurred = True  # Indicate a merge happened

                # Update temp grid to reflect the merge: the moving tile is removed
                temp_grid[current_row][current_col] = None
                break  # Stop checking in this direction after a merge
            else:
                # Cannot move past the next tile (either different value or already merged into)
                # The tile stops at its current position before this blocking tile
                break

        # Set the tile's target grid position based on the simulation
        tile.target_row, tile.target_col = target_row, target_col
        # If the tile's target is different from its current position, a move occurred
        if (tile.row, tile.col) != (tile.target_row, tile.target_col):
            move_or_merge_occurred = True
        # Update temp grid to reflect the tile's final simulated position if it wasn't removed by merge
        if tile not in tiles_to_remove and temp_grid[current_row][current_col] == tile:
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
            dx, dy = target_x - tile.x_position, target_y - tile.y_position

            # Move by MOVE_VELOCITY or the remaining distance, whichever is smaller
            move_x = min(abs(dx), MOVE_VELOCITY) * (1 if dx > 0 else -1)
            # If moving by MOVE_VELOCITY would overshoot, move exactly to the target
            if abs(move_x) > abs(dx):
                move_x = dx
            tile.x_position += move_x

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
        pygame.display.update()
        clock.tick(FPS)

    # --- After animation, update actual tile grid positions, values, and remove merged tiles ---
    new_tiles = {}

    for tile in tile_list:
        if tile not in tiles_to_remove:
            # Update the tile's actual grid row and col to the target
            tile.row, tile.col = tile.target_row, tile.target_col
            # Ensure pixel position is exactly at the center of the target cell
            tile.x_position, tile.y_position = tile.target_col * CELL_WIDTH, tile.target_row * CELL_HEIGHT
            # Update the tile's value to its final value AFTER animation
            tile.value = tile.final_value
            # Add to the new tiles dictionary using the final grid position as the key
            new_tiles[f"{tile.row}{tile.col}"] = tile

    tiles.clear()
    tiles.update(new_tiles)

    # Redraw one last time after the tiles dictionary is fully updated
    draw_elements(window, tiles)
    pygame.display.update()

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


def is_game_over(tiles):
    if len(tiles) < ROWS * COLS:
        return False
    for row in range(ROWS):
        for col in range(COLS):
            tile = tiles.get(f"{row}{col}")
            if tile:
                if col < COLS - 1:
                    right_tile = tiles.get(f"{row}{col + 1}")
                    if right_tile and right_tile.value == tile.value:
                        return False
                if row < ROWS - 1:
                    down_tile = tiles.get(f"{row + 1}{col}")
                    if down_tile and down_tile.value == tile.value:
                        return False
    return True


# --- Main Game Loop ---
def main(window):
    global GAME_STATE
    clock = pygame.time.Clock()
    game_running = True
    has_kept_playing = False
    tiles = generate_tiles()

    # --- FORCE WIN FOR TESTING ---
    # tiles["00"] = Tile(1024, 0, 0)
    # tiles["01"] = Tile(1024, 0, 1)

    # --- FORCE LOSE FOR TESTING ---
    # tiles.clear()
    # values = [
    #     [2, 4, 2, 4],
    #     [4, 2, 4, 2],
    #     [2, 4, 2, 4],
    #     [4, 2, 4, 2],
    # ]
    # for row in range(4):
    #     for col in range(4):
    #         tiles[f"{row}{col}"] = Tile(values[row][col], row, col)

    # Main loop
    while game_running:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False

            # Only process key presses if no animation is in progress
            if event.type == pygame.KEYDOWN and not IS_ANIMATING:
                # Handle arrow key presses for movement
                if GAME_STATE == "playing":
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
                            # Check for win before end_move
                            # Only show win screen if player hasn't chosen to keep playing
                            if not has_kept_playing and any(tile.value == 2048 for tile in tiles.values()):
                                GAME_STATE = "won"
                            else:
                                # Call end_move to add a new tile and check for loss
                                game_state_result = end_move(tiles)
                                if game_state_result == "lost":
                                    GAME_STATE = "lost"
                        else:
                            # If no move occurred check if the game is over (no possible moves)
                            if is_game_over(tiles):
                                GAME_STATE = "lost"
                elif GAME_STATE in ["won", "lost"]:
                    if event.key == pygame.K_SPACE:
                        # Restart the game
                        tiles = generate_tiles()
                        GAME_STATE = "playing"
                        has_kept_playing = False  # Reset when restarting
                    elif event.key == pygame.K_c and GAME_STATE == "won":
                        # Continue playing after winning
                        GAME_STATE = "playing"
                        has_kept_playing = True  # Set when continuing

        # Drawing (ensure the initial state is drawn and updates happen during animation)
        if not IS_ANIMATING:
            draw_elements(window, tiles)
            if GAME_STATE == "lost":  # Draw the lose overlay
                draw_game_over(window)
            elif GAME_STATE == "won":  # Draw the win overlay
                draw_game_won(window)
            pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(GAME_WINDOW)
