import pytest
import phototaxis
from random import Random
from collections import OrderedDict


# ####################### Mock Resources ####################### #
def mock_define_circle_edges(*args, **kwargs):
    print(args)
    if "fill" in kwargs:
        return [(0, 1), (0, 2), (0, 3),
                (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                (4, 1), (4, 2), (4, 3)]
    else:
        return [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0),
                (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)]
# ############################################################## #


def test_weighted_choice(monkeypatch, capsys):
    items = ["a", "b", "c"]
    weights = [1, 2, 3]
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.15)
    assert phototaxis.weighted_choice(items, weights) == ["a"]

    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.5)
    assert phototaxis.weighted_choice(items, weights) == ["b"]

    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.500001)
    assert phototaxis.weighted_choice(items, weights) == ["c"]

    rand = Random(1)
    monkeypatch.setattr(phototaxis, "rand", rand)
    assert phototaxis.weighted_choice(items, weights, 2) == ["a", "c"]
    assert phototaxis.weighted_choice(items, weights, 10, True) == ['c', 'b', 'b', 'b', 'c', 'c', 'a', 'a', 'c', 'b']
    assert phototaxis.weighted_choice(items, weights, 10, True, True) == [2, 0, 1, 2, 1, 2, 2, 0, 0, 2]

    with pytest.raises(ValueError) as err:
        phototaxis.weighted_choice(items, weights, 10)
    assert "Too many choices requested without replacement" in str(err)

    with pytest.raises(ValueError) as err:
        phototaxis.weighted_choice(items + items, weights)
    assert "The `items` and `weights` parameters are different sizes" in str(err)


def test_flood_fill():
    edges = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4),
             (4, 0), (4, 1), (4, 2), (4, 3), (4, 5)]
    filled_surface = phototaxis.flood_fill(1, 3, edges)
    assert sorted(filled_surface) == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                                      (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                                      (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                                      (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                                      (4, 0), (4, 1), (4, 2), (4, 3), (4, 5)]


def test_define_circle_edges():
    edges = phototaxis.define_circle_edges(5, 1)
    assert sorted(edges) == [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0),
                             (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)]

    expected = [(x+2, y+3) for x, y in sorted(edges)]
    edges = phototaxis.define_circle_edges(5, 1, x0=2, y0=3)
    assert sorted(edges) == expected

    edges = phototaxis.define_circle_edges(5, 1, fill=True)
    assert sorted(edges) == [(0, 1), (0, 2), (0, 3),
                             (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                             (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
                             (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
                             (4, 1), (4, 2), (4, 3)]


def test_world_init(monkeypatch):
    monkeypatch.setattr(phototaxis, "define_circle_edges", mock_define_circle_edges)
    world = phototaxis.World(2, 1)
    assert world.grid == [[None, None], [None, None]]

    assert world.dish_edges == {(0, 1): None, (0, 2): None, (0, 3): None, (1, 0): None,
                                (1, 4): None, (2, 0): None, (2, 4): None, (3, 0): None,
                                (3, 4): None, (4, 1): None, (4, 2): None, (4, 3): None}
    assert world.dish_surface == {(1, 1): None, (1, 2): None, (1, 3): None,
                                  (2, 1): None, (2, 2): None, (2, 3): None,
                                  (3, 1): None, (3, 2): None, (3, 3): None}
    assert world.light_spots == {}
    assert world.pop_size == 0
    assert world.sum_food_eaten == 0
    assert world.sum_suntan == 0


def test_world_scatter_food(ho, monkeypatch):
    rand = Random(1)
    monkeypatch.setattr(phototaxis, "rand", rand)
    world = ho.world()
    world.scatter_food = phototaxis.World.scatter_food
    world.scatter_food(world, 1)
    assert world.food_locations == {(2, 2): None, (3, 2): None, (1, 2): None}

def test_genome_init(monkeypatch):
    monkeypatch.setattr(phototaxis, "random_transition_matrix", lambda *_, **__: "foo")
    genome = phototaxis.Genome("Foo", "Bar", "Baz", "Bof")
    assert genome.p_dark == "Foo"
    assert genome.p_light == "Bar"
    assert genome.p_dark_wall == "Baz"
    assert genome.p_light_wall == "Bof"

    genome = phototaxis.Genome()
    assert genome.p_dark == "foo"
    assert genome.p_light == "foo"
    assert genome.p_dark_wall == "foo"
    assert genome.p_light_wall == "foo"


def test_worm_init(ho):
    worm = phototaxis.Worm(ho.world(), ho.genome())
    assert worm.world
    assert (worm.x, worm.y) in ho.world().dish_surface
    assert worm.direction in [0, 1, 2, 3]
    assert worm.state in phototaxis.STATES
    assert worm.genome
    assert worm.time_in_light == 1
    assert worm.age == 0
    assert worm.world.pop_size == 1


def test_worm_step(ho):
    worm = ho.worm()
    worm.step = phototaxis.Worm.step
    worm.move = lambda *_: True

    worm.x, worm.y = 1, 2
    worm.step(worm)
    assert worm.age == 1
    assert worm.time_in_light == 2
    assert worm.world.sum_suntan == 2

    worm.x, worm.y = 2, 2
    worm.step(worm)
    assert worm.age == 2
    assert worm.time_in_light == 1
    assert worm.world.sum_suntan == 1


def test_worm_move(monkeypatch, capsys, ho):
    worm = ho.worm()
    worm.move = phototaxis.Worm.move
    worm.move_forward = None
    worm.move_backward = None
    monkeypatch.setattr(worm, "move_forward", lambda *_: print("move_forward() called"))
    monkeypatch.setattr(worm, "move_backward", lambda *_: print("move_backward() called"))

    # NOTE: x, y, and time in light will never change in these tests, because the move_fwd/rev() functions are patched
    # Move fwd
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.05)

    worm.move(worm)
    out, err = capsys.readouterr()
    assert worm.x == 2
    assert worm.y == 2
    assert worm.direction == 0
    assert worm.state == "fwd"
    assert worm.time_in_light == 1
    assert out == "move_forward() called\n"

    # Move rev
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.19)
    worm.move(worm)
    out, err = capsys.readouterr()
    assert worm.x == 2
    assert worm.y == 2
    assert worm.direction == 0
    assert worm.state == "rev"
    assert worm.time_in_light == 1
    assert out == "move_backward() called\n"

    # Move left
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.39)
    worm.move(worm)
    out, err = capsys.readouterr()
    assert worm.x == 2
    assert worm.y == 2
    assert worm.direction == 3
    assert worm.state == "left"
    assert worm.time_in_light == 1
    assert not out

    # Move right
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.65)
    worm.move(worm)
    out, err = capsys.readouterr()
    assert worm.x == 2
    assert worm.y == 2
    assert worm.direction == 0
    assert worm.state == "right"
    assert worm.time_in_light == 1
    assert not out

    # Move stop
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.9)
    worm.move(worm)
    out, err = capsys.readouterr()
    assert worm.x == 2
    assert worm.y == 2
    assert worm.direction == 0
    assert worm.state == "stop"
    assert worm.time_in_light == 1
    assert not out

    # 360 rotation, in the light!
    worm.x, worm.y = 1, 2
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.65)
    worm.move(worm)
    assert worm.direction == 1
    worm.move(worm)
    assert worm.direction == 2
    worm.move(worm)
    assert worm.direction == 3
    worm.move(worm)
    assert worm.direction == 0

    # Off a wall
    monkeypatch.setattr(worm, "move_forward", lambda *_: print("Off the wall!") or True)
    monkeypatch.setattr(phototaxis.rand, "random", lambda *_: 0.05)
    worm.x, worm.y = 1, 1
    worm.move(worm)
    out, err = capsys.readouterr()
    assert out == "Off the wall!\nOff the wall!\n"


# outcome tuples are (direction, (x, y) end)
outcomes = [(0, (2, 1)), (1, (3, 2)), (2, (2, 3)), (3, (1, 2))]


@pytest.mark.parametrize("direction,end", outcomes)
def test_worm_move_forward(direction, end, ho):
    worm = ho.worm()
    worm.move_forward = phototaxis.Worm.move_forward
    worm.direction = direction

    # No wall in the way
    assert not worm.move_forward(worm)
    assert worm.direction == direction
    assert worm.x, worm.y == end

    # Wall in the way
    assert worm.move_forward(worm)
    assert worm.direction == direction
    assert worm.x, worm.y == end


# outcome tuples are (direction, (x, y) end)
outcomes = [(0, (1, 2)), (1, (2, 3)), (2, (3, 2)), (3, (2, 1))]


@pytest.mark.parametrize("direction,end", outcomes)
def test_worm_move_backward(direction, end, ho):
    worm = ho.worm()
    worm.move_backward = phototaxis.Worm.move_backward
    worm.direction = direction

    # No wall in the way
    assert not worm.move_backward(worm)
    assert worm.direction == direction
    assert worm.x, worm.y == end

    # Wall in the way
    assert worm.move_backward(worm)
    assert worm.direction == direction
    assert worm.x, worm.y == end


def test_worm_breed(ho, monkeypatch):
    rand = Random(1)
    monkeypatch.setattr(phototaxis, "rand", rand)
    world = ho.world()
    worm1 = ho.worm()
    worm2 = ho.worm()
    worm1.adjacent_spaces = lambda *_: list(world.dish_surface.keys())
    worm1.breed = phototaxis.Worm.breed
    worm1.genome.p_dark["fwd"] = OrderedDict([(state, 1) for state in phototaxis.STATES])
    worm1.genome.p_light["fwd"] = OrderedDict([(state, 1) for state in phototaxis.STATES])
    worm1.genome.p_dark_wall["fwd"] = OrderedDict([(state, 1) for state in phototaxis.STATES])
    worm1.genome.p_light_wall["fwd"] = OrderedDict([(state, 1) for state in phototaxis.STATES])
    offspring = worm1.breed(worm1, worm2)

    assert offspring.genome.p_dark["fwd"] == OrderedDict([('fwd', 1), ('rev', 1), ('left', 0.2),
                                                          ('right', 1), ('stop', 0.3333333333333333)])
    assert offspring.genome.p_light["fwd"] == OrderedDict([('fwd', 1), ('rev', 0.13333333333333333), ('left', 1),
                                                           ('right', 1), ('stop', 0.3333333333333333)])
    assert offspring.genome.p_dark_wall["fwd"] == OrderedDict([('fwd', 1), ('rev', 0.13333333333333333), ('left', 1),
                                                               ('right', 0.26666666666666666),
                                                               ('stop', 0.3333333333333333)])
    assert offspring.genome.p_light_wall["fwd"] == OrderedDict([('fwd', 1), ('rev', 0.13333333333333333), ('left', 0.2),
                                                                ('right', 0.26666666666666666),
                                                                ('stop', 0.3333333333333333)])
    assert (offspring.x, offspring.y) == (3, 3)
    assert worm1.world.grid[3][3] == 3


def test_worm_adjacent_spaces(ho):
    worm = ho.worm()
    worm.adjacent_spaces = phototaxis.Worm.adjacent_spaces
    assert worm.adjacent_spaces(worm) == [(1, 1), (1, 2), (1, 3),
                                          (2, 1), (2, 2), (2, 3),
                                          (3, 1), (3, 2), (3, 3)]


def test_random_transition_matrix(monkeypatch):
    rand = Random(1)
    monkeypatch.setattr(phototaxis, "rand", rand)
    trans_mat = phototaxis.random_transition_matrix(["a", "b", "c"])
    assert len(trans_mat) == 3
    for key, subset in trans_mat.items():
        assert len(subset) == 3
        assert sum([val for key_key, val in subset.items()]) == 1
    assert trans_mat["a"]["a"] == 0.09523809523809523
