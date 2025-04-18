from __future__ import annotations

import pygame

from ui.assets.images import GREENTOKEN, REDTOKEN
from ui.assets.sounds import HITSOUND, MISSSOUND, SHOTSOUND
from ui.elements.token import Token


# from ui.ui_manager import UIManager


class Player:
    def __init__(self):
        self.turn = True

    def makeAttack(self, grid, logicgrid, ui: UIManager):
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][
            1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                ui.tokens.append(Token(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                SHOTSOUND.play()
                                HITSOUND.play()
                                self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            SHOTSOUND.play()
                            MISSSOUND.play()
                            ui.tokens.append(Token(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False
