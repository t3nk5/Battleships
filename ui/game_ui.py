from typing import Literal
from game.game_class import GameLogic


class GameUI(GameLogic):
    def init(self, mode: Literal['PvP', 'PvIA', 'IAvIA']):
        super().__init__(mode, 'graphical')
        self.in_deployment: bool = True

    @property
    def is_playing(self):
        return not self.next_player.defensive_grid.alive

    def turn(self):
        coordinates = self.current_player.select_coordinates()
        result = self.current_player.shot(self.next_player, coordinates)
        print(('Touched' + (', Sunk' if result.sunken else '') if result.touched else 'Missed') + ' !')
