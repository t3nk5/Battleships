from __future__ import annotations

import pandas as pd


class Data:
    __instance: 'Data' = None
    __initialized = False
    __files: dict[str, str] = {
        'placements': './ia/data/placements.csv',
        'shots': './ia/data/shots.csv',
        'results': './ia/data/results.csv',
    }

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__initialized:
            self.placements = pd.DataFrame(
                columns=pd.MultiIndex.from_tuples([], names=["game_index", "player_index"])
            )
            self.shots = pd.DataFrame(
                columns=pd.MultiIndex.from_tuples([], names=["game_index", "player_index"])
            )
            self.results = pd.DataFrame(
                columns=pd.MultiIndex.from_tuples([], names=["game_index", "player_index"])
            )
            Data.__initialized = True

    def __repr__(self):
        return str(self.shots)

    @staticmethod
    def load():
        try:
            Data().placements = pd.read_csv(Data.__files['placements'], sep=';', header=[0, 1], index_col=0).map(
                lambda x: ShipPlacementData.parse(x) if isinstance(x, str) else x)
            Data().shots = pd.read_csv(Data.__files['shots'], sep=';', header=[0, 1], index_col=0).map(
                lambda x: ShotResultData.parse(x) if isinstance(x, str) else x)
            Data().results = pd.read_csv(Data.__files['results'], sep=';', header=[0, 1], index_col=0)

            print('Data loaded.')
        except FileNotFoundError:
            print('No data found.')
        return Data()

    @staticmethod
    def save():
        Data().placements.to_csv(Data.__files['placements'], sep=';')
        Data().shots.to_csv(Data.__files['shots'], sep=';')
        Data().results.to_csv(Data.__files['results'], sep=';')
        print('Data saved.')
        return Data()

    @staticmethod
    def add(game: Game):  # error due to circular import, fixed by __future__. Does not block correct script execution.
        return Data().__add_shots(game.datas).__add_placements(game.datas).__add_result(game.datas)

    def __add_shots(self, data: dict[str, pd.DataFrame]):
        shots = data['shots'].copy()

        if (shots_index_size := len(shots.index)) > (games_index_size := len(self.shots)):
            self.shots = self.shots.reindex(range(1, shots_index_size + 1))
        else:
            shots = shots.reindex(range(1, games_index_size + 1))

        game_index = len(self.shots.columns) // 2 + 1
        shots.columns = pd.MultiIndex.from_product([[game_index], shots.columns],
                                                   names=self.shots.columns.names)
        self.shots = pd.concat([self.shots, shots], axis=1)
        return self

    def __add_placements(self, data: dict[str, pd.DataFrame]):
        placements = data['placements'].copy()

        if (placements_index_size := len(placements.index)) > (games_index_size := len(self.placements)):
            self.placements = self.placements.reindex(range(1, placements_index_size + 1))
        else:
            placements = placements.reindex(range(1, games_index_size + 1))

        game_index = len(self.placements.columns) // 2 + 1
        placements.columns = pd.MultiIndex.from_product([[game_index], placements.columns],
                                                        names=self.placements.columns.names)
        self.placements = pd.concat([self.placements, placements], axis=1)
        return self

    def __add_result(self, data: dict[str, pd.DataFrame]):
        result = data['result'].copy()

        game_index = len(self.results.columns) // 2 + 1
        result.columns = pd.MultiIndex.from_product([[game_index], result.columns],
                                                    names=self.results.columns.names)
        self.results = pd.concat([self.results, result], axis=1)
        return self
