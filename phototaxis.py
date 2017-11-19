import pygame
from pygame.locals import *
from random import Random
from collections import OrderedDict

rand = Random()
STATES = ["fwd", "rev", "left", "right", "stop"]
type_colors = {0: (0, 0, 0), 1: (255, 255, 255), 2: (0, 128, 255), 3: (255, 100, 0)}


def flood_fill(x_ori, y_ori, edges):
    """
    Simple implementation of the 'flood fill' algorithm, to change the value of 'cells' in an array if they are
    inside a closed space.
    Note that this implementation forms infinite loop if surrounding structure is not closed
    :param x_ori:
    :param y_ori:
    :param edges:
    :return:
    """
    stack = [(x_ori, y_ori)]
    while len(stack) > 0:
        x, y = stack.pop()
        if (x, y) in edges:
            continue
        edges.append((x, y))
        stack.append((x + 1, y))  # right
        stack.append((x - 1, y))  # left
        stack.append((x, y + 1))  # down
        stack.append((x, y - 1))  # up


def define_circle_edges(len_side, pixel_size, x0=0, y0=0, fill=False):
    """
    Create an enclosed circle
    :param len_side: The length of a single side of the square display box
    :param pixel_size:
    :param x0: X offset
    :param y0: Y offset
    :param fill: include all encompassed pixels
    :return:
    """
    len_side = int(len_side / pixel_size) - 1
    radius = len_side / 2
    f = 1 - radius
    ddf_x = 1
    ddf_y = -2 * radius
    x = 0
    y = radius
    edges = [(radius, radius * 2), (radius, 0), (radius * 2, radius), (0, radius)]

    while x < y:
        if f >= 0:
            y -= 1
            ddf_y += 2
            f += ddf_y
        x += 1
        ddf_x += 2
        f += ddf_x
        edges.append((radius + x, radius + y))
        edges.append((radius - x, radius + y))
        edges.append((radius + x, radius - y))
        edges.append((radius - x, radius - y))
        edges.append((radius + y, radius + x))
        edges.append((radius - y, radius + x))
        edges.append((radius + y, radius - x))
        edges.append((radius - y, radius - x))

    edges = [(int(x + x0) * pixel_size, int(y + y0) * pixel_size) for x, y in edges]
    if fill:
        flood_fill(int(radius + x0), int(radius + y0), edges)
    edges = list(set(edges))
    return edges


class Grid(object):
    def __init__(self, len_side, pixel_size):
        """
        Create a square grid surface, with a circular 'plate' in its center
        :param len_side: The length of a side as passed into PyGame
        :param pixel_size: How many side units are contained in a single 'pixel' in the actual grid
        """
        pix_per_side = int(len_side / pixel_size)
        self.grid = [[None for _ in range(pix_per_side)] for _ in range(pix_per_side)]
        self.edges = define_circle_edges(len_side, pixel_size)
        self.surface = define_circle_edges(len_side, pixel_size, fill=True)
        for edge in self.edges:
            del self.surface[self.surface.index(edge)]


class Genome(object):
    def __init__(self, p_dark=None, p_light=None, p_dark_wall=None, p_light_wall=None):
        """
        A place to store all of the movement transition matrices
        :param p_dark: Actions in the dark
        :param p_light: Actions in the light
        :param p_dark_wall: Actions after hitting a wall in the light
        :param p_light_wall: Actions after hitting a wall in the dark
        """
        self.p_dark = p_dark if p_dark else random_transition_matrix(STATES)
        self.p_light = p_light if p_light else random_transition_matrix(STATES)
        self.p_dark_wall = p_dark_wall if p_dark_wall else random_transition_matrix(STATES)
        self.p_light_wall = p_light_wall if p_light_wall else random_transition_matrix(STATES)


class Worm(object):
    def __init__(self, grid, light, genome):
        """
        Create a virtual worm object
        :param grid: Grid object
        :param light: List of coords that are marked as 'illuminated' by light
        :param genome: Genome object
        """
        self.grid = grid
        self.x, self.y = rand.choice(self.grid.surface)
        self.light = light
        self.direction = rand.choice([0, 1, 2, 3])
        self.state = rand.choice(STATES)
        self.genome = genome
        self.age = 1
        self.time_in_light = 1
        self.time_in_dark = 1

    def step(self, *args):
        """
        Do a full step in the simulation
        :param args:
        :return:
        """
        if args:
            pass
        if (self.x, self.y) in self.light:
            self.time_in_light += 1
        else:
            self.time_in_dark += 1
        self.age += 1
        self.move()
        return

    def move(self, *args):
        """
        Execute an action from the appropriate movement transition matrix
        :param args: Not currently used for anything
        :return:
        """
        if args:
            pass

        wall = False
        for i in range(2):  # This allows a wall to be bumped into and responded to, but if they bump again, too bad.
            action = rand.random()
            sum_options = 0
            if (self.x, self.y) in self.light:
                prob_set = self.genome.p_light if not wall else self.genome.p_light_wall
            else:
                prob_set = self.genome.p_dark if not wall else self.genome.p_dark_wall
            direction = None
            for direction, prob in prob_set[self.state].items():
                sum_options += prob
                if sum_options >= action:
                    break

            if direction == "fwd":
                wall = self.move_forward()
            elif direction == "rev":
                wall = self.move_backward()
            elif direction == "left":
                self.direction = self.direction - 1 if self.direction > 0 else 3
            elif direction == "right":
                self.direction = self.direction + 1 if self.direction < 3 else 0
            elif direction == "stop":
                pass  # Do nothing

            if not wall or i == 1:
                self.state = direction
                self.grid.grid[self.x][self.y] = 3
                break

    def move_forward(self, *args):
        if args:
            pass

        wall = False
        if self.direction == 0:
            if (self.x, self.y - 1) in self.grid.edges:
                wall = True
            else:
                self.y -= 1
        elif self.direction == 1:
            if (self.x + 1, self.y) in self.grid.edges:
                wall = True
            else:
                self.x += 1
        elif self.direction == 2:
            if (self.x, self.y + 1) in self.grid.edges:
                wall = True
            else:
                self.y += 1
        elif self.direction == 3:
            if (self.x - 1, self.y) in self.grid.edges:
                wall = True
            else:
                self.x -= 1
        return wall

    def move_backward(self, *args):
        if args:
            pass

        wall = False
        if self.direction == 0:
            if (self.x, self.y + 1) in self.grid.edges:
                wall = True
            else:
                self.y += 1
        elif self.direction == 1:
            if (self.x - 1, self.y) in self.grid.edges:
                wall = True
            else:
                self.x -= 1
        elif self.direction == 2:
            if (self.x, self.y - 1) in self.grid.edges:
                wall = True
            else:
                self.y -= 1
        elif self.direction == 3:
            if (self.x + 1, self.y) in self.grid.edges:
                wall = True
            else:
                self.x += 1
        return wall


def random_transition_matrix(keys):
    """
    Create a square OrderedDict of OrderedDicts, setting the values in each matrix position randomly and converting
    into a stochastic/Markov matrix
    :param keys: The row/column headings
    :return:
    """
    output = OrderedDict()
    for i in keys:
        output[i] = OrderedDict()
        sum_i = 0
        for j in keys:
            rand_int = rand.randint(1, 100)
            sum_i += rand_int
            output[i][j] = rand_int
        for j in keys:
            output[i][j] /= sum_i
    return output


def event_handler():
    # This is the primary listener logic, it catches all types of input
    for event in pygame.event.get():
        print(event)
        if event.type == QUIT or (event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q])):
            pygame.quit()
            quit()


def draw_pixel(x, y, type_val, scale=10):
    pygame.draw.rect(game_display, type_colors[type_val], pygame.Rect(x * scale, y * scale, scale, scale))
    return


"""
Values:
0 = Edge (out of bounds) = black
1 = Open space, no light = white
2 = Open space, light    = blue
3 = Occupied             = orange

Directions:
0 = Up
1 = Right
2 = Down
3 = Left
"""


def main(len_side, pixel_size):
    if len_side % pixel_size:
        raise ValueError("len_side is not divisible by pixel_size")
    pix_per_side = int(len_side / pixel_size)
    grid = Grid(len_side, pixel_size)
    light = define_circle_edges(10, 1, 20, 20, fill=True)
    worms = [Worm(grid, light, Genome()) for _ in range(1000)]
    while True:
        event_handler()
        for i in range(pix_per_side):
            for j in range(pix_per_side):
                if (i * pixel_size, j * pixel_size) in grid.edges:
                    grid.grid[i][j] = 0
                elif (i * pixel_size, j * pixel_size) in light:
                    grid.grid[i][j] = 2
                else:
                    grid.grid[i][j] = 1
        for worm in worms:
            worm.step()
        for indx_i, i in enumerate(grid.grid):
            for indx_j, j in enumerate(i):
                draw_pixel(indx_i, indx_j, j)
        # print(max([worm.time_in_light for worm in worms]))
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()

    display_width = 1000
    display_height = 1000

    game_display = pygame.display.set_mode((display_width, display_height))
    game_display.fill((255, 255, 255))
    pygame.display.set_caption('Phototaxis Simulation')

    main(100, 1)
