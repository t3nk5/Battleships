import pandas as pd

from game.board.battleships import Ship, Battleship, Carrier, Destroyer, Submarine, PatrolBoat
from game.board.coordinates import Coordinates, select_direction
from game.board.grid import Grid, ShotResultData, ShipPlacementData
from utils.prompt import clear


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.defensive_grid = Grid(Grid.Type.DEFENSIVE)
        self.offensive_grid = Grid(Grid.Type.OFFENSIVE)
        self.ship_placement_datas = pd.Series()

    def __str__(self):
        return (f'Offensive grid:\n'
                f'{self.offensive_grid}'
                f'\n\nDefensive grid:\n'
                f'{self.defensive_grid}')

    def initiate_grid(self):
        if self.defensive_grid.initialized: return

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
                while True:
                    print(f'{self.name} grid initialization:', end='\n\n')
                    print(f'{self.defensive_grid}', end='\n\n')
                    print(f'You are currently placing a {type(ship).__name__} => size: {ship.size}', end='\n\n')

                    try:
                        self.defensive_grid.place_boat(ship,
                                                       direction := select_direction(),
                                                       coordinates := Coordinates.select())
                        self.ship_placement_datas[ship.id] = ShipPlacementData(
                            ship_type=ship.type_id,
                            coordinates=coordinates,
                            axis=direction,
                        )
                        break
                    except Grid.Exceptions.Placement as e:
                        clear()
                        print(e.message, end='\n\n')

        self.defensive_grid.initialized = True

    def shot(self, player_attacked: 'Player', *, coordinates: Coordinates | None = None, turn: int) -> ShotResultData:
        coordinates = coordinates or Coordinates.select()
        result = player_attacked.defensive_grid.get_shot(coordinates)

        if not result.already_shot:
            self.offensive_grid.get_shot(coordinates, result.touched)

        if result.sunken:
            player_attacked.ship_placement_datas[Ship.case_data(
                player_attacked.defensive_grid[coordinates.x, coordinates.y].value
            ).ID].death_turn = turn

        return result
