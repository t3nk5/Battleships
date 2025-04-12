from time import sleep
from typing import Literal

from game.player.player import Player
from utils.prompt import Prompt, clear


class Game:
    def __init__(self, mode: Literal['PvP', 'PvIA', 'IAvIA']):
        self.mode = mode
        self.players: list[Player] = []
        self._player_index = 0

        match self.mode:
            case 'PvP':
                self.players.extend([
                    Player(Prompt.get('Enter player 1 name: ', expected_type=str)),
                    Player(Prompt.get('Enter player 2 name: ', expected_type=str)),
                ])
            case 'PvIA':
                raise ValueError('Not implemented yet')
            case 'IAvIA':
                raise ValueError('Not implemented yet')
            case _:
                raise ValueError(f'Unknown mode: {self.mode}')

    @property
    def current_player(self) -> Player:
        return self.players[self._player_index]

    @property
    def _next_index(self) -> int:
        return (self._player_index + 1) % len(self.players)

    @property
    def next_player(self) -> Player:
        return self.players[self._next_index]

    def initiate(self):
        clear(1)
        for player in self.players:
            player.initiate_grid()
            sleep(0.5)
            print(f"{player.name}'s grid initialized !")
            sleep(2)
        clear(1)
        print(f'Grids initialized !')

    def play(self):
        while True:
            clear(3)
            print(f'Player {self.current_player.name} turn:\n')
            print(self.current_player)
            print()

            result = self.current_player.shot(self.next_player)
            print(('Touched' + (', Sunk' if result.sunken else '') if result.touched else 'Missed') + ' !')

            if not self.next_player.defensive_grid.alive: break

            self._player_index = self._next_index

    def end(self):
        clear(2)
        print(f'Player {self.current_player.name} won !\n')
        print(f'Player {self.current_player.name} grid:\n'
              f'{self.current_player.defensive_grid}\n')
        print(f'Player {self.next_player.name} grid:\n'
              f'{self.next_player.defensive_grid}')
