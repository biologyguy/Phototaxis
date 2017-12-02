import pygame
import numpy as np
from pygame.locals import *
from random import Random
from collections import OrderedDict
from scipy.stats import poisson
from buddysuite import buddy_resources as br

rand = Random()
STATES = ["fwd", "rev", "left", "right", "stop"]
type_colors = {0: (0, 0, 0), 1: (255, 255, 255), 2: (0, 128, 255), 3: (255, 100, 0), 4: (152, 251, 152)}


def weighted_choice(items, weights, number=1, replacement=False, return_index=False):
    if not replacement and number > len(items):
        raise ValueError("Too many choices requested without replacement "
                         "(%s items and %s requested)" % (len(items), number))
    if len(items) != len(weights):
        raise ValueError("The `items` and `weights` parameters are different sizes")

    results = []
    sum_weights = sum(weights)
    std_weights = [x / sum_weights for x in weights]
    for i in range(number):
        choice = rand.random()
        tally = 0
        for indx, weight in enumerate(std_weights):
            tally += weight
            if tally >= choice:
                if return_index:
                    results.append(indx)
                else:
                    results.append(items[indx])
                if not replacement:
                    std_weights[indx] = 0
                    sum_weights = sum(std_weights)
                    std_weights = [x / sum_weights for x in std_weights]
                break
    return results


def flood_fill(x_ori, y_ori, edges):
    """
    Simple implementation of the 'flood fill' algorithm, to change the value of 'cells' in an array if they are
    inside a closed space.
    Note that this implementation forms infinite loop if surrounding structure is not closed
    :param x_ori:
    :param y_ori:
    :param edges: Starting enclosure
    :return:
    """
    surface = edges
    stack = [(x_ori, y_ori)]
    while len(stack) > 0:
        x, y = stack.pop()
        if (x, y) in surface:
            continue
        surface.append((x, y))
        stack.append((x + 1, y))  # right
        stack.append((x - 1, y))  # left
        stack.append((x, y + 1))  # down
        stack.append((x, y - 1))  # up
    return surface


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


class World(object):
    def __init__(self, len_side, pixel_size):
        """
        Create a square grid surface, with a circular 'plate' in its center
        :param len_side: The length of a side as passed into PyGame
        :param pixel_size: How many side units are contained in a single 'pixel' in the actual grid

        Grid space type values:
        0 = Edge (out of bounds) = black
        1 = Open space, no light = white
        2 = Open space, light    = blue
        3 = Occupied             = orange
        4 = Food                 = light green
        """

        # Initiate the environment
        pix_per_side = int(len_side / pixel_size)
        self.grid = [[None for _ in range(pix_per_side)] for _ in range(pix_per_side)]
        self.dish_edges = {tup: None for tup in define_circle_edges(len_side, pixel_size)}
        self.dish_surface = {tup: None for tup in define_circle_edges(len_side, pixel_size, fill=True)}
        for edge in self.dish_edges:
            del self.dish_surface[edge]
        self.light_spots = {}
        self.food_locations = {}

        # Set a few global variables
        self.pop_size = 0
        self.sum_food_eaten = 0
        self.sum_suntan = 0

    def scatter_food(self, num_dropped):
        for food in rand.choices(list(self.dish_surface.keys()), k=num_dropped):
            self.food_locations[food] = None
        return


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
    def __init__(self, world, genome):
        """
        Create a virtual worm object
        :param world: World object
        :param genome: Genome object

        Directions:
        0 = Up
        1 = Right
        2 = Down
        3 = Left
        """
        self.world = world
        self.x, self.y = rand.choice(list(self.world.dish_surface.keys()))
        self.direction = rand.choice([0, 1, 2, 3])
        self.state = rand.choice(STATES)
        self.genome = genome
        self.age = 0
        self.food = 0
        self.time_in_light = 1
        self.world.sum_suntan += 1
        self.world.pop_size += 1

    def step(self, *args):
        """
        Do a full step in the simulation
        :param args:
        :return:
        """
        if args:
            pass
        if (self.x, self.y) in self.world.light_spots:
            self.time_in_light += 1
            self.world.sum_suntan += 1
        else:
            if self.time_in_light > 1:
                self.time_in_light -= 1
                self.world.sum_suntan -= 1
        if (self.x, self.y) in self.world.food_locations:
            self.food += 10
            self.world.sum_food_eaten += 10
            del self.world.food_locations[(self.x, self.y)]

        self.age += 1
        if self.food > 0:
            self.food -= 1
            self.world.sum_food_eaten -= 1
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
            if (self.x, self.y) in self.world.light_spots:
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
                self.world.grid[self.x][self.y] = 3
                break

    def move_forward(self, *args):
        if args:
            pass

        wall = False
        if self.direction == 0:
            if (self.x, self.y - 1) in self.world.dish_edges:
                wall = True
            else:
                self.y -= 1
        elif self.direction == 1:
            if (self.x + 1, self.y) in self.world.dish_edges:
                wall = True
            else:
                self.x += 1
        elif self.direction == 2:
            if (self.x, self.y + 1) in self.world.dish_edges:
                wall = True
            else:
                self.y += 1
        elif self.direction == 3:
            if (self.x - 1, self.y) in self.world.dish_edges:
                wall = True
            else:
                self.x -= 1
        return wall

    def move_backward(self, *args):
        if args:
            pass

        wall = False
        if self.direction == 0:
            if (self.x, self.y + 1) in self.world.dish_edges:
                wall = True
            else:
                self.y += 1
        elif self.direction == 1:
            if (self.x - 1, self.y) in self.world.dish_edges:
                wall = True
            else:
                self.x -= 1
        elif self.direction == 2:
            if (self.x, self.y - 1) in self.world.dish_edges:
                wall = True
            else:
                self.y -= 1
        elif self.direction == 3:
            if (self.x + 1, self.y) in self.world.dish_edges:
                wall = True
            else:
                self.x += 1
        return wall

    def breed(self, mate, *args):
        if args:
            pass

        p_dark = OrderedDict()
        for i in STATES:
            p_dark[i] = OrderedDict()
            for j in STATES:
                p_dark[i][j] = rand.choice([self.genome.p_dark[i][j], mate.genome.p_dark[i][j]])

        p_light = OrderedDict()
        for i in STATES:
            p_light[i] = OrderedDict()
            for j in STATES:
                p_light[i][j] = rand.choice([self.genome.p_light[i][j], mate.genome.p_light[i][j]])

        p_dark_wall = OrderedDict()
        for i in STATES:
            p_dark_wall[i] = OrderedDict()
            for j in STATES:
                p_dark_wall[i][j] = rand.choice([self.genome.p_dark_wall[i][j], mate.genome.p_dark_wall[i][j]])

        p_light_wall = OrderedDict()
        for i in STATES:
            p_light_wall[i] = OrderedDict()
            for j in STATES:
                p_light_wall[i][j] = rand.choice([self.genome.p_light_wall[i][j], mate.genome.p_light_wall[i][j]])

        new_genome = Genome(p_dark, p_light, p_dark_wall, p_light_wall)
        worm = Worm(self.world, new_genome)
        # Place the offspring in an adjacent (or the same) space
        worm.x, worm.y = rand.choice(self.adjacent_spaces())
        self.world.grid[worm.x][worm.y] = 3
        return worm

    def adjacent_spaces(self, *args):
        if args:
            pass
        spaces = [(self.x - 1, self.y - 1), (self.x - 1, self.y), (self.x - 1, self.y + 1),
                  (self.x, self.y - 1),     (self.x, self.y),     (self.x, self.y + 1),
                  (self.x + 1, self.y - 1), (self.x + 1, self.y), (self.x + 1, self.y + 1)]
        spaces = [space for space in spaces if space in self.world.dish_surface]
        return spaces


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
        if event.type == QUIT or (event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q])):
            print("\n")
            pygame.quit()
            quit()


def draw_pixel(x, y, type_val, scale=10):
    pygame.draw.rect(game_display, type_colors[type_val], pygame.Rect(x * scale, y * scale, scale, scale))
    return


def main(len_side, pixel_size, starting_pop_size):
    if len_side % pixel_size:
        raise ValueError("len_side is not divisible by pixel_size")
    pix_per_side = int(len_side / pixel_size)
    world = World(len_side, pixel_size)
    world.light_spots = {tup: None for tup in define_circle_edges(10, 1, 20, 20, fill=True)}
    world.light_spots = {}
    worms = [Worm(world, Genome()) for _ in range(starting_pop_size)]
    printer = br.DynamicPrint()
    print("Pop size    Sum eaten    Sum suntan    Num food spots")
    while True:
        event_handler()
        world.scatter_food(10)
        for i in range(pix_per_side):
            for j in range(pix_per_side):
                i *= pixel_size
                j *= pixel_size
                if (i, j) in world.dish_edges:
                    world.grid[i][j] = 0
                elif (i, j) in world.light_spots:
                    world.grid[i][j] = 2
                elif (i, j) in world.food_locations:
                    world.grid[i][j] = 4
                else:
                    world.grid[i][j] = 1
        # Sorting. Younger worms have greater initiative
        worms = sorted(worms, key=lambda x: x.age)

        # Movement
        for worm in worms:
            worm.step()

        # Breeding
        offspring = []
        for worm in worms:
            prob_breed = worm.time_in_light / world.sum_suntan
            breed_check = rand.random()
            if prob_breed > breed_check:
                mates = [mate for mate in worms if (mate.x, mate.y) == (worm.x, worm.y)]
                if mates:
                    mate = rand.choice(mates)
                    offspring.append(worm.breed(mate))
        worms += offspring

        # Killing: Each cycle, set the max population size by drawing from a poisson distribution with mu = 1000
        max_pop_size = poisson.rvs(starting_pop_size)
        number_deaths = world.pop_size - max_pop_size if max_pop_size < world.pop_size else 0

        # More food and younger age gives an advantage, so find relative amount of food eaten and subtract it from 1
        if world.sum_food_eaten:
            weights = [(worm, 1 - ((worm.food - (worm.age / 10)) / world.sum_food_eaten)) for worm in worms]
        else:
            weights = [(worm, 1) for worm in worms]
        death_row = weighted_choice([i[0] for i in weights], [i[1] for i in weights], number=number_deaths,
                                    return_index=True)
        for indx in sorted(death_row, reverse=True):
            world.sum_food_eaten -= worms[indx].food
            world.sum_suntan -= worms[indx].time_in_light
            del worms[indx]
        world.pop_size -= len(death_row)

        # Draw world
        for indx_i, i in enumerate(world.grid):
            for indx_j, j in enumerate(i):
                draw_pixel(indx_i, indx_j, j)

        output = "{:<12}{:<13}{:<14}{:<17}".format(world.pop_size, world.sum_food_eaten,
                                                   world.sum_suntan, len(world.food_locations))
        printer.write(output)
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()

    display_width = 1000
    display_height = 1000

    game_display = pygame.display.set_mode((display_width, display_height))
    game_display.fill((255, 255, 255))
    pygame.display.set_caption('Phototaxis Simulation')

    main(len_side=100, pixel_size=1, starting_pop_size=1000)
