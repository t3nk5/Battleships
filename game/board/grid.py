from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

from game.battleships import Ship
from game.board.coordinates import Coordinates, directions
from game.exceptions import GameException


@dataclass
class Case:
    Value: float
    IsEmpty: bool
    IsShot: bool
    ShipInfo: Ship.Data | None

    def __repr__(self):
        ship_info = repr(self.ShipInfo).replace('\n', "\n   ")
        return (f'Case(\n'
                f'   Value={self.Value},\n'
                f'   IsEmpty={self.IsEmpty},\n'
                f'   IsShot={self.IsShot},\n'
                f'   ShipInfo={ship_info},\n'
                f')')


class Grid:
    class Exceptions:
        class Initiation(GameException): pass

        class Placement(GameException): pass

    class Type(Enum):
        OFFENSIVE = 0
        DEFENSIVE = 1

    def __init__(self, grid_type: Type):
        self.type: Grid.Type = grid_type
        self.grid = pd.DataFrame(
            np.zeros((10, 10)),
            columns=Coordinates.Vertical.Values,
            index=Coordinates.Horizontal.Values,
        )
        self.grid.columns.name = 'X'
        self.grid.index.name = 'Y'

    def __repr__(self):
        return str(self.grid)

    def __getitem__(self, keys: tuple['Coordinates.Vertical.Type', 'Coordinates.Horizontal.Type']):
        x, y = keys
        value = self.grid.loc[y, x]
        is_empty = round(value, 2) == 0

        return Case(
            Value=value,
            IsEmpty=is_empty,
            IsShot=bool(int(abs(value * 1000) % 10)),
            ShipInfo=Ship.get_data(value) if not is_empty else None,
        )

    def place_boat(self, boat: Ship, direction: directions, coordinates: Coordinates) -> 'Grid':
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Initiation('A grid must be “DEFENSIVE” to accommodate a boat.')

        try:
            end_coordinate = coordinates[direction] + (boat.size - 1)

            boat_placement: pd.Series
            if direction == 'vertical' or direction == 'v':
                boat_placement = self.grid.loc[coordinates.y:end_coordinate, coordinates.x]
            elif direction == 'horizontal' or direction == 'h':
                boat_placement = self.grid.loc[coordinates.y, coordinates.x:end_coordinate]
            else:
                raise Grid.Exceptions.Placement(f'Wrong placement direction selected: {direction}.')

            if not (boat_placement == 0).all():
                raise Grid.Exceptions.Placement(
                    f"{type(boat).__name__} cannot be placed here, there's already a boat here.")

            if direction == 'vertical' or direction == 'v':
                self.grid.loc[boat_placement.index, coordinates.x] = [boat.uuid + i for i in range(1, boat.size + 1)]
            elif direction == 'horizontal' or direction == 'h':
                self.grid.loc[coordinates.y, boat_placement.index] = [boat.uuid + i for i in range(1, boat.size + 1)]
            else:
                raise Grid.Exceptions.Placement(f'Wrong placement direction selected: {direction}.')

        except IndexError:
            raise Grid.Exceptions.Placement(
                f'{type(boat).__name__} cannot be placed here, as it would extend beyond the playing area.')

        return self
