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
            Data().games = pd.read_csv(Data.__files['games'], sep=';', index_col=0)
            Data().games.columns = pd.MultiIndex.from_tuples([eval(col) for col in Data().games.columns],
                                                             names=["game_index", "player_index"])

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

        if actions.shape[0] > Data().games.shape[0]:
            Data().games = Data().games.reindex(range(1, actions.shape[0] + 1))
        else:
            actions = actions.reindex(range(1, Data().games.shape[0] + 1))

        game_index = Data().games.shape[1] // 2 + 1
        actions = actions.set_axis(pd.MultiIndex.from_product([[game_index], actions.columns]), axis=1)
        Data().games = pd.concat([Data().games, actions], axis=1)
        return Data()
