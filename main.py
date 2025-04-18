from typing import Literal
from game.game_class import Game
from ia.data import Data
from ia.stats import Stats
from utils.prompt import clear, Prompt


def play_game(game_mode: Literal['PvP', 'PvIA', 'IAvIA', 'Test']):
    game = Game(game_mode)
    game.initiate()
    game.play()
    game.end()
    Data.add(game).save()


if __name__ == "__main__":
    try:
        Data.load()
        clear(0)

        while True:
            print(f'Welcome to Battleship Game !')
            match Prompt.select(
                'Select:',
                choices=['Play a game', 'View statistics', 'Quit'],
            ).element:
                case 'Play a game':
                    clear(1)
                    play_game(Prompt.select(
                        'Select Game Mode:',
                        choices=['PvP', 'PvIA', 'IAvIA'],
                    ).element)
                case 'View statistics':
                    Stats.select()
                case 'Quit':
                    print()
                    break

            clear(2)
    except KeyboardInterrupt:
        print('''

===============================
        Manual interrupt
===============================
''')

    Data.save()
    print('Thanks for playing!')
