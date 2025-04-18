from __future__ import annotations

from typing import Literal

import pandas as pd

from game.board.grid import ShipPlacementData, ShotResultData


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
        return (
            f"{'=' * 20} Placements {'=' * 20}\n{self.placements}\n\n"
            f"{'=' * 22} Shots {'=' * 22}\n{self.shots}\n\n"
            f"{'=' * 21} Results {'=' * 21}\n{self.results}"
        )

    def __getitem__(self, key: tuple[Literal['placements', 'shots', 'results'], int | None, Literal[0, 1] | None]):
        df_name, game_index, player_index = key

        df = getattr(self, df_name)

        cols = df.columns
        if game_index is None and player_index is None:
            return df
        elif player_index is None:
            selected_cols = [col for col in cols if int(col[0]) == game_index]
        elif game_index is None:
            selected_cols = [col for col in cols if int(col[1]) == player_index]
        else:
            selected_cols = [(str(game_index), str(player_index))] if (str(game_index),
                                                                       str(player_index)) in cols else []
        return df[selected_cols]

    @staticmethod
    def load(message: bool = True):
        try:
            Data().placements = pd.read_csv(Data.__files['placements'], sep=';', header=[0, 1], index_col=0).map(
                lambda x: ShipPlacementData.parse(x) if isinstance(x, str) else x)
            if message:
                print('Placements data loaded.')
        except FileNotFoundError:
            if message:
                print('No placements data found.')

        try:
            Data().shots = pd.read_csv(Data.__files['shots'], sep=';', header=[0, 1], index_col=0).map(
                lambda x: ShotResultData.parse(x) if isinstance(x, str) else x)
            if message:
                print('Shots data loaded.')
        except FileNotFoundError:
            if message:
                print('No shots data found.')

        try:
            Data().results = pd.read_csv(Data.__files['results'], sep=';', header=[0, 1], index_col=0)
            if message:
                print('Results data loaded.')
        except FileNotFoundError:
            if message:
                print('No results data found.')
        return Data()

    @staticmethod
    def save():
        Data().placements.to_csv(Data.__files['placements'], sep=';')
        Data().shots.to_csv(Data.__files['shots'], sep=';')
        Data().results.to_csv(Data.__files['results'], sep=';')
        print('Data saved.')
        return Data()

    @staticmethod
    def add(game: GameLogic):
        game_index = Data().__game_index
        return (Data()
                .__add_shots(game.datas, game_index)
                .__add_placements(game.datas, game_index)
                .__add_result(game.datas, game_index))

    def __add_shots(self, data: dict[str, pd.DataFrame], game_index: int):
        shots = data['shots'].copy()

        if (shots_index_size := len(shots.index)) > (games_index_size := len(self.shots)):
            self.shots = self.shots.reindex(range(1, shots_index_size + 1))
        else:
            shots = shots.reindex(range(1, games_index_size + 1))

        shots.columns = pd.MultiIndex.from_product([[game_index], shots.columns],
                                                   names=self.shots.columns.names)
        self.shots = pd.concat([self.shots, shots], axis=1)
        return self

    def __add_placements(self, data: dict[str, pd.DataFrame], game_index: int):
        placements = data['placements'].copy()

        if (placements_index_size := len(placements.index)) > (games_index_size := len(self.placements)):
            self.placements = self.placements.reindex(range(1, placements_index_size + 1))
        else:
            placements = placements.reindex(range(1, games_index_size + 1))

        placements.columns = pd.MultiIndex.from_product([[game_index], placements.columns],
                                                        names=self.placements.columns.names)
        self.placements = pd.concat([self.placements, placements], axis=1)
        return self

    def __add_result(self, data: dict[str, pd.DataFrame], game_index: int):
        result = data['result'].copy()

        result.columns = pd.MultiIndex.from_product([[game_index], result.columns],
                                                    names=self.results.columns.names)
        self.results = pd.concat([self.results, result], axis=1)
        return self

    @property
    def __game_index(self):
        cols = [
            *[int(col[0]) for col in Data().placements.columns],
            *[int(col[0]) for col in Data().shots.columns],
            *[int(col[0]) for col in Data().results.columns],
        ]
        if len(cols) == 0 : return 0
        return int(max(cols)) + 1
