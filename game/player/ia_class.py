from collections import defaultdict
from typing import Literal, cast

import numpy as np

from game.board.battleships import Ship
from game.board.coordinates import Coordinates, random_direction, directions
from game.board.grid import ShotResultData, ShipPlacementData, Grid
from game.player.player import Player
from ia.data import Data


class IA(Player):
    def __init__(self, index: int | None = None):
        super().__init__('IA' + (f'-{index}' if index is not None else ''))
        self.shot_logic = ShotAI()

    def place_ship(self, ship: Ship):
        placement_index = 0
        best_placements = self._get_best_placements()[ship.type_id]
        best_placements = best_placements[: int(len(best_placements) * 0.1) + 1]
        np.random.shuffle(best_placements)

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

    def shot(self, player_attacked: 'Player', *, _: Coordinates | None = None, turn: int) -> ShotResultData:
        coordinates = self.shot_logic.get_shot_coordinates()
        shot_result = self.apply_shot_result(player_attacked.defensive_grid.get_shot(coordinates), player_attacked,
                                             turn)
        self.shot_logic.update(shot_result)
        return shot_result

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
    def _random_placement():
        return {
            'coordinates': str(Coordinates.random()),
            'axis': random_direction(),
        }


class ShotAI:
    def __init__(self):
        self.heatmap = Grid(Grid.Type.SHOTS).initialization(Data().shots)
        self.targets: dict[str, list[str]] = defaultdict(list)

    def get_shot_coordinates(self) -> Coordinates:
        max_value = self.heatmap.grid.values.max()

        row_indices, col_indices = np.where(self.heatmap.grid.values == max_value)
        max_coords = [
            f"{Coordinates.Vertical.Values[col]}{Coordinates.Horizontal.Values[row]}"
            for row, col in zip(row_indices, col_indices)
        ]
        print(max_coords)
        return Coordinates.parse(np.random.choice(max_coords))

    def update(self, result: ShotResultData):
        self.heatmap[result.coordinates] -= 10

        if result.already_shot:
            self.heatmap[result.coordinates] -= 5

        if result.touched and not result.sunken:
            if result.coordinates in self.target_list:
                self.remove_targets(result.coordinates)
            self.add_targets(result.coordinates)

        if result.sunken and result.coordinates in self.target_list:
            self.remove_targets(result.coordinates)

    @property
    def target_list(self):
        return [target for sublist in self.targets.values() for target in sublist]

    def add_targets(self, coordinate: Coordinates):
        adjacents = coordinate.get_adjacents()

        for coord in adjacents: self.heatmap[coord] += 3
        self.targets[str(coordinate)].extend(adjacents)

    def remove_targets(self, coordinate: Coordinates):
        keys_targets = [k for k, v in self.targets.items() if coordinate in v]
        for key in keys_targets:
            for coord in self.targets[key]:
                self.heatmap[coord] -= 3
            del self.targets[key]
