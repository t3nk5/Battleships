from game.battleships import Battleship, Carrier, Destroyer, Submarine, PatrolBoat
from game.board.coordinates import Coordinates, select_direction
from game.board.grid import Grid
from utils.prompt import clear


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.defensive_grid = Grid(Grid.Type.DEFENSIVE)
        self.offensive_grid = Grid(Grid.Type.OFFENSIVE)

    def initiate_grid(self):
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
                print(f'{self.defensive_grid}\n\n'
                      f'You are currently placing a {type(ship).__name__} => size: {ship.size}\n')

                while True:
                    try:
                        self.defensive_grid.place_boat(ship, select_direction(), Coordinates.select())
                        break
                    except Grid.Exceptions.Placement as e:
                        clear()
                        print(e.message)
                        print(f'{self.defensive_grid}\n\n'
                              f'You are currently placing a {type(ship).__name__} => size: {ship.size}\n')
