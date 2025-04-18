from abc import ABC, abstractmethod

from pygame import Surface
from game.board.coordinates import Coordinates
from game.player.player import Player


class PlayerUIInterface(ABC):
    @abstractmethod
    def select_coordinates(self) -> Coordinates:
        pass

    @abstractmethod
    def draw(self, window: Surface):
        pass


class PlayerUI(Player, PlayerUIInterface):
    pass
