from enum import Enum
from typing import Literal, cast

import numpy as np
import pandas as pd

from game.battleships import Ship, Carrier, Battleship, Destroyer, Submarine, PatrolBoat
from game.board.coordinates import Coordinates
from game.exceptions import GameException
from utils.prompt import Prompt, clear


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

    def __getitem__(self, key: tuple['Coordinates.Vertical.Type', 'Coordinates.Horizontal.Type']):
        x, y = key
        return self.grid.loc[y, x]

    def initiate(self):
        if self.type == Grid.Type.OFFENSIVE:
            raise Grid.Exceptions.Initiation('an “OFFENSIVE” grid cannot be initialized')

        ships = {
            Carrier: 1,
            Battleship: 1,
            Destroyer: 2,
            Submarine: 1,
            PatrolBoat: 1,
        }

        boat_id = 0
        for ship_type, number in ships.items():
            for i in range(number):
                boat_id += 1
                ship = ship_type(ship_id=boat_id)

                clear()
                print(f'{self.grid}\n\n'
                      f'You are currently placing a {type(ship).__name__} => size: {ship.size}\n')

                while True:
                    try:
                        self._place_boat(ship,
                                         self._select_direction(),
                                         Coordinates.select())
                        break
                    except Grid.Exceptions.Placement as e:
                        clear()
                        print(e.message)
                        print(f'{self.grid}\n\n'
                              f'You are currently placing a {type(ship).__name__} => size: {ship.size}\n')

    def _place_boat(self, boat: Ship, direction: Literal['horizontal', 'vertical'], coordinates: Coordinates):
        try:
            end_coordinate = coordinates[direction] + (boat.size - 1)

            boat_placement: pd.Series
            if direction == 'vertical':
                boat_placement = self.grid.loc[coordinates.y.value:end_coordinate, coordinates.x.value]
            elif direction == 'horizontal':
                boat_placement = self.grid.loc[coordinates.y.value, coordinates.x.value:end_coordinate]
            else:
                raise Grid.Exceptions.Placement(f'Wrong placement direction selected: {direction}.')

            if not (boat_placement == 0).all():
                raise Grid.Exceptions.Placement(
                    f"{type(boat).__name__} cannot be placed here, there's already a boat here.")

            if direction == 'vertical':
                self.grid.loc[boat_placement.index, coordinates.x.value] = [boat.uuid + i for i in
                                                                            range(1, boat.size + 1)]
            elif direction == 'horizontal':
                self.grid.loc[coordinates.y.value, boat_placement.index] = [boat.uuid + i for i in
                                                                            range(1, boat.size + 1)]
            else:
                raise Grid.Exceptions.Placement(f'Wrong placement direction selected: {direction}.')

        except IndexError:
            raise Grid.Exceptions.Placement(
                f'{type(boat).__name__} cannot be placed here, as it would extend beyond the playing area.')

    @staticmethod
    def _select_direction() -> Literal['horizontal', 'vertical']:
        return cast(Literal['horizontal', 'vertical'],
                    Prompt.select('Which way do you want to position your ship?',
                                  ['horizontal', 'vertical'],
                                  lambda x: x).element.lower())
