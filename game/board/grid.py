from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

from game.battleships import Ship
from game.board.coordinates import Coordinates, directions
from game.exceptions import GameException


class Case:
    @dataclass
    class Offensive:
        Value: float
        IsShot: bool
        IsTouch: bool

        def __repr__(self):
            return (f'Case(\n'
                    f'   Value={self.Value},\n'
                    f'   IsShot={self.IsShot},\n'
                    f'   IsTouch={self.IsTouch},\n'
                    f')')

    @dataclass
    class Defensive:
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

    def __getitem__(self, keys: tuple[
        'Coordinates.Vertical.Type', 'Coordinates.Horizontal.Type']) -> Case.Offensive | Case.Defensive | Case.Offensive:
        x, y = keys
        value = self.grid.loc[y, x]

        match self.type:
            case Grid.Type.OFFENSIVE:
                return Case.Offensive(
                    Value=value,
                    IsShot=bool(int(abs(value)) % 10),
                    IsTouch=bool(int(abs(value) * 10) % 10),
                )
            case Grid.Type.DEFENSIVE:
                is_empty = round(value, 2) == 0
                return Case.Defensive(
                    Value=value,
                    IsEmpty=is_empty,
                    IsShot=bool(int(abs(value * 1000) % 10)),
                    ShipInfo=Ship.case_data(value) if not is_empty else None,
                )
            case _:
                raise ValueError(f'Invalid grid type: {self.type}')

    @property
    def ships(self):
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Initiation(f'Only "DEFENSIVE" grids contain boats. Current type: {self.type}')

        return pd.DataFrame.from_dict(
            pd.DataFrame([{'uuid': val, 'ID': data.ID, 'Index': data.Index}
                          for _, row in self.grid.iterrows()
                          for _, val in row.items()
                          if round(val, 2) != 0
                          if (data := Ship.case_data(val))])
            .sort_values(['ID', 'Index'])
            .groupby('ID')['uuid'].apply(list)
            .to_dict(), orient='index').transpose()

    @property
    def alive(self) -> bool:
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Initiation(
                f'Only "DEFENSIVE" grids can be considered as ‘alive’. Current type: {self.type}')
        return any(self.ships.apply(lambda s: Ship.ship_data(s).Alive))

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

    def get_shot(self, coordinates: Coordinates, touched: bool | None = None) -> bool | None:
        match self.type:
            case Grid.Type.OFFENSIVE:
                if touched is not None:
                    self.grid.loc[coordinates.y, coordinates.x] = 1 + (0.1 if touched else 0)
                return None
            case Grid.Type.DEFENSIVE:
                case_info = self[coordinates.x, coordinates.y]

                if case_info.IsShot: return None

                self.grid.loc[coordinates.y, coordinates.x] += 0.001

                if not case_info.IsEmpty:
                    self.grid.loc[coordinates.y, coordinates.x] *= -1
                    return True
                return False
            case _:
                raise ValueError(f'Invalid grid type: {self.type}')
