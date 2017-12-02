#!/usr/bin/env python3
# coding=utf-8
""" Fixtures for py.test  """
import pytest
import types
from collections import OrderedDict
from copy import copy
import phototaxis


class HelperObjects(object):
    def __init__(self):
        pass

    @staticmethod
    def world():
        world_obj = types.SimpleNamespace()
        world_obj.grid = [[None for _ in range(4)] for _ in range(4)]
        world_obj.dish_edges = {(0, 1): None, (0, 2): None, (0, 3): None, (1, 0): None,
                                (1, 4): None, (2, 0): None, (2, 4): None, (3, 0): None,
                                (3, 4): None, (4, 1): None, (4, 2): None, (4, 3): None}
        world_obj.dish_surface = {(1, 1): None, (1, 2): None, (1, 3): None,
                                  (2, 1): None, (2, 2): None, (2, 3): None,
                                  (3, 1): None, (3, 2): None, (3, 3): None}

        world_obj.light_spots = {(1, 1): None, (1, 2): None}
        world_obj.food_locations = {(2, 2): None, (3, 2): None}
        world_obj.pop_size = 0
        world_obj.sum_food_eaten = 0
        world_obj.sum_suntan = 0
        return world_obj

    @staticmethod
    def genome():
        trans_mat = [(i, j / 15) for i, j in zip(phototaxis.STATES, range(1, 6))]
        trans_mat = OrderedDict([(i, OrderedDict(trans_mat)) for i in phototaxis.STATES])
        genome_obj = types.SimpleNamespace()
        genome_obj.p_dark = copy(trans_mat)
        genome_obj.p_light = copy(trans_mat)
        genome_obj.p_dark_wall = copy(trans_mat)
        genome_obj.p_light_wall = copy(trans_mat)
        return genome_obj

    def worm(self):
        worm_obj = types.SimpleNamespace(world=self.world(), x=2, y=2, direction=0, state='left',
                                         genome=self.genome(), age=0, food=0, time_in_light=1)
        worm_obj.world.sum_suntan += 1
        worm_obj.world.pop_size += 1
        return worm_obj


@pytest.fixture(scope="session")
def ho():
    """
    Collection of helper methods
    """
    return HelperObjects()
