import pygame
import random
import time


# absolute trash with grid_size > 10
debug_mode = False

# always a square. 100 takes a long time
grid_size = 25

# pick a tile set. "tileset1" or "tileset2"
tileset = "tileset1"

# weights for the random tile selection
weights = {
    "0": 100000,
    "1": 5000,
    "2": 5000,
    "3": 5000,
    "4": 5000,
    "5": 1,
    "6": 1,
    "7": 1,
    "8": 1,
    "9": 10000,
    "10": 10000,
}

# edge rules
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


# if True always choose a completely random tile
# rather than one with lowest entropy
more_random = False

# if the entropy is too high, collapse any random cell
# (if there are more than the set number of cells in
# the lowest entropy list)
super_random_threshold = 4

# sprinkle some random tiles
random_starting_cells = 1


# set the screen size and do some funky maths with it
# to get the sizes of other stuff
screen_size = 1000
cell_size = int(screen_size // grid_size)
width, height = cell_size * grid_size, cell_size * grid_size
cols, rows = grid_size, grid_size


# pygame setup
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("WFC")

# load the tileset
tiles = [
    pygame.image.load(f"./{tileset}/{i}.png").convert_alpha() for i in range(0, 11)
]

# lists to store the cells
cells = []
collapsed_cells = []
superposition_cells = []


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tile = "s"
        self.status = "s"

        # delete tiles from here to exclude them completely
        # may break the program if you delete too many
        self.possible_tiles = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    def update_possible_tiles(self, cells):
        """update the possible tiles for this cell"""
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
        """collapse the cell to a single tile"""
        self.status = "c"
        self.tile = random.choice(self.possible_tiles)
        self.possible_tiles = [self.tile]

    def __str__(self):
        return f"({self.x}, {self.y}) {self.tile}, {self.possible_tiles}"


def main():
    reset()
    running = True
    global finished
    global screenshot

    while running:
        running = check_events()

        window.fill(0)

        draw()

        # take a screenshot when finished
        # just the one though!
        if finished and not screenshot:
            screenshot = True
            pygame.image.save(window, f"./output/{int(time.time())}.png")

        draw_list_sizes()
        # draw_fps()

        if update_possibilities():
            if not collapse_cells():
                if more_random:
                    collapse_random_cell()
                else:
                    collapse_random_cell_with_lowest_entropy()

        if not finished:
            if len(superposition_cells) == 0:
                finished = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def update_possibilities():
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


def collapse_random_cell():
    global superposition_cells
    global collapsed_cells
    if len(superposition_cells) > 0:
        cell = random.choice(superposition_cells)
        cell.collapse()
        collapsed_cells.append(cell)
        superposition_cells.remove(cell)
        return True
    return False


def collapse_random_cell_with_lowest_entropy():
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
            if lowest_possibilities > super_random_threshold:
                return collapse_random_cell()
            cell = random.choice(temp)
            # pick a random number from the possible tiles, weighted towards lower numbers (hopefully)
            weights = get_weights(cell.possible_tiles)
            new_possible_tiles = random.choices(
                cell.possible_tiles, weights=weights, k=1
            )
            cell.possible_tiles = [new_possible_tiles[0]]
            cell.collapse()
            collapsed_cells.append(cell)
            superposition_cells.remove(cell)
            return True

    return False


def get_weights(possible_tiles):
    result = []
    for i in possible_tiles:
        result.append(weights[i])
    return result


def draw():
    """Draws the board"""
    for row in cells:
        for cell in row:
            if cell.tile == "s":
                pygame.draw.rect(
                    window,
                    (100, 100, 100, 0.1),
                    (
                        cell.x * cell_size,
                        cell.y * cell_size + 1,
                        (cell_size - 1),
                        (cell_size - 1),
                    ),
                    1,
                )
            else:
                window.blit(
                    pygame.transform.scale(
                        tiles[int(cell.tile)], (cell_size, cell_size)
                    ),
                    (cell.x * cell_size, cell.y * cell_size),
                )

    if debug_mode:
        # draw the grid
        # for x in range(0, width, cell_size):
        #     pygame.draw.line(window, (255, 255, 255), (x - 1, 0), (x, height), width=1)
        # for y in range(0, height, cell_size):
        #     pygame.draw.line(window, (255, 255, 255), (-1, y), (width, y), width=1)

        # write len(cell.possible_tiles) in each cell
        for cell in superposition_cells:
            font = pygame.font.SysFont("Arial", 18)
            text = font.render(f"{len(cell.possible_tiles)}", True, (255, 255, 255))
            window.blit(
                text,
                (
                    cell.x * cell_size + cell_size // 2 - text.get_width() // 2,
                    cell.y * cell_size + cell_size // 2 - text.get_height() // 2,
                ),
            )

        # draw boxes around superposition cells
        # for cell in superposition_cells:
        #     pygame.draw.rect(
        #         window,
        #         (255, 0, 0),
        #         (
        #             cell.x * cell_size,
        #             cell.y * cell_size + 1,
        #             (cell_size - 1),
        #             (cell_size - 1),
        #         ),
        #         1,
        #     )


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
    for _ in range(random_starting_cells):
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
    font = pygame.font.SysFont("Arial", 12)
    text = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
    window.blit(text, (5, height - 20))


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
