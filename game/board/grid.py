from dataclasses import dataclass
from enum import Enum
from typing import Union

import numpy as np
import pandas as pd

from game.board.battleships import Ship
from game.board.coordinates import Coordinates, directions
from game.exceptions import GameException


class Case:
    @dataclass
    class Offensive:
        value: float
        is_shot: bool
        is_touch: bool

        def __str__(self):
            return 'X' if self.is_touch else '*' if self.is_shot else ' '

        def __repr__(self):
            return (f'Case(\n'
                    f'   Value={self.value},\n'
                    f'   IsShot={self.is_shot},\n'
                    f'   IsTouch={self.is_touch},\n'
                    f')')

    @dataclass
    class Defensive:
        value: float
        is_empty: bool
        is_shot: bool
        ship_info: Ship.Data | None

        def __str__(self):
            if self.is_empty:
                return '*' if self.is_shot else ' '
            return 'X' if self.is_shot else 'o'

        def __repr__(self):
            ship_info = repr(self.ship_info).replace('\n', "\n   ")
            return (f'Case(\n'
                    f'   Value={self.value},\n'
                    f'   IsEmpty={self.is_empty},\n'
                    f'   IsShot={self.is_shot},\n'
                    f'   ShipInfo={ship_info},\n'
                    f')')


class Grid:
    class Exceptions:
        class Initiation(GameException): pass

        class Placement(GameException): pass

        class Type(GameException): pass

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
        self.initialized: bool = not self.type == Grid.Type.DEFENSIVE

    def __str__(self):
        df = pd.DataFrame({
            x: {
                y: self[x, y]
                for y in self.grid.index
            }
            for x in self.grid.columns
        })

        return str(df) + ('\nNot initialized' if not self.initialized else '')

    def __repr__(self):
        return str(self.grid)

    def __getitem__(self, keys: tuple[
        'Coordinates.Vertical.Type', 'Coordinates.Horizontal.Type']) -> Case.Offensive | Case.Defensive | Case.Offensive:
        x, y = keys
        value = self.grid.loc[y, x]

        match self.type:
            case Grid.Type.OFFENSIVE:
                return Case.Offensive(
                    value=value,
                    is_shot=bool(round(abs(value), 0) % 10),
                    is_touch=bool(round(abs(value) * 10, 0) % 10),
                )
            case Grid.Type.DEFENSIVE:
                is_empty = round(value, 2) == 0
                return Case.Defensive(
                    value=value,
                    is_empty=is_empty,
                    is_shot=bool(round(abs(value * 1000) % 10, 0)),
                    ship_info=Ship.case_data(value) if not is_empty else None,
                )
            case _:
                raise ValueError(f'Invalid grid type: {self.type}')

    @property
    def ships(self):
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Type(f'Only "DEFENSIVE" grids contain boats. Current type: {self.type}')
        if not self.initialized:
            raise Grid.Exceptions.Initiation('Grid must be initialized to retrieve the boats.')

        return pd.DataFrame.from_dict(
            pd.DataFrame([{'uuid': val, 'ID': data.ID, 'index': data.index}
                          for _, row in self.grid.iterrows()
                          for _, val in row.items()
                          if round(val, 2) != 0
                          if (data := Ship.case_data(val))])
            .sort_values(['ID', 'index'])
            .groupby('ID')['uuid'].apply(list)
            .to_dict(), orient='index').transpose()

    @property
    def alive(self) -> bool:
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Type(
                f'Only "DEFENSIVE" grids can be considered as ‘alive’. Current type: {self.type}')
        return any(self.ships.apply(lambda s: Ship.ship_data(s).alive))

    def place_boat(self, boat: Ship, direction: directions, coordinates: Coordinates) -> 'Grid':
        if self.type != Grid.Type.DEFENSIVE:
            raise Grid.Exceptions.Type('A grid must be “DEFENSIVE” to accommodate a boat.')

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

    def get_shot(self, coordinates: Coordinates, touched: bool | None = None) -> Union['ShotResult', None]:
        match self.type:
            case Grid.Type.OFFENSIVE:
                if touched is not None:
                    self.grid.loc[coordinates.y, coordinates.x] = 1 + (0.1 if touched else 0)
                return None
            case Grid.Type.DEFENSIVE:
                case_info = self[coordinates.x, coordinates.y]

                if case_info.is_shot: return ShotResult(already_shot=True)

                self.grid.loc[coordinates.y, coordinates.x] += 0.001

                if not case_info.is_empty:
                    self.grid.loc[coordinates.y, coordinates.x] *= -1
                    return ShotResult(
                        touched=True,
                        sunken=not Ship.ship_data(
                            self.ships[
                                Ship.case_data(self.grid.loc[coordinates.y, coordinates.x]).ID
                            ]).alive
                    )
                return ShotResult()
            case _:
                raise ValueError(f'Invalid grid type: {self.type}')


@dataclass
class ShotResult:
    already_shot: bool = False
    touched: bool = False
    sunken: bool = False
