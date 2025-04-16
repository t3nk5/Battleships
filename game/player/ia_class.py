from collections import defaultdict
from typing import Literal, cast

from game.board.battleships import Ship
from game.board.coordinates import Coordinates, random_direction, directions
from game.board.grid import ShotResultData, ShipPlacementData, Grid
from game.player.player import Player
from ia.data import Data


class IA(Player):
    def __init__(self, index: int | None = None):
        super().__init__('IA' + (f'-{index}' if not index else ''))
        Data.load()

    def place_ship(self, ship: Ship):
        placement_index = 0
        best_placements = self._get_best_placements()[ship.type_id]

        while True:
            try:
                placement = best_placements[placement_index] if placement_index < len(
                    best_placements) else self.__random_placement()
                self.defensive_grid.place_boat(ship,
                                               direction := cast(directions, placement['axis']),
                                               coordinates := Coordinates.parse(placement['coordinates']))
                self.ship_placement_datas[ship.id] = ShipPlacementData(
                    ship_type=ship.type_id,
                    coordinates=coordinates,
                    axis=direction,
                )
                break
            except Grid.Exceptions.Placement:
                placement_index += 1

    def shot(self, player_attacked: 'Player', *, coordinates: Coordinates | None = None, turn: int) -> ShotResultData:
        pass

    @staticmethod
    def _get_best_placements():
        value_type = dict[tuple[str, str], list[int | None]]
        stats: dict[int, value_type] = defaultdict(value_type)

        for _, row in Data().placements.iterrows():
            for _, value in row.items():
                if isinstance(value, ShipPlacementData):
                    if (str(value.coordinates), value.axis) not in stats[value.ship_type]:
                        stats[value.ship_type][(str(value.coordinates), value.axis)] = []
                    stats[value.ship_type][(str(value.coordinates), value.axis)].append(value.death_turn)

        best_placements: dict[int, list[dict[Literal['coordinates', 'axis', 'value'], str | float]]] = defaultdict(list)

        for ship_type, placements in stats.items():
            for (coordinates, ax), turns in placements.items():
                adjusted_turns = [t if t is not None else 125 for t in turns]
                avg_turn = sum(adjusted_turns) / len(adjusted_turns)
                best_placements[ship_type].append({
                    'coordinates': coordinates,
                    'axis': ax,
                    'value': avg_turn
                })
            best_placements[ship_type].sort(key=lambda p: p['value'], reverse=True)

        return best_placements

    @staticmethod
    def __random_placement():
        return {
            'coordinates': Coordinates.random(),
            'axis': random_direction(),
        }
