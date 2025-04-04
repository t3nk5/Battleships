import pygame
from pygame import FULLSCREEN

from Ui import Ui

class Game:
    def __init__(self):
        self.size_cell = 40

        self.ui_player1 = Ui(10, 10, offset_y=0)

        space_between_tab = 50
        self.ui_player2 = Ui(10, 10, offset_y=(10 * self.size_cell) + space_between_tab)

        self.ui_player1.screen = pygame.display.set_mode((2880, 1800), FULLSCREEN)

        self.check_finish()

    def check_finish(self):
        running = True
        while running:

            self.ui_player1.draw()
            self.ui_player2.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()

        pygame.quit()