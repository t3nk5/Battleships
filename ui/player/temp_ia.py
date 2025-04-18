from __future__ import annotations

import random
import pygame

from ui.assets.images import BLUETOKEN, EXPLOSIONIMAGELIST, FIRETOKENIMAGELIST, REDTOKEN
from ui.assets.screen import CELLSIZE, Window
from ui.assets.sounds import HITSOUND, MISSSOUND, SHOTSOUND
from ui.elements.token import Token


# from ui.ui_manager import UIManager


class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Player vs IA'

    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message

    def makeAttack(self, gamelogic, ui: UIManager):
        COMPTURNTIMER = pygame.time.get_ticks()
        if COMPTURNTIMER - ui.turn_timer >= 1000:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)

                if gamelogic[rowX][colX] == ' ' or gamelogic[rowX][colX] == 'O':
                    validChoice = True

            if gamelogic[rowX][colX] == 'O':
                ui.tokens.append(
                    Token(REDTOKEN, ui.pGameGrid[rowX][colX], 'Hit', FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None))
                gamelogic[rowX][colX] = 'T'
                SHOTSOUND.play()
                HITSOUND.play()
                self.turn = False
            else:
                gamelogic[rowX][colX] = 'X'
                ui.tokens.append(Token(BLUETOKEN, ui.pGameGrid[rowX][colX], 'Miss', None, None, None))
                SHOTSOUND.play()
                MISSSOUND.play()
                self.turn = False
        return self.turn

    def draw(self, ui: UIManager):
        if self.turn:
            Window.screen().blit(self.status, (ui.cGameGrid[0][0][0] - CELLSIZE, ui.cGameGrid[-1][-1][1] + CELLSIZE))
