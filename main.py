from game.game_class import Game
from utils.prompt import clear, Prompt


def play_game():
    game = Game('PvP')
    game.initiate()
    game.play()
    game.end()


if __name__ == "__main__":
    clear(0)

    while True:
        print(f'Welcome to Battleship Game !')
        match Prompt.select(
            'Select:',
            choices=['Play a game', 'View statistics', 'Quit'],
        ).element:
            case 'Play a game':
                clear(1)
                play_game()
            case 'View statistics':
                print('Not Implemented yet')
            case 'Quit':
                print()
                break

        clear(2)
    print('Thanks for playing!')
