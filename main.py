import pygame
import random
import time

debug_mode = False
grid_size = 50
screen_size = 1000
cell_size = int(screen_size // grid_size)
width, height = cell_size * grid_size, cell_size * grid_size
cols, rows = grid_size, grid_size

weights = { # weights for the random tile selection
    "0": 0,
    "1": 2,
    "2": 2,
    "3": 2,
    "4": 2,
    "5": 1,
    "6": 1,
    "7": 1,
    "8": 1,
    "9": 10,
    "10": 10,
}

rules = {
    "up": {
        "0": ["0", "1", "2", "5", "6", "7", "10"],
        "1": ["3", "4", "8", "9"],
        "2": ["3", "4", "8", "9"],
        "3": ["0", "1", "2", "5", "6", "7", "10"],
        "4": ["0", "1", "2", "5", "6", "7", "10"],
        "5": ["0", "1", "2", "5", "6", "7", "10"],
        "6": ["3", "4", "8", "9"],
        "7": ["0", "1", "2", "5", "6", "7", "10"],
        "8": ["0", "1", "2", "5", "6", "7", "10"],
        "9": ["3", "4", "8", "9"],
        "10": ["0", "1", "2", "5", "6", "7", "10"],
    },
    "right": {
        "0": ["0", "2", "3", "6", "7", "8", "9"],
        "1": ["0", "2", "3", "6", "7", "8", "9"],
        "2": ["1", "4", "5", "10"],
        "3": ["1", "4", "5", "10"],
        "4": ["0", "2", "3", "6", "7", "8", "9"],
        "5": ["0", "2", "3", "6", "7", "8", "9"],
        "6": ["0", "2", "3", "6", "7", "8", "9"],
        "7": ["1", "4", "5", "10"],
        "8": ["0", "2", "3", "6", "7", "8", "9"],
        "9": ["0", "2", "3", "6", "7", "8", "9"],
        "10": ["1", "4", "5", "10"],
    },
    "down": {
        "0": ["0", "3", "4", "5", "7", "8", "10"],
        "1": ["0", "3", "4", "5", "7", "8", "10"],
        "2": ["0", "3", "4", "5", "7", "8", "10"],
        "3": ["1", "2", "6", "9"],
        "4": ["1", "2", "6", "9"],
        "5": ["0", "3", "4", "5", "7", "8", "10"],
        "6": ["0", "3", "4", "5", "7", "8", "10"],
        "7": ["0", "3", "4", "5", "7", "8", "10"],
        "8": ["1", "2", "6", "9"],
        "9": ["1", "2", "6", "9"],
        "10": ["0", "3", "4", "5", "7", "8", "10"],
    },
    "left": {
        "0": ["0", "1", "4", "5", "6", "8", "9"],
        "1": ["2", "3", "7", "10"],
        "2": ["0", "1", "4", "5", "6", "8", "9"],
        "3": ["0", "1", "4", "5", "6", "8", "9"],
        "4": ["2", "3", "7", "10"],
        "5": ["2", "3", "7", "10"],
        "6": ["0", "1", "4", "5", "6", "8", "9"],
        "7": ["0", "1", "4", "5", "6", "8", "9"],
        "8": ["0", "1", "4", "5", "6", "8", "9"],
        "9": ["0", "1", "4", "5", "6", "8", "9"],
        "10": ["2", "3", "7", "10"],
    },
}


pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("WFC")
tiles = [pygame.image.load(f"./tiles/{i}.png").convert_alpha() for i in range(0, 11)]

cells = []
collapsed_cells = []
superposition_cells = []


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tile = "0"
        self.possible_tiles = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.status = "s"  # Superposition, Collapsed

    def update_possible_tiles(self, cells):
        is_updated = False
        if len(self.possible_tiles) > 1:
            if self.x > 0:
                if cells[self.y][self.x - 1].status == "c":
                    for tile in self.possible_tiles:
                        if tile not in rules["left"][cells[self.y][self.x - 1].tile]:
                            self.possible_tiles.remove(tile)
                            is_updated = True
            if self.x < grid_size - 1:
                if cells[self.y][self.x + 1].status == "c":
                    for tile in self.possible_tiles:
                        if tile not in rules["right"][cells[self.y][self.x + 1].tile]:
                            self.possible_tiles.remove(tile)
                            is_updated = True
            if self.y > 0:
                if cells[self.y - 1][self.x].status == "c":
                    for tile in self.possible_tiles:
                        if tile not in rules["up"][cells[self.y - 1][self.x].tile]:
                            self.possible_tiles.remove(tile)
                            is_updated = True
            if self.y < grid_size - 1:
                if cells[self.y + 1][self.x].status == "c":
                    for tile in self.possible_tiles:
                        if tile not in rules["down"][cells[self.y + 1][self.x].tile]:
                            self.possible_tiles.remove(tile)
                            is_updated = True

        return is_updated

    def collapse(self):
        self.status = "c"
        self.tile = random.choice(self.possible_tiles)
        self.possible_tiles = [self.tile]

    def __str__(self):
        return f"({self.x}, {self.y}) {self.tile}, {self.possible_tiles}"


def main():
    reset()
    counter = 0
    running = True
    global finished
    global cells
    global collapsed_cells
    global superposition_cells
    global screenshot

    while running:
        running = check_events()

        window.fill(0)

        # drawing all the things
        draw()

        if finished and not screenshot:
            screenshot = True
            pygame.image.save(window, f"./output/{int(time.time())}.png")

        draw_list_sizes()
        # draw_fps()
        # if not finished:
        #     counter = draw_counter(counter)
        # else:
        #     draw_counter(counter)

        if update_possibilities():
            if not collapse_cells():
                collapse_random_cell_with_lowest_possibilities()

        if not finished:
            if len(superposition_cells) == 0:
                finished = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def update_possibilities():
    global cells
    global finished
    global superposition_cells
    changes = 1
    while changes > 0:
        changes = 0
        for cell in superposition_cells:
            if cell.update_possible_tiles(cells):
                changes += 1
            if len(cell.possible_tiles) == 0:
                print("cell with no possibilities found")
                reset()
                return False
    return True


def collapse_cells():
    global superposition_cells
    global collapsed_cells
    collapse = False
    for cell in superposition_cells:
        if len(cell.possible_tiles) == 1:
            collapse = True
            cell.collapse()
            collapsed_cells.append(cell)
            superposition_cells.remove(cell)
    return collapse


def collapse_random_cell_with_lowest_possibilities():
    global superposition_cells
    global collapsed_cells
    lowest_possibilities = 11
    if len(superposition_cells) > 0:
        for cell in superposition_cells:
            if len(cell.possible_tiles) < lowest_possibilities:
                lowest_possibilities = len(cell.possible_tiles)
        temp = []
        for cell in superposition_cells:
            if len(cell.possible_tiles) == lowest_possibilities:
                temp.append(cell)
        if len(temp) > 0:
            cell = random.choice(temp)
            # pick a random number from the possible tiles, weighted towards lower numbers (hopefully)
            weights = get_weights(cell.possible_tiles)
            new_possible_tiles = random.choices(
                cell.possible_tiles, cum_weights=weights, k=1
            )
            cell.possible_tiles = [new_possible_tiles[0]]
            cell.collapse()
            collapsed_cells.append(cell)
            superposition_cells.remove(cell)
            return True

    return False


def get_weights(possible_tiles):
    global weights
    result = []
    for i in possible_tiles:
        result.append(weights[i])
    return result


def draw():
    """Draws the board"""
    global cells
    global superposition_cells
    for row in cells:
        for cell in row:
            window.blit(
                pygame.transform.scale(tiles[int(cell.tile)], (cell_size, cell_size)),
                (cell.x * cell_size, cell.y * cell_size),
            )

    if debug_mode:
        # draw the grid
        for x in range(0, width, cell_size):
            pygame.draw.line(window, (255, 255, 255), (x - 1, 0), (x, height), width=1)
        for y in range(0, height, cell_size):
            pygame.draw.line(window, (255, 255, 255), (-1, y), (width, y), width=1)
        # write cell.possible_tiles in each cell
        for row in cells:
            for cell in row:
                font = pygame.font.SysFont("Arial", 8)
                text = font.render(f"{cell.possible_tiles}", True, (255, 255, 255))
                window.blit(
                    text,
                    (
                        cell.x * cell_size + cell_size // 2 - text.get_width() // 2,
                        cell.y * cell_size + cell_size // 2 - text.get_height() // 2,
                    ),
                )


def reset():
    """Resets the board"""
    print("Resetting...")
    global screenshot
    global cells
    global finished
    global collapsed_cells
    global superposition_cells
    finished = False
    screenshot = False
    cells = [[Cell(x, y) for x in range(cols)] for y in range(rows)]
    collapsed_cells = []
    superposition_cells = []
    for row in cells:
        for cell in row:
            superposition_cells.append(cell)
    # pick a starting cell
    start_cell = cells[random.randint(0, grid_size - 1)][
        random.randint(0, grid_size - 1)
    ]
    start_cell.status = "c"
    collapsed_cells.append(start_cell)
    superposition_cells.remove(start_cell)
    start_cell.tile = random.choice(start_cell.possible_tiles)
    start_cell.possible_tiles = [start_cell.tile]
    print(f"Starting with cell {start_cell}")


def draw_list_sizes():
    """Draws the size of the lists on the screen"""
    collapsed_count = len(collapsed_cells)
    superposition_count = len(superposition_cells)
    cells_count = len(cells) * len(cells[0])
    font = pygame.font.SysFont("Arial", 12)
    text = font.render(
        f"Collapsed: {collapsed_count}, Superposition: {superposition_count}, Cells: {cells_count}",
        True,
        (255, 255, 255),
    )
    window.blit(text, (5, 5))


def draw_fps():
    """Draws the fps on the screen"""
    global clock
    font = pygame.font.SysFont("Arial", 12)
    text = font.render(str(int(clock.get_fps())), True, (0, 0, 0))
    window.blit(text, (5, height - 20))


def draw_counter(counter):
    """Draws the tick counter on the screen"""
    font = pygame.font.SysFont("Arial", 12)
    text = font.render(str(counter), True, (0))
    window.blit(text, (5, height - 20))
    counter += 1
    return counter


def check_events():
    """Checks for events"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("X button clicked")
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("escape key pressed")
                return False
            if event.key == pygame.K_SPACE:
                reset()
    return True


if __name__ == "__main__":
    main()
