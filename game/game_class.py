from time import sleep
from typing import Literal

import pandas as pd

from game.player.ia_class import IA
from game.player.player import Player
from ui.player.player_ui import PlayerUI
from utils.prompt import Prompt, clear


class GameLogic:
    PLAYERS_TYPES: dict[Literal['terminal', 'graphical'], dict[Literal['player', 'ia'], type[Player]]] = {
        'terminal': {
            'player': Player,
            'ia': IA,
        },
        'graphical': {
            'player': PlayerUI,
            'ia': None,
        },
    }

    def __init__(self, mode: Literal['PvP', 'PvIA', 'IAvIA'], type: Literal['terminal', 'graphical'] = 'terminal'):
        self.mode = mode
        self.players: list[Player] = []
        self._player_index = 0
        self.turn_index = 0
        self.datas = {
            'placements': pd.DataFrame(columns=[0, 1]),
            'shots': pd.DataFrame(columns=[0, 1]),
            'result': pd.DataFrame(columns=[0, 1],index=['winner', 'type', 'name']),
        }

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
        match self.mode:
            case 'PvP':
                self.players.extend([
                    Player(Prompt.get('Enter player 1 name: ', expected_type=str)),
                    Player(Prompt.get('Enter player 2 name: ', expected_type=str)),
                ])
            case 'PvIA':
                self.players.extend([
                    Player(Prompt.get('Enter player name: ', expected_type=str)),
                    IA(),
                ])
            case 'IAvIA':
                self.players.extend([
                    IA(1),
                    IA(2),
                ])
            case 'Test':
                pass
            case _:
                raise ValueError(f'Unknown mode: {self.mode}')

        clear(1)
        for player in self.players:
            player.initiate_grid()
            sleep(0.5)
            print(f"{player.name}'s grid initialized !")
            sleep(1.5)
        clear(1)
        print(f'Grids initialized !')
        self.turn_index = 1

    def turn(self):
        clear(2)
        print(f'Player {self.current_player.name} turn:\n')
        if not isinstance(self.current_player, IA):
            print(self.current_player)
        print()

        shot_result = self.current_player.shot(self.next_player, turn=int(self.turn_index))

        if isinstance(self.current_player, IA):
            print(f'{self.current_player.name} has shot in {shot_result.coordinates}')
        print(('Touched' + (', Sunk' if shot_result.sunken else '') if shot_result.touched else 'Missed') + ' !')
        self.datas['shots'].loc[int(self.turn_index), self._player_index] = shot_result
        self.turn_index += 0.5

    def play(self):
        while True:
            self.turn()

            if not self.next_player.defensive_grid.alive: break

            self._player_index = self._next_index

    def end(self):
        clear(2)
        print(f'Player {self.current_player.name} won !\n')
        print(f'Player {self.current_player.name} grid:\n'
              f'{self.current_player.defensive_grid}\n')

        print(f'Player {self.next_player.name} grid:\n'
              f'{self.next_player.defensive_grid}')
        print()

        for index, player in enumerate(self.players):
            self.datas['placements'][index] = player.ship_placement_datas
            self.datas['result'][index] = [index == self._player_index, type(player).__name__, player.name]

        Prompt.get('Press enter to continue', expected_type=str, authorized_empty_entry=True)
