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
    def grid():
        grid_obj = types.SimpleNamespace()
        grid_obj.surface = [(1, 1), (1, 2), (1, 3),
                            (2, 1), (2, 2), (2, 3),
                            (3, 1), (3, 2), (3, 3)]
        grid_obj.edges = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4),
                          (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)]
        grid_obj.grid = [[None for _ in range(4)] for _ in range(4)]
        return grid_obj

    @staticmethod
    def genome():
        trans_mat = [(i, j / 15) for i, j in zip(phototaxis.STATES, range(1, 6))]
        trans_mat = OrderedDict([(i, OrderedDict(trans_mat)) for i in phototaxis.STATES])
        genome_obj = types.SimpleNamespace()
        genome_obj.p_dark = genome_obj.p_light = genome_obj.p_dark_wall = genome_obj.p_light_wall = trans_mat
        return genome_obj

    def worm(self):
        light = [(1, 1), (1, 2)]
        worm_obj = types.SimpleNamespace(grid=self.grid(), x=2, y=2, light=light, direction=0,
                                         state='left', genome=self.genome(), age=1, time_in_light=1,
                                         time_in_dark=1)
        return worm_obj


@pytest.fixture(scope="session")
def ho():
    """
    Collection of helper methods
    """
    return HelperObjects()
