from collections import defaultdict
from matplotlib import pyplot as plt
import seaborn as sns

from game.board.grid import Grid, ShotResultData
from ia.data import Data
from utils.prompt import Prompt


class Stats:
    @staticmethod
    def shots_efficiency():
        heatmap = Grid(Grid.Type.SHOTS).initialization(Data().shots, 1)
        plt.figure(figsize=(8, 6))
        sns.heatmap(heatmap.grid, annot=True, fmt='.2f',cmap='Reds')
        plt.title('Pourcentage de touche des tirs')
        plt.show()

    @staticmethod
    def shots_heatmap():
        heatmap = Grid(Grid.Type.SHOTS)

        for cell in Data().shots.to_numpy().flatten():
            if isinstance(cell, ShotResultData): 
                heatmap[cell.coordinates] += 1

        sns.set_theme()
        sns.heatmap(heatmap.grid, cmap="YlOrRd", annot=True, fmt='g')
        plt.title("Carte de chaleur des tirs")
        plt.show()
    
    @staticmethod
    def games_stats():
        data: dict[str, dict[str, int]] = defaultdict(lambda: {'played': 0, 'win': 0})

        for _, column in Data().results.items():
            data[column['type']]['played'] += 1
            if column['winner'] == 'True':
                data[column['type']]['win'] += 1
        
        types = list(data.keys())
        played = [data[t]['played'] for t in types]
        wins = [data[t]['win'] for t in types]

        x = range(len(types))
        width = 0.35

        fig, ax = plt.subplots()
        ax.bar(x, played, width, label='Parties jouées', color='lightgray')
        ax.bar([p + width for p in x], wins, width, label='Parties gagnées', color='green')

        ax.set_xlabel('Type')
        ax.set_ylabel('Nombre de parties')
        ax.set_title('Parties jouées vs gagnées par type')
        ax.set_xticks([p + width / 2 for p in x])
        ax.set_xticklabels(types)
        ax.legend()

        plt.tight_layout()
        plt.show()

    @staticmethod
    def select():
        match Prompt.select(
            'Which statistic would you like to see?', 
            ['Games results', 'Shots heatmap', 'Shots efficiency'], 
        ).element: 
            case 'Games results':
                Stats.games_stats()
            case 'Shots heatmap':
                Stats.shots_heatmap()
            case 'Shots efficiency':
                Stats.shots_efficiency()