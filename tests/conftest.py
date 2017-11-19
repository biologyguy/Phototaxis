#!/usr/bin/env python3
# coding=utf-8
""" Fixtures for py.test  """
import pytest
import types
from collections import OrderedDict
import phototaxis


class HelperObjects(object):
    def __init__(self):
        pass

    @staticmethod
    def world():
        world_obj = types.SimpleNamespace()
        world_obj.grid = [[None for _ in range(4)] for _ in range(4)]
        world_obj.dish_surface = [(1, 1), (1, 2), (1, 3),
                                  (2, 1), (2, 2), (2, 3),
                                  (3, 1), (3, 2), (3, 3)]
        world_obj.dish_edges = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4),
                                (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)]
        world_obj.light_spots = [(1, 1), (1, 2)]
        world_obj.pop_size = 0
        world_obj.sum_food_eaten = 0
        world_obj.sum_suntan = 0
        return world_obj

    @staticmethod
    def genome():
        trans_mat = [(i, j / 15) for i, j in zip(phototaxis.STATES, range(1, 6))]
        trans_mat = OrderedDict([(i, OrderedDict(trans_mat)) for i in phototaxis.STATES])
        genome_obj = types.SimpleNamespace()
        genome_obj.p_dark = genome_obj.p_light = genome_obj.p_dark_wall = genome_obj.p_light_wall = trans_mat
        return genome_obj

    def worm(self):
        worm_obj = types.SimpleNamespace(world=self.world(), x=2, y=2, direction=0, state='left',
                                         genome=self.genome(), age=0, time_in_light=0)
        return worm_obj


@pytest.fixture(scope="session")
def ho():
    """
    Collection of helper methods
    """
    return HelperObjects()
