from game.game_class import Game
from utils.prompt import clear

player_index = 0

if __name__ == "__main__":
    clear(0)

    game = Game('PvP')
    game.initiate()
    game.play()
    game.end()
