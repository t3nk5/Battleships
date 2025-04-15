from __future__ import annotations

import pandas as pd


class Data:
    __instance: 'Data' = None
    __initialized = False
    __files: dict[str, str] = {
        'games': './ia/data/games.csv',
    }

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__initialized:
            self.games = pd.DataFrame(
                columns=pd.MultiIndex.from_tuples([], names=["game_index", "player_index"])
            )
            Data.__initialized = True

    def __repr__(self):
        return str(self.games)

    @staticmethod
    def load():
        try:
            Data().games = pd.read_csv(Data.__files['games'], sep=';', header=[0, 1], index_col=0)
            print('Data loaded.')
        except FileNotFoundError:
            print('No data found.')
        return Data()

    @staticmethod
    def save():
        Data().games.to_csv(Data.__files['games'], sep=';')
        print('Data saved.')
        return Data()

    @staticmethod
    def add(game: Game):  # error due to circular import, fixed by __future__. Does not block correct script execution.
        actions = game.actions.copy()

        if (actions_index_size := len(actions.index)) > (games_index_size := len(Data().games)):
            Data().games = Data().games.reindex(range(1, actions_index_size + 1))
        else:
            actions = actions.reindex(range(1, games_index_size + 1))

        game_index = len(Data().games.columns) // 2 + 1
        actions.columns = pd.MultiIndex.from_product([[game_index], actions.columns], names=Data().games.columns.names)
        Data().games = pd.concat([Data().games, actions], axis=1)
        return Data()
